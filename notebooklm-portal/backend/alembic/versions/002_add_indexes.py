"""add performance indexes

Revision ID: 002
Revises: 001_initial
Create Date: 2026-07-07
"""
from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # User indexes
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_google_id", "users", ["google_id"], unique=True)

    # Notebook indexes
    op.create_index("ix_notebooks_user_id_status", "notebooks", ["user_id", "status"])
    op.create_index("ix_notebooks_created_at", "notebooks", ["created_at"])

    # Source indexes
    op.create_index("ix_sources_notebook_id_type", "sources", ["notebook_id", "source_type"])
    op.create_index("ix_sources_status", "sources", ["status"])
    op.create_index("ix_sources_created_at", "sources", ["created_at"])

    # Output indexes
    op.create_index("ix_outputs_user_id", "outputs", ["user_id"])
    op.create_index("ix_outputs_notebook_id_type", "outputs", ["notebook_id", "output_type"])
    op.create_index("ix_outputs_created_at", "outputs", ["created_at"])

    # Execution log indexes
    op.create_index("ix_execution_logs_user_id", "execution_logs", ["user_id"])
    op.create_index("ix_execution_logs_status", "execution_logs", ["status"])
    op.create_index("ix_execution_logs_created_at", "execution_logs", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_execution_logs_created_at", "execution_logs")
    op.drop_index("ix_execution_logs_status", "execution_logs")
    op.drop_index("ix_execution_logs_user_id", "execution_logs")
    op.drop_index("ix_outputs_created_at", "outputs")
    op.drop_index("ix_outputs_notebook_id_type", "outputs")
    op.drop_index("ix_outputs_user_id", "outputs")
    op.drop_index("ix_sources_created_at", "sources")
    op.drop_index("ix_sources_status", "sources")
    op.drop_index("ix_sources_notebook_id_type", "sources")
    op.drop_index("ix_notebooks_created_at", "notebooks")
    op.drop_index("ix_notebooks_user_id_status", "notebooks")
    op.drop_index("ix_users_google_id", "users")
    op.drop_index("ix_users_email", "users")
