from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db
from app.models import User
from app.security import get_current_user, require_admin

router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post(
    "/",
    response_model=schemas.PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment(
    payment: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    order = crud.get_order(
        db,
        payment.order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    existing_payment = crud.get_payment_by_order(
        db,
        payment.order_id,
    )

    if existing_payment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This order already has a payment.",
        )

    return crud.create_payment(
        db,
        payment,
    )


@router.get(
    "/",
    response_model=list[schemas.PaymentResponse],
)
def get_payments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_payments(
        db,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/order/{order_id}",
    response_model=schemas.PaymentResponse,
)
def get_payment_by_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    order = crud.get_order(
        db,
        order_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    payment = crud.get_payment_by_order(
        db,
        order_id,
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this order.",
        )

    return payment


@router.get(
    "/{payment_id}",
    response_model=schemas.PaymentResponse,
)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payment = crud.get_payment(
        db,
        payment_id,
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    return payment


@router.delete(
    "/{payment_id}",
    response_model=schemas.PaymentResponse,
)
def delete_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    payment = crud.delete_payment(
        db,
        payment_id,
    )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found.",
        )

    return payment