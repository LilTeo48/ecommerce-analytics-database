from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/inventory",
    tags=["Inventory"],
)


@router.get(
    "/",
    response_model=list[schemas.InventoryResponse],
)
def get_inventory(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_inventory(db, skip=skip, limit=limit)


@router.get(
    "/low-stock",
    response_model=list[schemas.InventoryResponse],
)
def get_low_stock_products(
    threshold: int = Query(default=10, ge=0),
    db: Session = Depends(get_db),
):
    return crud.get_low_stock_products(db, threshold=threshold)


@router.get(
    "/{product_id}",
    response_model=schemas.InventoryResponse,
)
def get_product_inventory(
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


@router.put(
    "/{product_id}/stock",
    response_model=schemas.InventoryResponse,
)
def set_product_stock(
    product_id: int,
    stock_update: schemas.StockUpdate,
    db: Session = Depends(get_db),
):
    product = crud.set_product_stock(
        db,
        product_id=product_id,
        stock_quantity=stock_update.stock_quantity,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product


@router.patch(
    "/{product_id}/adjust",
    response_model=schemas.InventoryResponse,
)
def adjust_product_stock(
    product_id: int,
    stock_adjustment: schemas.StockAdjustment,
    db: Session = Depends(get_db),
):
    try:
        product = crud.adjust_product_stock(
            db,
            product_id=product_id,
            adjustment=stock_adjustment.adjustment,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    return product