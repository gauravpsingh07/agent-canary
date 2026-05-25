import type { ApprovalRequest, RetrievalResult, TestRun } from "@/lib/types";

function bucketKey(value?: string | null): string {
  if (!value) return "unknown";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "unknown";
  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric"
  }).format(date);
}

export function bucketPassFail(runs: TestRun[]): Array<{
  bucket: string;
  passed: number;
  failed: number;
}> {
  const buckets = new Map<string, { passed: number; failed: number }>();
  for (const run of runs) {
    const key = bucketKey(run.created_at);
    const existing = buckets.get(key) ?? { passed: 0, failed: 0 };
    if (run.passed === true) existing.passed += 1;
    else if (run.passed === false) existing.failed += 1;
    buckets.set(key, existing);
  }
  return Array.from(buckets.entries()).map(([bucket, value]) => ({ bucket, ...value }));
}

export function bucketAverageScore(runs: TestRun[]): Array<{
  bucket: string;
  avg_score: number;
}> {
  const buckets = new Map<string, { total: number; count: number }>();
  for (const run of runs) {
    if (run.overall_score == null) continue;
    const key = bucketKey(run.created_at);
    const existing = buckets.get(key) ?? { total: 0, count: 0 };
    existing.total += Number(run.overall_score);
    existing.count += 1;
    buckets.set(key, existing);
  }
  return Array.from(buckets.entries()).map(([bucket, value]) => ({
    bucket,
    avg_score: value.count > 0 ? Math.round(value.total / value.count) : 0
  }));
}

export function approvalOutcomeCounts(requests: ApprovalRequest[]): {
  pending: number;
  approved: number;
  rejected: number;
} {
  const counts = { pending: 0, approved: 0, rejected: 0 };
  for (const request of requests) {
    if (request.status === "approved") counts.approved += 1;
    else if (request.status === "rejected") counts.rejected += 1;
    else counts.pending += 1;
  }
  return counts;
}

export function bucketRetrievalQuality(
  results: RetrievalResult[]
): Array<{ bucket: string; avg_top_score: number; weak_rate: number }> {
  const buckets = new Map<string, { topScores: number[]; weak: number; total: number }>();
  for (const result of results) {
    const key = bucketKey(result.created_at);
    const existing = buckets.get(key) ?? { topScores: [], weak: 0, total: 0 };
    const topScore =
      result.results.length > 0
        ? result.results.reduce((acc, item) => Math.max(acc, item.score ?? 0), 0)
        : 0;
    existing.topScores.push(topScore);
    if (topScore < 0.35) existing.weak += 1;
    existing.total += 1;
    buckets.set(key, existing);
  }
  return Array.from(buckets.entries()).map(([bucket, value]) => {
    const avg =
      value.topScores.length > 0
        ? value.topScores.reduce((acc, item) => acc + item, 0) / value.topScores.length
        : 0;
    const weakRate = value.total > 0 ? value.weak / value.total : 0;
    return { bucket, avg_top_score: Number(avg.toFixed(3)), weak_rate: Number(weakRate.toFixed(3)) };
  });
}

export function bucketCitationCoverage(runs: TestRun[]): Array<{
  bucket: string;
  coverage_rate: number;
}> {
  const buckets = new Map<string, { withCitations: number; total: number }>();
  for (const run of runs) {
    const validated = (run.run_metadata?.["validated_output"] ?? null) as
      | { citations?: unknown }
      | null;
    if (!validated || typeof validated !== "object") continue;
    const citations = Array.isArray(validated.citations) ? validated.citations.length : 0;
    const key = bucketKey(run.created_at);
    const existing = buckets.get(key) ?? { withCitations: 0, total: 0 };
    existing.total += 1;
    if (citations > 0) existing.withCitations += 1;
    buckets.set(key, existing);
  }
  return Array.from(buckets.entries()).map(([bucket, value]) => ({
    bucket,
    coverage_rate: value.total > 0 ? Math.round((value.withCitations / value.total) * 100) : 0
  }));
}
