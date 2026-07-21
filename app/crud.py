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
