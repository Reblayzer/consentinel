# Consentinel

**A data-governance & compliance portal.** Consentinel helps "data citizens" register
datasets, automatically discover the personal data inside them, attach a lawful basis for
processing, and handle **right-to-be-forgotten** and **subject-access** requests through an
auditable approval workflow.

It is built around the everyday reality of a data-platform compliance team: reduce the manual
effort of doing the right thing with personal data, while strengthening the guarantees that the
right thing is being done.

> **Status:** actively built in SCRUM-style sprints — see [the backlog](docs/BACKLOG.md).
> Sprint 1 (backend foundation + automatic PII classification) is complete and tested.

---

## Why this exists

Most data-governance pain is manual: someone has to know a table contains email addresses,
remember why it's allowed to, and chase down every copy when a customer asks to be forgotten.
Consentinel turns those manual steps into APIs and interfaces:

| Capability | What it does |
| --- | --- |
| **Dataset manifests** | A data owner registers a dataset and its columns. |
| **Automatic PII classification** | Each column is scanned and tagged (email, phone, national ID, …) with a confidence score and a human-readable rationale. |
| **Usage agreements** | Each dataset records its GDPR Article 6 lawful basis and retention. *(Sprint 2)* |
| **Governance roles** | Role-based access for owners, stewards, and data subjects. *(Sprint 2)* |
| **Right-to-be-forgotten / access requests** | Data subjects file requests that flow through an approval workflow with a full audit trail. *(Sprint 2)* |

## Architecture

```
                 ┌──────────────────────────┐
  data owner ──► │  Next.js + TypeScript UI  │  (Sprint 4)
  data subject   └────────────┬─────────────┘
                              │ HTTP / JSON
                 ┌────────────▼─────────────┐
                 │     FastAPI (Python)      │   compliance API
                 │  ┌─────────────────────┐  │
                 │  │  PII classifier     │  │   data-engineering core
                 │  └─────────────────────┘  │
                 └────────────┬─────────────┘
                              │ SQLAlchemy
                 ┌────────────▼─────────────┐
                 │ SQLite (dev) / Postgres   │   provisioned via Terraform
                 └───────────────────────────┘   on LocalStack (Sprint 3)
```

## Tech stack

- **Backend:** Python · FastAPI · SQLAlchemy 2.0 · Pydantic v2
- **Data engineering:** dependency-free heuristic PII classifier (regex + multilingual
  name hints, including Danish field names and the CPR national-ID format)
- **Database:** SQLite for zero-setup local dev; PostgreSQL for the containerised stack
- **Infrastructure as code:** Terraform → LocalStack + Docker *(Sprint 3)*
- **Frontend:** Next.js + TypeScript *(Sprint 4)*
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

```bash
curl -X POST http://localhost:8000/datasets \
  -H 'content-type: application/json' \
  -d '{
        "name": "crm.customers",
        "owner": "marketing-data-team",
        "source_system": "snowflake",
        "fields": [
          {"name": "email",       "sample_values": ["a@lego.dk", "b@lego.dk"]},
          {"name": "cpr",         "sample_values": ["010203-1234"]},
          {"name": "order_total", "sample_values": ["12.50", "9.99"]}
        ]
      }'
```

Consentinel responds with the dataset, each column tagged with its PII category, a confidence
score, and the reasoning behind the decision.

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
