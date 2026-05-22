"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { DatabaseZap, Play, Plus, RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { apiFetch } from "@/lib/api";
import type { Project, TestCase, TestSuite } from "@/lib/types";

export default function TestSuitesPage() {
  const projects = useApi<Project[]>("/projects");
  const [projectId, setProjectId] = useState("");
  const [suites, setSuites] = useState<TestSuite[]>([]);
  const [cases, setCases] = useState<TestCase[]>([]);
  const [suiteId, setSuiteId] = useState("");
  const [loadingSuites, setLoadingSuites] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("prompt_injection");
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (!projectId && projects.data?.[0]) {
      setProjectId(projects.data[0].id);
    }
  }, [projectId, projects.data]);

  useEffect(() => {
    if (!projectId) return;
    void loadSuites(projectId);
  }, [projectId]);

  useEffect(() => {
    if (!suiteId) {
      setCases([]);
      return;
    }
    void apiFetch<TestCase[]>(`/test-suites/${suiteId}/test-cases`)
      .then(setCases)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load test cases"));
  }, [suiteId]);

  const selectedProject = useMemo(
    () => (projects.data ?? []).find((project) => project.id === projectId),
    [projectId, projects.data]
  );

  async function loadSuites(nextProjectId = projectId) {
    if (!nextProjectId) return;
    setLoadingSuites(true);
    setError(null);
    try {
      const data = await apiFetch<TestSuite[]>(`/projects/${nextProjectId}/test-suites`);
      setSuites(data);
      setSuiteId(data[0]?.id ?? "");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load suites");
    } finally {
      setLoadingSuites(false);
    }
  }

  async function createSuite(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!projectId) return;
    await apiFetch<TestSuite>(`/projects/${projectId}/test-suites`, {
      method: "POST",
      body: JSON.stringify({ name, category, description: description || null })
    });
    setName("");
    setDescription("");
    await loadSuites();
  }

  async function seedDemoData() {
    if (!projectId) return;
    await apiFetch(`/projects/${projectId}/seed-demo-data`, { method: "POST" });
    await loadSuites();
  }

  async function runSuite(id: string) {
    await apiFetch(`/test-suites/${id}/run`, { method: "POST" });
  }

  return (
    <>
      <PageHeader
        title="Test Suites"
        eyebrow="Evaluation Design"
        action={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" onClick={() => loadSuites()}>
              <RefreshCw className="h-4 w-4" />
              Refresh
            </Button>
            <Button onClick={seedDemoData} disabled={!projectId}>
              <DatabaseZap className="h-4 w-4" />
              Seed Demo
            </Button>
          </div>
        }
      />
      {projects.loading || loadingSuites ? <LoadingState /> : null}
      {projects.error || error ? <ErrorState message={projects.error ?? error ?? ""} /> : null}
      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Project</CardTitle>
            </CardHeader>
            <CardContent>
              <select
                className="h-9 w-full rounded-md border border-border bg-card px-3 text-sm outline-none focus:border-primary"
                value={projectId}
                onChange={(event) => setProjectId(event.target.value)}
              >
                {(projects.data ?? []).map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
              <div className="mt-3 text-sm text-muted-foreground">{selectedProject?.description ?? ""}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Create Suite</CardTitle>
            </CardHeader>
            <CardContent>
              <form className="space-y-3" onSubmit={createSuite}>
                <Input value={name} onChange={(event) => setName(event.target.value)} placeholder="Unsafe Tool Calling" />
                <Input value={category} onChange={(event) => setCategory(event.target.value)} placeholder="unsafe_tool_call" />
                <Textarea
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Tool safety regression checks"
                />
                <Button type="submit" disabled={!projectId || !name.trim()}>
                  <Plus className="h-4 w-4" />
                  Create
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Suites</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <thead>
                    <tr>
                      <Th>Name</Th>
                      <Th>Category</Th>
                      <Th>Run</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {suites.map((suite) => (
                      <tr key={suite.id} className={suite.id === suiteId ? "bg-muted/50" : ""}>
                        <Td>
                          <button className="text-left font-medium text-primary" onClick={() => setSuiteId(suite.id)}>
                            {suite.name}
                          </button>
                        </Td>
                        <Td>{suite.category}</Td>
                        <Td>
                          <Button size="sm" variant="secondary" onClick={() => runSuite(suite.id)}>
                            <Play className="h-4 w-4" />
                            Run
                          </Button>
                        </Td>
                      </tr>
                    ))}
                    {suites.length === 0 ? (
                      <tr>
                        <Td colSpan={3} className="text-muted-foreground">
                          No suites found.
                        </Td>
                      </tr>
                    ) : null}
                  </tbody>
                </Table>
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
                      <Th>Severity</Th>
                      <Th>Expected</Th>
                      <Th>Run</Th>
                    </tr>
                  </thead>
                  <tbody>
                    {cases.map((testCase) => (
                      <tr key={testCase.id}>
                        <Td className="font-medium">{testCase.name}</Td>
                        <Td>
                          <StatusBadge value={testCase.severity} />
                        </Td>
                        <Td>{testCase.expected_behavior}</Td>
                        <Td>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={async () => {
                              const run = await apiFetch<{ id: string }>(`/test-cases/${testCase.id}/run`, {
                                method: "POST"
                              });
                              window.location.href = `/test-runs/${run.id}`;
                            }}
                          >
                            <Play className="h-4 w-4" />
                            Run
                          </Button>
                        </Td>
                      </tr>
                    ))}
                    {cases.length === 0 ? (
                      <tr>
                        <Td colSpan={4} className="text-muted-foreground">
                          Select a suite to view cases.
                        </Td>
                      </tr>
                    ) : null}
                  </tbody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </>
  );
}
