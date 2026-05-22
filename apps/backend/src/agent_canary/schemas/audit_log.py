from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str | None
    entity_type: str
    entity_id: str | None
    event_type: str
    actor_type: str
    event_metadata: dict[str, Any]
    created_at: datetime
