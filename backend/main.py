import os 
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File 
from fastapi.middleware.cors import CORSMiddleware 
from sqlmodel import Session, select 
from typing import List, Optional 
import uvicorn 
import requests
import json 
from pydantic import BaseModel
import PyPDF2 
import io
from datetime import datetime
from database import engine, create_db_and_tables, get_session, test_connections
from models import User, Resume 

app = FastAPI(
    title = 'Resume analyzer with Qwen llm', 
    description = 'api for improving resumes', 
    version = '1.0.0'
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins = ['http://localhost:3000','http://localhost:5173']
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']    
)


class UserCreate(BaseModel):
    username:str 
    email:str

class UserResponse(BaseModel):
    id:int
    username:str
    email:str
    created_at: datetime

class ResumeCreate(BaseModel):
    user_id:int
    original_text:str

class ResumeResponse(BaseModel):
    id:int
    user_id:int
    original_text:str
    improved_text:Optional[str]
    created_at: datetime 

class AnalysisRequests(BaseModel):
    job_description:Optional[str]=None
    improvement_focus:Optional[str]='general'

#qwen configuration
QWEN_API_URL = os.getenv('QWEN_API_URL','http://localhost:11434/api/generate')
QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen2.5:7b-instruct')

def extract_text_from_pdf(file_content:bytes) -> str:
    try: 
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f'error extract text from pdf: {str(e)}'
        ) 
    
        

def call_qwen_llm(prompt:str) -> str: 
    try: 
        payload = {
            'model' : QWEN_MODEL, 
            'prompt' : prompt, 
            'stream' : False
        }
        response = requests.post(QWEN_API_URL, json=payload, timeout = 120)
        response.raise_for_status()

        result = response.json()
        return result.get('response','').strip()
    
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE,
            detial = f'error call qwel llm: {str(e)}'
        )

