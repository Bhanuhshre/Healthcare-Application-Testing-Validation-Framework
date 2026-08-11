# Test Plan — Clinic Scheduling Application

## 1. Purpose and scope

This document describes how the clinic scheduling application is tested
before a release. It covers the patient records API, doctor roster API,
appointment scheduling API, authentication, and the frontend that
consumes these APIs. It does not cover infrastructure provisioning or
database backup procedures, which are handled separately by whoever owns
deployment for a given environment.

## 2. What this application does

The system lets clinic staff register patients, maintain a roster of
doctors, and book, view, and update appointments. Access to patient data
requires authentication, and write operations are restricted by role
(admin, staff, doctor). A more complete description of the domain rules
is in the code itself (see `application/backend/app/core/scheduling.py`
and `app/core/mrn.py`), since keeping rules in one place and documenting
their intent there is more reliable than duplicating logic into prose
that can drift out of date.

## 3. Test levels

### 3.1 Unit tests (`tests/unit/`)

These test pure logic with no database, no HTTP layer, and no network
access:

- Medical record number (MRN) generation and formatting
- Appointment conflict detection (the minimum-gap rule between two
  appointments for the same doctor)
- Password hashing and JWT creation/verification, including rejection of
  a tampered token
- Pydantic schema validation rules (blank names, malformed contact
  numbers, weak passwords)

Unit tests are expected to run in well under a second each and are the
first thing run in CI, since a failure here means something is broken at
the logic level before any API or database concern is even involved.

### 3.2 API tests (`tests/api/`)

These exercise real HTTP requests against the FastAPI app through
`TestClient`, backed by an isolated in-memory SQLite database per test
(see `tests/conftest.py`). They cover:

- Registration and login, including duplicate-email rejection and wrong
  password rejection
- That protected endpoints reject unauthenticated requests
- Patient CRUD: creation (with MRN assignment), duplicate email
  rejection, invalid contact number rejection, retrieval, update,
  deletion, and the 404 case for a patient that does not exist
- Appointment booking: successful booking, rejection of past-dated
  appointments, rejection of appointments for a patient or doctor that
  does not exist, rejection of a conflicting time slot for the same
  doctor, status updates, and filtering by patient or doctor

### 3.3 End-to-end tests (`tests/e2e/`)

The E2E suite in this repository walks through the same sequence of
actions a front-desk staff member performs — log in, add a doctor,
register a patient, book an appointment, confirm it shows up on the
doctor's schedule, mark it complete — as a single test, run through the
API layer via `TestClient`. This is intentionally not a browser test: it
is fast enough to run on every commit and still validates that the
pieces work together correctly, not just in isolation.

A separate, browser-driven version of the same scenario using Playwright
against a deployed staging build is planned but not yet implemented in
this repository. That version would additionally cover things an
API-level test cannot: whether the login form actually renders, whether
a validation error from the API is displayed to the user, and whether
the patient table updates after a successful registration. Until that
exists, frontend behavior is currently verified manually before each
release (see Section 5).

### 3.4 What is intentionally not covered yet

- Load and concurrency testing (what happens if two staff members try to
  book the same slot for the same doctor at the same moment — the
  conflict check as written has a small race window between the read and
  the write)
- Browser-based frontend tests (see 3.3)
- Accessibility testing of the frontend
- PHI-specific security testing (encryption at rest, audit logging of who
  accessed which patient record) — the current models store PHI fields
  as plain columns, which is called out in
  `application/backend/app/database/models.py` as a known gap for a
  demonstration project rather than something safe to ship as-is

## 4. Test data strategy

API and E2E tests create their own data at the start of each test rather
than relying on shared fixtures or a seeded database, so tests can run in
any order and in parallel without interfering with each other. Test
emails use the `.test` top-level domain reserved for this purpose under
RFC 2606. Because of that, email format is validated with a plain regex
rather than `pydantic`'s `EmailStr`, which by default performs DNS/MX
lookups and rejects reserved test domains — both wrong for a test suite
that needs to run identically offline and in CI.

## 5. Manual verification before release

Until the Playwright suite described in 3.3 exists, the following is
checked by hand against a locally running frontend and backend before
tagging a release:

1. Load the app while logged out — confirm the login form appears and
   the patient table is not reachable.
2. Log in with valid and then invalid credentials — confirm success and
   failure states both display correctly.
3. Register a patient with a full form — confirm it appears in the table
   without a page reload.
4. Attempt to register a patient with a contact number under 10 digits —
   confirm the API's rejection is surfaced to the user, not swallowed.
5. Confirm the browser console has no errors during the above steps.

## 6. Running the suite locally

```
pip install -r requirements.txt
pytest                              # full suite
pytest -m unit                      # unit tests only
pytest -m api                       # API tests only
pytest -m e2e                       # end-to-end tests only
pytest --cov=application/backend/app --cov-report=term-missing
```

## 7. Continuous integration

`.github/workflows/tests.yml` runs on every push and pull request against
`main`. It lints the backend with `flake8`, runs each test tier
separately (so a failure is easy to attribute to a level), then runs the
full suite again with coverage enforcement at a minimum of 85%. It
separately builds the frontend to confirm it compiles, since a broken
frontend build should fail CI even if no test explicitly covers it yet.
