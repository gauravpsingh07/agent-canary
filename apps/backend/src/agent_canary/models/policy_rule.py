from typing import Any

from sqlalchemy import JSON, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from agent_canary.models.base import Base, IdMixin, TimestampMixin


class PolicyRule(IdMixin, TimestampMixin, Base):
    __tablename__ = "policy_rules"

    name: Mapped[str] = mapped_column(String(160), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rule_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    tool_name: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    violation_code: Mapped[str] = mapped_column(String(120), nullable=False)
    effect: Mapped[str] = mapped_column(String(40), nullable=False)
    condition: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

