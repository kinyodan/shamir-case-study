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


models.Base.metadata.create_all(bind=engine)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

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

class Token(BaseModel):
    access_token: str
    token_type: str

def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db ,email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def save_user(db: Session,name: str,email: EmailStr, hashed_password: str):
    db_user = models.User(name = name,email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def check_user_exists(db: Session, email: EmailStr):
    return True if get_user(db,email) else False
 

 
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
    
    db_user = save_user(db,request.name,request.email,hashed_password)
    print(db_user)
    return {"msg":"Successfully signed up "}

@app.get("/users/")
def read_users(token: Annotated[str, Depends(oauth2_scheme)],skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users
