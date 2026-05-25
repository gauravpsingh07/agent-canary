# API Reference

All endpoints are mounted at the root. The interactive OpenAPI UI is available at `/docs` when the backend is running.

Conventions:

- Request and response bodies are JSON.
- All ID fields are UUIDv4 strings.
- `created_at` / `updated_at` are ISO-8601 UTC timestamps.
- Deletes return `204 No Content`. Other writes return `201 Created` or `200 OK`.

---

## Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service health probe. Returns `{status, service, environment}`. |

---

## Projects

| Method | Path | Description |
|---|---|---|
| GET | `/projects` | List projects, newest first. |
| POST | `/projects` | Create a project. Body: `{name, description?}`. |
| GET | `/projects/{project_id}` | Read one project. |
| PUT | `/projects/{project_id}` | Partial update. |
| DELETE | `/projects/{project_id}` | Cascade-delete project. |
| POST | `/projects/{project_id}/seed-demo-data` | Idempotently seed 6 adversarial suites with 25 cases. |
| POST | `/projects/{project_id}/seed-rag-demo-data` | Idempotently seed 3 RAG docs + a RAG failure suite with 4 cases. |

---

## Test Suites

| Method | Path | Description |
|---|---|---|
| GET | `/projects/{project_id}/test-suites` | List suites in a project. |
| POST | `/projects/{project_id}/test-suites` | Create a suite. Body: `{name, description?, category}`. |
| GET | `/test-suites/{suite_id}` | Read one suite. |
| PUT | `/test-suites/{suite_id}` | Partial update. |
| DELETE | `/test-suites/{suite_id}` | Cascade-delete. |
| POST | `/test-suites/{suite_id}/run` | Run every test case in the suite. Optional `?async_mode=true` runs in BackgroundTasks. |

---

## Test Cases

| Method | Path | Description |
|---|---|---|
| GET | `/test-suites/{suite_id}/test-cases` | List cases in a suite. |
| POST | `/test-suites/{suite_id}/test-cases` | Create a case. Body: full `TestCaseCreate` schema (see below). |
| GET | `/test-cases/{test_case_id}` | Read one case. |
| PUT | `/test-cases/{test_case_id}` | Partial update. |
| DELETE | `/test-cases/{test_case_id}` | Cascade-delete. |
| POST | `/test-cases/{test_case_id}/run` | Synchronously run one case and return the `TestRun`. |

`TestCaseCreate` fields:

```
{
  "name": "string",
  "description": "string|null",
  "category": "prompt_injection|unsafe_tool_call|structured_output|approval_required|weak_retrieval|stale_context|hallucination|secret_leakage|policy_bypass|refusal_behavior|retrieval_quality|citation_failure|unsupported_claim",
  "input_prompt": "string",
  "system_prompt": "string|null",
  "expected_behavior": "string",
  "expected_tool_name": "string|null",
  "should_call_tool": false,
  "should_require_approval": false,
  "expected_refusal": false,
  "expected_schema_valid": true,
  "requires_retrieval": false,
  "expected_citations": false,
  "min_retrieval_score": null,
  "tags": ["string"],
  "severity": "low|medium|high|critical"
}
```

---

## Test Runs

| Method | Path | Description |
|---|---|---|
| GET | `/test-runs` | All runs, newest first. |
| GET | `/test-runs/{test_run_id}` | One run with `run_metadata`. |
| GET | `/test-runs/{test_run_id}/steps` | LangGraph step ledger for one run. |

---

## Tools

| Method | Path | Description |
|---|---|---|
| GET | `/tools` | List tool definitions. |
| POST | `/tools` | Create a new tool definition. Validates `example_valid_call` and `example_invalid_call` against the schema. |
| GET | `/tools/{tool_id}` | Read one tool. |
| PUT | `/tools/{tool_id}` | Partial update. |
| DELETE | `/tools/{tool_id}` | Delete. |
| POST | `/tools/seed-defaults` | Idempotently seed the 9 simulated tools. |
| POST | `/tools/validate-call` | Validate a `{tool_name, arguments}` payload without executing anything. |

---

## Policy

| Method | Path | Description |
|---|---|---|
| GET | `/policy-rules` | List rules. |
| POST | `/policy-rules` | Create a rule. |
| GET | `/policy-rules/{rule_id}` | Read one. |
| PUT | `/policy-rules/{rule_id}` | Partial update. |
| DELETE | `/policy-rules/{rule_id}` | Delete. |
| POST | `/policy-rules/seed-defaults` | Idempotently seed the 13 default rules. |
| POST | `/policy/evaluate` | Evaluate a proposed tool call. Optional `persist_violations: true` writes `PolicyViolation` rows. |

