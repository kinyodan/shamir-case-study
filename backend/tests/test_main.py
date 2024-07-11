import os
from sqlalchemy import create_engine
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from main import app
from sqlalchemy.ext.declarative import declarative_base
from models.database import get_db
from uuid import uuid4

DATABASE_URL = os.getenv("DATABASE_URL")
test_engine = create_engine(DATABASE_URL)
Base = declarative_base()
Base.metadata.create_all(bind=test_engine)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
rand_token = uuid4()

@pytest.fixture(scope="module")
def test_app():
    yield client

def test_read_root(test_app):
    response = test_app.get("/")
    assert response.status_code == 200
    assert response.json() == ["Hello world"]

def test_sign_up(test_app):
    response = test_app.post("/sign_up/", json={"name": f"Test User{rand_token}", "password": "testpassword", "email": f"testuser{rand_token}@example.com"})
    assert response.status_code == 200
    assert response.json() == {"msg":"Successfully signed up "}

def test_login(test_app):
    response = test_app.post("/login", json={"email": f"testuser{rand_token}@example.com", "password": "testpassword"})
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token is not None

def test_create_journal(test_app):
    login_response = test_app.post("/login", json={"email": f"testuser{rand_token}@example.com", "password": "testpassword"})
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    response = test_app.post("/new_journal", json={"owner_id": 1, "title": "My Journal", "content": "Journal content", "category": "General"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == True

def test_get_journals(test_app):
    login_response = test_app.post("/login", json={"email": f"testuser{rand_token}@example.com", "password": "testpassword"})
    token = login_response.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}
    test_app.post("/new_journal", json={"owner_id": 1, "title": "My Journal", "content": "Journal content", "category": "General"}, headers=headers)
    response = test_app.get("/list_journals", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == True
