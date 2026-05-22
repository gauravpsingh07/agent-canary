from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_canary.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_canary.models.approval_request import ApprovalRequest
    from agent_canary.models.evaluation_result import EvaluationResult
    from agent_canary.models.test_case import TestCase
    from agent_canary.models.test_run_step import TestRunStep


class TestRun(IdMixin, TimestampMixin, Base):
    __tablename__ = "test_runs"

    test_case_id: Mapped[str] = mapped_column(
        ForeignKey("test_cases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(40), index=True, default="pending", nullable=False)
    provider_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    failure_reasons: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    run_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    test_case: Mapped[TestCase] = relationship(back_populates="test_runs")
    steps: Mapped[list[TestRunStep]] = relationship(
        back_populates="test_run",
        cascade="all, delete-orphan",
    )
    evaluation_result: Mapped[EvaluationResult | None] = relationship(
        back_populates="test_run",
        cascade="all, delete-orphan",
        uselist=False,
    )
    approval_requests: Mapped[list[ApprovalRequest]] = relationship(
        back_populates="test_run",
        cascade="all, delete-orphan",
    )
