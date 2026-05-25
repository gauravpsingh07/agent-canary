import { describe, expect, it } from "vitest";
import {
  approvalOutcomeCounts,
  bucketAverageScore,
  bucketCitationCoverage,
  bucketPassFail,
  bucketRetrievalQuality
} from "@/lib/timeseries";
import type { ApprovalRequest, RetrievalResult, TestRun } from "@/lib/types";

function run(partial: Partial<TestRun>): TestRun {
  return {
    id: "run_" + Math.random().toString(36).slice(2, 8),
    test_case_id: "tc",
    status: "completed",
    failure_reasons: [],
    run_metadata: {},
    created_at: "2026-05-01T10:00:00Z",
    ...partial
  };
}

describe("timeseries helpers", () => {
  it("buckets pass/fail counts by day", () => {
    const data = bucketPassFail([
      run({ passed: true, created_at: "2026-05-01T10:00:00Z" }),
      run({ passed: false, created_at: "2026-05-01T15:00:00Z" }),
      run({ passed: true, created_at: "2026-05-02T10:00:00Z" })
    ]);
    expect(data).toHaveLength(2);
    expect(data.reduce((acc, item) => acc + item.passed + item.failed, 0)).toBe(3);
  });

  it("computes average score per bucket", () => {
    const data = bucketAverageScore([
      run({ overall_score: 80, created_at: "2026-05-01T10:00:00Z" }),
      run({ overall_score: 100, created_at: "2026-05-01T11:00:00Z" })
    ]);
    expect(data).toHaveLength(1);
    expect(data[0].avg_score).toBe(90);
  });

  it("counts approval outcomes", () => {
    const requests: ApprovalRequest[] = [
      {
        id: "a",
        test_run_id: "r",
        risk_level: "high",
        reason: "",
        status: "pending",
        proposed_tool_call: {},
        created_at: ""
      },
      {
        id: "b",
        test_run_id: "r",
        risk_level: "high",
        reason: "",
        status: "approved",
        proposed_tool_call: {},
        created_at: ""
      },
      {
        id: "c",
        test_run_id: "r",
        risk_level: "high",
        reason: "",
        status: "rejected",
        proposed_tool_call: {},
        created_at: ""
      }
    ];
    expect(approvalOutcomeCounts(requests)).toEqual({ pending: 1, approved: 1, rejected: 1 });
  });

  it("computes retrieval quality buckets", () => {
    const retrievals: RetrievalResult[] = [
      {
        id: "r1",
        query: "x",
        result_count: 1,
        provider_name: "mock",
        model_name: "mock",
        results: [{ chunk_id: "c", document_id: "d", document_title: "t", content: "", score: 0.8 }],
        created_at: "2026-05-01T10:00:00Z"
      },
      {
        id: "r2",
        query: "x",
        result_count: 1,
        provider_name: "mock",
        model_name: "mock",
        results: [{ chunk_id: "c", document_id: "d", document_title: "t", content: "", score: 0.1 }],
        created_at: "2026-05-01T11:00:00Z"
      }
    ];
    const buckets = bucketRetrievalQuality(retrievals);
    expect(buckets).toHaveLength(1);
    expect(buckets[0].avg_top_score).toBeCloseTo(0.45, 2);
    expect(buckets[0].weak_rate).toBeCloseTo(0.5, 2);
  });

  it("computes citation coverage from run metadata", () => {
    const runs: TestRun[] = [
      run({
        run_metadata: { validated_output: { citations: [{ chunk_id: "c1" }] } },
        created_at: "2026-05-01T10:00:00Z"
      }),
      run({
        run_metadata: { validated_output: { citations: [] } },
        created_at: "2026-05-01T12:00:00Z"
      })
    ];
    const data = bucketCitationCoverage(runs);
    expect(data).toHaveLength(1);
    expect(data[0].coverage_rate).toBe(50);
  });
});
