"""add last login timestamp to users

Revision ID: 3c126f756e20
Revises: 2ab7a84506f1
Create Date: 2026-08-14 16:51:46.125817

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c126f756e20"
down_revision: Union[str, Sequence[str], None] = "2ab7a84506f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add last_login_at to users."""
    op.add_column(
        "users",
        sa.Column(
            "last_login_at",
            sa.DateTime(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Remove last_login_at from users."""
    op.drop_column(
        "users",
        "last_login_at",
    )