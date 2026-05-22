from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from agent_canary.models.base import Base, IdMixin, TimestampMixin

if TYPE_CHECKING:
    from agent_canary.models.rag_document import RagDocument


class DocumentIngestionJob(IdMixin, TimestampMixin, Base):
    __tablename__ = "document_ingestion_jobs"

    project_id: Mapped[str | None] = mapped_column(
        ForeignKey("projects.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    document_id: Mapped[str | None] = mapped_column(
        ForeignKey("rag_documents.id", ondelete="CASCADE"),
        index=True,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(40), index=True, default="pending", nullable=False)
    chunks_created: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_metadata: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSON,
        default=dict,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    document: Mapped[RagDocument | None] = relationship(back_populates="ingestion_jobs")
