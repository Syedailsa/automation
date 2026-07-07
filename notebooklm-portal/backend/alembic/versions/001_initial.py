"""initial

Revision ID: 001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("google_id", sa.String(255), unique=True, nullable=True),
        sa.Column("avatar_url", sa.Text, nullable=True),
        sa.Column("access_token", sa.Text, nullable=True),
        sa.Column("refresh_token", sa.Text, nullable=True),
        sa.Column("token_expiry", sa.DateTime, nullable=True),
        sa.Column("notebooklm_connected", sa.Boolean, default=False),
        sa.Column("preferred_llm", sa.String(50), default="openai"),
        sa.Column("llm_api_key", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("last_login", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "notebooks",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("notebooklm_id", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), default="active"),
        sa.Column("source_count", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "sources",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "notebook_id",
            UUID(as_uuid=True),
            sa.ForeignKey("notebooks.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("url", sa.Text, nullable=True),
        sa.Column("file_path", sa.Text, nullable=True),
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("status", sa.String(50), default="processing"),
        sa.Column("notebooklm_source_id", sa.String(255), nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "outputs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "notebook_id",
            UUID(as_uuid=True),
            sa.ForeignKey("notebooks.id"),
            nullable=True,
        ),
        sa.Column("output_type", sa.String(50), nullable=False),
        sa.Column("file_path", sa.String(500), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "execution_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
            index=True,
        ),
        sa.Column("original_input", sa.Text, nullable=False),
        sa.Column("detected_language", sa.String(20), nullable=True),
        sa.Column("refined_input", sa.Text, nullable=True),
        sa.Column("actions", JSONB, nullable=True),
        sa.Column("result", JSONB, nullable=True),
        sa.Column("status", sa.String(50), default="pending"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("execution_logs")
    op.drop_table("outputs")
    op.drop_table("sources")
    op.drop_table("notebooks")
    op.drop_table("users")
