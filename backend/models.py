from sqlmodel import SQLModel, Field 
from typing import Optional 
from datetime import datetime 

class User(SQLModel,table=True):
    id: Optional[int] = Field(default = None, primary_key = True) 
    username: Optional[str] 
    email: Optional[str] 
    created_at: datetime = Field(default_factory = datetime.utcnow)

class Resume(SQLModel,table=True):
    id: Optional[int] = Field(default = None, primary_key = True)
    user_id: int
    original_text: str 
    improved_text: Optional[str] = None 
    created_at: datetime = Field(default_factory = datetime.utcnow)




    