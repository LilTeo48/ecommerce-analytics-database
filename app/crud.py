from decimal import Decimal

from sqlalchemy import func, select
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


class OrderCreationError(Exception):
    """Base exception for transactional order creation."""


class CustomerNotFoundError(OrderCreationError):
    def __init__(self, customer_id: int):
        self.customer_id = customer_id
        super().__init__(
            f"Customer {customer_id} not found."
        )


class ProductNotFoundError(OrderCreationError):
    def __init__(self, product_id: int):
        self.product_id = product_id
        super().__init__(
            f"Product {product_id} not found."
        )


class InsufficientStockError(OrderCreationError):
    def __init__(
        self,
        product_id: int,
        requested: int,
        available: int,
    ):
        self.product_id = product_id
        self.requested = requested
        self.available = available

        super().__init__(
            f"Insufficient stock for product {product_id}. "
            f"Requested {requested}, available {available}."
        )


def create_order(
    db: Session,
    order: schemas.OrderCreate,
) -> models.Order:
    try:
        customer = db.get(
            models.Customer,
            order.customer_id,
        )

        if customer is None:
            raise CustomerNotFoundError(
                order.customer_id
            )

        validated_items: list[
            tuple[schemas.OrderItemCreate, models.Product]
        ] = []

        total_amount = Decimal("0.00")

        for item in order.items:
            product = db.scalar(
                select(models.Product)
                .where(
                    models.Product.product_id
                    == item.product_id
                )
                .with_for_update()
            )

            if product is None:
                raise ProductNotFoundError(
                    item.product_id
                )

            if product.stock_quantity < item.quantity:
                raise InsufficientStockError(
                    product_id=product.product_id,
                    requested=item.quantity,
                    available=product.stock_quantity,
                )

            total_amount += (
                product.price * item.quantity
            )

            validated_items.append(
                (item, product)
            )

        db_order = models.Order(
            customer_id=order.customer_id,
            order_date=order.order_date,
            order_status=order.order_status,
            total_amount=total_amount,
        )

        db.add(db_order)

        # Flush gives us order_id without committing.
        db.flush()

        for item, product in validated_items:
            db_order_item = models.OrderItem(
                order_id=db_order.order_id,
                product_id=product.product_id,
                quantity=item.quantity,
                unit_price=product.price,
            )

            db.add(db_order_item)

            product.stock_quantity -= item.quantity

        # One commit for:
        # - order
        # - order items
        # - inventory changes
        db.commit()

        db.refresh(db_order)

        return db_order

    except Exception:
        db.rollback()
        raise


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
        .filter(
            models.Order.customer_id == customer_id
        )
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

# -------------------------
# Inventory CRUD
# -------------------------

