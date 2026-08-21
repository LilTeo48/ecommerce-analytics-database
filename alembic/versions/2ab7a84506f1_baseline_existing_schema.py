"""baseline existing schema

Revision ID: 2ab7a84506f1
Revises:
Create Date: 2026-08-14 16:36:56.441461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2ab7a84506f1"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial e-commerce schema."""

    op.create_table(
        "users",
        sa.Column(
            "user_id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="user",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.CheckConstraint(
            "role IN ('user', 'admin')",
            name="check_user_role",
        ),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "customers",
        sa.Column(
            "customer_id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "first_name",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "last_name",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "city",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "state",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "signup_date",
            sa.Date(),
            nullable=False,
        ),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "products",
        sa.Column(
            "product_id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "product_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "category",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "price",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.Column(
            "stock_quantity",
            sa.Integer(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "price >= 0",
            name="products_price_check",
        ),
        sa.CheckConstraint(
            "stock_quantity >= 0",
            name="products_stock_quantity_check",
        ),
    )

    op.create_table(
        "orders",
        sa.Column(
            "order_id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "customer_id",
            sa.Integer(),
            sa.ForeignKey("customers.customer_id"),
            nullable=False,
        ),
        sa.Column(
            "order_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "order_status",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "total_amount",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.CheckConstraint(
            "total_amount >= 0",
            name="orders_total_amount_check",
        ),
    )

    op.create_table(
        "order_items",
        sa.Column(
            "order_item_id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.order_id"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.product_id"),
            nullable=False,
        ),
        sa.Column(
            "quantity",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "unit_price",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name="order_items_quantity_check",
        ),
        sa.CheckConstraint(
            "unit_price >= 0",
            name="order_items_unit_price_check",
        ),
    )

    op.create_table(
        "payments",
        sa.Column(
            "payment_id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.order_id"),
            nullable=False,
        ),
        sa.Column(
            "payment_date",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "payment_method",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "amount",
            sa.Numeric(10, 2),
            nullable=False,
        ),
        sa.CheckConstraint(
            "amount >= 0",
            name="payments_amount_check",
        ),
        sa.UniqueConstraint("order_id"),
    )

    op.create_table(
        "shipments",
        sa.Column(
            "shipment_id",
            sa.Integer(),
            primary_key=True,
            autoincrement=True,
        ),
        sa.Column(
            "order_id",
            sa.Integer(),
            sa.ForeignKey("orders.order_id"),
            nullable=False,
        ),
        sa.Column(
            "shipment_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "delivery_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "shipping_status",
            sa.String(length=50),
            nullable=True,
        ),
        sa.UniqueConstraint("order_id"),
    )


def downgrade() -> None:
    """Drop the initial e-commerce schema."""

    op.drop_table("shipments")
    op.drop_table("payments")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_table("customers")
    op.drop_table("users")