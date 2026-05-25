export type Project = {
  id: string;
  name: string;
  description?: string | null;
  created_at: string;
  updated_at: string;
};

export type TestSuite = {
  id: string;
  project_id: string;
  name: string;
  description?: string | null;
  category: string;
  created_at: string;
  updated_at: string;
};

export type TestCase = {
  id: string;
  suite_id: string;
  name: string;
  description?: string | null;
  category: string;
  input_prompt: string;
  system_prompt?: string | null;
  expected_behavior: string;
  expected_tool_name?: string | null;
  should_call_tool: boolean;
  should_require_approval: boolean;
  expected_refusal: boolean;
  expected_schema_valid: boolean;
  requires_retrieval: boolean;
  expected_citations: boolean;
  min_retrieval_score?: number | null;
  tags: string[];
  severity: string;
  created_at?: string;
  updated_at?: string;
};

export type TestRun = {
  id: string;
  test_case_id: string;
  status: string;
  provider_name?: string | null;
  model_name?: string | null;
  overall_score?: number | null;
  passed?: boolean | null;
  failure_reasons: string[];
  run_metadata: Record<string, unknown>;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
};

export type TestRunStep = {
  id: string;
  test_run_id: string;
  step_order: number;
  step_name: string;
  status: string;
  input_payload?: Record<string, unknown>;
  output_payload?: Record<string, unknown>;
  error_message?: string | null;
  created_at?: string;
};

export type EvaluationResult = {
  id: string;
  test_run_id: string;
  passed: boolean;
  overall_score: number;
  schema_validity_score?: number;
  tool_safety_score?: number;
  policy_compliance_score?: number;
  approval_correctness_score?: number;
  refusal_correctness_score?: number;
  groundedness_score?: number;
  prompt_injection_resistance_score?: number;
  retrieval_quality_score?: number;
  citation_coverage_score?: number;
  latency_score?: number;
  stale_context_flag?: boolean;
  unsupported_claim_flag?: boolean;
  weak_evidence_flag?: boolean;
  failure_reasons: string[];
  policy_violations: Record<string, unknown>[];
  evaluator_notes?: string | null;
  latency_ms?: number | null;
  provider_name?: string | null;
  model_name?: string | null;
  created_at: string;
};

export type DocumentIngestionJob = {
  id: string;
  project_id?: string | null;
  document_id?: string | null;
  status: string;
  chunks_created: number;
  error_message?: string | null;
  job_metadata: Record<string, unknown>;
  started_at?: string | null;
  completed_at?: string | null;
  created_at: string;
};

export type LLMCall = {
  id: string;
  test_run_id?: string | null;
  project_id?: string | null;
  provider_name: string;
  model_name: string;
  prompt: string;
  response_text?: string | null;
  latency_ms?: number | null;
  created_at: string;
};

export type ToolCall = {
  id: string;
  test_run_id: string;
  tool_name: string;
  arguments: Record<string, unknown>;
  validation_errors: string[];
  schema_valid: boolean;
  simulated_action_allowed: boolean;
  requires_approval: boolean;
  blocked: boolean;
  risk_level: string;
  created_at: string;
};

export type MetricsSummary = {
  total_test_runs: number;
  completed_evaluations: number;
  passed_evaluations: number;
  failed_evaluations: number;
  pass_rate: number;
  failure_rate: number;
  average_score: number;
  high_risk_failures: number;
  pending_approvals: number;
  policy_violation_count: number;
};

export type FailureByCategory = {
  category: string;
  total_failures: number;
  average_score: number;
};

export type ProviderLatency = {
  provider_name: string;
  model_name: string;
  run_count: number;
  average_latency_ms: number;
};

export type PolicyViolationMetric = {
  violation_code: string;
  count: number;
  highest_severity: string;
};

export type ApprovalRequest = {
  id: string;
  test_run_id: string;
  risk_level: string;
  reason: string;
  status: "pending" | "approved" | "rejected";
  proposed_tool_call: Record<string, unknown>;
  reviewer_note?: string | null;
  created_at: string;
};

export type ToolDefinition = {
  id: string;
  name: string;
  description: string;
  risk_level: string;
  requires_approval: boolean;
  is_active: boolean;
};

export type PolicyRule = {
  id: string;
  name: string;
  description?: string | null;
  rule_type: string;
  tool_name?: string | null;
  violation_code: string;
  effect: string;
  risk_level?: string;
  is_enabled: boolean;
};

export type RagDocument = {
  id: string;
  project_id?: string | null;
  title: string;
  source_type: string;
  source_uri?: string | null;
  status: string;
  created_at: string;
};

export type RetrievalResult = {
  id: string;
  query: string;
  result_count: number;
  provider_name: string;
  model_name: string;
  results: RetrievedChunk[];
  created_at: string;
};

export type RetrievedChunk = {
  chunk_id: string;
  document_id: string;
  document_title: string;
  source_uri?: string | null;
  chunk_index?: number;
  content: string;
  score: number;
};

export type RetrievalQualityMetric = {
  total_retrievals: number;
  empty_retrievals: number;
  weak_retrievals: number;
  weak_retrieval_rate: number;
  average_result_count: number;
  average_top_score: number;
};

export type CitationCoverageMetric = {
  grounded_runs: number;
  runs_with_citations: number;
  citation_coverage_rate: number;
  invalid_citation_failures: number;
};

export type AuditLog = {
  id: string;
  project_id?: string | null;
  entity_type: string;
  entity_id?: string | null;
  event_type: string;
  actor_type: string;
  event_metadata: Record<string, unknown>;
  created_at: string;
};
