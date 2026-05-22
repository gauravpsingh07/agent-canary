from typing import Any

from sqlalchemy import JSON, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agent_canary.models.base import Base, IdMixin, TimestampMixin


class ToolDefinition(IdMixin, TimestampMixin, Base):
    __tablename__ = "tool_definitions"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    argument_schema: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(40), nullable=False)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allowed_conditions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    blocked_conditions: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    example_valid_call: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    example_invalid_call: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

