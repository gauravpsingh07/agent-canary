from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

PolicyEffect = Literal["allow", "flag", "require_approval", "block"]
RiskLevel = Literal["low", "medium", "high", "critical"]


class PolicyRuleBase(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(min_length=1)
    rule_type: str = Field(min_length=1, max_length=80)
    tool_name: str | None = Field(default=None, max_length=120)
    violation_code: str = Field(min_length=1, max_length=120)
    effect: PolicyEffect
    condition: dict[str, Any] = Field(default_factory=dict)
    is_enabled: bool = True


class PolicyRuleCreate(PolicyRuleBase):
    pass


class PolicyRuleUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, min_length=1)
    rule_type: str | None = Field(default=None, min_length=1, max_length=80)
    tool_name: str | None = Field(default=None, max_length=120)
    violation_code: str | None = Field(default=None, min_length=1, max_length=120)
    effect: PolicyEffect | None = None
    condition: dict[str, Any] | None = None
    is_enabled: bool | None = None


class PolicyRuleRead(PolicyRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class PolicyRuleSeedResponse(BaseModel):
    rules_created: int
    total_rules: int


class ProposedToolCall(BaseModel):
    tool_name: str = Field(min_length=1, max_length=120)
    arguments: dict[str, Any] = Field(default_factory=dict)


class PolicyEvaluateRequest(BaseModel):
    tool_call: ProposedToolCall
    project_id: str | None = None
    test_run_id: str | None = None
    test_case_metadata: dict[str, Any] = Field(default_factory=dict)
    agent_output: dict[str, Any] | str | None = None
    retrieved_evidence: list[dict[str, Any]] = Field(default_factory=list)
    risk_level: RiskLevel | None = None
    persist_violations: bool = False


class PolicyViolationRead(BaseModel):
    violation_code: str
    severity: RiskLevel
    message: str
    effect: PolicyEffect
    policy_rule_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyEvaluationResponse(BaseModel):
    tool_name: str
    allowed: bool
    blocked: bool
    requires_approval: bool
    risk_level: RiskLevel
    violations: list[PolicyViolationRead]
    explanation: str

