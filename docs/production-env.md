# Production Environment Reference

Do not commit real secrets, API keys, database passwords, Vercel project files, Render env exports, or Supabase connection strings. Store production values only in the hosting provider dashboards.

## Render Backend

Required:

```text
APP_NAME=Agent Canary
APP_ENV=production
APP_DEBUG=false
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
JWT_SECRET=<long random production secret>
CORS_ORIGINS=https://<vercel-domain>
LLM_PROVIDER=mock
MOCK_LLM_MODEL=mock-agent-canary-v1
EMBEDDING_PROVIDER=mock
MOCK_EMBEDDING_MODEL=mock-embedding-v1
EMBEDDING_DIMENSION=768
RAG_CHUNK_MAX_CHARS=1000
RAG_CHUNK_OVERLAP_CHARS=120
RETRIEVAL_DEFAULT_MIN_SCORE=0.25
RETRIEVAL_DEFAULT_MAX_RESULTS=5
```

Optional model providers:

```text
GEMINI_API_KEY=<render-secret>
GEMINI_MODEL=<current-gemini-model>
GEMINI_EMBEDDING_MODEL=text-embedding-004
GROQ_API_KEY=<render-secret>
GROQ_MODEL=<current-groq-model>
OPENAI_API_KEY=<optional-render-secret>
OPENAI_MODEL=<optional-openai-model>
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
LLM_TIMEOUT_SECONDS=30
EMBEDDING_TIMEOUT_SECONDS=30
```

Optional queue:

```text
REDIS_URL=<upstash-redis-url>
```

## Vercel Frontend

Required:

```text
NEXT_PUBLIC_API_BASE_URL=https://<render-service>.onrender.com
```

`NEXT_PUBLIC_API_BASE_URL` is intentionally public because it is embedded into the client bundle. Do not put secrets in `NEXT_PUBLIC_*` variables.

## GitHub Actions

The current CI workflow validates code only and does not deploy. It does not require secrets.

If custom Vercel deployment is added later, set these as GitHub repository secrets:

```text
VERCEL_TOKEN=<vercel-token>
VERCEL_ORG_ID=<vercel-org-id>
VERCEL_PROJECT_ID=<vercel-project-id>
```

If Render deployment is automated later, use a Render deploy hook or API key as a GitHub secret. Do not commit the hook URL.

## Local Demo Defaults

For a free local or portfolio demo, use:

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
```

This keeps seeded test runs deterministic and avoids dependency on external model quotas.

## Secret Rotation Checklist

- Rotate `JWT_SECRET` before a public live demo if it was ever shared.
- Rotate Supabase credentials if a connection string was pasted into logs.
- Rotate Gemini, Groq, or OpenAI keys after accidental exposure.
- Remove local `.env` files before zipping or sharing the repository.
- Verify `git status --ignored` does not show secrets as tracked files.
