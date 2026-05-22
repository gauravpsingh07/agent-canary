"""Create evaluation results table.

Revision ID: 0005_create_evaluation_results
Revises: 0004_create_test_run_steps
Create Date: 2026-05-21
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0005_create_evaluation_results"
down_revision = "0004_create_test_run_steps"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evaluation_results",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("test_run_id", sa.String(length=36), nullable=False),
        sa.Column("schema_validity_score", sa.Integer(), nullable=False),
        sa.Column("tool_safety_score", sa.Integer(), nullable=False),
        sa.Column("policy_compliance_score", sa.Integer(), nullable=False),
        sa.Column("approval_correctness_score", sa.Integer(), nullable=False),
        sa.Column("refusal_correctness_score", sa.Integer(), nullable=False),
        sa.Column("groundedness_score", sa.Integer(), nullable=False),
        sa.Column("prompt_injection_resistance_score", sa.Integer(), nullable=False),
        sa.Column("overall_score", sa.Integer(), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("failure_reasons", sa.JSON(), nullable=False),
        sa.Column("policy_violations", sa.JSON(), nullable=False),
        sa.Column("evaluator_notes", sa.Text(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("provider_name", sa.String(length=80), nullable=True),
        sa.Column("model_name", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["test_runs.id"],
            name=op.f("fk_evaluation_results_test_run_id_test_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_evaluation_results")),
        sa.UniqueConstraint("test_run_id", name=op.f("uq_evaluation_results_test_run_id")),
    )
    op.create_index(
        op.f("ix_evaluation_results_provider_name"),
        "evaluation_results",
        ["provider_name"],
    )
    op.create_index(op.f("ix_evaluation_results_passed"), "evaluation_results", ["passed"])
    op.create_index(
        op.f("ix_evaluation_results_test_run_id"),
        "evaluation_results",
        ["test_run_id"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_evaluation_results_test_run_id"), table_name="evaluation_results")
    op.drop_index(op.f("ix_evaluation_results_passed"), table_name="evaluation_results")
    op.drop_index(op.f("ix_evaluation_results_provider_name"), table_name="evaluation_results")
    op.drop_table("evaluation_results")
