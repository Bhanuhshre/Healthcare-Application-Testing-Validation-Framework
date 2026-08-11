import os
import sys

import pytest
from pydantic import ValidationError

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "application", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from app.schemas import PatientCreate, UserCreate  # noqa: E402

pytestmark = pytest.mark.unit


def test_patient_create_rejects_blank_name():
    with pytest.raises(ValidationError):
        PatientCreate(
            full_name="   ",
            date_of_birth="1990-01-01",
            contact_number="9876543210",
        )


def test_patient_create_rejects_short_contact_number():
    with pytest.raises(ValidationError):
        PatientCreate(
            full_name="Ravi Kumar",
            date_of_birth="1990-01-01",
            contact_number="12345",
        )


def test_patient_create_accepts_valid_payload():
    patient = PatientCreate(
        full_name="Ravi Kumar",
        date_of_birth="1990-01-01",
        contact_number="9876543210",
    )
    assert patient.full_name == "Ravi Kumar"


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError):
        UserCreate(email="staff@clinic.test", password="short")


def test_user_create_accepts_valid_password():
    user = UserCreate(email="staff@clinic.test", password="longenough1")
    assert user.email == "staff@clinic.test"
