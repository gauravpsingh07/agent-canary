"use client";

import { useParams } from "next/navigation";
import { ErrorState, LoadingState } from "@/components/data-state";
import { JsonBlock } from "@/components/json-block";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { formatDate } from "@/lib/api";
import type { TestRun, TestRunStep } from "@/lib/types";

export default function TestRunDetailPage() {
  const params = useParams<{ id: string }>();
  const run = useApi<TestRun>(`/test-runs/${params.id}`);
  const steps = useApi<TestRunStep[]>(`/test-runs/${params.id}/steps`);

  return (
    <>
      <PageHeader title="Test Run Detail" eyebrow={params.id.slice(0, 8)} />
      {run.loading || steps.loading ? <LoadingState /> : null}
      {run.error || steps.error ? <ErrorState message={run.error ?? steps.error ?? ""} /> : null}
      {run.data ? (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardContent>
                <div className="text-sm text-muted-foreground">Status</div>
                <div className="mt-2">
                  <StatusBadge value={run.data.passed ?? run.data.status} />
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <div className="text-sm text-muted-foreground">Overall Score</div>
                <div className="mt-2 text-2xl font-semibold">{run.data.overall_score ?? "-"}</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <div className="text-sm text-muted-foreground">Provider</div>
                <div className="mt-2 font-medium">{run.data.provider_name ?? "mock"}</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent>
                <div className="text-sm text-muted-foreground">Created</div>
                <div className="mt-2 font-medium">{formatDate(run.data.created_at)}</div>
              </CardContent>
            </Card>
          </div>
          <Card>
            <CardHeader>
              <CardTitle>Workflow Steps</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <thead>
                    <tr>
                      <Th>#</Th>
                      <Th>Step</Th>
                      <Th>Status</Th>
                      <Th>Error</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {(steps.data ?? []).map((step) => (
                      <tr key={step.id}>
                        <Td>{step.step_order}</Td>
                        <Td className="font-medium">{step.step_name}</Td>
                        <Td>
                          <StatusBadge value={step.status} />
                        </Td>
                        <Td>{step.error_message ?? "-"}</Td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </CardContent>
          </Card>
          <div className="grid gap-4 xl:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Failure Reasons</CardTitle>
              </CardHeader>
              <CardContent>
                {run.data.failure_reasons.length > 0 ? (
                  <ul className="space-y-2 text-sm">
                    {run.data.failure_reasons.map((reason) => (
                      <li key={reason} className="rounded-md border border-border bg-muted p-3">
                        {reason}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-sm text-muted-foreground">No failure reasons stored.</div>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Run Metadata</CardTitle>
              </CardHeader>
              <CardContent>
                <JsonBlock value={run.data.run_metadata} />
              </CardContent>
            </Card>
          </div>
        </div>
      ) : null}
    </>
  );
}
