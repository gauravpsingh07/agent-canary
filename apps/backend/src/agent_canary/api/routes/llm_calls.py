from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import LLMCall
from agent_canary.schemas import LLMCallRead

router = APIRouter(tags=["llm calls"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/llm-calls", response_model=list[LLMCallRead])
def list_llm_calls(
    db: DbSession,
    limit: int = Query(default=100, ge=1, le=500),
    test_run_id: str | None = None,
    project_id: str | None = None,
    provider_name: str | None = None,
) -> list[LLMCall]:
    statement = select(LLMCall).order_by(LLMCall.created_at.desc()).limit(limit)
    if test_run_id is not None:
        statement = statement.where(LLMCall.test_run_id == test_run_id)
    if project_id is not None:
        statement = statement.where(LLMCall.project_id == project_id)
    if provider_name is not None:
        statement = statement.where(LLMCall.provider_name == provider_name)
    return list(db.scalars(statement).all())


@router.get("/llm-calls/{call_id}", response_model=LLMCallRead)
def get_llm_call(call_id: str, db: DbSession) -> LLMCall:
    llm_call = db.get(LLMCall, call_id)
    if llm_call is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="LLM call not found")
    return llm_call
