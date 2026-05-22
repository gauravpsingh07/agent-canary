from typing import Any

from sqlalchemy import JSON, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agent_canary.models.base import Base, IdMixin, TimestampMixin


class PolicyViolation(IdMixin, TimestampMixin, Base):
    __tablename__ = "policy_violations"

    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    test_run_id: Mapped[str | None] = mapped_column(
        ForeignKey("test_runs.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    policy_rule_id: Mapped[str | None] = mapped_column(
        ForeignKey("policy_rules.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    tool_name: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    violation_code: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    severity: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    violation_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )

