from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_canary.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_canary.models.test_run import TestRun


class ApprovalRequest(IdMixin, TimestampMixin, Base):
    __tablename__ = "approval_requests"

    test_run_id: Mapped[str] = mapped_column(
        ForeignKey("test_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    proposed_tool_call_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    proposed_tool_call: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), index=True, default="pending", nullable=False)
    reviewer_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    test_run: Mapped[TestRun] = relationship(back_populates="approval_requests")
