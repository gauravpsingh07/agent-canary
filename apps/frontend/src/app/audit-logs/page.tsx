"use client";

import { RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { JsonBlock } from "@/components/json-block";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { formatDate } from "@/lib/api";
import type { AuditLog } from "@/lib/types";

export default function AuditLogsPage() {
  const logs = useApi<AuditLog[]>("/audit-logs?limit=150");

  return (
    <>
      <PageHeader
        title="Audit Logs"
        eyebrow="Event Trail"
        action={
          <Button variant="secondary" onClick={() => logs.refresh()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        }
      />
      {logs.loading ? <LoadingState /> : null}
      {logs.error ? <ErrorState message={logs.error} /> : null}
      <Card>
        <CardHeader>
          <CardTitle>Events</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <thead>
                <tr>
                  <Th>Event</Th>
                  <Th>Entity</Th>
                  <Th>Actor</Th>
                  <Th>Metadata</Th>
                  <Th>Created</Th>
                </tr>
              </thead>
              <tbody>
                {(logs.data ?? []).map((log) => (
                  <tr key={log.id}>
                    <Td className="font-medium">{log.event_type}</Td>
                    <Td>
                      {log.entity_type}
                      {log.entity_id ? ` / ${log.entity_id.slice(0, 8)}` : ""}
                    </Td>
                    <Td>{log.actor_type}</Td>
                    <Td className="min-w-80">
                      <JsonBlock value={log.event_metadata} />
                    </Td>
                    <Td>{formatDate(log.created_at)}</Td>
                  </tr>
                ))}
                {(logs.data ?? []).length === 0 ? (
                  <tr>
                    <Td colSpan={5} className="text-muted-foreground">
                      No audit events found.
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
