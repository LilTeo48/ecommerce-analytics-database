from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import text

load_dotenv(".env")

from app import auth
from app.database import SessionLocal
from app.routers import (
    analytics,
    customers,
    inventory,
    orders,
    payments,
    products,
    shipments,
)

app = FastAPI(
    title="E-Commerce Analytics API",
    version="1.0.0",
)

app.include_router(customers.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(payments.router)
app.include_router(shipments.router)
app.include_router(inventory.router)
app.include_router(analytics.router)
app.include_router(auth.router)


@app.get("/")
def root():
    return {"message": "API is running!"}


@app.get("/db")
def test_db():
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))

    return {"database": "Connected!"}