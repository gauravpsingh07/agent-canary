from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_canary.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_canary.models.audit_log import AuditLog
    from agent_canary.models.rag_document import RagDocument
    from agent_canary.models.test_suite import TestSuite


class Project(IdMixin, TimestampMixin, Base):
    __tablename__ = "projects"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    test_suites: Mapped[list[TestSuite]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(back_populates="project")
    rag_documents: Mapped[list[RagDocument]] = relationship(back_populates="project")
