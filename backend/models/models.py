from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Journal(Base):
    __tablename__ = "journals"
    id = Column(Integer,primary_key=True,index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String)
    content = Column(String)
    category = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    owner = relationship('User', back_populates='journals')
    created_at = Column(DateTime, default=datetime.utcnow)

User.journals = relationship('Journal', back_populates='owner')
