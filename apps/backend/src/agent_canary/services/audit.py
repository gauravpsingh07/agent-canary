from typing import Any

from sqlalchemy.orm import Session

from agent_canary.models import AuditLog


def write_audit_log(
    db: Session,
    *,
    project_id: str | None,
    entity_type: str,
    entity_id: str | None,
    event_type: str,
    actor_type: str = "system",
    metadata: dict[str, Any] | None = None,
) -> AuditLog:
    audit_log = AuditLog(
        project_id=project_id,
        entity_type=entity_type,
        entity_id=entity_id,
        event_type=event_type,
        actor_type=actor_type,
        event_metadata=metadata or {},
    )
    db.add(audit_log)
    return audit_log

