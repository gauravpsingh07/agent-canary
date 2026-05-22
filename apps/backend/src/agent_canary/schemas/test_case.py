from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TestCaseBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    category: str = Field(min_length=1, max_length=80)
    input_prompt: str = Field(min_length=1)
    system_prompt: str | None = None
    expected_behavior: str = Field(min_length=1)
    expected_tool_name: str | None = Field(default=None, max_length=120)
    should_call_tool: bool = False
    should_require_approval: bool = False
    expected_refusal: bool = False
    expected_schema_valid: bool = True
    tags: list[str] = Field(default_factory=list)
    severity: str = Field(default="medium", min_length=1, max_length=40)


class TestCaseCreate(TestCaseBase):
    pass


class TestCaseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = None
    category: str | None = Field(default=None, min_length=1, max_length=80)
    input_prompt: str | None = Field(default=None, min_length=1)
    system_prompt: str | None = None
    expected_behavior: str | None = Field(default=None, min_length=1)
    expected_tool_name: str | None = Field(default=None, max_length=120)
    should_call_tool: bool | None = None
    should_require_approval: bool | None = None
    expected_refusal: bool | None = None
    expected_schema_valid: bool | None = None
    tags: list[str] | None = None
    severity: str | None = Field(default=None, min_length=1, max_length=40)


class TestCaseRead(TestCaseBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    suite_id: str
    created_at: datetime
    updated_at: datetime

