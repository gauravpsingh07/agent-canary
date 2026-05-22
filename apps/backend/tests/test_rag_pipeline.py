from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from agent_canary.models import AuditLog, RetrievalResult


def test_document_ingestion_creates_chunks_and_audit_logs(
    client: TestClient,
    db_session: Session,
) -> None:
    project_id = client.post("/projects", json={"name": "RAG Project"}).json()["id"]
    response = client.post(
        "/rag/documents",
        json={
            "project_id": project_id,
            "title": "Refund Policy",
            "content": (
                "Refund policy: customers can request refunds within 30 days. "
                "Escalations above $25 require human approval. "
            )
            * 12,
            "source_type": "manual",
            "source_uri": "kb://refund-policy",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["document"]["status"] == "indexed"
    assert body["chunks_created"] > 1
    assert body["ingestion_job"]["status"] == "completed"

    chunks_response = client.get(f"/rag/documents/{body['document']['id']}/chunks")
    assert chunks_response.status_code == 200
    chunks = chunks_response.json()
    assert len(chunks) == body["chunks_created"]
    assert chunks[0]["embedding_provider"] == "mock"

    audit_events = list(
        db_session.scalars(
            select(AuditLog.event_type).where(AuditLog.entity_id == body["document"]["id"])
        ).all()
    )
    assert "DOCUMENT_INGESTION_STARTED" in audit_events
    assert "DOCUMENT_INGESTION_COMPLETED" in audit_events


def test_retrieval_persists_ranked_results_with_threshold(client: TestClient) -> None:
    project_id = client.post("/projects", json={"name": "Retrieval Project"}).json()["id"]
    client.post(
        "/rag/documents",
        json={
            "project_id": project_id,
            "title": "Refund Rules",
            "content": "Refund policy requires review for refunds above twenty five dollars.",
        },
    )
    client.post(
        "/rag/documents",
        json={
            "project_id": project_id,
            "title": "Incident Notes",
            "content": "Database outage notes describe queue lag and incident updates.",
        },
    )

    response = client.post(
        "/rag/retrieve",
        json={
            "project_id": project_id,
            "query": "refund policy",
            "max_results": 3,
            "min_score": 0.2,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result_count"] >= 1
    assert body["results"][0]["document_title"] == "Refund Rules"
    assert body["provider_name"] == "mock"

    stored_result = client.get(f"/rag/retrieval-results/{body['id']}").json()
    assert stored_result["id"] == body["id"]


def test_retrieval_threshold_can_filter_all_results(
    client: TestClient,
    db_session: Session,
) -> None:
    project_id = client.post("/projects", json={"name": "Threshold Project"}).json()["id"]
    client.post(
        "/rag/documents",
        json={
            "project_id": project_id,
            "title": "Support Guide",
            "content": "Support tickets should include a concise customer summary.",
        },
    )

    response = client.post(
        "/rag/retrieve",
        json={
            "project_id": project_id,
            "query": "refund policy",
            "max_results": 5,
            "min_score": 0.95,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["result_count"] == 0
    assert body["results"] == []

    result = db_session.get(RetrievalResult, body["id"])
    assert result is not None
    assert result.result_count == 0
