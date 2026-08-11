from datetime import timedelta

import pytest

pytestmark = pytest.mark.api


def register_patient(client, headers):
    payload = {
        "full_name": "Karthik Reddy",
        "date_of_birth": "1988-09-01T00:00:00",
        "contact_number": "9988776655",
    }
    return client.post("/api/patients", json=payload, headers=headers).json()


def test_create_appointment_succeeds(client, admin_headers, sample_doctor, future_datetime):
    patient = register_patient(client, admin_headers)
    response = client.post(
        "/api/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": sample_doctor.id,
            "scheduled_at": future_datetime.isoformat(),
            "reason": "Routine checkup",
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    assert response.json()["status"] == "scheduled"


def test_create_appointment_rejects_past_datetime(client, admin_headers, sample_doctor):
    patient = register_patient(client, admin_headers)
    response = client.post(
        "/api/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": sample_doctor.id,
            "scheduled_at": "2020-01-01T09:00:00",
        },
        headers=admin_headers,
    )
    assert response.status_code == 400


def test_create_appointment_rejects_unknown_patient(client, admin_headers, sample_doctor, future_datetime):
    response = client.post(
        "/api/appointments",
        json={
            "patient_id": 999999,
            "doctor_id": sample_doctor.id,
            "scheduled_at": future_datetime.isoformat(),
        },
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_create_appointment_rejects_conflicting_slot(client, admin_headers, sample_doctor, future_datetime):
    patient = register_patient(client, admin_headers)
    first = client.post(
        "/api/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": sample_doctor.id,
            "scheduled_at": future_datetime.isoformat(),
        },
        headers=admin_headers,
    )
    assert first.status_code == 201

    conflicting_time = future_datetime + timedelta(minutes=10)
    second = client.post(
        "/api/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": sample_doctor.id,
            "scheduled_at": conflicting_time.isoformat(),
        },
        headers=admin_headers,
    )
    assert second.status_code == 409


def test_update_appointment_status(client, admin_headers, sample_doctor, future_datetime):
    patient = register_patient(client, admin_headers)
    created = client.post(
        "/api/appointments",
        json={
            "patient_id": patient["id"],
            "doctor_id": sample_doctor.id,
            "scheduled_at": future_datetime.isoformat(),
        },
        headers=admin_headers,
    ).json()

    response = client.patch(
        f"/api/appointments/{created['id']}/status",
        json={"status": "completed"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


def test_list_appointments_filters_by_patient(client, admin_headers, sample_doctor, future_datetime):
    patient_a = register_patient(client, admin_headers)
    patient_b = client.post(
        "/api/patients",
        json={
            "full_name": "Meera Iyer",
            "date_of_birth": "1995-02-10T00:00:00",
            "contact_number": "9000011122",
        },
        headers=admin_headers,
    ).json()

    client.post(
        "/api/appointments",
        json={
            "patient_id": patient_a["id"],
            "doctor_id": sample_doctor.id,
            "scheduled_at": future_datetime.isoformat(),
        },
        headers=admin_headers,
    )
    client.post(
        "/api/appointments",
        json={
            "patient_id": patient_b["id"],
            "doctor_id": sample_doctor.id,
            "scheduled_at": (future_datetime + timedelta(hours=2)).isoformat(),
        },
        headers=admin_headers,
    )

    response = client.get(
        "/api/appointments", params={"patient_id": patient_a["id"]}, headers=admin_headers
    )
    results = response.json()
    assert len(results) == 1
    assert results[0]["patient_id"] == patient_a["id"]
