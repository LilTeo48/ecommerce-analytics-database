"""add email verification

Revision ID: 774b3f2bb1e1
Revises: 67b712df3cf7
Create Date: 2026-08-17 23:32:17.899337

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "774b3f2bb1e1"
down_revision: Union[str, Sequence[str], None] = "67b712df3cf7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            server_default="false",
            nullable=False,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "verification_token",
            sa.String(length=64),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "verification_token_expires_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.create_unique_constraint(
        "uq_users_verification_token",
        "users",
        ["verification_token"],
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "uq_users_verification_token",
        "users",
        type_="unique",
    )

    op.drop_column(
        "users",
        "verification_token_expires_at",
    )

    op.drop_column(
        "users",
        "verification_token",
    )

    op.drop_column(
        "users",
        "is_verified",
    )