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


from database import engine, create_db_and_tables, get_session, test_connections
from models import User, Resume 

