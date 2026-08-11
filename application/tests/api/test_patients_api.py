import pytest

pytestmark = pytest.mark.api


def create_sample_patient(client, headers, **overrides):
    payload = {
        "full_name": "Lakshmi Nair",
        "date_of_birth": "1992-04-15T00:00:00",
        "contact_number": "9876543210",
        "email": "lakshmi.nair@example.test",
    }
    payload.update(overrides)
    return client.post("/api/patients", json=payload, headers=headers)


def test_create_patient_assigns_mrn(client, admin_headers):
    response = create_sample_patient(client, admin_headers)
    assert response.status_code == 201
    body = response.json()
    assert body["medical_record_number"].startswith("MRN-")
    assert body["full_name"] == "Lakshmi Nair"


def test_create_patient_rejects_duplicate_email(client, admin_headers):
    create_sample_patient(client, admin_headers)
    response = create_sample_patient(client, admin_headers, full_name="Another Person")
    assert response.status_code == 400


def test_create_patient_rejects_invalid_contact_number(client, admin_headers):
    response = create_sample_patient(client, admin_headers, contact_number="123")
    assert response.status_code == 422


def test_list_patients_returns_created_patient(client, admin_headers):
    create_sample_patient(client, admin_headers)
    response = client.get("/api/patients", headers=admin_headers)
    assert response.status_code == 200
    names = [p["full_name"] for p in response.json()]
    assert "Lakshmi Nair" in names


def test_get_patient_by_id(client, admin_headers):
    created = create_sample_patient(client, admin_headers).json()
    response = client.get(f"/api/patients/{created['id']}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_nonexistent_patient_returns_404(client, admin_headers):
    response = client.get("/api/patients/999999", headers=admin_headers)
    assert response.status_code == 404


def test_update_patient_contact_number(client, admin_headers):
    created = create_sample_patient(client, admin_headers).json()
    response = client.patch(
        f"/api/patients/{created['id']}",
        json={"contact_number": "9123456780"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["contact_number"] == "9123456780"


def test_delete_patient(client, admin_headers):
    created = create_sample_patient(client, admin_headers).json()
    delete_response = client.delete(f"/api/patients/{created['id']}", headers=admin_headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/api/patients/{created['id']}", headers=admin_headers)
    assert get_response.status_code == 404
