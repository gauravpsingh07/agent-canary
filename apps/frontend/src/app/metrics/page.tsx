"use client";

import { BookOpenCheck, Clock, Gauge, RefreshCw, ShieldAlert } from "lucide-react";
import {
  FailureCategoryChart,
  PolicyViolationChart,
  ProviderLatencyChart,
  RetrievalHealthChart
} from "@/components/charts";
import { ErrorState, LoadingState } from "@/components/data-state";
import { MetricCard } from "@/components/metric-card";
import { PageHeader } from "@/components/page-header";
import { Button } from "@/components/ui/button";
import { useApi } from "@/components/use-api";
import { asPercent } from "@/lib/api";
import type {
  CitationCoverageMetric,
  FailureByCategory,
  MetricsSummary,
  PolicyViolationMetric,
  ProviderLatency,
  RetrievalQualityMetric
} from "@/lib/types";

export default function MetricsPage() {
  const summary = useApi<MetricsSummary>("/metrics/summary");
  const failures = useApi<FailureByCategory[]>("/metrics/failures-by-category");
  const violations = useApi<PolicyViolationMetric[]>("/metrics/policy-violations");
  const latency = useApi<ProviderLatency[]>("/metrics/provider-latency");
  const retrieval = useApi<RetrievalQualityMetric>("/metrics/retrieval-quality");
  const citations = useApi<CitationCoverageMetric>("/metrics/citation-coverage");
  const loading =
    summary.loading || failures.loading || violations.loading || latency.loading || retrieval.loading || citations.loading;
  const error =
    summary.error ?? failures.error ?? violations.error ?? latency.error ?? retrieval.error ?? citations.error;

  function refreshAll() {
    void Promise.all([
      summary.refresh(),
      failures.refresh(),
      violations.refresh(),
      latency.refresh(),
      retrieval.refresh(),
      citations.refresh()
    ]);
  }

  return (
    <>
      <PageHeader
        title="Metrics"
        eyebrow="Evaluation Signals"
        action={
          <Button variant="secondary" onClick={refreshAll}>
            <RefreshCw className="h-4 w-4" />
            Refresh
          </Button>
        }
      />
      {loading ? <LoadingState /> : null}
      {error ? <ErrorState message={error} /> : null}
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <MetricCard
            label="Average Score"
            value={(summary.data?.average_score ?? 0).toFixed(1)}
            icon={Gauge}
            tone="blue"
          />
          <MetricCard
            label="Pass Rate"
            value={asPercent(summary.data?.pass_rate ?? 0)}
            icon={BookOpenCheck}
            tone="green"
          />
          <MetricCard
            label="Weak Retrieval Rate"
            value={asPercent(retrieval.data?.weak_retrieval_rate ?? 0)}
            icon={ShieldAlert}
            tone="amber"
          />
          <MetricCard
            label="Citation Coverage"
            value={asPercent(citations.data?.citation_coverage_rate ?? 0)}
            icon={Clock}
            tone="default"
          />
        </div>
        <div className="grid gap-4 xl:grid-cols-2">
          <FailureCategoryChart data={failures.data ?? []} />
          <PolicyViolationChart data={violations.data ?? []} />
          <ProviderLatencyChart data={latency.data ?? []} />
          <RetrievalHealthChart retrieval={retrieval.data} citations={citations.data} />
        </div>
      </div>
    </>
  );
}
