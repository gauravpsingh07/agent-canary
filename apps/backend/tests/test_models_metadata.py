from agent_canary.db.base import Base


def test_phase_one_tables_are_registered() -> None:
    assert {
        "projects",
        "test_suites",
        "test_cases",
        "test_runs",
        "test_run_steps",
        "evaluation_results",
        "approval_requests",
        "rag_documents",
        "rag_chunks",
        "retrieval_results",
        "document_ingestion_jobs",
        "audit_logs",
        "tool_definitions",
        "policy_rules",
        "policy_violations",
    }.issubset(Base.metadata.tables)


def test_test_case_model_has_expected_evaluation_fields() -> None:
    columns = Base.metadata.tables["test_cases"].columns.keys()

    assert {
        "input_prompt",
        "expected_behavior",
        "expected_tool_name",
        "should_call_tool",
        "should_require_approval",
        "expected_refusal",
        "expected_schema_valid",
        "tags",
        "severity",
    }.issubset(columns)
