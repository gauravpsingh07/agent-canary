from collections import defaultdict
from statistics import mean
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import (
    ApprovalRequest,
    EvaluationResult,
    PolicyViolation,
    RetrievalResult,
    TestRun,
)
from agent_canary.schemas import (
    CitationCoverageMetric,
    EvaluationResultRead,
    FailureByCategoryMetric,
    MetricsSummary,
    PolicyViolationMetric,
    ProviderLatencyMetric,
    RetrievalQualityMetric,
)

router = APIRouter(tags=["evaluation"])
DbSession = Annotated[Session, Depends(get_db)]

RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def get_evaluation_result_or_404(db: Session, result_id: str) -> EvaluationResult:
    result = db.get(EvaluationResult, result_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation result not found",
        )
    return result


@router.get("/evaluation-results", response_model=list[EvaluationResultRead])
def list_evaluation_results(db: DbSession) -> list[EvaluationResult]:
    statement = select(EvaluationResult).order_by(EvaluationResult.created_at.desc())
    return list(db.scalars(statement).all())


@router.get("/evaluation-results/{result_id}", response_model=EvaluationResultRead)
def get_evaluation_result(result_id: str, db: DbSession) -> EvaluationResult:
    return get_evaluation_result_or_404(db, result_id)


@router.get("/metrics/summary", response_model=MetricsSummary)
def get_metrics_summary(db: DbSession) -> MetricsSummary:
    results = list(db.scalars(select(EvaluationResult)).all())
    total_test_runs = db.scalar(select(func.count()).select_from(TestRun)) or 0
    completed = len(results)
    passed = sum(1 for result in results if result.passed)
    failed = completed - passed
    policy_violation_count = (
        db.scalar(select(func.count()).select_from(PolicyViolation)) or 0
    )
    pending_approvals = (
        db.scalar(
            select(func.count())
            .select_from(ApprovalRequest)
            .where(ApprovalRequest.status == "pending")
        )
        or 0
    )

    return MetricsSummary(
        total_test_runs=total_test_runs,
        completed_evaluations=completed,
        passed_evaluations=passed,
        failed_evaluations=failed,
        pass_rate=percentage(passed, completed),
        failure_rate=percentage(failed, completed),
        average_score=average([result.overall_score for result in results]),
        high_risk_failures=count_high_risk_failures(results),
        pending_approvals=pending_approvals,
        policy_violation_count=policy_violation_count,
    )


@router.get("/metrics/failures-by-category", response_model=list[FailureByCategoryMetric])
def get_failures_by_category(db: DbSession) -> list[FailureByCategoryMetric]:
    buckets: dict[str, list[int]] = defaultdict(list)
    for result in db.scalars(select(EvaluationResult)).all():
        if result.passed:
            continue
        category = result.test_run.test_case.category
        buckets[category].append(result.overall_score)

    return [
        FailureByCategoryMetric(
            category=category,
            total_failures=len(scores),
            average_score=average(scores),
        )
        for category, scores in sorted(
            buckets.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )
    ]


@router.get("/metrics/provider-latency", response_model=list[ProviderLatencyMetric])
def get_provider_latency(db: DbSession) -> list[ProviderLatencyMetric]:
    buckets: dict[tuple[str, str], list[int]] = defaultdict(list)
    for result in db.scalars(select(EvaluationResult)).all():
        if result.latency_ms is None:
            continue
        key = (
            result.provider_name or "unknown",
            result.model_name or "unknown",
        )
        buckets[key].append(result.latency_ms)

    return [
        ProviderLatencyMetric(
            provider_name=provider_name,
            model_name=model_name,
            run_count=len(latencies),
            average_latency_ms=average(latencies),
        )
        for (provider_name, model_name), latencies in sorted(buckets.items())
    ]


@router.get("/metrics/policy-violations", response_model=list[PolicyViolationMetric])
def get_policy_violation_metrics(db: DbSession) -> list[PolicyViolationMetric]:
    buckets: dict[str, dict[str, int | str]] = {}
    for violation in db.scalars(select(PolicyViolation)).all():
        bucket = buckets.setdefault(
            violation.violation_code,
            {"count": 0, "highest_severity": violation.severity},
        )
        bucket["count"] = int(bucket["count"]) + 1
        bucket["highest_severity"] = highest_severity(
            str(bucket["highest_severity"]),
            violation.severity,
        )

    return [
        PolicyViolationMetric(
            violation_code=violation_code,
            count=int(bucket["count"]),
            highest_severity=str(bucket["highest_severity"]),
        )
        for violation_code, bucket in sorted(
            buckets.items(),
            key=lambda item: (-int(item[1]["count"]), item[0]),
        )
    ]


@router.get("/metrics/retrieval-quality", response_model=RetrievalQualityMetric)
def get_retrieval_quality_metrics(db: DbSession) -> RetrievalQualityMetric:
    retrievals = list(db.scalars(select(RetrievalResult)).all())
    top_scores = [top_result_score(result) for result in retrievals]
    empty_retrievals = sum(1 for result in retrievals if result.result_count == 0)
    weak_retrievals = sum(1 for score in top_scores if score < 0.35)
    return RetrievalQualityMetric(
        total_retrievals=len(retrievals),
        empty_retrievals=empty_retrievals,
        weak_retrievals=weak_retrievals,
        weak_retrieval_rate=percentage(weak_retrievals, len(retrievals)),
        average_result_count=average([result.result_count for result in retrievals]),
        average_top_score=round(float(mean(top_scores)), 4) if top_scores else 0.0,
    )


@router.get("/metrics/citation-coverage", response_model=CitationCoverageMetric)
def get_citation_coverage_metrics(db: DbSession) -> CitationCoverageMetric:
    grounded_categories = {"weak_retrieval", "stale_context", "hallucination"}
    grounded_runs = [
        run
        for run in db.scalars(select(TestRun)).all()
        if run.test_case.category in grounded_categories
        or bool({"rag", "citations", "grounding"}.intersection(set(run.test_case.tags)))
    ]
    runs_with_citations = sum(1 for run in grounded_runs if run_has_citations(run))
    invalid_citation_failures = sum(
        1
        for run in grounded_runs
        if any("citations did not reference" in reason for reason in run.failure_reasons)
    )
    return CitationCoverageMetric(
        grounded_runs=len(grounded_runs),
        runs_with_citations=runs_with_citations,
        citation_coverage_rate=percentage(runs_with_citations, len(grounded_runs)),
        invalid_citation_failures=invalid_citation_failures,
    )


def count_high_risk_failures(results: list[EvaluationResult]) -> int:
    high_risk = {"high", "critical"}
    return sum(
        1
        for result in results
        if not result.passed and result.test_run.test_case.severity in high_risk
    )


def percentage(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return round((numerator / denominator) * 100, 2)


def average(values: list[int]) -> float:
    if not values:
        return 0.0
    return round(float(mean(values)), 2)


def highest_severity(left: str, right: str) -> str:
    if RISK_ORDER.get(right, 1) > RISK_ORDER.get(left, 1):
        return right
    return left


def top_result_score(result: RetrievalResult) -> float:
    scores = [
        float(item.get("score", 0))
        for item in result.results
        if isinstance(item.get("score", 0), int | float)
    ]
    return max(scores, default=0.0)


def run_has_citations(run: TestRun) -> bool:
    validated_output = run.run_metadata.get("validated_output")
    if not isinstance(validated_output, dict):
        return False
    citations = validated_output.get("citations")
    return isinstance(citations, list) and len(citations) > 0
