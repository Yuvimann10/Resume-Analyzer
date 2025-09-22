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
    allow_headers = ['*'],    
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