from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.db.session import get_db
from agent_canary.models import ToolDefinition
from agent_canary.schemas import (
    ToolCallValidationRequest,
    ToolCallValidationResponse,
    ToolDefinitionCreate,
    ToolDefinitionRead,
    ToolDefinitionUpdate,
    ToolSeedResponse,
)
from agent_canary.services.audit import write_audit_log
from agent_canary.services.tool_registry import (
    ToolSchemaError,
    seed_default_tools,
    validate_tool_arguments,
    validate_tool_definition_contract,
)

router = APIRouter(tags=["tools"])
DbSession = Annotated[Session, Depends(get_db)]


def get_tool_or_404(db: Session, tool_id: str) -> ToolDefinition:
    tool = db.get(ToolDefinition, tool_id)
    if tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return tool


def get_tool_by_name_or_404(db: Session, tool_name: str) -> ToolDefinition:
    tool = db.scalar(select(ToolDefinition).where(ToolDefinition.name == tool_name))
    if tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found")
    return tool


def ensure_unique_tool_name(db: Session, name: str, current_tool_id: str | None = None) -> None:
    existing_tool = db.scalar(select(ToolDefinition).where(ToolDefinition.name == name))
    if existing_tool is not None and existing_tool.id != current_tool_id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tool name already exists")


def validate_tool_payload(
    *,
    argument_schema: dict[str, object],
    example_valid_call: dict[str, object],
    example_invalid_call: dict[str, object],
) -> None:
    try:
        validate_tool_definition_contract(
            schema=argument_schema,
            example_valid_call=example_valid_call,
            example_invalid_call=example_invalid_call,
        )
    except ToolSchemaError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc


@router.get("/tools", response_model=list[ToolDefinitionRead])
def list_tools(db: DbSession) -> list[ToolDefinition]:
    statement = select(ToolDefinition).order_by(ToolDefinition.name.asc())
    return list(db.scalars(statement).all())


@router.post("/tools", response_model=ToolDefinitionRead, status_code=status.HTTP_201_CREATED)
def create_tool(payload: ToolDefinitionCreate, db: DbSession) -> ToolDefinition:
    ensure_unique_tool_name(db, payload.name)
    validate_tool_payload(
        argument_schema=payload.argument_schema,
        example_valid_call=payload.example_valid_call,
        example_invalid_call=payload.example_invalid_call,
    )

    tool = ToolDefinition(**payload.model_dump())
    db.add(tool)
    db.flush()
    write_audit_log(
        db,
        project_id=None,
        entity_type="tool_definition",
        entity_id=tool.id,
        event_type="TOOL_DEFINITION_CREATED",
        metadata={"tool_name": tool.name},
    )
    db.commit()
    db.refresh(tool)
    return tool


@router.post("/tools/seed-defaults", response_model=ToolSeedResponse)
def seed_tools(db: DbSession) -> ToolSeedResponse:
    tools_created, total_tools = seed_default_tools(db)
    db.commit()
    return ToolSeedResponse(tools_created=tools_created, total_tools=total_tools)


@router.post("/tools/validate-call", response_model=ToolCallValidationResponse)
def validate_tool_call(
    payload: ToolCallValidationRequest,
    db: DbSession,
) -> ToolCallValidationResponse:
    tool = get_tool_by_name_or_404(db, payload.tool_name)
    if not tool.is_active:
        return ToolCallValidationResponse(
            tool_name=tool.name,
            valid=False,
            errors=["Tool is inactive"],
            risk_level=tool.risk_level,
            requires_approval=tool.requires_approval,
        )

    errors = validate_tool_arguments(tool, payload.arguments)
    return ToolCallValidationResponse(
        tool_name=tool.name,
        valid=not errors,
        errors=errors,
        risk_level=tool.risk_level,
        requires_approval=tool.requires_approval,
    )


@router.get("/tools/{tool_id}", response_model=ToolDefinitionRead)
def get_tool(tool_id: str, db: DbSession) -> ToolDefinition:
    return get_tool_or_404(db, tool_id)


@router.put("/tools/{tool_id}", response_model=ToolDefinitionRead)
def update_tool(
    tool_id: str,
    payload: ToolDefinitionUpdate,
    db: DbSession,
) -> ToolDefinition:
    tool = get_tool_or_404(db, tool_id)
    updates = payload.model_dump(exclude_unset=True)

    next_name = updates.get("name", tool.name)
    if isinstance(next_name, str):
        ensure_unique_tool_name(db, next_name, current_tool_id=tool.id)

    next_schema = updates.get("argument_schema", tool.argument_schema)
    next_valid_call = updates.get("example_valid_call", tool.example_valid_call)
    next_invalid_call = updates.get("example_invalid_call", tool.example_invalid_call)
    if (
        isinstance(next_schema, dict)
        and isinstance(next_valid_call, dict)
        and isinstance(next_invalid_call, dict)
    ):
        validate_tool_payload(
            argument_schema=next_schema,
            example_valid_call=next_valid_call,
            example_invalid_call=next_invalid_call,
        )

    for field, value in updates.items():
        setattr(tool, field, value)

    write_audit_log(
        db,
        project_id=None,
        entity_type="tool_definition",
        entity_id=tool.id,
        event_type="TOOL_DEFINITION_UPDATED",
        metadata={"tool_name": tool.name, "updated_fields": sorted(updates)},
    )
    db.commit()
    db.refresh(tool)
    return tool


@router.delete("/tools/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tool(tool_id: str, db: DbSession) -> Response:
    tool = get_tool_or_404(db, tool_id)
    db.delete(tool)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
