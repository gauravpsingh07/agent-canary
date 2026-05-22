from typing import Any, Literal

from pydantic import BaseModel, Field

ActionType = Literal["tool_call", "refusal", "answer", "request_human_review"]
RiskLevel = Literal["low", "medium", "high", "critical"]


class AgentToolCall(BaseModel):
    tool_name: str = Field(min_length=1)
    arguments: dict[str, Any] = Field(default_factory=dict)


class AgentCitation(BaseModel):
    document_id: str | None = None
    chunk_id: str | None = None
    quote: str | None = None


class AgentOutput(BaseModel):
    reasoning_summary: str = Field(min_length=1)
    action_type: ActionType
    answer: str | None = None
    tool_call: AgentToolCall | None = None
    risk_level: RiskLevel
    requires_approval: bool
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[AgentCitation] = Field(default_factory=list)

