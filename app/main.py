from fastapi import FastAPI
from sqlalchemy import text

from app.database import SessionLocal

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API is running!"}


@app.get("/db")
def test_db():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"database": "Connected!"}