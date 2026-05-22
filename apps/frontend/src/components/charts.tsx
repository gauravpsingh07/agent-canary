"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type {
  CitationCoverageMetric,
  FailureByCategory,
  PolicyViolationMetric,
  ProviderLatency,
  RetrievalQualityMetric
} from "@/lib/types";

const palette = ["#0f766e", "#d97706", "#be123c", "#0891b2", "#4b5563", "#65a30d"];

function EmptyChart() {
  return <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">No data yet</div>;
}

export function FailureCategoryChart({ data }: { data: FailureByCategory[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Failures By Category</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="category" tick={{ fontSize: 11 }} interval={0} height={58} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total_failures" radius={[4, 4, 0, 0]} fill="#be123c" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function PolicyViolationChart({ data }: { data: PolicyViolationMetric[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Policy Violations</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="violation_code" tick={{ fontSize: 11 }} interval={0} height={70} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" radius={[4, 4, 0, 0]} fill="#d97706" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ProviderLatencyChart({ data }: { data: ProviderLatency[] }) {
  const chartData = data.map((item) => ({
    provider: `${item.provider_name}/${item.model_name}`,
    latency: item.average_latency_ms
  }));
  return (
    <Card>
      <CardHeader>
        <CardTitle>Provider Latency</CardTitle>
      </CardHeader>
      <CardContent>
        {chartData.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="provider" tick={{ fontSize: 11 }} interval={0} height={58} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="latency" radius={[4, 4, 0, 0]} fill="#0891b2" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function PassFailChart({ passed, failed }: { passed: number; failed: number }) {
  const data = [
    { name: "Passed", value: passed },
    { name: "Failed", value: failed }
  ].filter((item) => item.value > 0);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Pass / Fail Split</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data} dataKey="value" nameKey="name" innerRadius={58} outerRadius={88} paddingAngle={3}>
                  {data.map((_, index) => (
                    <Cell key={index} fill={palette[index % palette.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ScoreTrendChart({ data }: { data: Array<{ label: string; score: number }> }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Scores</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="score" stroke="#0f766e" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function RetrievalHealthChart({
  retrieval,
  citations
}: {
  retrieval?: RetrievalQualityMetric | null;
  citations?: CitationCoverageMetric | null;
}) {
  const data = [
    { label: "Weak Retrieval", value: retrieval?.weak_retrieval_rate ?? 0 },
    { label: "Citation Coverage", value: citations?.citation_coverage_rate ?? 0 }
  ];
  return (
    <Card>
      <CardHeader>
        <CardTitle>RAG Safety Signals</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Bar dataKey="value" radius={[4, 4, 0, 0]} fill="#0f766e" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
