from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.post(
    "/",
    response_model=schemas.ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
):
    return crud.create_product(db, product)


@router.get(
    "/",
    response_model=list[schemas.ProductResponse],
)
def get_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_products(db, skip=skip, limit=limit)


@router.get(
    "/{product_id}",
    response_model=schemas.ProductResponse,
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = crud.get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product


@router.patch(
    "/{product_id}/stock",
    response_model=schemas.ProductResponse,
)
def update_product_stock(
    product_id: int,
    stock_quantity: int = Query(ge=0),
    db: Session = Depends(get_db),
):
    product = crud.update_product_stock(
        db,
        product_id=product_id,
        stock_quantity=stock_quantity,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product


@router.delete(
    "/{product_id}",
    response_model=schemas.ProductResponse,
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = crud.delete_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product