"""Create approval requests table.

Revision ID: 0006_create_approval_requests
Revises: 0005_create_evaluation_results
Create Date: 2026-05-21
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0006_create_approval_requests"
down_revision = "0005_create_evaluation_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "approval_requests",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("test_run_id", sa.String(length=36), nullable=False),
        sa.Column("proposed_tool_call_id", sa.String(length=36), nullable=True),
        sa.Column("proposed_tool_call", sa.JSON(), nullable=False),
        sa.Column("risk_level", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("reviewer_note", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["test_runs.id"],
            name=op.f("fk_approval_requests_test_run_id_test_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_approval_requests")),
    )
    op.create_index(
        op.f("ix_approval_requests_test_run_id"),
        "approval_requests",
        ["test_run_id"],
    )
    op.create_index(op.f("ix_approval_requests_status"), "approval_requests", ["status"])
    op.create_index(op.f("ix_approval_requests_risk_level"), "approval_requests", ["risk_level"])


def downgrade() -> None:
    op.drop_index(op.f("ix_approval_requests_risk_level"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_status"), table_name="approval_requests")
    op.drop_index(op.f("ix_approval_requests_test_run_id"), table_name="approval_requests")
    op.drop_table("approval_requests")
