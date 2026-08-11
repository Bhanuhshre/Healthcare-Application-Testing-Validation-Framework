"""
End-to-end workflow test.

This walks through the same sequence of actions a front-desk staff member
would perform in the UI: log in, add a doctor, register a patient, book an
appointment, and mark it complete after the visit. It runs against the
API layer through FastAPI's TestClient rather than a real browser, which
keeps it fast enough to run on every commit.

A browser-driven version of this same scenario (using Playwright against
a deployed staging build) is described in docs/TEST_PLAN.md and is what
would run before a release, not on every commit.
"""

from datetime import datetime, timedelta

import pytest

pytestmark = pytest.mark.e2e


def test_full_clinic_workflow(client):
    # 1. An administrator account is created and logs in.
    client.post(
        "/api/auth/register",
        json={"email": "frontdesk@clinic.test", "password": "supersecure1", "role": "admin"},
    )
    login_response = client.post(
        "/api/auth/login",
        data={"username": "frontdesk@clinic.test", "password": "supersecure1"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. A doctor is added to the roster.
    doctor_response = client.post(
        "/api/doctors",
        json={
            "full_name": "Dr. Priya Menon",
            "specialty": "Family Medicine",
            "email": "priya.menon@clinic.test",
        },
        headers=headers,
    )
    assert doctor_response.status_code == 201
    doctor_id = doctor_response.json()["id"]

    # 3. A new patient walks in and is registered.
    patient_response = client.post(
        "/api/patients",
        json={
            "full_name": "Anjali Verma",
            "date_of_birth": "1994-03-22T00:00:00",
            "contact_number": "9812345670",
            "email": "anjali.verma@example.test",
        },
        headers=headers,
    )
    assert patient_response.status_code == 201
    patient = patient_response.json()
    assert patient["medical_record_number"].startswith("MRN-")

    # 4. The patient is booked in for a same-week appointment.
    scheduled_at = datetime.utcnow() + timedelta(days=2)
    appointment_response = client.post(
        "/api/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": doctor_id,
            "scheduled_at": scheduled_at.isoformat(),
            "reason": "Annual physical",
        },
        headers=headers,
    )
    assert appointment_response.status_code == 201
    appointment = appointment_response.json()
    assert appointment["status"] == "scheduled"

    # 5. The appointment shows up when the doctor's schedule is queried.
    schedule_response = client.get(
        "/api/appointments", params={"doctor_id": doctor_id}, headers=headers
    )
    assert any(a["id"] == appointment["id"] for a in schedule_response.json())

    # 6. After the visit, front desk marks the appointment as completed.
    completion_response = client.patch(
        f"/api/appointments/{appointment['id']}/status",
        json={"status": "completed"},
        headers=headers,
    )
    assert completion_response.status_code == 200
    assert completion_response.json()["status"] == "completed"

    # 7. The patient record still resolves correctly after the visit.
    final_patient_check = client.get(f"/api/patients/{patient['id']}", headers=headers)
    assert final_patient_check.status_code == 200
    assert final_patient_check.json()["full_name"] == "Anjali Verma"


def test_unauthenticated_user_cannot_touch_patient_data(client):
    """A logged-out visitor should never be able to reach patient records."""
    response = client.get("/api/patients")
    assert response.status_code == 401

    response = client.post(
        "/api/patients",
        json={
            "full_name": "Should Not Save",
            "date_of_birth": "1990-01-01T00:00:00",
            "contact_number": "9000000000",
        },
    )
    assert response.status_code == 401
