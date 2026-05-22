"""Create tool definitions table.

Revision ID: 0002_create_tool_definitions
Revises: 0001_create_foundation_tables
Create Date: 2026-05-21
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0002_create_tool_definitions"
down_revision = "0001_create_foundation_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tool_definitions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("argument_schema", sa.JSON(), nullable=False),
        sa.Column("risk_level", sa.String(length=40), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False),
        sa.Column("allowed_conditions", sa.JSON(), nullable=False),
        sa.Column("blocked_conditions", sa.JSON(), nullable=False),
        sa.Column("example_valid_call", sa.JSON(), nullable=False),
        sa.Column("example_invalid_call", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tool_definitions")),
    )
    op.create_index(op.f("ix_tool_definitions_name"), "tool_definitions", ["name"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_tool_definitions_name"), table_name="tool_definitions")
    op.drop_table("tool_definitions")

