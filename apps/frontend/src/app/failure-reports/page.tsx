"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { Download, RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { FailureCategoryChart, PolicyViolationChart } from "@/components/charts";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { formatDate } from "@/lib/api";
import type { FailureByCategory, PolicyViolationMetric, TestRun } from "@/lib/types";

export default function FailureReportsPage() {
  const runs = useApi<TestRun[]>("/test-runs");
  const failures = useApi<FailureByCategory[]>("/metrics/failures-by-category");
  const violations = useApi<PolicyViolationMetric[]>("/metrics/policy-violations");
  const [filter, setFilter] = useState<string>("all");

  const failed = useMemo(
    () => (runs.data ?? []).filter((run) => run.passed === false),
    [runs.data]
  );

  const categories = useMemo(() => {
    const set = new Set<string>();
    for (const failure of failures.data ?? []) {
      set.add(failure.category);
    }
    return ["all", ...Array.from(set).sort()];
  }, [failures.data]);

  const filtered = useMemo(() => {
    if (filter === "all") return failed;
    return failed.filter(
      (run) => (run.failure_reasons ?? []).some((reason) => reason.toLowerCase().includes(filter))
    );
  }, [failed, filter]);

  function refreshAll() {
    void runs.refresh();
    void failures.refresh();
    void violations.refresh();
  }

  function exportCsv() {
    const header = ["run_id", "score", "provider", "created_at", "failure_reasons"].join(",");
    const lines = filtered.map((run) =>
      [
        run.id,
        String(run.overall_score ?? ""),
        run.provider_name ?? "",
        run.created_at ?? "",
        '"' + (run.failure_reasons ?? []).join(" | ").replace(/"/g, '""') + '"'
      ].join(",")
    );
    const blob = new Blob([[header, ...lines].join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `agent-canary-failures-${Date.now()}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <>
      <PageHeader
        title="Failure Reports"
        eyebrow="Triage"
        action={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={refreshAll}>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button variant="secondary" onClick={exportCsv}>
              <Download className="h-4 w-4" />
              Export CSV
            </Button>
          </div>
        }
      />
      {runs.loading || failures.loading || violations.loading ? <LoadingState /> : null}
      {runs.error || failures.error || violations.error ? (
        <ErrorState message={runs.error ?? failures.error ?? violations.error ?? ""} />
      ) : null}
      <div className="space-y-4">
        <div className="grid gap-4 xl:grid-cols-2">
          <FailureCategoryChart data={failures.data ?? []} />
          <PolicyViolationChart data={violations.data ?? []} />
        </div>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>Failed Runs ({filtered.length})</span>
              <select
                className="h-8 rounded-md border border-border bg-card px-2 text-xs"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
              >
                {categories.map((category) => (
                  <option key={category} value={category}>
                    {category}
                  </option>
                ))}
              </select>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <thead>
                  <tr>
                    <Th>Run</Th>
                    <Th>Status</Th>
                    <Th>Score</Th>
                    <Th>Provider</Th>
                    <Th>Failure Reasons</Th>
                    <Th>Created</Th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((run) => (
                    <tr key={run.id}>
                      <Td>
                        <Link className="font-medium text-primary" href={`/test-runs/${run.id}`}>
                          {run.id.slice(0, 8)}
                        </Link>
                      </Td>
                      <Td>
                        <StatusBadge value={run.passed ?? run.status} />
                      </Td>
                      <Td>{run.overall_score ?? "-"}</Td>
                      <Td>{run.provider_name ?? "mock"}</Td>
                      <Td className="max-w-[28rem] text-xs">
                        <ul className="space-y-1">
                          {(run.failure_reasons ?? []).slice(0, 4).map((reason) => (
                            <li key={reason} className="text-muted-foreground">
                              {reason}
                            </li>
                          ))}
                          {(run.failure_reasons ?? []).length > 4 ? (
                            <li className="text-muted-foreground">
                              +{(run.failure_reasons ?? []).length - 4} more
                            </li>
                          ) : null}
                        </ul>
                      </Td>
                      <Td>{formatDate(run.created_at)}</Td>
                    </tr>
                  ))}
                  {filtered.length === 0 ? (
                    <tr>
                      <Td colSpan={6} className="text-muted-foreground">
                        No failed runs match this filter.
                      </Td>
                    </tr>
                  ) : null}
                </tbody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
