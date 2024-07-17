from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Any
from models import models


class UserCreate(BaseModel):
    name: str
    password: str
    email: EmailStr

class UserOut(BaseModel):
    id: int
    email: EmailStr

class UserInDB(BaseModel):
    password: str
    email: EmailStr

class UserProfile(BaseModel):
    id: int    

class UsersInDB(BaseModel):
    id: int
    email: EmailStr
    name: str

class Token(BaseModel):
    message: str
    status: bool
    access_token: str
    token_type: str
    data: List[Any] 

class UserUpdate(BaseModel):
    name: str
    email: EmailStr

class JournalCreate(BaseModel):
    title: str
    content: str
    category: str
    
class JournalInDB(BaseModel):
    id: int
class JournalOut(BaseModel):
    id: int    

class JournalsOutFiltered(BaseModel):
    start_date: datetime
    end_date: datetime

class JournalUpdate(BaseModel):
    title: str 
    content: str 
    category: str 

class GroupedJournals(BaseModel):
    category: str
    journals: List[Any]


class JournalSchema(BaseModel):
    id: int
    owner_id: Any
    title: str
    content: str
    category: str
    date: datetime

    class Config:
        orm_mode = True

class PaginatedGroupedJournals(BaseModel):
    total: int
    limit: int
    offset: int
    data: Any  