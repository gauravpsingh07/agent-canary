from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import ApprovalRequest
from agent_canary.schemas import ApprovalDecisionRequest, ApprovalRequestRead
from agent_canary.schemas.approval_request import APPROVAL_STATUSES
from agent_canary.services.approvals import ApprovalDecision, decide_approval_request

router = APIRouter(tags=["approvals"])
DbSession = Annotated[Session, Depends(get_db)]


def get_approval_request_or_404(db: Session, request_id: str) -> ApprovalRequest:
    approval_request = db.get(ApprovalRequest, request_id)
    if approval_request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval request not found",
        )
    return approval_request


@router.get("/approval-requests", response_model=list[ApprovalRequestRead])
def list_approval_requests(
    db: DbSession,
    status_filter: str | None = Query(default=None, alias="status"),
) -> list[ApprovalRequest]:
    statement = select(ApprovalRequest).order_by(ApprovalRequest.created_at.desc())
    if status_filter is not None:
        if status_filter not in APPROVAL_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Status must be pending, approved, or rejected",
            )
        statement = statement.where(ApprovalRequest.status == status_filter)
    return list(db.scalars(statement).all())


@router.get("/approval-requests/{request_id}", response_model=ApprovalRequestRead)
def get_approval_request(request_id: str, db: DbSession) -> ApprovalRequest:
    return get_approval_request_or_404(db, request_id)


@router.post("/approval-requests/{request_id}/approve", response_model=ApprovalRequestRead)
def approve_request(
    request_id: str,
    payload: ApprovalDecisionRequest,
    db: DbSession,
) -> ApprovalRequest:
    approval_request = get_approval_request_or_404(db, request_id)
    return decide_request(
        db,
        approval_request,
        decision="approved",
        reviewer_note=payload.reviewer_note,
    )


@router.post("/approval-requests/{request_id}/reject", response_model=ApprovalRequestRead)
def reject_request(
    request_id: str,
    payload: ApprovalDecisionRequest,
    db: DbSession,
) -> ApprovalRequest:
    approval_request = get_approval_request_or_404(db, request_id)
    return decide_request(
        db,
        approval_request,
        decision="rejected",
        reviewer_note=payload.reviewer_note,
    )


def decide_request(
    db: Session,
    approval_request: ApprovalRequest,
    *,
    decision: ApprovalDecision,
    reviewer_note: str | None,
) -> ApprovalRequest:
    try:
        decided_request = decide_approval_request(
            db,
            approval_request,
            decision=decision,
            reviewer_note=reviewer_note,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc
    db.commit()
    db.refresh(decided_request)
    return decided_request
