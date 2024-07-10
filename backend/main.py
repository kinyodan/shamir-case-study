from datetime import timedelta
from lib.custom_oauth2 import OAuth2EmailPasswordRequestForm
from pydantic import BaseModel, EmailStr

from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from models import models
from models.database import engine, get_db
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from typing import Annotated
from passlib.context import CryptContext
from lib.utils import create_access_token, verify_token
from lib.config import ACCESS_TOKEN_EXPIRE_MINUTES
from lib.user_action_manager import get_user,verify_password,authenticate_user,save_user,check_user_exists,not_autheticated_message,get_users
from lib.journal_action_manager import get_journals,save_journal,get_journal,delete_journal
from lib.auth_manager import verify_token_middleware

models.Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.middleware('http')(verify_token_middleware)

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

class UsersInDB(BaseModel):
    id: int
    email: EmailStr
    name: str


class Token(BaseModel):
    access_token: str
    token_type: str

class JournalCreate(BaseModel):
    owner_id: int
    title: str
    content: str
    category: str
    date: str

class JournalInDB(BaseModel):
    id: int

class JournalOut(BaseModel):
    id: int    


@app.get("/")
def read_root():
    return {"Hello world"}

@app.post("/login", response_model=Token)
async def login_for_access_token(request: UserInDB,db: Session = Depends(get_db),):
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/sign_up/")
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(request.password)
    user_exists = check_user_exists(db,request.email)
    if user_exists:
        return {"msg": "sign up failed email already exists "}
    
    user = save_user(db,request.name,request.email,hashed_password)
    print(user)
    return {"msg":"Successfully signed up "}

@app.get("/users/" )
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = get_users(db, skip, limit)
    return users

@app.post("/new_journal")
def read_journals( request: JournalCreate, db: Session = Depends(get_db)):
    print(request)
    journal =  save_journal(db,request)
    return {"message": "Journals created successfully"}

@app.get("/get_journal")
def read_journals(request: JournalInDB, db: Session = Depends(get_db)):
    journal= get_journal(db,request.id)
    return {"message": journal["message"] ,"status": journal["status"] , "data": journal["data"]}

@app.get("/list_journals")
def read_journals(token: Annotated[str, Depends(oauth2_scheme)],skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    journals = get_journals(db,skip,limit)
    print(journals["status"])
    return {"message": journals["message"] , "status": journals["status"] , "data": journals["data"]}


@app.post("/delete_journal")
def read_journals(request: JournalOut,db: Session = Depends(get_db)):
    deleted_journal = delete_journal(db,request.id)
    return {"message": deleted_journal["message"]}


