"""add password reset

Revision ID: c75c7e2556de
Revises: 774b3f2bb1e1
Create Date: 2026-08-18 22:03:38.953869

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c75c7e2556de"
down_revision: Union[str, Sequence[str], None] = "774b3f2bb1e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column(
            "password_reset_token",
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "password_reset_token_expires_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_users_password_reset_token",
        "users",
        ["password_reset_token"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "uq_users_password_reset_token",
        "users",
        type_="unique",
    )

    op.drop_column(
        "users",
        "password_reset_token_expires_at",
    )

    op.drop_column(
        "users",
        "password_reset_token",
    )