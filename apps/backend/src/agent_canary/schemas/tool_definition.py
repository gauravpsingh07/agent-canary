from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

RiskLevel = Literal["low", "medium", "high", "critical"]


class ToolDefinitionBase(BaseModel):
    name: str = Field(min_length=1, max_length=120, pattern=r"^[a-z][a-z0-9_]*$")
    description: str = Field(min_length=1)
    argument_schema: dict[str, Any]
    risk_level: RiskLevel
    requires_approval: bool = False
    allowed_conditions: list[str] = Field(default_factory=list)
    blocked_conditions: list[str] = Field(default_factory=list)
    example_valid_call: dict[str, Any]
    example_invalid_call: dict[str, Any]
    is_active: bool = True


class ToolDefinitionCreate(ToolDefinitionBase):
    pass


class ToolDefinitionUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
        pattern=r"^[a-z][a-z0-9_]*$",
    )
    description: str | None = Field(default=None, min_length=1)
    argument_schema: dict[str, Any] | None = None
    risk_level: RiskLevel | None = None
    requires_approval: bool | None = None
    allowed_conditions: list[str] | None = None
    blocked_conditions: list[str] | None = None
    example_valid_call: dict[str, Any] | None = None
    example_invalid_call: dict[str, Any] | None = None
    is_active: bool | None = None


class ToolDefinitionRead(ToolDefinitionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class ToolCallValidationRequest(BaseModel):
    tool_name: str = Field(min_length=1, max_length=120)
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolCallValidationResponse(BaseModel):
    tool_name: str
    valid: bool
    errors: list[str]
    risk_level: str | None = None
    requires_approval: bool | None = None


class ToolSeedResponse(BaseModel):
    tools_created: int
    total_tools: int
