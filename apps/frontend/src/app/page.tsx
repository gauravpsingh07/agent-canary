"use client";

import Link from "next/link";
import { Activity, AlertTriangle, CheckCircle2, Clock, Gauge, ShieldAlert } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { FailureCategoryChart, PassFailChart, PolicyViolationChart, ScoreTrendChart } from "@/components/charts";
import { MetricCard } from "@/components/metric-card";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { asPercent, formatDate } from "@/lib/api";
import type { FailureByCategory, MetricsSummary, PolicyViolationMetric, TestRun } from "@/lib/types";

export default function OverviewPage() {
  const summary = useApi<MetricsSummary>("/metrics/summary");
  const failures = useApi<FailureByCategory[]>("/metrics/failures-by-category");
  const violations = useApi<PolicyViolationMetric[]>("/metrics/policy-violations");
  const runs = useApi<TestRun[]>("/test-runs");
  const loading = summary.loading || failures.loading || violations.loading || runs.loading;
  const error = summary.error ?? failures.error ?? violations.error ?? runs.error;
  const recentRuns = (runs.data ?? []).slice(0, 8);
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
            <MetricCard label="Pass Rate" value={asPercent(summary.data.pass_rate)} icon={CheckCircle2} tone="green" />
            <MetricCard label="Average Score" value={summary.data.average_score.toFixed(1)} icon={Gauge} tone="blue" />
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
              label="Policy Violations"
              value={summary.data.policy_violation_count}
              icon={ShieldAlert}
              tone="amber"
            />
            <MetricCard label="Failure Rate" value={asPercent(summary.data.failure_rate)} icon={AlertTriangle} tone="red" />
          </div>
          <div className="grid gap-4 xl:grid-cols-2">
            <PassFailChart passed={summary.data.passed_evaluations} failed={summary.data.failed_evaluations} />
            <ScoreTrendChart data={trend} />
            <FailureCategoryChart data={failures.data ?? []} />
            <PolicyViolationChart data={violations.data ?? []} />
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
