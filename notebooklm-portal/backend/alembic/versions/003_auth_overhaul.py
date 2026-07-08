"""add password_hash, remove google token columns

Revision ID: 003
Revises: 002
Create Date: 2026-07-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add password_hash column
    op.add_column("users", sa.Column("password_hash", sa.Text(), nullable=True))

    # Remove columns no longer needed (per-user Google tokens)
    op.drop_column("users", "access_token")
    op.drop_column("users", "refresh_token")
    op.drop_column("users", "token_expiry")
    op.drop_column("users", "notebooklm_connected")


def downgrade() -> None:
    op.add_column("users", sa.Column("notebooklm_connected", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.add_column("users", sa.Column("token_expiry", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("refresh_token", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("access_token", sa.Text(), nullable=True))
    op.drop_column("users", "password_hash")
