from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    city: Mapped[str | None] = mapped_column(String(100))
    state: Mapped[str | None] = mapped_column(String(50))
    signup_date: Mapped[date] = mapped_column(Date, nullable=False)

    orders: Mapped[list["Order"]] = relationship(
        back_populates="customer",
    )


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_product_price"),
        CheckConstraint(
            "stock_quantity >= 0",
            name="check_product_stock_quantity",
        ),
    )

    product_id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    category: Mapped[str | None] = mapped_column(String(50))
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )
    stock_quantity: Mapped[int] = mapped_column(nullable=False)

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="product",
    )


class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        CheckConstraint(
            "total_amount >= 0",
            name="check_order_total_amount",
        ),
    )

    order_id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.customer_id"),
        nullable=False,
    )
    order_date: Mapped[date] = mapped_column(Date, nullable=False)
    order_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    customer: Mapped["Customer"] = relationship(
        back_populates="orders",
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
    )
    payment: Mapped["Payment | None"] = relationship(
        back_populates="order",
        uselist=False,
    )
    shipment: Mapped["Shipment | None"] = relationship(
        back_populates="order",
        uselist=False,
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        CheckConstraint(
            "quantity > 0",
            name="check_order_item_quantity",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="check_order_item_unit_price",
        ),
    )

    order_item_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.product_id"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        back_populates="order_items",
    )
    product: Mapped["Product"] = relationship(
        back_populates="order_items",
    )


class Payment(Base):
    __tablename__ = "payments"
    __table_args__ = (
        CheckConstraint(
            "amount >= 0",
            name="check_payment_amount",
        ),
    )

    payment_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id"),
        unique=True,
        nullable=False,
    )
    payment_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )
    payment_method: Mapped[str | None] = mapped_column(String(50))
    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        back_populates="payment",
    )


class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.order_id"),
        unique=True,
        nullable=False,
    )
    shipment_date: Mapped[date | None] = mapped_column(Date)
    delivery_date: Mapped[date | None] = mapped_column(Date)
    shipping_status: Mapped[str | None] = mapped_column(String(50))

    order: Mapped["Order"] = relationship(
        back_populates="shipment",
    )

class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'admin')",
            name="check_user_role",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="user",
        server_default="user",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    failed_login_attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    verification_token: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        unique=True,
    )

    verification_token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    refresh_token_id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    jti: Mapped[str] = mapped_column(
        String(36),
        unique=True,
        nullable=False,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )    