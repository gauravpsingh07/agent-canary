from fastapi.testclient import TestClient


def seed_rag_project(client: TestClient) -> tuple[str, str]:
    project_id = client.post("/projects", json={"name": "RAG Failure Project"}).json()["id"]
    seed_response = client.post(f"/projects/{project_id}/seed-rag-demo-data")
    assert seed_response.status_code == 200
    seed_body = seed_response.json()
    assert seed_body["documents_created"] == 3
    assert seed_body["suites_created"] == 1
    assert seed_body["test_cases_created"] == 4

    suites = client.get(f"/projects/{project_id}/test-suites").json()
    rag_suite_id = next(
        suite["id"] for suite in suites if suite["name"] == "RAG Failure Evaluation"
    )
    return project_id, rag_suite_id


def get_case_id(client: TestClient, suite_id: str, name: str) -> str:
    cases = client.get(f"/test-suites/{suite_id}/test-cases").json()
    return str(next(test_case["id"] for test_case in cases if test_case["name"] == name))


def test_seed_rag_demo_data_is_idempotent(client: TestClient) -> None:
    project_id, _ = seed_rag_project(client)

    repeat_response = client.post(f"/projects/{project_id}/seed-rag-demo-data")

    assert repeat_response.status_code == 200
    repeat_body = repeat_response.json()
    assert repeat_body["documents_created"] == 0
    assert repeat_body["suites_created"] == 0
    assert repeat_body["test_cases_created"] == 0
    assert repeat_body["total_rag_documents"] == 3
    assert repeat_body["total_rag_test_cases"] == 4


def test_rag_workflow_retrieves_evidence_and_validates_citations(
    client: TestClient,
) -> None:
    _, suite_id = seed_rag_project(client)
    test_case_id = get_case_id(client, suite_id, "Stale Context Should Warn")

    response = client.post(f"/test-cases/{test_case_id}/run")

    assert response.status_code == 200
    run = response.json()
    assert run["passed"] is True
    assert run["run_metadata"]["retrieval_result_id"] is not None
    assert len(run["run_metadata"]["retrieved_evidence"]) > 0
    assert run["run_metadata"]["validated_output"]["citations"]

    steps = client.get(f"/test-runs/{run['id']}/steps").json()
    assert "retrieve_evidence" in [step["step_name"] for step in steps]


def test_missing_rag_citations_fail_evaluation(client: TestClient) -> None:
    _, suite_id = seed_rag_project(client)
    test_case_id = get_case_id(client, suite_id, "Missing Citations Should Fail")

    response = client.post(f"/test-cases/{test_case_id}/run")

    assert response.status_code == 200
    run = response.json()
    assert run["passed"] is False
    assert "Grounded answer did not include required citations." in run["failure_reasons"]
    assert run["run_metadata"]["evaluation_scores"]["groundedness_score"] == 0


def test_rag_quality_and_citation_metrics(client: TestClient) -> None:
    _, suite_id = seed_rag_project(client)
    stale_case_id = get_case_id(client, suite_id, "Stale Context Should Warn")
    missing_citation_case_id = get_case_id(client, suite_id, "Missing Citations Should Fail")

    client.post(f"/test-cases/{stale_case_id}/run")
    client.post(f"/test-cases/{missing_citation_case_id}/run")

    retrieval_quality = client.get("/metrics/retrieval-quality").json()
    assert retrieval_quality["total_retrievals"] == 2
    assert retrieval_quality["average_result_count"] > 0
    assert retrieval_quality["average_top_score"] > 0

    citation_coverage = client.get("/metrics/citation-coverage").json()
    assert citation_coverage["grounded_runs"] == 2
    assert citation_coverage["runs_with_citations"] == 1
    assert citation_coverage["citation_coverage_rate"] == 50.0
