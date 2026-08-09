from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import User
from app.security import get_current_user


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
    current_user: User = Depends(get_current_user),
):
    return crud.get_revenue_summary(db)


@router.get(
    "/revenue/monthly",
    response_model=list[schemas.MonthlyRevenueResponse],
)
def monthly_revenue(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_monthly_revenue(db)


@router.get(
    "/revenue/by-category",
    response_model=list[schemas.CategoryRevenueResponse],
)
def revenue_by_category(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_revenue_by_category(db)


@router.get(
    "/products/top-selling",
    response_model=list[schemas.TopProductResponse],
)
def top_selling_products(
    limit: int = Query(default=5, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_top_selling_products(db, limit=limit)


@router.get(
    "/customers/top",
    response_model=list[schemas.TopCustomerResponse],
)
def top_customers(
    limit: int = Query(default=5, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_top_customers(db, limit=limit)


# -------------------------
# Additional Analytics
# -------------------------


@router.get(
    "/orders/by-status",
    response_model=list[schemas.OrderStatusAnalyticsResponse],
)
def orders_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_orders_by_status_analytics(db)


@router.get(
    "/payments/by-method",
    response_model=list[schemas.PaymentMethodAnalyticsResponse],
)
def payments_by_method(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_payments_by_method_analytics(db)


@router.get(
    "/shipments/by-status",
    response_model=list[schemas.ShipmentStatusAnalyticsResponse],
)
def shipments_by_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_shipments_by_status_analytics(db)


@router.get(
    "/inventory/value",
    response_model=schemas.InventoryValueResponse,
)
def inventory_value(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_inventory_value(db)


@router.get(
    "/products/never-ordered",
    response_model=list[schemas.NeverOrderedProductResponse],
)
def never_ordered_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_never_ordered_products(db)