from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/revenue/summary",
    response_model=schemas.RevenueSummary,
)
def revenue_summary(
    db: Session = Depends(get_db),
):
    return crud.get_revenue_summary(db)


@router.get(
    "/revenue/monthly",
    response_model=list[schemas.MonthlyRevenueResponse],
)
def monthly_revenue(
    db: Session = Depends(get_db),
):
    return crud.get_monthly_revenue(db)


@router.get(
    "/revenue/by-category",
    response_model=list[schemas.CategoryRevenueResponse],
)
def revenue_by_category(
    db: Session = Depends(get_db),
):
    return crud.get_revenue_by_category(db)


@router.get(
    "/products/top-selling",
    response_model=list[schemas.TopProductResponse],
)
def top_selling_products(
    limit: int = Query(default=5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_top_selling_products(db, limit=limit)


@router.get(
    "/customers/top",
    response_model=list[schemas.TopCustomerResponse],
)
def top_customers(
    limit: int = Query(default=5, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_top_customers(db, limit=limit)