---

## Approvals

| Method | Path | Description |
|---|---|---|
| GET | `/approval-requests` | List approval requests. `?status=pending|approved|rejected` filter. |
| GET | `/approval-requests/{request_id}` | One request. |
| POST | `/approval-requests/{request_id}/approve` | Approve. Body: `{reviewer_note?}`. |
| POST | `/approval-requests/{request_id}/reject` | Reject. |

A repeated approve/reject on a non-pending request returns `409`.

---

## Audit Logs

| Method | Path | Description |
|---|---|---|
| GET | `/audit-logs?limit=N&project_id=&event_type=` | Most recent N audit events. Filterable. |

---

## Evaluation Results & Metrics

| Method | Path | Description |
|---|---|---|
| GET | `/evaluation-results` | All evaluation results. |
| GET | `/evaluation-results/{result_id}` | One result with all 10 scores + 3 flags. |
| GET | `/metrics/summary` | Aggregate counts: total_test_runs, pass_rate, average_score, high_risk_failures, etc. |
| GET | `/metrics/failures-by-category` | Failure count + avg score grouped by test-case category. |
| GET | `/metrics/provider-latency` | Avg latency grouped by `(provider_name, model_name)`. |
| GET | `/metrics/policy-violations` | Count + highest severity grouped by violation_code. |
| GET | `/metrics/retrieval-quality` | Total retrievals, empty count, weak count, avg top score. |
| GET | `/metrics/citation-coverage` | Grounded run count, runs with citations, coverage rate. |

---

## RAG

| Method | Path | Description |
|---|---|---|
| POST | `/rag/documents` | Ingest a document (synchronous). Optional `?async_mode=true` schedules a BackgroundTask and returns immediately with `status: pending` and a queued ingestion job. |
| POST | `/rag/documents/{document_id}/ingest` | Re-ingest an existing document with new content. Deletes prior chunks. |
| GET | `/rag/documents` | List documents. |
| GET | `/rag/documents/{document_id}` | Read one document. |
| GET | `/rag/documents/{document_id}/chunks` | List chunks for a document. |
| GET | `/rag/ingestion-jobs` | List ingestion jobs across all documents. |
| POST | `/rag/retrieve` | Run a retrieval query. Uses pgvector cosine distance on Postgres, falls back to Python cosine on SQLite. |
| GET | `/rag/retrieval-results` | List retrieval queries. Filters: `?project_id=`, `?test_run_id=`, `?limit=N`. |
| GET | `/rag/retrieval-results/{result_id}` | Read one retrieval, including `used_in_answer` per chunk. |

---

## LLM Calls

| Method | Path | Description |
|---|---|---|
| GET | `/llm-calls` | List LLM calls. Filters: `?test_run_id=`, `?project_id=`, `?provider_name=`, `?limit=N`. |
| GET | `/llm-calls/{call_id}` | One LLM call with prompt + response. |

---

## Tool Calls

| Method | Path | Description |
|---|---|---|
| GET | `/tool-calls` | List tool calls. Filters: `?test_run_id=`, `?tool_name=`, `?limit=N`. |
| GET | `/tool-calls/{call_id}` | One tool call with policy decisions. |

---

## Audit event types

The full set of event names you may see in `/audit-logs`:

```
PROJECT_CREATED  PROJECT_UPDATED
TEST_SUITE_CREATED  TEST_SUITE_UPDATED
TEST_CASE_CREATED  TEST_CASE_UPDATED
TOOL_DEFINITION_CREATED  TOOL_DEFINITION_UPDATED
POLICY_RULE_CREATED  POLICY_RULE_UPDATED  POLICY_RULE_DELETED
TEST_RUN_STARTED  TEST_RUN_QUEUED  TEST_RUN_COMPLETED  TEST_RUN_FAILED
LLM_CALLED  AGENT_OUTPUT_RECEIVED
STRUCTURED_OUTPUT_VALIDATED
TOOL_CALL_PROPOSED
POLICY_CHECK_COMPLETED
RETRIEVAL_STARTED  RETRIEVAL_COMPLETED  RAG_RETRIEVAL_COMPLETED
EMBEDDINGS_GENERATED
DOCUMENT_INGESTION_STARTED  DOCUMENT_INGESTION_COMPLETED  DOCUMENT_INGESTION_FAILED
DOCUMENT_INGESTED
RAG_EVALUATION_COMPLETED
EVALUATION_COMPLETED
APPROVAL_REQUEST_CREATED  APPROVAL_APPROVED  APPROVAL_REJECTED
```
