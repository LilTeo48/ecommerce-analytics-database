from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -------------------------
# Customer schemas
# -------------------------

class CustomerBase(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    city: str | None = Field(default=None, max_length=100)
    state: str | None = Field(default=None, max_length=50)
    signup_date: date


class CustomerCreate(CustomerBase):
    pass


class CustomerResponse(CustomerBase):
    customer_id: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Product schemas
# -------------------------

class ProductBase(BaseModel):
    product_name: str = Field(min_length=1, max_length=100)
    category: str | None = Field(default=None, max_length=50)
    price: Decimal = Field(ge=0, decimal_places=2)
    stock_quantity: int = Field(ge=0)


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    product_id: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Order item schemas
# -------------------------

class OrderItemBase(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0, decimal_places=2)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    order_item_id: int
    order_id: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Order schemas
# -------------------------

class OrderBase(BaseModel):
    customer_id: int = Field(gt=0)
    order_date: date
    order_status: str = Field(min_length=1, max_length=30)
    total_amount: Decimal = Field(ge=0, decimal_places=2)


class OrderCreate(OrderBase):
    pass


class OrderResponse(OrderBase):
    order_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponse(OrderResponse):
    order_items: list[OrderItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Payment schemas
# -------------------------

class PaymentBase(BaseModel):
    order_id: int = Field(gt=0)
    payment_date: date
    payment_method: str | None = Field(default=None, max_length=50)
    amount: Decimal = Field(ge=0, decimal_places=2)


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    payment_id: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Shipment schemas
# -------------------------

class ShipmentBase(BaseModel):
    order_id: int = Field(gt=0)
    shipment_date: date | None = None
    delivery_date: date | None = None
    shipping_status: str | None = Field(default=None, max_length=50)


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentResponse(ShipmentBase):
    shipment_id: int

    model_config = ConfigDict(from_attributes=True)