from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from agent_canary.models.base import Base, IdMixin, utc_now


class ToolCall(IdMixin, Base):
    __tablename__ = "tool_calls"

    test_run_id: Mapped[str] = mapped_column(
        ForeignKey("test_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tool_name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    arguments: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    validation_errors: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    schema_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    simulated_action_allowed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(40), default="medium", nullable=False)
    policy_violations: Mapped[list[dict[str, Any]]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )
    call_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
