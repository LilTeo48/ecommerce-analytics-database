from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post(
    "/",
    response_model=schemas.OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order(
    order: schemas.OrderCreate,
    db: Session = Depends(get_db),
):
    customer = crud.get_customer(db, order.customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return crud.create_order(db, order)


@router.get(
    "/",
    response_model=list[schemas.OrderResponse],
)
def get_orders(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_orders(db, skip=skip, limit=limit)


@router.get(
    "/customer/{customer_id}",
    response_model=list[schemas.OrderResponse],
)
def get_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = crud.get_customer(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return crud.get_orders_by_customer(db, customer_id)


@router.get(
    "/{order_id}",
    response_model=schemas.OrderResponse,
)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = crud.get_order(db, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    return order