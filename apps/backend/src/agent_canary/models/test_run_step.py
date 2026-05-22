from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_canary.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_canary.models.test_run import TestRun


class TestRunStep(IdMixin, TimestampMixin, Base):
    __tablename__ = "test_run_steps"

    test_run_id: Mapped[str] = mapped_column(
        ForeignKey("test_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    input_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    output_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    test_run: Mapped[TestRun] = relationship(back_populates="steps")

