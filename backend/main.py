from datetime import timedelta
from lib.custom_oauth2 import OAuth2EmailPasswordRequestForm
from pydantic import BaseModel, EmailStr
from lib.validators import *
from fastapi import FastAPI, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from models.database import engine, get_db
from models import models
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, List
from passlib.context import CryptContext
from lib.utils import create_access_token, verify_token
from lib.config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from lib.auth_manager import VerifyTokenMiddleware
from lib.user_action_manager import *
from lib.journal_action_manager import *
from lib.utils import verify_token
from fastapi.responses import JSONResponse
from datetime import datetime
from fastapi import FastAPI, Depends, Query
from pydantic import Field


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

app.add_middleware(VerifyTokenMiddleware)


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
    data =[ user.name , user.email]
    return Token(access_token=access_token, token_type="bearer", data=data, status = True ,message="Login successful")

@app.post("/sign_up/")
def create_user(request: UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(request.password)
    user_exists = check_user_exists(db,request.email)
    username = request.name.replace(" ","_")
    if user_exists:
        return {"Message": "sign up failed email already exists "}
    
    user = save_user(db,username,request.email,hashed_password)
    return {"Message":"Successfully signed up "}

@app.post("/update_user")
def update_user_details(request: UserUpdate,db: Session = Depends(get_db)):
    user = get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = update_user_data(db, user, request)
    if update_user_data:
        data = [updated_user.name, updated_user.email]
        return {"message": "Update Done","status": True ,"data": data}

    return updated_user

@app.get("/user_profile/" )
def read_user(request: UserProfile, db: Session = Depends(get_db)):
    user = get_user_profile(db,request.id)
    if not user:
        return {"message":"User profile Not found"}
    return user

@app.get("/users/" )
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    users = get_users(db, skip, limit)
    if not users:
        return {"message":"Users Not found"}
    return users

@app.post("/new_journal")
def create_journal( request: JournalCreate, db: Session = Depends(get_db)):
    print(request)
    journal =  save_journal(db,request)
    return {"message": "Journal created","status": journal["status"] ,"data": journal["data"]}

@app.post("/update_journal/{journal_id}")
def update_journal(journal_id: int, request: JournalUpdate, db: Session = Depends(get_db)):
    journal = journal_update(db,request,journal_id)
    print("journal---")
    print(journal)
    if not journal['status']:
        return {"message": "Problem updating JOurnal", "status": False , "data": []}
        
    return {"message": "Journal updated successfully", "status": "success", "data": journal}

@app.get("/get_journal")
def read_journals(request: JournalInDB, db: Session = Depends(get_db)):
    journal= get_journal(db,request.id)
    return {"message": journal["message"] ,"status": journal["status"] , "data": journal["data"]}

@app.get("/list_journals")
def read_journals(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    journals = get_journals(db,skip,limit)
    return {"message": journals["message"] , "status": journals["status"] , "data": journals["data"]}

@app.post("/delete_journal/{journal_id}")
def read_journals(journal_id: int,request: JournalOut,db: Session = Depends(get_db)):
    deleted_journal = delete_journal(db,journal_id)
    return {"message": deleted_journal["message"], "status": True,"data": {}}

@app.get("/get_filtered_journals")
def read_filtered_journals(request: JournalsOutFiltered, db: Session = Depends(get_db)):
    filtered_journals = get_filtered_journals(db,request.start_date,request.end_date)
    return {"message": filtered_journals["message"], "status": filtered_journals["status"], "data": filtered_journals["data"]}

@app.get("/journals/daily")
def read_daily_journals(date: datetime = Query(None), db: Session = Depends(get_db)):
    if not date:
        date = datetime.utcnow()
    journals = get_daily_journals(db, date)
    return journals

@app.get("/journals/weekly")
def read_weekly_journals(date: datetime = Query(None), db: Session = Depends(get_db)):
    if not date:
        date = datetime.utcnow()
    journals = get_weekly_journals(db, date)
    return journals

@app.get("/journals/monthly")
def read_monthly_journals(year: int, month: int, db: Session = Depends(get_db)):
    journals = get_monthly_journals(db, year, month)
    return journals

@app.get("/journals/grouped")
def get_journals_grouped_by_category(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size")
):
    status = False
    query = db.query(models.Journal).order_by(models.Journal.category)
    journals = query.all()
    if query:
        status = True
    grouped_journals = {}
    for journal in journals:
        if journal.category not in grouped_journals:
            print(journal.category)
            grouped_journals[journal.category] = []
        grouped_journals[journal.category].append(JournalSchema(**journal.__dict__))

    return {"message": "Data retrived", "status": status, "data": grouped_journals}