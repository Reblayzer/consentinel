# Consentinel

**A data-governance & compliance portal.** Consentinel helps "data citizens" register
datasets, automatically discover the personal data inside them, attach a lawful basis for
processing, and handle **right-to-be-forgotten** and **subject-access** requests through an
auditable approval workflow.

It is built around the everyday reality of a data-platform compliance team: reduce the manual
effort of doing the right thing with personal data, while strengthening the guarantees that the
right thing is being done.

> **Status:** built in SCRUM-style sprints — see [the backlog](docs/BACKLOG.md).
> Sprints 1–4 are complete and verified: backend foundation, automatic PII
> classification, the full compliance workflow, the containerised stack
> (Postgres + LocalStack) provisioned with Terraform, and a Next.js + TypeScript
> dashboard.

---

## Why this exists

Most data-governance pain is manual: someone has to know a table contains email addresses,
remember why it's allowed to, and chase down every copy when a customer asks to be forgotten.
Consentinel turns those manual steps into APIs and interfaces:

| Capability | What it does |
| --- | --- |
| **Dataset manifests** | A data owner registers a dataset and its columns. |
| **Automatic PII classification** | Each column is scanned and tagged (email, phone, national ID, …) with a confidence score and a human-readable rationale. |
| **Usage agreements** | Each dataset records its GDPR Article 6 lawful basis and retention. |
| **Governance roles** | Role-based access for owners, stewards, and data subjects. |
| **Right-to-be-forgotten / access requests** | Data subjects file requests that flow through an approval workflow with a full audit trail. |

## Architecture

```
                 ┌──────────────────────────┐
  data owner ──► │  Next.js + TypeScript UI  │  dashboard
  data subject   └────────────┬─────────────┘
                              │ HTTP / JSON
                 ┌────────────▼─────────────┐
                 │     FastAPI (Python)      │   compliance API
                 │  ┌─────────────────────┐  │
                 │  │  PII classifier     │  │   data-engineering core
                 │  └─────────────────────┘  │
                 └────────────┬─────────────┘   (UI proxies /api/* here)
                              │ SQLAlchemy
                 ┌────────────▼─────────────┐
                 │ SQLite (dev) / Postgres   │   S3 + SQS provisioned via
                 └───────────────────────────┘   Terraform on LocalStack
```

## Tech stack

- **Backend:** Python · FastAPI · SQLAlchemy 2.0 · Pydantic v2
- **Data engineering:** dependency-free heuristic PII classifier (regex + multilingual
  name hints, including Danish field names and the CPR national-ID format)
- **Database:** SQLite for zero-setup local dev; PostgreSQL for the containerised stack
- **Infrastructure as code:** Terraform → LocalStack + Docker *(Sprint 3)*
- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS v4, with a typed API client
- **Quality:** pytest · ruff · GitHub Actions CI

## Quickstart (backend)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# run the test suite
pytest

# run the API (interactive docs at http://localhost:8000/docs)
uvicorn app.main:app --reload
```

### Try it

Register a dataset (requires the `data_owner` role — see *Roles & access* below):

```bash
curl -X POST http://localhost:8000/datasets \
  -H 'content-type: application/json' \
  -H 'X-Actor: alice' -H 'X-Role: data_owner' \
  -d '{
        "name": "crm.customers",
        "owner": "marketing-data-team",
        "source_system": "snowflake",
        "fields": [
          {"name": "email",       "sample_values": ["a@example.dk", "b@example.dk"]},
          {"name": "cpr",         "sample_values": ["010203-1234"]},
          {"name": "order_total", "sample_values": ["12.50", "9.99"]}
        ]
      }'
```

Consentinel responds with the dataset, each column tagged with its PII category, a confidence
score, and the reasoning behind the decision.

A data subject can then ask to be forgotten, and a steward works the request:

```bash
# data subject files a right-to-be-forgotten request
curl -X POST http://localhost:8000/requests \
  -H 'content-type: application/json' \
  -H 'X-Actor: jens' -H 'X-Role: data_subject' \
  -d '{"request_type": "erasure", "subject_ref": "jens@example.dk", "reason": "please delete my data"}'

# steward approves, then completes it (id from the response above)
curl -X POST http://localhost:8000/requests/1/approve \
  -H 'content-type: application/json' \
  -H 'X-Actor: sam' -H 'X-Role: data_steward' -d '{"note": "identity verified"}'
```

Every action lands in the append-only audit trail at `GET /audit`.

### Roles & access

Identity is supplied per request via `X-Actor` and `X-Role` headers — a deliberately small
stand-in for OIDC/JWT, isolated in [`app/core/security.py`](backend/app/core/security.py) so
real auth can replace it without touching the rest of the app. Roles:

| Role | Can |
| --- | --- |
| `data_owner` | Register datasets, attach usage agreements |
| `data_steward` | Approve / reject / complete requests, read the audit trail |
| `data_subject` | File right-to-be-forgotten / access requests |
| `admin` | Everything |

## Run the full stack (Docker + Terraform)

The production-like stack runs the API against PostgreSQL, with
[LocalStack](https://localstack.cloud/) standing in for AWS:

```bash
# build & start Postgres + LocalStack + API
docker compose up -d --build      # API on http://localhost:8080

# provision the S3 evidence bucket + SQS request queue on LocalStack
cd infra && terraform init && terraform apply -auto-approve
```

On boot the API applies its **Alembic migrations** automatically, so the Postgres
schema always matches the deployed code. (Host ports: API `8080`, Postgres `5433`,
LocalStack `4566`.)

## Dashboard (Next.js + TypeScript)

A dashboard for data citizens lives in [`frontend/`](frontend). Run the backend
(`uvicorn app.main:app` on :8000), then:

```bash
cd frontend
pnpm install
pnpm dev            # http://localhost:3000
```

The UI proxies `/api/*` to the backend (set via `CONSENTINEL_API_URL`, default
`http://localhost:8000`), so there's no CORS to configure. A **role switcher** in
the header lets you act as a data owner, steward, or subject — exercising the
RBAC rules from the browser. Screens:

- **Datasets** — every registered dataset with its columns' PII badges and the
  classifier's rationale.
- **Register dataset** — submit a manifest and watch each column get classified.
- **Requests** — file right-to-be-forgotten / access requests and, as a steward,
  approve / reject / complete them.

```bash
cd frontend && pnpm test        # Vitest unit tests (API client + PII helpers)
```

## Continuous integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every push and pull
request: `ruff` + `pytest` for the backend, `pnpm test` + `pnpm build` for the
frontend, and `terraform fmt -check` + `validate` for the infrastructure.

## Configuration

All settings are environment variables with the `CONSENTINEL_` prefix (see
[`app/core/config.py`](backend/app/core/config.py)). The most important one:

```bash
# default — zero-setup local dev
CONSENTINEL_DATABASE_URL=sqlite:///./consentinel.db
# containerised stack
CONSENTINEL_DATABASE_URL=postgresql+psycopg://consentinel:consentinel@db:5432/consentinel
```

## Tests

```bash
cd backend && pytest        # unit + API tests
ruff check .                # lint
```

## License

MIT
