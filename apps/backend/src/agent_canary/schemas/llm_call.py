from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class LLMCallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    test_run_id: str | None
    project_id: str | None
    provider_name: str
    model_name: str
    system_prompt: str | None
    prompt: str
    response_text: str | None
    temperature: float | None
    max_tokens: int | None
    latency_ms: int | None
    error_message: str | None
    call_metadata: dict[str, Any]
    created_at: datetime
