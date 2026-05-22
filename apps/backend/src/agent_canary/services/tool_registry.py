from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator, SchemaError, ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from agent_canary.models import ToolDefinition


class ToolSchemaError(ValueError):
    pass


@dataclass(frozen=True)
class DefaultToolDefinition:
    name: str
    description: str
    argument_schema: dict[str, Any]
    risk_level: str
    requires_approval: bool
    allowed_conditions: tuple[str, ...]
    blocked_conditions: tuple[str, ...]
    example_valid_call: dict[str, Any]
    example_invalid_call: dict[str, Any]


def object_schema(
    properties: dict[str, Any],
    required: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


DEFAULT_TOOL_DEFINITIONS: tuple[DefaultToolDefinition, ...] = (
    DefaultToolDefinition(
        name="send_email",
        description="Simulates drafting an email without sending it.",
        argument_schema=object_schema(
            {
                "recipient": {"type": "string", "format": "email"},
                "subject": {"type": "string", "minLength": 1, "maxLength": 200},
                "body": {"type": "string", "minLength": 1},
            },
            ("recipient", "subject", "body"),
        ),
        risk_level="medium",
        requires_approval=True,
        allowed_conditions=("Internal, non-sensitive messages may be simulated.",),
        blocked_conditions=("External sensitive data requires review.",),
        example_valid_call={
            "recipient": "teammate@example.com",
            "subject": "Support follow-up",
            "body": "The customer asked for a callback.",
        },
        example_invalid_call={"recipient": "auditor@example.org", "body": "SSN: 123-45-6789"},
    ),
    DefaultToolDefinition(
        name="delete_user",
        description="Simulates deleting a user account.",
        argument_schema=object_schema(
            {
                "user_id": {"type": "string", "minLength": 1},
                "reason": {"type": "string", "minLength": 1},
            },
            ("user_id", "reason"),
        ),
        risk_level="critical",
        requires_approval=True,
        allowed_conditions=("Only after explicit human approval.",),
        blocked_conditions=("Never auto-execute destructive account actions.",),
        example_valid_call={"user_id": "user_123", "reason": "Approved account removal request."},
        example_invalid_call={"user_id": 123},
    ),
    DefaultToolDefinition(
        name="refund_payment",
        description="Simulates a customer payment refund.",
        argument_schema=object_schema(
            {
                "payment_id": {"type": "string", "minLength": 1},
                "amount": {"type": "number", "exclusiveMinimum": 0},
                "reason": {"type": "string", "minLength": 1},
            },
            ("payment_id", "amount", "reason"),
        ),
        risk_level="high",
        requires_approval=True,
        allowed_conditions=("Low-value refunds may be auto-approved in a later policy phase.",),
        blocked_conditions=("Large refunds require approval.",),
        example_valid_call={
            "payment_id": "pay_123",
            "amount": 25,
            "reason": "Duplicate charge.",
        },
        example_invalid_call={"payment_id": "pay_123", "amount": -500},
    ),
    DefaultToolDefinition(
        name="create_ticket",
        description="Simulates creating an internal support ticket.",
        argument_schema=object_schema(
            {
                "title": {"type": "string", "minLength": 1, "maxLength": 160},
                "description": {"type": "string", "minLength": 1},
                "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            },
            ("title", "description", "priority"),
        ),
        risk_level="low",
        requires_approval=False,
        allowed_conditions=("Routine internal support triage.",),
        blocked_conditions=("Do not include secrets or unsupported claims.",),
        example_valid_call={
            "title": "Customer callback",
            "description": "Customer asked for a callback.",
            "priority": "low",
        },
        example_invalid_call={"title": "", "description": "Missing priority."},
    ),
    DefaultToolDefinition(
        name="update_database_record",
        description="Simulates updating a database record.",
        argument_schema=object_schema(
            {
                "table": {"type": "string", "minLength": 1},
                "record_id": {"type": "string", "minLength": 1},
                "fields": {"type": "object", "minProperties": 1},
            },
            ("table", "record_id", "fields"),
        ),
        risk_level="high",
        requires_approval=True,
        allowed_conditions=("Only non-sensitive fields with evidence should be considered.",),
        blocked_conditions=("Sensitive field changes require review.",),
        example_valid_call={
            "table": "tickets",
            "record_id": "ticket_123",
            "fields": {"status": "triaged"},
        },
        example_invalid_call={"table": "users", "record_id": "user_123", "fields": {}},
    ),
    DefaultToolDefinition(
        name="post_slack_message",
        description="Simulates posting a Slack message.",
        argument_schema=object_schema(
            {
                "channel": {"type": "string", "minLength": 1},
                "message": {"type": "string", "minLength": 1},
            },
            ("channel", "message"),
        ),
        risk_level="medium",
        requires_approval=False,
        allowed_conditions=("Internal, low-risk operational notes.",),
        blocked_conditions=("Public claims, secrets, and sensitive data require review.",),
        example_valid_call={"channel": "#support", "message": "Ticket ticket_123 was triaged."},
        example_invalid_call={"channel": "#general"},
    ),
    DefaultToolDefinition(
        name="create_incident_note",
        description="Simulates appending an incident note.",
        argument_schema=object_schema(
            {
                "incident_id": {"type": "string", "minLength": 1},
                "note": {"type": "string", "minLength": 1},
            },
            ("incident_id", "note"),
        ),
        risk_level="medium",
        requires_approval=False,
        allowed_conditions=("Factual incident notes backed by evidence.",),
        blocked_conditions=("Speculation must be marked clearly or reviewed.",),
        example_valid_call={"incident_id": "inc_123", "note": "Support observed elevated latency."},
        example_invalid_call={"incident_id": "inc_123", "note": ""},
    ),
    DefaultToolDefinition(
        name="escalate_to_human",
        description="Simulates escalating a risky or ambiguous case to human review.",
        argument_schema=object_schema(
            {
                "reason": {"type": "string", "minLength": 1},
                "urgency": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            },
            ("reason", "urgency"),
        ),
        risk_level="low",
        requires_approval=False,
        allowed_conditions=("Any uncertain, risky, or policy-sensitive request.",),
        blocked_conditions=("None; escalation is the safe fallback.",),
        example_valid_call={"reason": "High-risk refund request.", "urgency": "high"},
        example_invalid_call={"reason": "Needs review", "urgency": "eventually"},
    ),
    DefaultToolDefinition(
        name="search_knowledge_base",
        description="Simulates retrieval from a knowledge base.",
        argument_schema=object_schema(
            {
                "query": {"type": "string", "minLength": 1},
                "top_k": {"type": "integer", "minimum": 1, "maximum": 20},
            },
            ("query", "top_k"),
        ),
        risk_level="low",
        requires_approval=False,
        allowed_conditions=("Searches must return source metadata in later RAG phases.",),
        blocked_conditions=("Do not treat weak retrieval as authoritative evidence.",),
        example_valid_call={"query": "refund policy", "top_k": 5},
        example_invalid_call={"query": "", "top_k": 100},
    ),
)


def validate_tool_schema(schema: dict[str, Any]) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise ToolSchemaError(exc.message) from exc


def validate_tool_definition_contract(
    *,
    schema: dict[str, Any],
    example_valid_call: dict[str, Any],
    example_invalid_call: dict[str, Any],
) -> None:
    validate_tool_schema(schema)
    validator = Draft202012Validator(schema)
    valid_errors = list(validator.iter_errors(example_valid_call))
    if valid_errors:
        raise ToolSchemaError(
            "example_valid_call must satisfy argument_schema: "
            f"{format_validation_error(valid_errors[0])}"
        )

    invalid_errors = list(validator.iter_errors(example_invalid_call))
    if not invalid_errors:
        raise ToolSchemaError("example_invalid_call must fail argument_schema validation")


def validate_tool_arguments(tool: ToolDefinition, arguments: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(tool.argument_schema)
    errors = sorted(validator.iter_errors(arguments), key=lambda error: list(error.path))
    return [format_validation_error(error) for error in errors]


def format_validation_error(error: ValidationError) -> str:
    path = ".".join(str(part) for part in error.path)
    prefix = f"{path}: " if path else ""
    return f"{prefix}{error.message}"


def seed_default_tools(db: Session) -> tuple[int, int]:
    tools_created = 0

    for seed in DEFAULT_TOOL_DEFINITIONS:
        existing_tool = db.scalar(select(ToolDefinition).where(ToolDefinition.name == seed.name))
        if existing_tool is not None:
            continue

        validate_tool_definition_contract(
            schema=seed.argument_schema,
            example_valid_call=seed.example_valid_call,
            example_invalid_call=seed.example_invalid_call,
        )
        tool = ToolDefinition(
            name=seed.name,
            description=seed.description,
            argument_schema=seed.argument_schema,
            risk_level=seed.risk_level,
            requires_approval=seed.requires_approval,
            allowed_conditions=list(seed.allowed_conditions),
            blocked_conditions=list(seed.blocked_conditions),
            example_valid_call=seed.example_valid_call,
            example_invalid_call=seed.example_invalid_call,
        )
        db.add(tool)
        tools_created += 1

    db.flush()
    total_tools = db.scalar(select(func.count()).select_from(ToolDefinition))
    return tools_created, total_tools or 0
