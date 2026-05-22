# Portfolio Notes

This document is a quick presentation guide for talking through Agent Canary in interviews, GitHub project descriptions, and portfolio case studies.

## One-Line Pitch

Agent Canary is a live AI agent evaluation and safety testing platform that stress-tests agents against prompt injection, unsafe tool calls, structured output failures, RAG failures, and missing human approval gates.

## Short Walkthrough

1. Open the dashboard overview and explain the safety posture metrics.
2. Show a seeded test suite such as Prompt Injection Defense or Unsafe Tool Calling.
3. Run a test case or suite.
4. Open the test-run detail page and explain the LangGraph workflow steps.
5. Show how structured output, tool calls, policy checks, and scores are persisted.
6. Open the approval queue and explain why risky simulated actions need human review.
7. Open audit logs to show the event trail.
8. Open RAG documents and retrieval results to show weak retrieval and citation evaluation.
9. Finish on the metrics page to show pass rate, failure categories, policy violations, latency, and RAG safety signals.

## Interview Talking Points

- The app does not execute real dangerous tools. It evaluates proposed tool calls in a simulated environment.
- The provider layer keeps the workflow independent from a single LLM vendor.
- The mock provider makes tests deterministic and keeps the deployed demo free.
- LangGraph is used for stateful, step-level evaluation instead of one large function.
- Pydantic and JSON Schema enforce structured outputs and tool-call arguments.
- The policy engine catches risky autonomous actions before execution.
- Approval requests model human-in-the-loop controls for high-risk behavior.
- Audit logs make decisions inspectable after the run.
- RAG tests focus on what agents should do when context is weak, stale, or missing.

## Strong Demo Script

Use this order for a 3 to 5 minute walkthrough:

1. "This is not a chatbot. It is an evaluation harness for AI agents."
2. "I seed adversarial suites for prompt injection, unsafe tools, schema failures, approvals, and RAG failures."
3. "A run goes through LangGraph nodes: load case, call provider, parse output, validate schema, evaluate tool call, run policy, score, create review, persist, audit."
4. "The model can propose a refund or delete action, but the backend only simulates and evaluates it."
5. "The approval queue shows where autonomous behavior should stop and ask a human."
6. "The metrics page summarizes safety regressions across runs."

## Resume Bullets

- Built Agent Canary, a full-stack AI agent evaluation platform using Next.js, FastAPI, Supabase Postgres, LangGraph, and provider adapters for Gemini, Groq, OpenAI, and deterministic mocks.
- Implemented structured-output and tool-call validation with Pydantic and JSON Schema to detect malformed agent responses and unsafe proposed actions.
- Designed a rule-based policy engine and human approval queue for blocked, high-risk, or approval-gated simulated tool calls.
- Added RAG failure testing for weak retrieval, stale context, unsupported claims, and missing citations, with dashboard metrics for retrieval quality and citation coverage.
- Productionized the project with Alembic migrations, Docker, GitHub Actions CI, deployment docs, environment-based configuration, Ruff, mypy, and pytest coverage.

## Case Study Outline

Use this outline for a portfolio write-up:

1. Problem: AI agents can fail through unsafe actions and unreliable outputs.
2. Goal: Build a production-style evaluation platform, not another chat UI.
3. Architecture: Next.js, FastAPI, LangGraph, SQLAlchemy, Supabase, provider adapters.
4. Safety model: simulated tools, schema validation, policy engine, approval queue.
5. RAG testing: weak retrieval, stale context, unsupported claims, citations.
6. Observability: audit logs, run steps, metrics dashboards.
7. Deployment: Vercel, Render, Supabase, mock providers for free demo operation.
8. Outcome: repeatable safety tests and a dashboard for agent reliability.
