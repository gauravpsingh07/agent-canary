from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import PolicyRule
from agent_canary.schemas import (
    PolicyEvaluateRequest,
    PolicyEvaluationResponse,
    PolicyRuleCreate,
    PolicyRuleRead,
    PolicyRuleSeedResponse,
    PolicyRuleUpdate,
)
from agent_canary.services.audit import write_audit_log
from agent_canary.services.policy_engine import evaluate_policy, seed_default_policy_rules

router = APIRouter(tags=["policy"])
DbSession = Annotated[Session, Depends(get_db)]


def get_policy_rule_or_404(db: Session, rule_id: str) -> PolicyRule:
    rule = db.get(PolicyRule, rule_id)
    if rule is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy rule not found")
    return rule


def ensure_unique_policy_rule_name(
    db: Session,
    name: str,
    current_rule_id: str | None = None,
) -> None:
    existing_rule = db.scalar(select(PolicyRule).where(PolicyRule.name == name))
    if existing_rule is not None and existing_rule.id != current_rule_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Policy rule name already exists",
        )


@router.get("/policy-rules", response_model=list[PolicyRuleRead])
def list_policy_rules(db: DbSession) -> list[PolicyRule]:
    statement = select(PolicyRule).order_by(PolicyRule.created_at.desc())
    return list(db.scalars(statement).all())


@router.post(
    "/policy-rules",
    response_model=PolicyRuleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_policy_rule(payload: PolicyRuleCreate, db: DbSession) -> PolicyRule:
    ensure_unique_policy_rule_name(db, payload.name)
    rule = PolicyRule(**payload.model_dump())
    db.add(rule)
    db.flush()
    write_audit_log(
        db,
        project_id=None,
        entity_type="policy_rule",
        entity_id=rule.id,
        event_type="POLICY_RULE_CREATED",
        metadata={"rule_name": rule.name},
    )
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/policy-rules/seed-defaults", response_model=PolicyRuleSeedResponse)
def seed_policy_rules(db: DbSession) -> PolicyRuleSeedResponse:
    rules_created, total_rules = seed_default_policy_rules(db)
    db.commit()
    return PolicyRuleSeedResponse(rules_created=rules_created, total_rules=total_rules)


@router.get("/policy-rules/{rule_id}", response_model=PolicyRuleRead)
def get_policy_rule(rule_id: str, db: DbSession) -> PolicyRule:
    return get_policy_rule_or_404(db, rule_id)


@router.put("/policy-rules/{rule_id}", response_model=PolicyRuleRead)
def update_policy_rule(
    rule_id: str,
    payload: PolicyRuleUpdate,
    db: DbSession,
) -> PolicyRule:
    rule = get_policy_rule_or_404(db, rule_id)
    updates = payload.model_dump(exclude_unset=True)
    next_name = updates.get("name", rule.name)
    if isinstance(next_name, str):
        ensure_unique_policy_rule_name(db, next_name, current_rule_id=rule.id)

    for field, value in updates.items():
        setattr(rule, field, value)

    write_audit_log(
        db,
        project_id=None,
        entity_type="policy_rule",
        entity_id=rule.id,
        event_type="POLICY_RULE_UPDATED",
        metadata={"rule_name": rule.name, "updated_fields": sorted(updates)},
    )
    db.commit()
    db.refresh(rule)
    return rule


@router.post("/policy/evaluate", response_model=PolicyEvaluationResponse)
def evaluate_policy_request(
    payload: PolicyEvaluateRequest,
    db: DbSession,
) -> PolicyEvaluationResponse:
    evaluation = evaluate_policy(db, payload)
    if payload.persist_violations:
        db.commit()
    return PolicyEvaluationResponse(
        tool_name=evaluation.tool_name,
        allowed=evaluation.allowed,
        blocked=evaluation.blocked,
        requires_approval=evaluation.requires_approval,
        risk_level=evaluation.risk_level,
        violations=evaluation.violations,
        explanation=evaluation.explanation,
    )

