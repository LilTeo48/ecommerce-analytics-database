from sqlalchemy.orm import Session

from app import models, schemas


# -------------------------
# Customer CRUD
# -------------------------

def create_customer(
    db: Session,
    customer: schemas.CustomerCreate,
) -> models.Customer:
    db_customer = models.Customer(**customer.model_dump())

    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)

    return db_customer


def get_customer(
    db: Session,
    customer_id: int,
) -> models.Customer | None:
    return (
        db.query(models.Customer)
        .filter(models.Customer.customer_id == customer_id)
        .first()
    )


def get_customer_by_email(
    db: Session,
    email: str,
) -> models.Customer | None:
    return (
        db.query(models.Customer)
        .filter(models.Customer.email == email)
        .first()
    )


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Customer]:
    return (
        db.query(models.Customer)
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_customer(
    db: Session,
    customer_id: int,
) -> models.Customer | None:
    customer = get_customer(db, customer_id)

    if customer is None:
        return None

    db.delete(customer)
    db.commit()

    return customer


# -------------------------
# Product CRUD
# -------------------------

def create_product(
    db: Session,
    product: schemas.ProductCreate,
) -> models.Product:
    db_product = models.Product(**product.model_dump())

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


def get_product(
    db: Session,
    product_id: int,
) -> models.Product | None:
    return (
        db.query(models.Product)
        .filter(models.Product.product_id == product_id)
        .first()
    )


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Product]:
    return (
        db.query(models.Product)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_product_stock(
    db: Session,
    product_id: int,
    stock_quantity: int,
) -> models.Product | None:
    product = get_product(db, product_id)

    if product is None:
        return None

    product.stock_quantity = stock_quantity

    db.commit()
    db.refresh(product)

    return product


def delete_product(
    db: Session,
    product_id: int,
) -> models.Product | None:
    product = get_product(db, product_id)

    if product is None:
        return None

    db.delete(product)
    db.commit()

    return product

# -------------------------
# Order CRUD
# -------------------------


def create_order(
    db: Session,
    order: schemas.OrderCreate,
) -> models.Order:
    db_order = models.Order(**order.model_dump())

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    return db_order


def get_order(
    db: Session,
    order_id: int,
) -> models.Order | None:
    return (
        db.query(models.Order)
        .filter(models.Order.order_id == order_id)
        .first()
    )


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Order]:
    return (
        db.query(models.Order)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_orders_by_customer(
    db: Session,
    customer_id: int,
) -> list[models.Order]:
    return (
        db.query(models.Order)
        .filter(models.Order.customer_id == customer_id)
        .all()
    )

# -------------------------
# Payment CRUD
# -------------------------

def create_payment(
    db: Session,
    payment: schemas.PaymentCreate,
) -> models.Payment:
    db_payment = models.Payment(**payment.model_dump())

    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)

    return db_payment


def get_payment(
    db: Session,
    payment_id: int,
) -> models.Payment | None:
    return (
        db.query(models.Payment)
        .filter(models.Payment.payment_id == payment_id)
        .first()
    )


def get_payment_by_order(
    db: Session,
    order_id: int,
) -> models.Payment | None:
    return (
        db.query(models.Payment)
        .filter(models.Payment.order_id == order_id)
        .first()
    )


def get_payments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Payment]:
    return (
        db.query(models.Payment)
        .offset(skip)
        .limit(limit)
        .all()
    )


def delete_payment(
    db: Session,
    payment_id: int,
) -> models.Payment | None:
    payment = get_payment(db, payment_id)

    if payment is None:
        return None

    db.delete(payment)
    db.commit()

    return payment  

# -------------------------
# Shipment CRUD
# -------------------------

def create_shipment(
    db: Session,
    shipment: schemas.ShipmentCreate,
) -> models.Shipment:
    db_shipment = models.Shipment(**shipment.model_dump())

    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)

    return db_shipment


def get_shipment(
    db: Session,
    shipment_id: int,
) -> models.Shipment | None:
    return (
        db.query(models.Shipment)
        .filter(models.Shipment.shipment_id == shipment_id)
        .first()
    )


def get_shipment_by_order(
    db: Session,
    order_id: int,
) -> models.Shipment | None:
    return (
        db.query(models.Shipment)
        .filter(models.Shipment.order_id == order_id)
        .first()
    )


def get_shipments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Shipment]:
    return (
        db.query(models.Shipment)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_shipment_status(
    db: Session,
    shipment_id: int,
    shipping_status: str,
) -> models.Shipment | None:
    shipment = get_shipment(db, shipment_id)

    if shipment is None:
        return None

    shipment.shipping_status = shipping_status

    db.commit()
    db.refresh(shipment)

    return shipment


def delete_shipment(
    db: Session,
    shipment_id: int,
) -> models.Shipment | None:
    shipment = get_shipment(db, shipment_id)

    if shipment is None:
        return None

    db.delete(shipment)
    db.commit()

    return shipment     