def get_inventory(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Product]:
    return (
        db.query(models.Product)
        .order_by(models.Product.stock_quantity.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_low_stock_products(
    db: Session,
    threshold: int = 10,
) -> list[models.Product]:
    return (
        db.query(models.Product)
        .filter(models.Product.stock_quantity <= threshold)
        .order_by(models.Product.stock_quantity.asc())
        .all()
    )


def set_product_stock(
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


def adjust_product_stock(
    db: Session,
    product_id: int,
    adjustment: int,
) -> models.Product | None:
    product = get_product(db, product_id)

    if product is None:
        return None

    new_quantity = product.stock_quantity + adjustment

    if new_quantity < 0:
        raise ValueError("Stock quantity cannot be negative.")

    product.stock_quantity = new_quantity

    db.commit()
    db.refresh(product)

    return product

# -------------------------
# Analytics queries
# -------------------------

def get_revenue_summary(
    db: Session,
) -> dict:
    total_revenue = (
        db.query(func.coalesce(func.sum(models.Order.total_amount), 0))
        .scalar()
    )

    total_orders = db.query(func.count(models.Order.order_id)).scalar()

    average_order_value = (
        db.query(func.coalesce(func.avg(models.Order.total_amount), 0))
        .scalar()
    )

    return {
        "total_revenue": total_revenue,
        "average_order_value": average_order_value,
        "total_orders": total_orders,
    }


def get_monthly_revenue(
    db: Session,
) -> list[dict]:
    month = func.date_trunc("month", models.Order.order_date).label("month")
    revenue = func.sum(models.Order.total_amount).label("revenue")

    rows = (
        db.query(month, revenue)
        .group_by(month)
        .order_by(month)
        .all()
    )

    return [
        {
            "month": row.month.date(),
            "revenue": row.revenue,
        }
        for row in rows
    ]


def get_revenue_by_category(
    db: Session,
) -> list[dict]:
    revenue = func.sum(
        models.OrderItem.quantity * models.OrderItem.unit_price
    ).label("revenue")

    rows = (
        db.query(
            models.Product.category.label("category"),
            revenue,
        )
        .join(
            models.OrderItem,
            models.Product.product_id == models.OrderItem.product_id,
        )
        .group_by(models.Product.category)
        .order_by(revenue.desc())
        .all()
    )

    return [
        {
            "category": row.category,
            "revenue": row.revenue,
        }
        for row in rows
    ]


def get_top_selling_products(
    db: Session,
    limit: int = 5,
) -> list[dict]:
    units_sold = func.sum(models.OrderItem.quantity).label("units_sold")
    revenue = func.sum(
        models.OrderItem.quantity * models.OrderItem.unit_price
    ).label("revenue")

    rows = (
        db.query(
            models.Product.product_id,
            models.Product.product_name,
            units_sold,
            revenue,
        )
        .join(
            models.OrderItem,
            models.Product.product_id == models.OrderItem.product_id,
        )
        .group_by(
            models.Product.product_id,
            models.Product.product_name,
        )
        .order_by(units_sold.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "units_sold": row.units_sold,
            "revenue": row.revenue,
        }
        for row in rows
    ]


def get_top_customers(
    db: Session,
    limit: int = 5,
) -> list[dict]:
    total_orders = func.count(models.Order.order_id).label("total_orders")
    total_spent = func.sum(models.Order.total_amount).label("total_spent")

    rows = (
        db.query(
            models.Customer.customer_id,
            models.Customer.first_name,
            models.Customer.last_name,
            total_orders,
            total_spent,
        )
        .join(
            models.Order,
            models.Customer.customer_id == models.Order.customer_id,
        )
        .group_by(
            models.Customer.customer_id,
            models.Customer.first_name,
            models.Customer.last_name,
        )
        .order_by(total_spent.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "customer_id": row.customer_id,
            "first_name": row.first_name,
            "last_name": row.last_name,
            "total_orders": row.total_orders,
            "total_spent": row.total_spent,
        }
        for row in rows
    ]

# -------------------------
# Additional analytics queries
# -------------------------

def get_orders_by_status_analytics(
    db: Session,
) -> list[dict]:
    total_orders = func.count(
        models.Order.order_id
    ).label("total_orders")

    total_revenue = func.sum(
        models.Order.total_amount
    ).label("total_revenue")

    rows = (
        db.query(
            models.Order.order_status,
            total_orders,
            total_revenue,
        )
        .group_by(models.Order.order_status)
        .order_by(total_orders.desc())
        .all()
    )

    return [
        {
            "order_status": row.order_status,
            "total_orders": row.total_orders,
            "total_revenue": row.total_revenue,
        }
        for row in rows
    ]


def get_payments_by_method_analytics(
    db: Session,
) -> list[dict]:
    payment_count = func.count(
        models.Payment.payment_id
    ).label("payment_count")

    total_amount = func.sum(
        models.Payment.amount
    ).label("total_amount")

    rows = (
        db.query(
            models.Payment.payment_method,
            payment_count,
            total_amount,
        )
        .group_by(models.Payment.payment_method)
        .order_by(total_amount.desc())
        .all()
    )

    return [
        {
            "payment_method": row.payment_method,
            "payment_count": row.payment_count,
            "total_amount": row.total_amount,
        }
        for row in rows
    ]


def get_shipments_by_status_analytics(
    db: Session,
) -> list[dict]:
    shipment_count = func.count(
        models.Shipment.shipment_id
    ).label("shipment_count")

    rows = (
        db.query(
            models.Shipment.shipping_status,
            shipment_count,
        )
        .group_by(models.Shipment.shipping_status)
        .order_by(shipment_count.desc())
        .all()
    )

    return [
        {
            "shipping_status": row.shipping_status,
            "shipment_count": row.shipment_count,
        }
        for row in rows
    ]


def get_inventory_value(
    db: Session,
) -> dict:
    total_units = func.coalesce(
        func.sum(models.Product.stock_quantity),
        0,
    ).label("total_units")

    total_inventory_value = func.coalesce(
        func.sum(
            models.Product.stock_quantity
            * models.Product.price
        ),
        0,
    ).label("total_inventory_value")

    row = (
        db.query(
            total_units,
            total_inventory_value,
        )
        .one()
    )

    return {
        "total_units": row.total_units,
        "total_inventory_value": row.total_inventory_value,
    }


def get_never_ordered_products(
    db: Session,
) -> list[models.Product]:
    return (
        db.query(models.Product)
        .outerjoin(
            models.OrderItem,
            models.Product.product_id
            == models.OrderItem.product_id,
        )
        .filter(
            models.OrderItem.order_item_id.is_(None)
        )
        .order_by(models.Product.product_name.asc())
        .all()
    )