# Healthcare Application Testing & Validation

A small clinic scheduling system (patient records, doctor roster,
appointment booking) built to demonstrate a realistic development,
testing, validation, and release workflow — not just the application
code, but the process around it: unit tests, API tests, an end-to-end
workflow test, a test plan, a UAT plan, and a CI pipeline that actually
runs all of it.

The application itself is intentionally scoped small. The point of this
repository is the practice around it, not feature count.

## What is actually here

- A FastAPI backend with patient, doctor, and appointment endpoints,
  JWT-based authentication, and role-based permissions (admin / staff /
  doctor)
- A React frontend that logs in, registers patients, and lists them
- 41 automated tests across three tiers (unit, API, end-to-end), all
  passing, at 95% statement coverage on the backend
- A GitHub Actions workflow that lints, runs each test tier separately,
  then runs the full suite with coverage enforcement, and separately
  confirms the frontend builds
- A test plan and a UAT plan that describe what is and is not covered,
  including the gaps

## Project structure

```
application/
    backend/         FastAPI service (app/, requirements.txt)
    frontend/         React + Vite frontend (src/)
tests/
    unit/             Logic tests, no database or network
    api/               HTTP-level tests against the FastAPI app
    e2e/               Full workflow tests (register, book, complete)
docs/
    TEST_PLAN.md       What is tested, how, and what is not yet covered
    UAT_PLAN.md        How the application is validated with real users
.github/workflows/tests.yml   CI pipeline
```

## Running it locally

### Backend

```
cd application/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
```

The API is then available at `http://localhost:8000`, with interactive
docs at `http://localhost:8000/docs`.

### Frontend

```
cd application/frontend
npm install
npm run dev
```

### Tests

From the repository root:

```
pip install -r requirements.txt
pytest                                              # everything
pytest -m unit                                      # unit tier only
pytest -m api                                        # API tier only
pytest -m e2e                                        # end-to-end tier only
pytest --cov=application/backend/app --cov-report=term-missing
```

## Design decisions worth knowing about

**SQLite for tests, configurable for real deployments.** The backend
defaults to a local SQLite file and the test suite uses an isolated
in-memory SQLite database per test. Point `DATABASE_URL` at PostgreSQL
for anything beyond local development.

**No DNS-dependent email validation.** Email fields use a plain regex
check rather than `pydantic`'s `EmailStr`, which by default performs
live DNS/MX lookups and rejects reserved test domains like `.test`. That
combination made the test suite dependent on network access and
unable to use standard test-only email addresses — the wrong tradeoff
for a project whose test suite needs to run the same in CI as offline.

**Scheduling and MRN logic live outside the API layer.** Appointment
conflict detection (`app/core/scheduling.py`) and medical record number
generation (`app/core/mrn.py`) are plain functions with no database or
HTTP dependency, specifically so they can be unit tested directly. This
is also why the unit test tier runs in well under a second.

**PHI is not encrypted at rest in this version.** Patient contact
details and appointment notes are stored as plain columns. That is
flagged directly in `application/backend/app/database/models.py` and in
the test plan, rather than left implicit — a demonstration project
having this gap is normal; a real clinic system shipping it silently
would not be.

## What is not done yet

- Browser-driven end-to-end tests (Playwright against a staging build) —
  the current E2E tier tests the same workflow through the API layer,
  which is fast but does not catch frontend rendering bugs
- Load/concurrency testing of the appointment-conflict check, which has
  a small race window between reading existing appointments and writing
  a new one
- Encryption at rest for PHI fields

These are documented, not hidden, in `docs/TEST_PLAN.md`.
