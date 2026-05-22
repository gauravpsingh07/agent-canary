"""Create policy rule and violation tables.

Revision ID: 0003_create_policy_tables
Revises: 0002_create_tool_definitions
Create Date: 2026-05-21
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "0003_create_policy_tables"
down_revision = "0002_create_tool_definitions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_rules",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("rule_type", sa.String(length=80), nullable=False),
        sa.Column("tool_name", sa.String(length=120), nullable=True),
        sa.Column("violation_code", sa.String(length=120), nullable=False),
        sa.Column("effect", sa.String(length=40), nullable=False),
        sa.Column("condition", sa.JSON(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_policy_rules")),
    )
    op.create_index(op.f("ix_policy_rules_name"), "policy_rules", ["name"], unique=True)
    op.create_index(op.f("ix_policy_rules_rule_type"), "policy_rules", ["rule_type"])
    op.create_index(op.f("ix_policy_rules_tool_name"), "policy_rules", ["tool_name"])

    op.create_table(
        "policy_violations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("project_id", sa.String(length=36), nullable=True),
        sa.Column("test_run_id", sa.String(length=36), nullable=True),
        sa.Column("policy_rule_id", sa.String(length=36), nullable=True),
        sa.Column("tool_name", sa.String(length=120), nullable=True),
        sa.Column("violation_code", sa.String(length=120), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["policy_rule_id"],
            ["policy_rules.id"],
            name=op.f("fk_policy_violations_policy_rule_id_policy_rules"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name=op.f("fk_policy_violations_project_id_projects"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["test_run_id"],
            ["test_runs.id"],
            name=op.f("fk_policy_violations_test_run_id_test_runs"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_policy_violations")),
    )
    op.create_index(
        op.f("ix_policy_violations_policy_rule_id"),
        "policy_violations",
        ["policy_rule_id"],
    )
    op.create_index(op.f("ix_policy_violations_project_id"), "policy_violations", ["project_id"])
    op.create_index(op.f("ix_policy_violations_test_run_id"), "policy_violations", ["test_run_id"])
    op.create_index(op.f("ix_policy_violations_tool_name"), "policy_violations", ["tool_name"])
    op.create_index(
        op.f("ix_policy_violations_violation_code"),
        "policy_violations",
        ["violation_code"],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_policy_violations_violation_code"), table_name="policy_violations")
    op.drop_index(op.f("ix_policy_violations_tool_name"), table_name="policy_violations")
    op.drop_index(op.f("ix_policy_violations_test_run_id"), table_name="policy_violations")
    op.drop_index(op.f("ix_policy_violations_project_id"), table_name="policy_violations")
    op.drop_index(op.f("ix_policy_violations_policy_rule_id"), table_name="policy_violations")
    op.drop_table("policy_violations")
    op.drop_index(op.f("ix_policy_rules_tool_name"), table_name="policy_rules")
    op.drop_index(op.f("ix_policy_rules_rule_type"), table_name="policy_rules")
    op.drop_index(op.f("ix_policy_rules_name"), table_name="policy_rules")
    op.drop_table("policy_rules")

