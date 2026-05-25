from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ToolCallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    test_run_id: str
    tool_name: str
    arguments: dict[str, Any]
    validation_errors: list[str]
    schema_valid: bool
    simulated_action_allowed: bool
    requires_approval: bool
    blocked: bool
    risk_level: str
    policy_violations: list[dict[str, Any]]
    call_metadata: dict[str, Any]
    created_at: datetime
