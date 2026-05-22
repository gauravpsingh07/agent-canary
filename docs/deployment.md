# Deployment Guide

This guide describes the low-cost live deployment path for Agent Canary:

- Frontend: Vercel
- Backend: Render
- Database: Supabase Postgres
- Optional queue: Upstash Redis

The live demo can run with `LLM_PROVIDER=mock` and `EMBEDDING_PROVIDER=mock` so it does not require paid model usage. Gemini or Groq can be enabled later by setting provider keys and model names.

## Deployment Order

1. Create Supabase project and database.
2. Enable the `vector` extension in Supabase.
3. Configure backend environment variables on Render.
4. Run Alembic migrations against Supabase.
5. Deploy the FastAPI backend on Render.
6. Configure frontend environment variables on Vercel.
7. Deploy the Next.js frontend on Vercel.
8. Seed demo data.
9. Smoke-test the live dashboard and API.

## Supabase

Create a Supabase project and copy the pooled Postgres connection string.

The backend expects a SQLAlchemy URL:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

Supabase often provides a URI beginning with `postgresql://`. Convert it to `postgresql+psycopg://` for SQLAlchemy.

Enable pgvector in the SQL editor:

```sql
create extension if not exists vector;
```

Run migrations from `apps/backend` with `DATABASE_URL` pointed at Supabase:

```powershell
$env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE"
alembic upgrade head
```

## Render Backend

Create a Render Web Service from the repository.

Recommended settings:

- Root directory: `apps/backend`
- Runtime: Python
- Build command: `python -m pip install -e .`
- Start command: `uvicorn agent_canary.main:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

Set production environment variables on Render:

```text
APP_ENV=production
APP_DEBUG=false
DATABASE_URL=postgresql+psycopg://...
JWT_SECRET=<long random secret>
CORS_ORIGINS=https://<vercel-app-domain>
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
```

Optional live-provider variables:

```text
GEMINI_API_KEY=<set in Render only>
GEMINI_MODEL=<current Gemini model>
GROQ_API_KEY=<set in Render only>
GROQ_MODEL=<current Groq model>
OPENAI_API_KEY=<optional>
OPENAI_MODEL=<optional>
```

After deploy, verify:

```text
https://<render-service>.onrender.com/health
https://<render-service>.onrender.com/docs
```

## Vercel Frontend

Create a Vercel project from the repository.

Recommended settings:

- Framework preset: Next.js
- Root directory: `apps/frontend`
- Install command: `npm ci`
- Build command: `npm run build`
- Output directory: `.next`

Set the frontend API variable:

```text
NEXT_PUBLIC_API_BASE_URL=https://<render-service>.onrender.com
```

Vercel Git integration will create preview deployments for pull requests and production deployments from `main`. If using custom CI later, prefer the Vercel CLI `vercel build` plus `vercel deploy --prebuilt` flow so tests can gate deployment before promotion.

## CORS

Render must allow the Vercel domain:

```text
CORS_ORIGINS=https://<vercel-app-domain>
```

For local development, keep:

```text
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Seed Demo Data

After the backend is live, seed a project through the dashboard or API:

```bash
curl -X POST https://<render-service>.onrender.com/projects \
  -H "Content-Type: application/json" \
  -d '{"name":"Agent Canary Demo","description":"Seeded portfolio demo"}'
```

Use the returned `project_id`:

```bash
curl -X POST https://<render-service>.onrender.com/projects/<project_id>/seed-demo-data
curl -X POST https://<render-service>.onrender.com/projects/<project_id>/seed-rag-demo-data
curl -X POST https://<render-service>.onrender.com/tools/seed-defaults
curl -X POST https://<render-service>.onrender.com/policy-rules/seed-defaults
```

Then run one suite from the dashboard to populate metrics, audit logs, approval requests, and test run detail views.

## Smoke Test Checklist

- `GET /health` returns 200.
- `GET /metrics/summary` returns JSON.
- Frontend overview loads.
- Projects page can create a project.
- Test suites page can seed demo cases.
- Tools and policy pages can seed defaults.
- A test case can run and open a test-run detail page.
- Audit logs show the create/seed/run events.
- Approval queue shows high-risk review items when generated.
- RAG documents and retrieval pages return results after RAG seed data is loaded.

## Rollback Notes

Vercel can roll back or promote deployments from the dashboard. Render can redeploy a previous commit from its deploy history. Supabase schema changes should be treated as forward migrations; avoid deleting production data during demo prep.
