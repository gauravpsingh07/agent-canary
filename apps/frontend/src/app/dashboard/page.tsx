"use client";

import Link from "next/link";
import {
  Activity,
  AlertTriangle,
  BookOpenCheck,
  CheckCircle2,
  Clock,
  Gauge,
  ShieldAlert
} from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import {
  FailureCategoryChart,
  PassFailChart,
  PolicyViolationChart,
  ScoreTrendChart
} from "@/components/charts";
import { MetricCard } from "@/components/metric-card";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { asPercent, formatDate } from "@/lib/api";
import type {
  CitationCoverageMetric,
  FailureByCategory,
  MetricsSummary,
  PolicyViolationMetric,
  RetrievalQualityMetric,
  TestRun
} from "@/lib/types";

export default function DashboardOverviewPage() {
  const summary = useApi<MetricsSummary>("/metrics/summary");
  const failures = useApi<FailureByCategory[]>("/metrics/failures-by-category");
  const violations = useApi<PolicyViolationMetric[]>("/metrics/policy-violations");
  const retrieval = useApi<RetrievalQualityMetric>("/metrics/retrieval-quality");
  const citations = useApi<CitationCoverageMetric>("/metrics/citation-coverage");
  const runs = useApi<TestRun[]>("/test-runs");

  const loading =
    summary.loading ||
    failures.loading ||
    violations.loading ||
    retrieval.loading ||
    citations.loading ||
    runs.loading;
  const error =
    summary.error ??
    failures.error ??
    violations.error ??
    retrieval.error ??
    citations.error ??
    runs.error;

  const recentRuns = (runs.data ?? []).slice(0, 8);
  const recentFailures = (runs.data ?? []).filter((run) => run.passed === false).slice(0, 5);
  const topViolations = (violations.data ?? []).slice(0, 5);

  const trend = recentRuns
    .slice()
    .reverse()
    .map((run, index) => ({
      label: run.created_at ? formatDate(run.created_at) : `Run ${index + 1}`,
      score: Number(run.overall_score ?? 0)
    }));

  return (
    <>
      <PageHeader title="Dashboard Overview" eyebrow="Agent Canary" />
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      {summary.data ? (
        <div className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
            <MetricCard label="Total Test Runs" value={summary.data.total_test_runs} icon={Activity} />
            <MetricCard
              label="Pass Rate"
              value={asPercent(summary.data.pass_rate)}
              icon={CheckCircle2}
              tone="green"
            />
            <MetricCard
              label="Average Score"
              value={summary.data.average_score.toFixed(1)}
              icon={Gauge}
              tone="blue"
            />
            <MetricCard
              label="Pending Approvals"
              value={summary.data.pending_approvals}
              icon={Clock}
              tone="amber"
            />
            <MetricCard
              label="Failed Evaluations"
              value={summary.data.failed_evaluations}
              icon={AlertTriangle}
              tone="red"
            />
            <MetricCard
              label="High-Risk Failures"
              value={summary.data.high_risk_failures}
              icon={ShieldAlert}
              tone="red"
            />
            <MetricCard
              label="Avg Retrieval Score"
              value={(retrieval.data?.average_top_score ?? 0).toFixed(2)}
              icon={BookOpenCheck}
              tone="default"
            />
            <MetricCard
              label="Citation Coverage"
              value={asPercent(citations.data?.citation_coverage_rate ?? 0)}
              icon={BookOpenCheck}
              tone="default"
            />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <PassFailChart passed={summary.data.passed_evaluations} failed={summary.data.failed_evaluations} />
            <ScoreTrendChart data={trend} />
            <FailureCategoryChart data={failures.data ?? []} />
            <PolicyViolationChart data={violations.data ?? []} />
          </div>

          <div className="grid gap-4 xl:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Recent Failures</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <thead>
                      <tr>
                        <Th>Run</Th>
                        <Th>Score</Th>
                        <Th>Reasons</Th>
                        <Th>When</Th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentFailures.map((run) => (
                        <tr key={run.id}>
                          <Td>
                            <Link className="font-medium text-primary" href={`/test-runs/${run.id}`}>
                              {run.id.slice(0, 8)}
                            </Link>
                          </Td>
                          <Td>{run.overall_score ?? "-"}</Td>
                          <Td className="max-w-[26rem] text-xs text-muted-foreground">
                            {run.failure_reasons.slice(0, 2).join("; ") || "—"}
                          </Td>
                          <Td>{formatDate(run.created_at)}</Td>
                        </tr>
                      ))}
                      {recentFailures.length === 0 ? (
                        <tr>
                          <Td colSpan={4} className="text-muted-foreground">
                            No failures yet.
                          </Td>
                        </tr>
                      ) : null}
                    </tbody>
                  </Table>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Recent Policy Violations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <Table>
                    <thead>
                      <tr>
                        <Th>Violation</Th>
                        <Th>Severity</Th>
                        <Th>Count</Th>
                      </tr>
                    </thead>
                    <tbody>
                      {topViolations.map((violation) => (
                        <tr key={violation.violation_code}>
                          <Td className="font-mono text-xs">{violation.violation_code}</Td>
                          <Td>
                            <StatusBadge value={violation.highest_severity} />
                          </Td>
                          <Td>{violation.count}</Td>
                        </tr>
                      ))}
                      {topViolations.length === 0 ? (
                        <tr>
                          <Td colSpan={3} className="text-muted-foreground">
                            No policy violations recorded.
                          </Td>
                        </tr>
                      ) : null}
                    </tbody>
                  </Table>
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Test Runs</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <thead>
                    <tr>
                      <Th>Status</Th>
                      <Th>Score</Th>
                      <Th>Provider</Th>
                      <Th>Created</Th>
                      <Th>Run</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentRuns.map((run) => (
                      <tr key={run.id}>
                        <Td>
                          <StatusBadge value={run.passed ?? run.status} />
                        </Td>
                        <Td>{run.overall_score ?? "-"}</Td>
                        <Td>{run.provider_name ?? "mock"}</Td>
                        <Td>{formatDate(run.created_at)}</Td>
                        <Td>
                          <Link className="font-medium text-primary" href={`/test-runs/${run.id}`}>
                            {run.id.slice(0, 8)}
                          </Link>
                        </Td>
                      </tr>
                    ))}
                    {recentRuns.length === 0 ? (
                      <tr>
                        <Td colSpan={5} className="text-muted-foreground">
                          No runs recorded yet.
                        </Td>
                      </tr>
                    ) : null}
                  </tbody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      ) : null}
    </>
  );
}
