from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models import models
from passlib.context import CryptContext
from fastapi.encoders import jsonable_encoder

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

not_autheticated_message ={"message": "missing , corrupted or incorrect token"}

def get_users(db: Session, skip: int ,limit: int):
    users = db.query(models.User.id, models.User.name, models.User.email).offset(skip).limit(limit).all()
    user_list = [UserOut(id=user[0], name=user[1], email=user[2]) for user in users]
    return jsonable_encoder(user_list)

def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_profile(db: Session, id: int):
    data = db.query(models.User).filter(models.User.id == id).first()
    if not data:
        return False
    user = {"id": data.id, "name": data.name, "email": data.email}
    return user

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
