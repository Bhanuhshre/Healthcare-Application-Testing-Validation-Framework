# User Acceptance Testing Plan — Clinic Scheduling Application

## 1. Purpose

Automated tests (see `docs/TEST_PLAN.md`) confirm the system behaves
correctly against the requirements as understood by whoever wrote the
code. UAT exists to catch the gap between that and what clinic staff
actually need day to day — wording that is confusing, a workflow that
technically works but is annoying in practice, a rule that is correct on
paper but wrong for how a real front desk operates.

## 2. Participants

- Two front-desk staff members who would use the patient registration and
  appointment booking screens
- One doctor or nurse who would use the schedule view
- One person from whoever owns the release, to record and triage
  findings

Participants should not have written any of the code, and ideally have
not seen the application before the session.

## 3. Environment

UAT runs against a staging deployment seeded with realistic but fake
data (no real patient information), not against a developer's local
machine and not against production. The staging build should be the
exact commit intended for release, built through the same CI pipeline
described in the test plan.

## 4. Scenarios

Each scenario below is given to a participant as a plain task, not as a
script of clicks — the point is to see what they naturally try, not to
verify they can follow instructions.

### Scenario 1 — Register a new patient

"A new patient has just arrived and needs to be added to the system.
Register them using any realistic details."

Watched for: whether the medical record number is visible and makes
sense to the participant, whether required fields are obvious, what
happens if they leave the form half-filled and try to submit.

### Scenario 2 — Handle a duplicate

"Try registering the same patient a second time."

Watched for: whether the resulting error message would actually make
sense to someone who is not a developer, or whether it reads like a raw
API error.

### Scenario 3 — Book an appointment

"Book that patient in for an appointment with any available doctor,
sometime next week."

Watched for: how the participant expects to find or type a time slot,
whether the concept of a doctor's schedule is clear from the UI as it
exists today.

### Scenario 4 — Attempt a conflicting booking

"Try booking a second appointment with the same doctor at a time very
close to the first one."

Watched for: whether the resulting rejection is understandable, and
whether the 30-minute minimum gap enforced by the backend
(`MIN_APPOINTMENT_GAP_MINUTES` in
`application/backend/app/core/scheduling.py`) matches what clinic staff
actually consider a reasonable gap. If it does not, that is a product
decision to revisit, not a bug to fix silently.

### Scenario 5 — Mark a visit complete

"That appointment has now happened. Update its status accordingly."

Watched for: whether the available status options match what staff
actually track (the current set is scheduled, completed, cancelled,
no-show).

## 5. What UAT is not checking

UAT is not the place to catch things like SQL injection, broken
authentication, or race conditions in the booking logic — those belong
in the automated test suite and in a security review. UAT is checking
whether the thing that technically works is actually usable by the
people who will use it every day.

## 6. Recording findings

Each finding is logged with:

- The scenario it came up in
- What the participant expected versus what happened
- A severity: blocks release, should fix before release, worth fixing
  later
- Whether it is a bug (does not match the intended behavior) or a design
  gap (matches intended behavior, but the intended behavior is wrong)

Findings that block release are fixed and re-tested with the same
participant before sign-off, not waved through with a promise to fix
post-release.

## 7. Sign-off

Release proceeds only once every participant has completed all five
scenarios and every "blocks release" finding has been resolved and
re-verified. Sign-off is recorded with the date, the commit hash of the
build tested, and the names of participants — not just a checkbox, so
there is a record of what was actually tested if a defect surfaces
later.
