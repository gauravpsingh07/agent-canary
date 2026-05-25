from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import ToolCall
from agent_canary.schemas import ToolCallRead

router = APIRouter(tags=["tool calls"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get("/tool-calls", response_model=list[ToolCallRead])
def list_tool_calls(
    db: DbSession,
    limit: int = Query(default=100, ge=1, le=500),
    test_run_id: str | None = None,
    tool_name: str | None = None,
) -> list[ToolCall]:
    statement = select(ToolCall).order_by(ToolCall.created_at.desc()).limit(limit)
    if test_run_id is not None:
        statement = statement.where(ToolCall.test_run_id == test_run_id)
    if tool_name is not None:
        statement = statement.where(ToolCall.tool_name == tool_name)
    return list(db.scalars(statement).all())


@router.get("/tool-calls/{call_id}", response_model=ToolCallRead)
def get_tool_call(call_id: str, db: DbSession) -> ToolCall:
    tool_call = db.get(ToolCall, call_id)
    if tool_call is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool call not found")
    return tool_call
