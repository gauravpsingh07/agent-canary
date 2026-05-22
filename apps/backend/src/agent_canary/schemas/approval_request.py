from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

ApprovalStatus = Literal["pending", "approved", "rejected"]
APPROVAL_STATUSES = {"pending", "approved", "rejected"}


class ApprovalDecisionRequest(BaseModel):
    reviewer_note: str | None = Field(default=None, max_length=2000)


class ApprovalRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    test_run_id: str
    proposed_tool_call_id: str | None
    proposed_tool_call: dict[str, Any]
    risk_level: str
    reason: str
    status: ApprovalStatus
    reviewer_note: str | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime
