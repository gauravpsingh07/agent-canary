"use client";

import Link from "next/link";
import { RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { formatDate } from "@/lib/api";
import type { TestRun } from "@/lib/types";

export default function TestRunsPage() {
  const runs = useApi<TestRun[]>("/test-runs");

  return (
    <>
      <PageHeader
        title="Test Runs"
        eyebrow="Execution History"
        action={
          <Button variant="secondary" onClick={() => runs.refresh()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        }
      />
      {runs.loading ? <LoadingState /> : null}
      {runs.error ? <ErrorState message={runs.error} /> : null}
      <Card>
        <CardHeader>
          <CardTitle>Runs</CardTitle>
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
                  <Th>Created</Th>
                </tr>
              </thead>
              <tbody>
                {(runs.data ?? []).map((run) => (
                  <tr key={run.id}>
                    <Td>
                      <Link href={`/test-runs/${run.id}`} className="font-medium text-primary">
                        {run.id.slice(0, 8)}
                      </Link>
                    </Td>
                    <Td>
                      <StatusBadge value={run.passed ?? run.status} />
                    </Td>
                    <Td>{run.overall_score ?? "-"}</Td>
                    <Td>{run.provider_name ?? "mock"}</Td>
                    <Td>{formatDate(run.created_at)}</Td>
                  </tr>
                ))}
                {(runs.data ?? []).length === 0 ? (
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
    </>
  );
}
