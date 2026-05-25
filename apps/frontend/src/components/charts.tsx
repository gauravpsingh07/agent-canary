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

export function PassFailTrendChart({
  data
}: {
  data: Array<{ bucket: string; passed: number; failed: number }>;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Pass / Fail Trend</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Line type="monotone" dataKey="passed" stroke="#0f766e" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="failed" stroke="#be123c" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function AverageScoreTrendChart({
  data
}: {
  data: Array<{ bucket: string; avg_score: number }>;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Average Score Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="avg_score" stroke="#0891b2" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function ApprovalOutcomeChart({
  pending,
  approved,
  rejected
}: {
  pending: number;
  approved: number;
  rejected: number;
}) {
  const data = [
    { name: "Approved", value: approved, color: "#0f766e" },
    { name: "Rejected", value: rejected, color: "#be123c" },
    { name: "Pending", value: pending, color: "#d97706" }
  ].filter((entry) => entry.value > 0);
  return (
    <Card>
      <CardHeader>
        <CardTitle>Approval Outcomes</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={data} dataKey="value" nameKey="name" innerRadius={58} outerRadius={88} paddingAngle={3}>
                  {data.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
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

export function RagFailureCategoryChart({ data }: { data: FailureByCategory[] }) {
  const ragCategories = new Set([
    "weak_retrieval",
    "stale_context",
    "hallucination",
    "retrieval_quality",
    "citation_failure",
    "unsupported_claim"
  ]);
  const filtered = data.filter((entry) => ragCategories.has(entry.category));
  return (
    <Card>
      <CardHeader>
        <CardTitle>RAG Failure Categories</CardTitle>
      </CardHeader>
      <CardContent>
        {filtered.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={filtered}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="category" tick={{ fontSize: 11 }} interval={0} height={58} />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="total_failures" radius={[4, 4, 0, 0]} fill="#65a30d" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function RetrievalQualityTrendChart({
  data
}: {
  data: Array<{ bucket: string; avg_top_score: number; weak_rate: number }>;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Retrieval Quality Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 1]} />
                <Tooltip />
                <Line type="monotone" dataKey="avg_top_score" stroke="#0f766e" strokeWidth={2} dot={{ r: 3 }} />
                <Line type="monotone" dataKey="weak_rate" stroke="#d97706" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

export function CitationCoverageTrendChart({
  data
}: {
  data: Array<{ bucket: string; coverage_rate: number }>;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Citation Coverage Over Time</CardTitle>
      </CardHeader>
      <CardContent>
        {data.length === 0 ? (
          <EmptyChart />
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="bucket" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="coverage_rate" stroke="#0891b2" strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
