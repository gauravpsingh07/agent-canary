from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_canary.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_canary.models.test_run import TestRun


class EvaluationResult(IdMixin, TimestampMixin, Base):
    __tablename__ = "evaluation_results"

    test_run_id: Mapped[str] = mapped_column(
        ForeignKey("test_runs.id", ondelete="CASCADE"),
        index=True,
        unique=True,
        nullable=False,
    )
    schema_validity_score: Mapped[int] = mapped_column(Integer, nullable=False)
    tool_safety_score: Mapped[int] = mapped_column(Integer, nullable=False)
    policy_compliance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    approval_correctness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    refusal_correctness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    groundedness_score: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_injection_resistance_score: Mapped[int] = mapped_column(Integer, nullable=False)
    retrieval_quality_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    citation_coverage_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    latency_score: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, index=True, nullable=False)
    stale_context_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unsupported_claim_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    weak_evidence_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failure_reasons: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    policy_violations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    evaluator_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    provider_name: Mapped[str | None] = mapped_column(String(80), index=True, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    test_run: Mapped[TestRun] = relationship(back_populates="evaluation_result")
