from datetime import date
from decimal import Decimal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


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

class OrderItemCreate(BaseModel):
    product_id: int = Field(gt=0)
    quantity: int = Field(gt=0)


class OrderItemResponse(BaseModel):
    order_item_id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Order schemas
# -------------------------

class OrderBase(BaseModel):
    customer_id: int = Field(gt=0)
    order_date: date
    order_status: str = Field(min_length=1, max_length=30)
    total_amount: Decimal = Field(ge=0, decimal_places=2)


class OrderCreate(BaseModel):
    customer_id: int = Field(gt=0)
    order_date: date
    order_status: str = Field(min_length=1, max_length=30)
    items: list[OrderItemCreate] = Field(min_length=1)

    @field_validator("items")
    @classmethod
    def products_must_be_unique(
        cls,
        items: list[OrderItemCreate],
    ) -> list[OrderItemCreate]:
        product_ids = [
            item.product_id
            for item in items
        ]

        if len(product_ids) != len(set(product_ids)):
            raise ValueError(
                "Each product may only appear once per order."
            )

        return items


class OrderResponse(OrderBase):
    order_id: int

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponse(OrderResponse):
    order_items: list[OrderItemResponse] = Field(
        default_factory=list
    )

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
    shipping_status: str | None = Field(
        default=None,
        max_length=50,
    )


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentResponse(ShipmentBase):
    shipment_id: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Inventory schemas
# -------------------------

class StockUpdate(BaseModel):
    stock_quantity: int = Field(ge=0)


class StockAdjustment(BaseModel):
    adjustment: int

    @field_validator("adjustment")
    @classmethod
    def adjustment_cannot_be_zero(
        cls,
        value: int,
    ) -> int:
        if value == 0:
            raise ValueError(
                "Adjustment cannot be zero."
            )

        return value


class InventoryResponse(BaseModel):
    product_id: int
    product_name: str
    category: str | None
    stock_quantity: int

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Analytics schemas
# -------------------------

class RevenueSummary(BaseModel):
    total_revenue: Decimal
    average_order_value: Decimal
    total_orders: int


class MonthlyRevenueResponse(BaseModel):
    month: date
    revenue: Decimal


class CategoryRevenueResponse(BaseModel):
    category: str | None
    revenue: Decimal


class TopProductResponse(BaseModel):
    product_id: int
    product_name: str
    units_sold: int
    revenue: Decimal


class TopCustomerResponse(BaseModel):
    customer_id: int
    first_name: str
    last_name: str
    total_orders: int
    total_spent: Decimal


# -------------------------
# Additional analytics schemas
# -------------------------

class OrderStatusAnalyticsResponse(BaseModel):
    order_status: str
    total_orders: int
    total_revenue: Decimal


class PaymentMethodAnalyticsResponse(BaseModel):
    payment_method: str | None
    payment_count: int
    total_amount: Decimal


class ShipmentStatusAnalyticsResponse(BaseModel):
    shipping_status: str | None
    shipment_count: int


class InventoryValueResponse(BaseModel):
    total_units: int
    total_inventory_value: Decimal


class NeverOrderedProductResponse(BaseModel):
    product_id: int
    product_name: str
    category: str | None
    stock_quantity: int


# -------------------------
# Authentication schemas
# -------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str