import Link from "next/link";
import {
  Activity,
  BookOpenCheck,
  CheckSquare,
  Database,
  Gauge,
  ShieldCheck,
  Siren,
  Workflow
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const featureGrid = [
  {
    title: "Adversarial Test Suites",
    description:
      "Seeded suites for prompt injection, unsafe tool calls, structured output, RAG failures, approvals, and retrieval quality.",
    icon: ShieldCheck
  },
  {
    title: "LangGraph Evaluation Workflow",
    description:
      "Eleven deterministic workflow steps. Every step's input, output, and audit event is persisted.",
    icon: Workflow
  },
  {
    title: "Policy Engine",
    description:
      "Rule-based safety enforcement: prompt injection, sensitive content, schema failures, citation integrity, weak retrieval.",
    icon: ShieldCheck
  },
  {
    title: "Human Approval Queue",
    description: "High-risk and policy-flagged tool calls route to a queue for explicit human review.",
    icon: CheckSquare
  },
  {
    title: "RAG Failure Detection",
    description:
      "Weak retrieval, stale context, unsupported claims and missing citations — measured, flagged, and persisted.",
    icon: BookOpenCheck
  },
  {
    title: "Observable Metrics",
    description:
      "Pass rate, failure categories, provider latency, policy violations, retrieval quality, citation coverage.",
    icon: Gauge
  }
];

export default function LandingPage() {
  return (
    <div className="space-y-12">
      <section className="rounded-lg border border-border bg-card p-8 md:p-12">
        <div className="flex items-center gap-3 text-primary">
          <Siren className="h-6 w-6" />
          <span className="text-xs font-semibold uppercase tracking-wider">Agent Canary</span>
        </div>
        <h1 className="mt-3 text-3xl font-semibold tracking-tight md:text-4xl">
          Stress-test AI agents before they get to production.
        </h1>
        <p className="mt-4 max-w-2xl text-base text-muted-foreground">
          Agent Canary is a live AI agent evaluation and safety testing platform. It scores agents
          against prompt injection, unsafe tool calls, malformed JSON outputs, weak retrieval,
          hallucination, policy bypass, and missing approval flows — with deterministic, repeatable
          tests and full audit history.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            href="/dashboard"
            className="inline-flex h-10 items-center justify-center rounded-md bg-primary px-4 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            <Activity className="mr-2 h-4 w-4" />
            Open Dashboard
          </Link>
          <Link
            href="/test-suites"
            className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium hover:bg-muted"
          >
            <Database className="mr-2 h-4 w-4" />
            Browse Test Suites
          </Link>
          <Link
            href="/metrics"
            className="inline-flex h-10 items-center justify-center rounded-md border border-border bg-card px-4 text-sm font-medium hover:bg-muted"
          >
            <Gauge className="mr-2 h-4 w-4" />
            See Metrics
          </Link>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-semibold">What this platform does</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Production AI agents fail in ways traditional apps don't. Agent Canary makes those
          failure modes visible and measurable.
        </p>
        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {featureGrid.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card key={feature.title}>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-sm">
                    <Icon className="h-4 w-4 text-primary" />
                    {feature.title}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            );
          })}
        </div>
      </section>

      <section className="rounded-lg border border-border bg-card p-6">
        <h2 className="text-xl font-semibold">How a test run works</h2>
        <ol className="mt-4 grid gap-3 text-sm md:grid-cols-2 xl:grid-cols-3">
          {[
            "Load the test case",
            "Retrieve evidence (if RAG)",
            "Build the agent prompt",
            "Call the LLM provider",
            "Parse and validate JSON",
            "Validate proposed tool call",
            "Run the policy engine",
            "Score ten safety dimensions",
            "Create approval if risky",
            "Persist run, llm_call, tool_call, audit log"
          ].map((step, index) => (
            <li
              key={step}
              className="flex items-start gap-3 rounded-md border border-border bg-background p-3"
            >
              <span className="flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
                {index + 1}
              </span>
              <span>{step}</span>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
