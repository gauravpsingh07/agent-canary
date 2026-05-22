from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TestRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    test_case_id: str
    status: str
    provider_name: str | None
    model_name: str | None
    overall_score: int | None
    passed: bool | None
    failure_reasons: list[str]
    run_metadata: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class TestRunStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    test_run_id: str
    step_order: int
    step_name: str
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SuiteRunResponse(BaseModel):
    suite_id: str
    test_run_ids: list[str] = Field(default_factory=list)

