from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post(
    "/",
    response_model=schemas.CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db),
):
    existing_customer = crud.get_customer_by_email(db, customer.email)

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists.",
        )

    return crud.create_customer(db, customer)


@router.get(
    "/",
    response_model=list[schemas.CustomerResponse],
)
def get_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return crud.get_customers(db, skip=skip, limit=limit)


@router.get(
    "/{customer_id}",
    response_model=schemas.CustomerResponse,
)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = crud.get_customer(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return customer


@router.delete(
    "/{customer_id}",
    response_model=schemas.CustomerResponse,
)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
):
    customer = crud.delete_customer(db, customer_id)

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found.",
        )

    return customer