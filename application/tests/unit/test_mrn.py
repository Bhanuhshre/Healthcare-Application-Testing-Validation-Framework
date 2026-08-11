import os
import sys

import pytest

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "application", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from app.core.mrn import generate_mrn  # noqa: E402

pytestmark = pytest.mark.unit


def test_generate_mrn_pads_sequence_to_five_digits():
    assert generate_mrn(sequence=1, year=2026) == "MRN-2026-00001"


def test_generate_mrn_handles_large_sequence():
    assert generate_mrn(sequence=123456, year=2026) == "MRN-2026-123456"


def test_generate_mrn_defaults_to_current_year():
    from datetime import datetime

    mrn = generate_mrn(sequence=7)
    assert mrn.startswith(f"MRN-{datetime.utcnow().year}-")


def test_generate_mrn_rejects_negative_sequence():
    with pytest.raises(ValueError):
        generate_mrn(sequence=-1)
