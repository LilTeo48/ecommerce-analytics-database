from fastapi import FastAPI
from sqlalchemy import text

from app.database import SessionLocal
from app.routers import customers, products

app = FastAPI(
    title="E-Commerce Analytics API",
    version="1.0.0",
)

app.include_router(customers.router)
app.include_router(products.router)


@app.get("/")
def root():
    return {"message": "API is running!"}


@app.get("/db")
def test_db():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))

    return {"database": "Connected!"}