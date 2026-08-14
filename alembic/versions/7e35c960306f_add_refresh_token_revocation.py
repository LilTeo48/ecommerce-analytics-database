"""add refresh token revocation

Revision ID: 7e35c960306f
Revises: 3c126f756e20
Create Date: 2026-08-14 17:17:40.676142

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7e35c960306f"
down_revision: Union[str, Sequence[str], None] = "3c126f756e20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add refresh token revocation storage."""

    op.create_table(
        "refresh_tokens",
        sa.Column(
            "refresh_token_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "jti",
            sa.String(length=36),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "refresh_token_id"
        ),
    )

    op.create_index(
        op.f("ix_refresh_tokens_jti"),
        "refresh_tokens",
        ["jti"],
        unique=True,
    )

    op.create_index(
        op.f("ix_refresh_tokens_user_id"),
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove refresh token revocation storage."""

    op.drop_index(
        op.f("ix_refresh_tokens_user_id"),
        table_name="refresh_tokens",
    )

    op.drop_index(
        op.f("ix_refresh_tokens_jti"),
        table_name="refresh_tokens",
    )

    op.drop_table(
        "refresh_tokens"
    )