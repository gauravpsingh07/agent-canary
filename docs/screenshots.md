# Screenshot Checklist

Use this file to track screenshots for the README, portfolio page, and GitHub repository after the live deployment is seeded.

Recommended image directory after screenshots are captured:

```text
docs/assets/screenshots/
```

Do not commit raw secrets, browser profile data, local `.env` files, or screenshots that expose API keys or database URLs.

## Required Screenshots

| Screenshot | Page | What It Should Show | Status |
| --- | --- | --- | --- |
| `01-overview.png` | Dashboard overview | pass rate, average score, pending approvals, charts | placeholder |
| `02-test-suites.png` | Test suites | seeded adversarial suites and test cases | placeholder |
| `03-test-run-detail.png` | Test run detail | workflow steps, score, failure reasons, metadata | placeholder |
| `04-tool-registry.png` | Tool registry | simulated tools and risk levels | placeholder |
| `05-policy-rules.png` | Policy rules | default safety rules and effects | placeholder |
| `06-approval-queue.png` | Approval queue | pending high-risk action review | placeholder |
| `07-audit-logs.png` | Audit logs | immutable event trail | placeholder |
| `08-rag-documents.png` | RAG documents | seeded documents and indexing status | placeholder |
| `09-retrieval-results.png` | Retrieval results | ranked chunks for a query | placeholder |
| `10-metrics.png` | Metrics | failures, policy violations, latency, RAG safety charts | placeholder |

## Capture Flow

1. Deploy backend and frontend.
2. Create a demo project.
3. Seed demo test suites.
4. Seed tools and policy rules.
5. Seed RAG demo data.
6. Run at least one full test suite.
7. Approve or reject one approval request.
8. Capture the screenshots above.
9. Add images under `docs/assets/screenshots/`.
10. Update this file from `placeholder` to `captured`.

## README Placement

Recommended README section after screenshots are captured:

```md
## Screenshots

![Dashboard overview](docs/assets/screenshots/01-overview.png)
![Test run detail](docs/assets/screenshots/03-test-run-detail.png)
![Metrics dashboard](docs/assets/screenshots/10-metrics.png)
```

Keep the README screenshot set small. Use the full checklist for the portfolio case study.
