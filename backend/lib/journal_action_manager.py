from datetime import datetime
from typing import List
from pydantic import EmailStr
from sqlalchemy.orm import Session
from models.database import get_db
from models import models
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, Query, status

data_success_message = "Data retrieved successfully"
data_failed_message = "No data retrieved or its empty "
deleted_message  =  "Deleted successfully"

def set_return_values(db_data):
    status = True if db_data else False
    message = data_success_message if status else data_failed_message
    return {"message": message, "status": status}

def save_journal(db: Session,request: any):
    db_journal = models.Journal(**request.dict(), date=datetime.utcnow())
    db.add(db_journal)
    db.commit()
    db.refresh(db_journal)
    status = True if db_journal else False
    return {"status": status, "data": db_journal}

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
