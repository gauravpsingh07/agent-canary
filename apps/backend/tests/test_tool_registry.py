from collections import Counter

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.models import AuditLog, ToolDefinition

CUSTOM_TOOL_PAYLOAD = {
    "name": "archive_ticket",
    "description": "Simulates archiving a support ticket.",
    "argument_schema": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "ticket_id": {"type": "string", "minLength": 1},
            "reason": {"type": "string", "minLength": 1},
        },
        "required": ["ticket_id", "reason"],
        "additionalProperties": False,
    },
    "risk_level": "medium",
    "requires_approval": True,
    "allowed_conditions": ["Only after ticket resolution is confirmed."],
    "blocked_conditions": ["Do not archive active incidents."],
    "example_valid_call": {"ticket_id": "ticket_123", "reason": "Resolved by support."},
    "example_invalid_call": {"ticket_id": ""},
}


def test_seed_default_tools_is_idempotent_and_validates_examples(
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post("/tools/seed-defaults")

    assert response.status_code == 200
    assert response.json() == {"tools_created": 9, "total_tools": 9}

    second_response = client.post("/tools/seed-defaults")
    assert second_response.status_code == 200
    assert second_response.json() == {"tools_created": 0, "total_tools": 9}

    tools_response = client.get("/tools")
    assert tools_response.status_code == 200
    tools = tools_response.json()
    tool_names = {tool["name"] for tool in tools}

    assert {
        "send_email",
        "delete_user",
        "refund_payment",
        "create_ticket",
        "update_database_record",
        "post_slack_message",
        "create_incident_note",
        "escalate_to_human",
        "search_knowledge_base",
    } == tool_names

    refund_tool = db_session.scalar(
        select(ToolDefinition).where(ToolDefinition.name == "refund_payment")
    )
    assert refund_tool is not None
    assert refund_tool.requires_approval is True
    assert refund_tool.risk_level == "high"


def test_create_update_and_read_tool_definition(
    client: TestClient,
    db_session: Session,
) -> None:
    create_response = client.post("/tools", json=CUSTOM_TOOL_PAYLOAD)
    assert create_response.status_code == 201
    tool = create_response.json()
    assert tool["name"] == "archive_ticket"

    duplicate_response = client.post("/tools", json=CUSTOM_TOOL_PAYLOAD)
    assert duplicate_response.status_code == 409

    get_response = client.get(f"/tools/{tool['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == tool["id"]

    update_response = client.put(
        f"/tools/{tool['id']}",
        json={"description": "Updated archive simulation.", "risk_level": "low"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["description"] == "Updated archive simulation."
    assert update_response.json()["risk_level"] == "low"

    audit_events = db_session.scalars(select(AuditLog.event_type)).all()
    assert Counter(audit_events) == Counter(
        ["TOOL_DEFINITION_CREATED", "TOOL_DEFINITION_UPDATED"]
    )


def test_create_tool_rejects_bad_json_schema_contract(client: TestClient) -> None:
    bad_payload = {
        **CUSTOM_TOOL_PAYLOAD,
        "name": "bad_archive_ticket",
        "example_valid_call": {"ticket_id": ""},
    }

    response = client.post("/tools", json=bad_payload)

    assert response.status_code == 422
    assert "example_valid_call" in response.json()["detail"]


def test_validate_tool_call_accepts_valid_arguments(client: TestClient) -> None:
    client.post("/tools/seed-defaults")

    response = client.post(
        "/tools/validate-call",
        json={
            "tool_name": "create_ticket",
            "arguments": {
                "title": "Customer callback",
                "description": "Customer requested a callback.",
                "priority": "low",
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "tool_name": "create_ticket",
        "valid": True,
        "errors": [],
        "risk_level": "low",
        "requires_approval": False,
    }


def test_validate_tool_call_rejects_invalid_arguments(client: TestClient) -> None:
    client.post("/tools/seed-defaults")

    response = client.post(
        "/tools/validate-call",
        json={"tool_name": "refund_payment", "arguments": {"payment_id": "pay_123", "amount": -1}},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid"] is False
    assert body["risk_level"] == "high"
    assert any("amount" in error for error in body["errors"])


def test_validate_tool_call_rejects_inactive_tool(client: TestClient) -> None:
    create_response = client.post("/tools", json=CUSTOM_TOOL_PAYLOAD)
    tool_id = create_response.json()["id"]
    client.put(f"/tools/{tool_id}", json={"is_active": False})

    response = client.post(
        "/tools/validate-call",
        json={
            "tool_name": "archive_ticket",
            "arguments": {"ticket_id": "ticket_123", "reason": "Resolved."},
        },
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert response.json()["errors"] == ["Tool is inactive"]


def test_validate_tool_call_returns_404_for_unknown_tool(client: TestClient) -> None:
    response = client.post(
        "/tools/validate-call",
        json={"tool_name": "missing_tool", "arguments": {}},
    )

    assert response.status_code == 404

