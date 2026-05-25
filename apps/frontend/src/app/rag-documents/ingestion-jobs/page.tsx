"use client";

import { RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { JsonBlock } from "@/components/json-block";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { formatDate } from "@/lib/api";
import type { DocumentIngestionJob } from "@/lib/types";

export default function RagIngestionJobsPage() {
  const jobs = useApi<DocumentIngestionJob[]>("/rag/ingestion-jobs");

  return (
    <>
      <PageHeader
        title="Ingestion Jobs"
        eyebrow="RAG Pipeline"
        action={
          <Button variant="secondary" onClick={() => jobs.refresh()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        }
      />
      {jobs.loading ? <LoadingState /> : null}
      {jobs.error ? <ErrorState message={jobs.error} /> : null}
      <Card>
        <CardHeader>
          <CardTitle>Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <thead>
                <tr>
                  <Th>Status</Th>
                  <Th>Document</Th>
                  <Th>Chunks</Th>
                  <Th>Started</Th>
                  <Th>Completed</Th>
                  <Th>Error</Th>
                  <Th>Metadata</Th>
                </tr>
              </thead>
              <tbody>
                {(jobs.data ?? []).map((job) => (
                  <tr key={job.id}>
                    <Td>
                      <StatusBadge value={job.status} />
                    </Td>
                    <Td className="font-mono text-xs">
                      {job.document_id ? job.document_id.slice(0, 8) : "—"}
                    </Td>
                    <Td>{job.chunks_created}</Td>
                    <Td>{formatDate(job.started_at ?? null)}</Td>
                    <Td>{formatDate(job.completed_at ?? null)}</Td>
                    <Td className="max-w-[18rem] text-xs text-muted-foreground">
                      {job.error_message ?? "—"}
                    </Td>
                    <Td className="min-w-72">
                      <JsonBlock value={job.job_metadata} />
                    </Td>
                  </tr>
                ))}
                {(jobs.data ?? []).length === 0 ? (
                  <tr>
                    <Td colSpan={7} className="text-muted-foreground">
                      No ingestion jobs yet.
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
