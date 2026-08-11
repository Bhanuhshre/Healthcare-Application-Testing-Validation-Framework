import os
import sys

import pytest

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "application", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from app.core.security import (  # noqa: E402
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)

pytestmark = pytest.mark.unit


def test_hashed_password_does_not_match_plain_text():
    hashed = hash_password("mySecret123")
    assert hashed != "mySecret123"


def test_verify_password_succeeds_for_correct_password():
    hashed = hash_password("mySecret123")
    assert verify_password("mySecret123", hashed) is True


def test_verify_password_fails_for_incorrect_password():
    hashed = hash_password("mySecret123")
    assert verify_password("wrongPassword", hashed) is False


def test_access_token_round_trip():
    token = create_access_token({"sub": "nurse@clinic.test", "role": "staff"})
    payload = decode_access_token(token)
    assert payload["sub"] == "nurse@clinic.test"
    assert payload["role"] == "staff"


def test_decode_rejects_tampered_token():
    token = create_access_token({"sub": "nurse@clinic.test"})
    tampered = token[:-2] + "xx"
    assert decode_access_token(tampered) is None
