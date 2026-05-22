"use client";

import { FormEvent, useState } from "react";
import { Search } from "lucide-react";
import { ErrorState } from "@/components/data-state";
import { JsonBlock } from "@/components/json-block";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Table, Td, Th } from "@/components/ui/table";
import { apiFetch } from "@/lib/api";
import type { RetrievalResult } from "@/lib/types";

export default function RetrievalResultsPage() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<RetrievalResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function retrieve(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    try {
      setResult(
        await apiFetch<RetrievalResult>("/rag/retrieve", {
          method: "POST",
          body: JSON.stringify({ query, max_results: 5, min_score: 0.2 })
        })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Retrieval failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <PageHeader title="Retrieval Results" eyebrow="RAG Checks" />
      {error ? <ErrorState message={error} /> : null}
      <div className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Query</CardTitle>
          </CardHeader>
          <CardContent>
            <form className="flex flex-col gap-3 sm:flex-row" onSubmit={retrieve}>
              <Input
                placeholder="refund policy approval threshold"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
              <Button type="submit" disabled={!query.trim() || loading}>
                <Search className="h-4 w-4" />
                Search
              </Button>
            </form>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Latest Result</CardTitle>
          </CardHeader>
          <CardContent>
            {result ? (
              <div className="space-y-4">
                <div className="grid gap-4 md:grid-cols-4">
                  <div>
                    <div className="text-sm text-muted-foreground">Provider</div>
                    <div className="font-medium">{result.provider_name}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Model</div>
                    <div className="font-medium">{result.model_name}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Results</div>
                    <div className="font-medium">{result.result_count}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Result ID</div>
                    <div className="font-mono text-xs">{result.id.slice(0, 12)}</div>
                  </div>
                </div>
                <div className="overflow-x-auto">
                  <Table>
                    <thead>
                      <tr>
                        <Th>Document</Th>
                        <Th>Score</Th>
                        <Th>Content</Th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.results.map((chunk) => (
                        <tr key={chunk.chunk_id}>
                          <Td className="font-medium">{chunk.document_title}</Td>
                          <Td>{chunk.score.toFixed(3)}</Td>
                          <Td>{chunk.content}</Td>
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
                <JsonBlock value={result} />
              </div>
            ) : (
              <div className="text-sm text-muted-foreground">No retrieval result selected.</div>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
