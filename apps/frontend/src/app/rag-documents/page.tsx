"use client";

import { FormEvent, useState } from "react";
import { Plus, RefreshCw } from "lucide-react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { PageHeader } from "@/components/page-header";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Table, Td, Th } from "@/components/ui/table";
import { useApi } from "@/components/use-api";
import { apiFetch, formatDate } from "@/lib/api";
import type { RagDocument } from "@/lib/types";

export default function RagDocumentsPage() {
  const documents = useApi<RagDocument[]>("/rag/documents");
  const [title, setTitle] = useState("");
  const [sourceUri, setSourceUri] = useState("");
  const [content, setContent] = useState("");

  async function ingestDocument(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await apiFetch("/rag/documents", {
      method: "POST",
      body: JSON.stringify({
        title,
        source_uri: sourceUri || null,
        source_type: "manual",
        content,
        metadata: {}
      })
    });
    setTitle("");
    setSourceUri("");
    setContent("");
    await documents.refresh();
  }

  return (
    <>
      <PageHeader
        title="RAG Documents"
        eyebrow="Grounding Corpus"
        action={
          <Button variant="secondary" onClick={() => documents.refresh()}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        }
      />
      {documents.loading ? <LoadingState /> : null}
      {documents.error ? <ErrorState message={documents.error} /> : null}
      <div className="grid gap-4 xl:grid-cols-[420px_1fr]">
        <Card>
          <CardHeader>
            <CardTitle>Ingest Document</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="space-y-3" onSubmit={ingestDocument}>
              <Input placeholder="Refund Policy" value={title} onChange={(event) => setTitle(event.target.value)} />
              <Input
                placeholder="kb://refund-policy"
                value={sourceUri}
                onChange={(event) => setSourceUri(event.target.value)}
              />
              <Textarea
                className="min-h-48"
                placeholder="Document text"
                value={content}
                onChange={(event) => setContent(event.target.value)}
              />
              <Button type="submit" disabled={!title.trim() || !content.trim()}>
                <Plus className="h-4 w-4" />
                Ingest
              </Button>
            </form>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Documents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <Table>
                <thead>
                  <tr>
                    <Th>Title</Th>
                    <Th>Source</Th>
                    <Th>Status</Th>
                    <Th>Created</Th>
                  </tr>
                </thead>
                <tbody>
                  {(documents.data ?? []).map((document) => (
                    <tr key={document.id}>
                      <Td className="font-medium">{document.title}</Td>
                      <Td>{document.source_uri ?? document.source_type}</Td>
                      <Td>
                        <StatusBadge value={document.status} />
                      </Td>
                      <Td>{formatDate(document.created_at)}</Td>
                    </tr>
                  ))}
                  {(documents.data ?? []).length === 0 ? (
                    <tr>
                      <Td colSpan={4} className="text-muted-foreground">
                        No RAG documents found.
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
