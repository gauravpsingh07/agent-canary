from fastapi.testclient import TestClient


def test_audit_logs_are_listed_newest_first(client: TestClient) -> None:
    first = client.post("/projects", json={"name": "First Project"}).json()
    second = client.post("/projects", json={"name": "Second Project"}).json()

    response = client.get("/audit-logs")

    assert response.status_code == 200
    logs = response.json()
    assert [log["event_type"] for log in logs[:2]] == ["PROJECT_CREATED", "PROJECT_CREATED"]
    assert logs[0]["project_id"] == second["id"]
    assert logs[1]["project_id"] == first["id"]
    assert logs[0]["event_metadata"] == {}


def test_audit_logs_can_be_filtered(client: TestClient) -> None:
    project = client.post("/projects", json={"name": "Filtered Project"}).json()
    client.put(f"/projects/{project['id']}", json={"description": "updated"})

    response = client.get(f"/audit-logs?project_id={project['id']}&event_type=PROJECT_UPDATED")

    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 1
    assert logs[0]["event_type"] == "PROJECT_UPDATED"
    assert logs[0]["event_metadata"]["updated_fields"] == ["description"]
