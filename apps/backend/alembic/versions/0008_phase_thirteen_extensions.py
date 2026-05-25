"""Phase 13 — model extensions.

Adds retrieval-aware test case fields, retrieval/citation/latency scores and
RAG flags on evaluation results, llm_calls and tool_calls tables, and a
test_run_id link on retrieval_results.

Revision ID: 0008_phase_thirteen_extensions
Revises: 0007_create_rag_tables
Create Date: 2026-05-22
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0008_phase_thirteen_extensions"
down_revision = "0007_create_rag_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- Test case retrieval-aware fields -----------------------------------
    with op.batch_alter_table("test_cases") as batch_op:
        batch_op.add_column(
            sa.Column(
                "requires_retrieval",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "expected_citations",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(sa.Column("min_retrieval_score", sa.Float(), nullable=True))

    # --- Evaluation result new score columns + RAG flags --------------------
    with op.batch_alter_table("evaluation_results") as batch_op:
        batch_op.add_column(
            sa.Column(
                "retrieval_quality_score",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("100"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "citation_coverage_score",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("100"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "latency_score",
                sa.Integer(),
                nullable=False,
                server_default=sa.text("100"),
            )
        )
        batch_op.add_column(
            sa.Column(
                "stale_context_flag",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "unsupported_claim_flag",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )
        batch_op.add_column(
            sa.Column(
                "weak_evidence_flag",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            )
        )

    # --- RetrievalResult: add test_run_id link ------------------------------
    with op.batch_alter_table("retrieval_results") as batch_op:
        batch_op.add_column(sa.Column("test_run_id", sa.String(length=36), nullable=True))
        batch_op.create_index(
            op.f("ix_retrieval_results_test_run_id"),
            ["test_run_id"],
        )
        batch_op.create_foreign_key(
            op.f("fk_retrieval_results_test_run_id_test_runs"),
            "test_runs",
            ["test_run_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # --- llm_calls ----------------------------------------------------------
    op.create_table(
        "llm_calls",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("test_run_id", sa.String(length=36), nullable=True),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("provider_name", sa.String(length=80), nullable=False),
        sa.Column("model_name", sa.String(length=160), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=True),
        sa.Column("temperature", sa.Float(), nullable=True),
        sa.Column("max_tokens", sa.Integer(), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["test_runs.id"],
            name=op.f("fk_llm_calls_test_run_id_test_runs"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_llm_calls_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_llm_calls")),
    )
    op.create_index(op.f("ix_llm_calls_test_run_id"), "llm_calls", ["test_run_id"])
    op.create_index(op.f("ix_llm_calls_project_id"), "llm_calls", ["project_id"])
    op.create_index(op.f("ix_llm_calls_provider_name"), "llm_calls", ["provider_name"])

    # --- tool_calls ---------------------------------------------------------
    op.create_table(
        "tool_calls",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("test_run_id", sa.String(length=36), nullable=False),
        sa.Column("tool_name", sa.String(length=120), nullable=False),
        sa.Column("arguments", sa.JSON(), nullable=False),
        sa.Column("validation_errors", sa.JSON(), nullable=False),
        sa.Column("schema_valid", sa.Boolean(), nullable=False),
        sa.Column("simulated_action_allowed", sa.Boolean(), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False),
        sa.Column("blocked", sa.Boolean(), nullable=False),
        sa.Column("risk_level", sa.String(length=40), nullable=False),
        sa.Column("policy_violations", sa.JSON(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["test_runs.id"],
            name=op.f("fk_tool_calls_test_run_id_test_runs"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_tool_calls")),
    )
    op.create_index(op.f("ix_tool_calls_test_run_id"), "tool_calls", ["test_run_id"])
    op.create_index(op.f("ix_tool_calls_tool_name"), "tool_calls", ["tool_name"])


def downgrade() -> None:
    op.drop_index(op.f("ix_tool_calls_tool_name"), table_name="tool_calls")
    op.drop_index(op.f("ix_tool_calls_test_run_id"), table_name="tool_calls")
    op.drop_table("tool_calls")

    op.drop_index(op.f("ix_llm_calls_provider_name"), table_name="llm_calls")
    op.drop_index(op.f("ix_llm_calls_project_id"), table_name="llm_calls")
    op.drop_index(op.f("ix_llm_calls_test_run_id"), table_name="llm_calls")
    op.drop_table("llm_calls")

    with op.batch_alter_table("retrieval_results") as batch_op:
        batch_op.drop_constraint(
            op.f("fk_retrieval_results_test_run_id_test_runs"),
            type_="foreignkey",
        )
        batch_op.drop_index(op.f("ix_retrieval_results_test_run_id"))
        batch_op.drop_column("test_run_id")

    with op.batch_alter_table("evaluation_results") as batch_op:
        batch_op.drop_column("weak_evidence_flag")
        batch_op.drop_column("unsupported_claim_flag")
        batch_op.drop_column("stale_context_flag")
        batch_op.drop_column("latency_score")
        batch_op.drop_column("citation_coverage_score")
        batch_op.drop_column("retrieval_quality_score")

    with op.batch_alter_table("test_cases") as batch_op:
        batch_op.drop_column("min_retrieval_score")
        batch_op.drop_column("expected_citations")
        batch_op.drop_column("requires_retrieval")
