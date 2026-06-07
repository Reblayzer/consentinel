# Product backlog

Consentinel is built in short, shippable increments. Each sprint leaves the project in a
working, tested state. This mirrors how a data-platform compliance squad would deliver.

## Vision

Reduce the manual effort of handling personal data compliantly, and make compliance
guarantees verifiable, by exposing governance as clean APIs and interfaces.

## Sprints

### Sprint 1 — Backend foundation & PII classification ✅
- [x] FastAPI application skeleton + health check
- [x] Domain model: `Dataset` (manifest) and `DataField`
- [x] Environment-driven config (SQLite by default, Postgres-ready)
- [x] Heuristic PII classifier — value patterns + multilingual (EN/DA) name hints,
      including the Danish CPR national-ID format and Luhn-checked card numbers
- [x] Dataset registration endpoint that auto-classifies every column
- [x] pytest suite (classifier units + API integration) and ruff lint

### Sprint 2 — Compliance workflows ✅
- [x] Usage agreements: lawful basis (GDPR Art. 6) + retention per dataset
- [x] Governance roles & role-based access (owner / steward / subject / admin)
- [x] Compliance requests: right-to-be-forgotten (Art. 17) and access (Art. 15)
- [x] Approval workflow (pending → approved/rejected → completed)
- [x] Immutable audit trail of every governance action

### Sprint 3 — Infrastructure as code
- [ ] `docker-compose`: Postgres + LocalStack + API
- [ ] Terraform provisioning S3 (evidence store) + SQS (request queue) on LocalStack
- [ ] Alembic migrations replacing dev-time table creation
- [ ] GitHub Actions CI: ruff + pytest on every push

### Sprint 4 — TypeScript frontend
- [ ] Next.js + TypeScript dashboard
- [ ] Register datasets and visualise PII findings
- [ ] File and review right-to-be-forgotten / access requests
- [ ] Typed API client + Vitest component tests

### Sprint 5 — Polish & delivery
- [ ] Architecture diagram + screenshots / demo GIF
- [ ] Deployment / demo notes
- [ ] Portfolio + CV integration

## Definition of done (per story)

- Code has tests and they pass.
- `ruff check` is clean.
- Behaviour is documented (docstring or README) where it isn't obvious.
- The app still runs end-to-end.
