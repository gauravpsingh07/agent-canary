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
import type { PolicyRule } from "@/lib/types";

export default function PolicyRulesPage() {
  const rules = useApi<PolicyRule[]>("/policy-rules");

  async function seedRules() {
    await apiFetch("/policy-rules/seed-defaults", { method: "POST" });
    await rules.refresh();
  }

  return (
    <>
      <PageHeader
        title="Policy Rules"
        eyebrow="Safety Controls"
        action={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => rules.refresh()}>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button onClick={seedRules}>
              <DatabaseZap className="h-4 w-4" />
              Seed Defaults
            </Button>
          </div>
        }
      />
      {rules.loading ? <LoadingState /> : null}
      {rules.error ? <ErrorState message={rules.error} /> : null}
      <Card>
        <CardHeader>
          <CardTitle>Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <thead>
                <tr>
                  <Th>Name</Th>
                  <Th>Tool</Th>
                  <Th>Violation</Th>
                  <Th>Effect</Th>
                  <Th>Enabled</Th>
                </tr>
              </thead>
              <tbody>
                {(rules.data ?? []).map((rule) => (
                  <tr key={rule.id}>
                    <Td className="font-medium">{rule.name}</Td>
                    <Td>{rule.tool_name ?? "global"}</Td>
                    <Td>{rule.violation_code}</Td>
                    <Td>
                      <StatusBadge value={rule.effect} />
                    </Td>
                    <Td>{rule.is_enabled ? "Yes" : "No"}</Td>
                  </tr>
                ))}
                {(rules.data ?? []).length === 0 ? (
                  <tr>
                    <Td colSpan={5} className="text-muted-foreground">
                      No policy rules found.
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