def create_improvement_prompt(resume_text:str, job_description:Optional[str] = None, focus:str = 'general') -> str:
    base_prompt = f'''Analyze my resume for ATS compatibility. Identify missing keywords or formatting issues that might prevent it from passing through applicant tracking systems.
    Your expertise includes:
    ATS (Applicant Tracking System) optimization
    Action verb selection and impact statement creation
    Quantifying achievements effectively
    Industry-specific terminology and best practices
    Modern resume formatting and structure'''

    base_prompt += f"""===== ORIGINAL RESUME =====
    {resume_text}
    ===== END OF ORIGINAL RESUME ====="""
    if job_description:
        base_prompt += f"""===== TARGET JOB DESCRIPTION =====
        {job_description}
        ===== END OF JOB DESCRIPTION =====
        IMPORTANT: Carefully analyze the job description and identify:
        1. Key required skills and qualifications
        2. Important keywords and phrases that should appear in the resume
        3. Specific responsibilities mentioned
        4. Technical tools or technologies required
        Tailor the resume to highlight experiences and skills that match these requirements."""

    focus_instruction = {
        'general': """
===== IMPROVEMENT FOCUS: GENERAL ENHANCEMENT =====

Apply these improvements to the resume:

    1. IMPACT & CLARITY:
   - Transform weak bullet points into strong impact statements
   - Start each bullet with powerful action verbs (Led, Developed, Implemented, Achieved, etc.)
   - Remove passive voice and make statements direct and confident
   
    2. QUANTIFICATION:
   - Add numbers, percentages, and metrics wherever possible
   - Examples: "Increased revenue by 30%", "Managed team of 8 developers", "Reduced costs by $50K annually"
   
    3. STRUCTURE & FORMATTING:
   - Ensure consistent formatting throughout
   - Use standard section headers (Experience, Education, Skills, etc.)
   - Keep bullet points concise (1-2 lines maximum)
   
    4. ATS OPTIMIZATION:
   - Remove special characters and complex formatting
   - Use standard fonts and simple structure
   - Include relevant keywords naturally
   - Avoid tables, text boxes, and headers/footers

    5. PROFESSIONAL LANGUAGE:
   - Remove clichés and buzzwords ("team player", "hard worker", etc.)
   - Use industry-specific terminology
   - Maintain professional tone throughout
""",
'technical': """
===== IMPROVEMENT FOCUS: TECHNICAL SKILLS EMPHASIS =====

Optimize this resume for technical roles:

    1. TECHNICAL SKILLS SHOWCASE:
   - Create a prominent Technical Skills section with categories
   - List programming languages, frameworks, tools, and technologies
   - Use correct version numbers and spellings (React.js, Node.js, Python 3.x)
   
    2. PROJECT HIGHLIGHTS:
   - Emphasize technical projects and their impact
   - Include tech stack used for each project
   - Mention scale (users served, data processed, performance metrics)
   
    3. TECHNICAL ACHIEVEMENTS:
   - Highlight system improvements, optimizations, and innovations
   - Quantify technical impact (e.g., "Reduced API response time by 60%")
   - Mention architecture decisions and their rationale
   
    4. PROBLEM-SOLVING:
   - Showcase debugging, troubleshooting, and optimization skills
   - Highlight complex technical challenges overcome
   - Mention algorithmic improvements or efficiency gains
   
    5. TECHNICAL KEYWORDS:
   - Include relevant technical keywords from the job description
   - Use industry-standard terminology
   - Mention methodologies (Agile, Scrum, CI/CD, TDD)
""",
'leadership': """
===== IMPROVEMENT FOCUS: LEADERSHIP & MANAGEMENT =====

Enhance leadership and management aspects:

    1. LEADERSHIP SCOPE:
   - Clearly state team sizes managed (e.g., "Led team of 12 engineers")
   - Mention budget responsibilities if applicable
   - Highlight cross-functional collaboration and stakeholder management
   
    2. STRATEGIC IMPACT:
   - Emphasize strategic decisions and their business impact
   - Show how your leadership drove company/team success
   - Include metrics on team performance improvements
   
    3. PEOPLE DEVELOPMENT:
   - Highlight mentoring and coaching experiences
   - Mention hiring, onboarding, and training responsibilities
   - Show career advancement of team members you mentored
   
    4. PROJECT/PROGRAM MANAGEMENT:
   - Emphasize end-to-end project ownership
   - Show successful delivery of complex initiatives
   - Quantify project scope, timeline, and budget
   
    5. COMMUNICATION & INFLUENCE:
   - Highlight presentations to leadership or external stakeholders
   - Show conflict resolution and negotiation skills
   - Mention change management and organizational improvements
""",
'ats': """
===== IMPROVEMENT FOCUS: ATS (APPLICANT TRACKING SYSTEM) OPTIMIZATION =====

Optimize this resume to pass ATS screening:

    1. KEYWORD OPTIMIZATION:
   - Extract keywords from the job description
   - Naturally incorporate these keywords throughout the resume
   - Use exact phrases from job posting when appropriate
   - Include both acronyms and full terms (e.g., "API" and "Application Programming Interface")
   
    2. STANDARD FORMATTING:
   - Use simple, clean formatting with no tables or columns
   - Stick to standard section headings (Work Experience, Education, Skills)
   - Use standard bullet points (•) not custom symbols
   - Avoid headers, footers, text boxes, and images
   
    3. FILE FORMAT COMPATIBILITY:
   - Ensure resume works as plain text
   - Use standard fonts (Arial, Calibri, Times New Roman)
   - Avoid special characters and symbols

    4. SECTION ORGANIZATION:
   - Place most relevant sections first
   - Use clear, standard section names
   - Ensure dates are in consistent format (MM/YYYY)

    5. SKILLS SECTION:
   - Create a dedicated skills section with categorized skills
   - List skills exactly as they appear in job descriptions
   - Include both soft and technical skills relevant to the role
""",
    }



    


    

    







    
