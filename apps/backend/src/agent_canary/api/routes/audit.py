from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import AuditLog
from agent_canary.schemas import AuditLogRead

router = APIRouter(tags=["audit logs"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/audit-logs", response_model=list[AuditLogRead])
def list_audit_logs(
    db: DbSession,
    limit: int = Query(default=100, ge=1, le=500),
    project_id: str | None = None,
    event_type: str | None = None,
) -> list[AuditLog]:
    statement = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)
    if project_id is not None:
        statement = statement.where(AuditLog.project_id == project_id)
    if event_type is not None:
        statement = statement.where(AuditLog.event_type == event_type)
    return list(db.scalars(statement).all())
