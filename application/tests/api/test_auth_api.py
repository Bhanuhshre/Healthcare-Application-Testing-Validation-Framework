import pytest

pytestmark = pytest.mark.api


def test_register_creates_user(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "newstaff@clinic.test", "password": "supersecure1", "role": "staff"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newstaff@clinic.test"


def test_register_rejects_duplicate_email(client):
    payload = {"email": "dupe@clinic.test", "password": "supersecure1", "role": "staff"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400


def test_login_succeeds_with_correct_credentials(client):
    client.post(
        "/api/auth/register",
        json={"email": "login@clinic.test", "password": "supersecure1", "role": "staff"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "login@clinic.test", "password": "supersecure1"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_fails_with_wrong_password(client):
    client.post(
        "/api/auth/register",
        json={"email": "login2@clinic.test", "password": "supersecure1", "role": "staff"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "login2@clinic.test", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_patients_endpoint_requires_authentication(client):
    response = client.get("/api/patients")
    assert response.status_code == 401

