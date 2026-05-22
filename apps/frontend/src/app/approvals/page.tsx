"use client";

import { Check, RefreshCw, X } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { JsonBlock } from "@/components/json-block";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { apiFetch, formatDate } from "@/lib/api";
import type { ApprovalRequest } from "@/lib/types";

export default function ApprovalsPage() {
  const approvals = useApi<ApprovalRequest[]>("/approval-requests");

  async function decide(id: string, action: "approve" | "reject") {
    await apiFetch(`/approval-requests/${id}/${action}`, {
      method: "POST",
      body: JSON.stringify({ reviewer_note: `Reviewed from Agent Canary dashboard: ${action}` })
    });
    await approvals.refresh();
  }

  return (
    <>
      <PageHeader
        title="Approval Queue"
        eyebrow="Human Review"
        action={
          <Button variant="secondary" onClick={() => approvals.refresh()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        }
      />
      {approvals.loading ? <LoadingState /> : null}
      {approvals.error ? <ErrorState message={approvals.error} /> : null}
      <Card>
        <CardHeader>
          <CardTitle>Requests</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <thead>
                <tr>
                  <Th>Status</Th>
                  <Th>Risk</Th>
                  <Th>Reason</Th>
                  <Th>Tool Call</Th>
                  <Th>Created</Th>
                  <Th>Decision</Th>
                </tr>
              </thead>
              <tbody>
                {(approvals.data ?? []).map((request) => (
                  <tr key={request.id}>
                    <Td>
                      <StatusBadge value={request.status} />
                    </Td>
                    <Td>
                      <StatusBadge value={request.risk_level} />
                    </Td>
                    <Td>{request.reason}</Td>
                    <Td className="min-w-72">
                      <JsonBlock value={request.proposed_tool_call} />
                    </Td>
                    <Td>{formatDate(request.created_at)}</Td>
                    <Td>
                      <div className="flex gap-2">
                        <Button
                          size="icon"
                          variant="secondary"
                          aria-label="Approve request"
                          disabled={request.status !== "pending"}
                          onClick={() => decide(request.id, "approve")}
                        >
                          <Check className="h-4 w-4" />
                        </Button>
                        <Button
                          size="icon"
                          variant="danger"
                          aria-label="Reject request"
                          disabled={request.status !== "pending"}
                          onClick={() => decide(request.id, "reject")}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    </Td>
                  </tr>
                ))}
                {(approvals.data ?? []).length === 0 ? (
                  <tr>
                    <Td colSpan={6} className="text-muted-foreground">
                      No approval requests found.
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
