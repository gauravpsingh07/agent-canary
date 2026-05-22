"use client";

import { DatabaseZap, RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { apiFetch } from "@/lib/api";
import type { ToolDefinition } from "@/lib/types";

export default function ToolsPage() {
  const tools = useApi<ToolDefinition[]>("/tools");

  async function seedTools() {
    await apiFetch("/tools/seed-defaults", { method: "POST" });
    await tools.refresh();
  }

  return (
    <>
      <PageHeader
        title="Tool Registry"
        eyebrow="Simulated Actions"
        action={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => tools.refresh()}>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button onClick={seedTools}>
              <DatabaseZap className="h-4 w-4" />
              Seed Defaults
            </Button>
          </div>
        }
      />
      {tools.loading ? <LoadingState /> : null}
      {tools.error ? <ErrorState message={tools.error} /> : null}
      <Card>
        <CardHeader>
          <CardTitle>Registered Tools</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <thead>
                <tr>
                  <Th>Name</Th>
                  <Th>Risk</Th>
                  <Th>Approval</Th>
                  <Th>Status</Th>
                  <Th>Description</Th>
                </tr>
              </thead>
              <tbody>
                {(tools.data ?? []).map((tool) => (
                  <tr key={tool.id}>
                    <Td className="font-medium">{tool.name}</Td>
                    <Td>
                      <StatusBadge value={tool.risk_level} />
                    </Td>
                    <Td>{tool.requires_approval ? "Required" : "Automatic"}</Td>
                    <Td>{tool.is_active ? "Active" : "Disabled"}</Td>
                    <Td>{tool.description}</Td>
                  </tr>
                ))}
                {(tools.data ?? []).length === 0 ? (
                  <tr>
                    <Td colSpan={5} className="text-muted-foreground">
                      No tools found.
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
