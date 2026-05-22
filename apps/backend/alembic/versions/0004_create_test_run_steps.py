"""Create test run steps table.

Revision ID: 0004_create_test_run_steps
Revises: 0003_create_policy_tables
Create Date: 2026-05-21
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0004_create_test_run_steps"
down_revision = "0003_create_policy_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "test_run_steps",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("test_run_id", sa.String(length=36), nullable=False),
        sa.Column("step_order", sa.Integer(), nullable=False),
        sa.Column("step_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("output_payload", sa.JSON(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["test_runs.id"],
            name=op.f("fk_test_run_steps_test_run_id_test_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_test_run_steps")),
    )
    op.create_index(op.f("ix_test_run_steps_step_name"), "test_run_steps", ["step_name"])
    op.create_index(op.f("ix_test_run_steps_status"), "test_run_steps", ["status"])
    op.create_index(op.f("ix_test_run_steps_test_run_id"), "test_run_steps", ["test_run_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_test_run_steps_test_run_id"), table_name="test_run_steps")
    op.drop_index(op.f("ix_test_run_steps_status"), table_name="test_run_steps")
    op.drop_index(op.f("ix_test_run_steps_step_name"), table_name="test_run_steps")
    op.drop_table("test_run_steps")

