"use client";

import { FormEvent, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { apiFetch, formatDate } from "@/lib/api";
import type { Project } from "@/lib/types";

export default function ProjectsPage() {
  const projects = useApi<Project[]>("/projects");
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [saving, setSaving] = useState(false);

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    try {
      await apiFetch<Project>("/projects", {
        method: "POST",
        body: JSON.stringify({ name, description: description || null })
      });
      setName("");
      setDescription("");
      await projects.refresh();
    } finally {
      setSaving(false);
    }
  }

  return (
    <>
      <PageHeader
        title="Projects"
        eyebrow="Workspaces"
        action={
          <Button variant="secondary" onClick={() => projects.refresh()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        }
      />
      {projects.loading ? <LoadingState /> : null}
      {projects.error ? <ErrorState message={projects.error} /> : null}
      <div className="grid gap-4 xl:grid-cols-[360px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Create Project</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-3" onSubmit={createProject}>
              <Input placeholder="Agent Canary Demo" value={name} onChange={(event) => setName(event.target.value)} />
              <Textarea
                placeholder="Safety evaluation workspace"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
              />
              <Button type="submit" disabled={!name.trim() || saving}>
                <Plus className="h-4 w-4" />
                Create
              </Button>
            </form>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Project List</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <thead>
                  <tr>
                    <Th>Name</Th>
                    <Th>Description</Th>
                    <Th>Created</Th>
                  </tr>
                </thead>
                <tbody>
                  {(projects.data ?? []).map((project) => (
                    <tr key={project.id}>
                      <Td className="font-medium">{project.name}</Td>
                      <Td>{project.description ?? "-"}</Td>
                      <Td>{formatDate(project.created_at)}</Td>
                    </tr>
                  ))}
                  {(projects.data ?? []).length === 0 ? (
                    <tr>
                      <Td colSpan={3} className="text-muted-foreground">
                        No projects found.
                      </Td>
                    </tr>
                  ) : null}
                </tbody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
