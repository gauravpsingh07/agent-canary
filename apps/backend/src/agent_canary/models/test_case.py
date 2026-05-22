from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_canary.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_canary.models.test_run import TestRun
    from agent_canary.models.test_suite import TestSuite


class TestCase(IdMixin, TimestampMixin, Base):
    __tablename__ = "test_cases"

    suite_id: Mapped[str] = mapped_column(
        ForeignKey("test_suites.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    input_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_behavior: Mapped[str] = mapped_column(Text, nullable=False)
    expected_tool_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    should_call_tool: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    should_require_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expected_refusal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    expected_schema_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    severity: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)

    suite: Mapped[TestSuite] = relationship(back_populates="test_cases")
    test_runs: Mapped[list[TestRun]] = relationship(
        back_populates="test_case",
        cascade="all, delete-orphan",
    )
