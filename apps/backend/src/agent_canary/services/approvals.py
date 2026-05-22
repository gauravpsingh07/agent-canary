from __future__ import annotations

from typing import Any, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.models import ApprovalRequest
from agent_canary.models.base import utc_now
from agent_canary.services.audit import write_audit_log

ApprovalDecision = Literal["approved", "rejected"]
RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def create_approval_request_if_needed(
    db: Session,
    *,
    test_run_id: str,
    project_id: str | None,
    proposed_tool_call: dict[str, Any] | None,
    policy_result: dict[str, Any] | None,
    validated_output: dict[str, Any] | None,
    passed: bool,
    failure_reasons: list[str],
) -> ApprovalRequest | None:
    risk_level = resolve_risk_level(policy_result, validated_output)
    requires_approval = bool(
        (validated_output or {}).get("requires_approval")
        or (policy_result or {}).get("requires_approval")
    )
    blocked = bool((policy_result or {}).get("blocked"))
    high_risk = RISK_ORDER.get(risk_level, 1) >= RISK_ORDER["high"]
    should_create = requires_approval or blocked or high_risk or not passed

    if not should_create:
        return None

    existing_request = db.scalar(
        select(ApprovalRequest).where(ApprovalRequest.test_run_id == test_run_id)
    )
    if existing_request is not None:
        return existing_request

    request = ApprovalRequest(
        test_run_id=test_run_id,
        proposed_tool_call=proposed_tool_call or {},
        risk_level=risk_level,
        reason=build_review_reason(
            requires_approval=requires_approval,
            blocked=blocked,
            high_risk=high_risk,
            passed=passed,
            failure_reasons=failure_reasons,
        ),
    )
    db.add(request)
    db.flush()
    write_audit_log(
        db,
        project_id=project_id,
        entity_type="approval_request",
        entity_id=request.id,
        event_type="APPROVAL_REQUEST_CREATED",
        metadata={
            "test_run_id": test_run_id,
            "risk_level": risk_level,
            "reason": request.reason,
        },
    )
    return request


def decide_approval_request(
    db: Session,
    approval_request: ApprovalRequest,
    *,
    decision: ApprovalDecision,
    reviewer_note: str | None,
) -> ApprovalRequest:
    if approval_request.status != "pending":
        raise ValueError("Approval request has already been reviewed.")

    approval_request.status = decision
    approval_request.reviewer_note = reviewer_note
    approval_request.reviewed_at = utc_now()
    update_test_run_approval_metadata(
        approval_request,
        decision=decision,
        reviewer_note=reviewer_note,
    )
    write_audit_log(
        db,
        project_id=approval_request.test_run.test_case.suite.project_id,
        entity_type="approval_request",
        entity_id=approval_request.id,
        event_type="APPROVAL_APPROVED" if decision == "approved" else "APPROVAL_REJECTED",
        actor_type="human",
        metadata={
            "test_run_id": approval_request.test_run_id,
            "reviewer_note": reviewer_note,
            "simulated_action_allowed": decision == "approved",
        },
    )
    return approval_request


def update_test_run_approval_metadata(
    approval_request: ApprovalRequest,
    *,
    decision: ApprovalDecision,
    reviewer_note: str | None,
) -> None:
    run_metadata = dict(approval_request.test_run.run_metadata or {})
    run_metadata["approval_decision"] = {
        "approval_request_id": approval_request.id,
        "status": decision,
        "reviewer_note": reviewer_note,
        "reviewed_at": approval_request.reviewed_at.isoformat()
        if approval_request.reviewed_at
        else None,
    }
    run_metadata["simulated_action_allowed"] = decision == "approved"
    approval_request.test_run.run_metadata = run_metadata


def resolve_risk_level(
    policy_result: dict[str, Any] | None,
    validated_output: dict[str, Any] | None,
) -> str:
    policy_risk = (policy_result or {}).get("risk_level")
    output_risk = (validated_output or {}).get("risk_level")
    return highest_risk(
        normalize_risk(str(policy_risk or "medium")),
        normalize_risk(str(output_risk or "medium")),
    )


def build_review_reason(
    *,
    requires_approval: bool,
    blocked: bool,
    high_risk: bool,
    passed: bool,
    failure_reasons: list[str],
) -> str:
    reasons: list[str] = []
    if requires_approval:
        reasons.append("Policy or agent output requires human approval before simulation.")
    if blocked:
        reasons.append("Policy engine blocked the proposed action.")
    if high_risk:
        reasons.append("High-risk or critical agent behavior needs review.")
    if not passed:
        summary = "; ".join(failure_reasons) if failure_reasons else "Evaluation failed."
        reasons.append(f"Evaluation failed: {summary}")
    return " ".join(reasons)


def normalize_risk(value: str) -> str:
    if value in RISK_ORDER:
        return value
    return "medium"


def highest_risk(left: str, right: str) -> str:
    if RISK_ORDER[right] > RISK_ORDER[left]:
        return right
    return left
