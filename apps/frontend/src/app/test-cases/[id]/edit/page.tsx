"use client";

import { FormEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { Play, Save } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { useApi } from "@/components/use-api";
import { apiFetch } from "@/lib/api";
import type { TestCase } from "@/lib/types";

export default function TestCaseEditPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const testCase = useApi<TestCase>(`/test-cases/${params.id}`);

  const [form, setForm] = useState<Partial<TestCase>>({});
  const [saving, setSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (testCase.data) {
      setForm(testCase.data);
    }
  }, [testCase.data]);

  function update<K extends keyof TestCase>(key: K, value: TestCase[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setErrorMessage(null);
    try {
      await apiFetch(`/test-cases/${params.id}`, {
        method: "PUT",
        body: JSON.stringify({
          name: form.name,
          description: form.description ?? null,
          category: form.category,
          input_prompt: form.input_prompt,
          system_prompt: form.system_prompt ?? null,
          expected_behavior: form.expected_behavior,
          expected_tool_name: form.expected_tool_name ?? null,
          should_call_tool: form.should_call_tool ?? false,
          should_require_approval: form.should_require_approval ?? false,
          expected_refusal: form.expected_refusal ?? false,
          expected_schema_valid: form.expected_schema_valid ?? true,
          requires_retrieval: form.requires_retrieval ?? false,
          expected_citations: form.expected_citations ?? false,
          min_retrieval_score: form.min_retrieval_score ?? null,
          tags: form.tags ?? [],
          severity: form.severity
        })
      });
      await testCase.refresh();
    } catch (err) {
      setErrorMessage(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function runNow() {
    const run = await apiFetch<{ id: string }>(`/test-cases/${params.id}/run`, { method: "POST" });
    router.push(`/test-runs/${run.id}`);
  }

  return (
    <>
      <PageHeader
        title="Edit Test Case"
        eyebrow={params.id.slice(0, 8)}
        action={
          <Button variant="secondary" onClick={runNow}>
            <Play className="h-4 w-4" />
            Run Now
          </Button>
        }
      />
      {testCase.loading ? <LoadingState /> : null}
      {testCase.error ? <ErrorState message={testCase.error} /> : null}
      {errorMessage ? <ErrorState message={errorMessage} /> : null}
      {testCase.data ? (
        <form onSubmit={save} className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Identity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-xs font-medium text-muted-foreground">Name</label>
                <Input value={form.name ?? ""} onChange={(e) => update("name", e.target.value)} />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Description</label>
                <Textarea
                  value={form.description ?? ""}
                  onChange={(e) => update("description", e.target.value)}
                />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <div>
                  <label className="text-xs font-medium text-muted-foreground">Category</label>
                  <Input
                    value={form.category ?? ""}
                    onChange={(e) => update("category", e.target.value)}
                  />
                </div>
                <div>
                  <label className="text-xs font-medium text-muted-foreground">Severity</label>
                  <Input
                    value={form.severity ?? ""}
                    onChange={(e) => update("severity", e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Prompt</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-xs font-medium text-muted-foreground">System Prompt</label>
                <Textarea
                  value={form.system_prompt ?? ""}
                  onChange={(e) => update("system_prompt", e.target.value)}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Input Prompt</label>
                <Textarea
                  className="min-h-32"
                  value={form.input_prompt ?? ""}
                  onChange={(e) => update("input_prompt", e.target.value)}
                />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">Expected Behavior</label>
                <Textarea
                  value={form.expected_behavior ?? ""}
                  onChange={(e) => update("expected_behavior", e.target.value)}
                />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Expectations</CardTitle>
            </CardHeader>
            <CardContent className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-xs font-medium text-muted-foreground">Expected Tool Name</label>
                <Input
                  value={form.expected_tool_name ?? ""}
                  onChange={(e) =>
                    update("expected_tool_name", e.target.value ? e.target.value : null)
                  }
                />
              </div>
              <div>
                <label className="text-xs font-medium text-muted-foreground">
                  Min Retrieval Score (0–1)
                </label>
                <Input
                  type="number"
                  step="0.05"
                  min={0}
                  max={1}
                  value={form.min_retrieval_score ?? ""}
                  onChange={(e) =>
                    update(
                      "min_retrieval_score",
                      e.target.value === "" ? null : Number(e.target.value)
                    )
                  }
                />
              </div>
              <BooleanField
                label="Should call tool"
                value={form.should_call_tool ?? false}
                onChange={(v) => update("should_call_tool", v)}
              />
              <BooleanField
                label="Should require approval"
                value={form.should_require_approval ?? false}
                onChange={(v) => update("should_require_approval", v)}
              />
              <BooleanField
                label="Expected refusal"
                value={form.expected_refusal ?? false}
                onChange={(v) => update("expected_refusal", v)}
              />
              <BooleanField
                label="Expected schema valid"
                value={form.expected_schema_valid ?? true}
                onChange={(v) => update("expected_schema_valid", v)}
              />
              <BooleanField
                label="Requires retrieval"
                value={form.requires_retrieval ?? false}
                onChange={(v) => update("requires_retrieval", v)}
              />
              <BooleanField
                label="Expected citations"
                value={form.expected_citations ?? false}
                onChange={(v) => update("expected_citations", v)}
              />
              <div className="md:col-span-2">
                <label className="text-xs font-medium text-muted-foreground">
                  Tags (comma-separated)
                </label>
                <Input
                  value={(form.tags ?? []).join(", ")}
                  onChange={(e) =>
                    update(
                      "tags",
                      e.target.value
                        .split(",")
                        .map((tag) => tag.trim())
                        .filter(Boolean)
                    )
                  }
                />
              </div>
            </CardContent>
          </Card>
          <div className="flex justify-end">
            <Button type="submit" disabled={saving}>
              <Save className="h-4 w-4" />
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </form>
      ) : null}
    </>
  );
}

function BooleanField({
  label,
  value,
  onChange
}: {
  label: string;
  value: boolean;
  onChange: (v: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-2 rounded-md border border-border bg-card px-3 py-2 text-sm">
      <input
        type="checkbox"
        checked={value}
        onChange={(e) => onChange(e.target.checked)}
        className="h-4 w-4"
      />
      <span>{label}</span>
    </label>
  );
}
