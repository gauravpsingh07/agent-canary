from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvaluationResultRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    test_run_id: str
    schema_validity_score: int
    tool_safety_score: int
    policy_compliance_score: int
    approval_correctness_score: int
    refusal_correctness_score: int
    groundedness_score: int
    prompt_injection_resistance_score: int
    retrieval_quality_score: int
    citation_coverage_score: int
    latency_score: int
    overall_score: int
    passed: bool
    stale_context_flag: bool
    unsupported_claim_flag: bool
    weak_evidence_flag: bool
    failure_reasons: list[str]
    policy_violations: list[dict[str, Any]]
    evaluator_notes: str | None
    latency_ms: int | None
    provider_name: str | None
    model_name: str | None
    created_at: datetime
    updated_at: datetime


class MetricsSummary(BaseModel):
    total_test_runs: int
    completed_evaluations: int
    passed_evaluations: int
    failed_evaluations: int
    pass_rate: float
    failure_rate: float
    average_score: float
    high_risk_failures: int
    pending_approvals: int
    policy_violation_count: int


class FailureByCategoryMetric(BaseModel):
    category: str
    total_failures: int
    average_score: float


class ProviderLatencyMetric(BaseModel):
    provider_name: str
    model_name: str
    run_count: int
    average_latency_ms: float


class PolicyViolationMetric(BaseModel):
    violation_code: str
    count: int = Field(ge=0)
    highest_severity: str


class RetrievalQualityMetric(BaseModel):
    total_retrievals: int
    empty_retrievals: int
    weak_retrievals: int
    weak_retrieval_rate: float
    average_result_count: float
    average_top_score: float


class CitationCoverageMetric(BaseModel):
    grounded_runs: int
    runs_with_citations: int
    citation_coverage_rate: float
    invalid_citation_failures: int


class TimeSeriesPoint(BaseModel):
    bucket: str
    value: float
    count: int = 0


class ApprovalOutcomeMetric(BaseModel):
    pending: int
    approved: int
    rejected: int
