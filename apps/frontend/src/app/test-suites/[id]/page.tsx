"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { Play, RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { apiFetch, formatDate } from "@/lib/api";
import type { TestCase, TestSuite } from "@/lib/types";

export default function TestSuiteDetailPage() {
  const params = useParams<{ id: string }>();
  const suite = useApi<TestSuite>(`/test-suites/${params.id}`);
  const cases = useApi<TestCase[]>(`/test-suites/${params.id}/test-cases`);

  async function runSuite(asyncMode = false) {
    const path = asyncMode
      ? `/test-suites/${params.id}/run?async_mode=true`
      : `/test-suites/${params.id}/run`;
    await apiFetch(path, { method: "POST" });
  }

  async function runCase(caseId: string) {
    const run = await apiFetch<{ id: string }>(`/test-cases/${caseId}/run`, { method: "POST" });
    window.location.href = `/test-runs/${run.id}`;
  }

  return (
    <>
      <PageHeader
        title={suite.data?.name ?? "Test Suite"}
        eyebrow={suite.data?.category ?? ""}
        action={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => cases.refresh()}>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button variant="secondary" onClick={() => runSuite(true)}>
              <Play className="h-4 w-4" />
              Run Suite (Background)
            </Button>
            <Button onClick={() => runSuite(false)}>
              <Play className="h-4 w-4" />
              Run Suite
            </Button>
          </div>
        }
      />
      {suite.loading || cases.loading ? <LoadingState /> : null}
      {suite.error || cases.error ? <ErrorState message={suite.error ?? cases.error ?? ""} /> : null}
      {suite.data ? (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>About</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">{suite.data.description ?? "—"}</p>
              <div className="mt-3 grid gap-2 text-sm md:grid-cols-3">
                <div>
                  <span className="text-muted-foreground">Suite ID:</span>{" "}
                  <span className="font-mono text-xs">{suite.data.id}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Category:</span>{" "}
                  <span className="font-medium">{suite.data.category}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Created:</span>{" "}
                  {formatDate(suite.data.created_at)}
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Test Cases</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <thead>
                    <tr>
                      <Th>Name</Th>
                      <Th>Category</Th>
                      <Th>Severity</Th>
                      <Th>Expected Tool</Th>
                      <Th>Tags</Th>
                      <Th>Actions</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {(cases.data ?? []).map((testCase) => (
                      <tr key={testCase.id}>
                        <Td className="font-medium">
                          <Link href={`/test-cases/${testCase.id}/edit`} className="text-primary">
                            {testCase.name}
                          </Link>
                        </Td>
                        <Td>{testCase.category}</Td>
                        <Td>
                          <StatusBadge value={testCase.severity} />
                        </Td>
                        <Td>{testCase.expected_tool_name ?? "—"}</Td>
                        <Td className="text-xs text-muted-foreground">{testCase.tags.join(", ")}</Td>
                        <Td>
                          <div className="flex gap-2">
                            <Button size="sm" variant="secondary" onClick={() => runCase(testCase.id)}>
                              <Play className="h-4 w-4" />
                              Run
                            </Button>
                            <Link
                              href={`/test-cases/${testCase.id}/edit`}
                              className="inline-flex h-8 items-center justify-center rounded-md border border-border bg-card px-2 text-xs font-medium hover:bg-muted"
                            >
                              Edit
                            </Link>
                          </div>
                        </Td>
                      </tr>
                    ))}
                    {(cases.data ?? []).length === 0 ? (
                      <tr>
                        <Td colSpan={6} className="text-muted-foreground">
                          No test cases in this suite.
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
