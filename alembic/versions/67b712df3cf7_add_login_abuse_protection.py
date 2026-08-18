"""add login abuse protection

Revision ID: 67b712df3cf7
Revises: 7e35c960306f
Create Date: 2026-08-17 23:13:56.792830

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "67b712df3cf7"
down_revision: Union[str, Sequence[str], None] = "7e35c960306f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "failed_login_attempts",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "locked_until",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "users",
        "locked_until",
    )

    op.drop_column(
        "users",
        "failed_login_attempts",
    )