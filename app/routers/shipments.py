from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(
    prefix="/shipments",
    tags=["Shipments"],
)


@router.post(
    "/",
    response_model=schemas.ShipmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_shipment(
    shipment: schemas.ShipmentCreate,
    db: Session = Depends(get_db),
):
    order = crud.get_order(db, shipment.order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    existing_shipment = crud.get_shipment_by_order(
        db,
        shipment.order_id,
    )

    if existing_shipment is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This order already has a shipment.",
        )

    return crud.create_shipment(db, shipment)


@router.get(
    "/",
    response_model=list[schemas.ShipmentResponse],
)
def get_shipments(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return crud.get_shipments(db, skip=skip, limit=limit)


@router.get(
    "/order/{order_id}",
    response_model=schemas.ShipmentResponse,
)
def get_shipment_by_order(
    order_id: int,
    db: Session = Depends(get_db),
):
    order = crud.get_order(db, order_id)

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found.",
        )

    shipment = crud.get_shipment_by_order(db, order_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found for this order.",
        )

    return shipment


@router.get(
    "/{shipment_id}",
    response_model=schemas.ShipmentResponse,
)
def get_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
):
    shipment = crud.get_shipment(db, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    return shipment


@router.patch(
    "/{shipment_id}/status",
    response_model=schemas.ShipmentResponse,
)
def update_shipment_status(
    shipment_id: int,
    shipping_status: str = Query(min_length=1, max_length=50),
    db: Session = Depends(get_db),
):
    shipment = crud.update_shipment_status(
        db,
        shipment_id=shipment_id,
        shipping_status=shipping_status,
    )

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    return shipment


@router.delete(
    "/{shipment_id}",
    response_model=schemas.ShipmentResponse,
)
def delete_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
):
    shipment = crud.delete_shipment(db, shipment_id)

    if shipment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shipment not found.",
        )

    return shipment