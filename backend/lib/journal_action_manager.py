from datetime import datetime
from typing import List
from pydantic import EmailStr
from sqlalchemy.orm import Session
from models.database import get_db
from models import models
from passlib.context import CryptContext
from fastapi import HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi import Request, HTTPException, status

data_success_message = "Data retrieved successfully"
data_failed_message = "No data retrieved or its empty "
deleted_message  =  "Deleted successfully"


def set_return_values(db_data):
    status = True if db_data else False
    message = data_success_message if status else data_failed_message
    return {"message": message, "status": status}

def save_journal(db: Session,request: any):
    journal = models.Journal(**request.dict(), date=datetime.utcnow())
    db.add(journal)
    db.commit()
    db.refresh(journal)
    status = True if journal else False
    return {"status": status, "data": journal}

def journal_update(db: Session, request: any, journal_id: int ):
    journal = db.query(models.Journal).filter(models.Journal.id == journal_id).first()
    if not journal:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail="Journal not found")
    
    if request.title is not None:
        journal.title = request.title
    if request.content is not None:
        journal.content = request.content
    if request.category is not None:
        journal.category = request.category

    db.commit()
    db.refresh(journal)
    data_status = True if journal else False
    journaldfs = db.query(models.Journal).filter(models.Journal.id == journal_id).first()

    print(journaldfs.title)
    return {"status": data_status, "data": journaldfs}


def get_journal(db: Session, id: int):
    db_data  = db.query(models.Journal).filter(models.Journal.id == id).first()
    data_keys = set_return_values(db_data)
    return {"message": data_keys["message"], "status": data_keys["status"], "data": db_data}

def get_journals(db: Session, skip: int,limit: int):
    db_data = db.query(models.Journal).offset(skip).limit(limit).all()
    data_keys = set_return_values(db_data)
    return {"message": data_keys["message"], "status": data_keys["status"], "data": db_data}

def delete_journal(db: Session, id: int):
    user = db.query(models.Journal).filter(models.Journal.id == id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    db.delete(user)
    db.commit()
    return {"message": deleted_message }

def get_filtered_journals( db: Session ,  
    start_date: datetime = Query(None, description="Start date for filtering journals"),
    end_date: datetime = Query(None, description="End date for filtering journals"))-> List[models.Journal]:
    query = db.query(models.Journal)
    if start_date:
        query = query.filter(models.Journal.date >= start_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
    if end_date:
        query = query.filter(models.Journal.date <= end_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
    journals = query.all()
    data_keys = set_return_values(query)

    return {"message": data_keys["message"], "status": data_keys["status"], "data": journals}

def get_daily_journals(db: Session, date: datetime):
    status = False
    start = datetime(date.year, date.month, date.day)
    end = start + timedelta(days=1)
    journals = db.query(models.Journal).filter(models.Journal.created_at >= start, models.Journal.created_at < end).all()
    if journals:
        status = True
        return {"message": "Journal data", "status": status , "data": journals}

    return {"message": "No Journal data retrieved ", "status": False , "data": []}


def get_weekly_journals(db: Session, date: datetime):
    status = False
    start = date - timedelta(days=date.weekday())
    end = start + timedelta(days=7)
    journals = db.query(models.Journal).filter(models.Journal.created_at >= start, models.Journal.created_at < end).all()
    if journals:
        status = True
        return {"message": "Journal data", "status": status , "data": journals}

    return {"message": "No Journal data retrieved ", "status": False , "data": []}


def get_monthly_journals(db: Session, year: int, month: int):
    status = False
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    journals = db.query(models.Journal).filter(models.Journal.created_at >= start, models.Journal.created_at < end).all()
    if journals:
        status = True
        return {"message": "Journal data", "status": status , "data": journals}

    return {"message": "No Journal data retrieved ", "status": False , "data": []}
