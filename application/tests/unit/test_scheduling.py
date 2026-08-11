import os
import sys
from datetime import datetime, timedelta

import pytest

BACKEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "application", "backend")
sys.path.insert(0, os.path.abspath(BACKEND_DIR))

from app.core.scheduling import has_conflict, is_in_the_past  # noqa: E402

pytestmark = pytest.mark.unit


def test_no_conflict_when_no_existing_appointments():
    assert has_conflict(datetime(2026, 1, 1, 10, 0), []) is False


def test_conflict_when_within_default_gap():
    existing = [datetime(2026, 1, 1, 10, 0)]
    new_time = datetime(2026, 1, 1, 10, 15)  # 15 minutes later, gap is 30
    assert has_conflict(new_time, existing) is True


def test_no_conflict_when_outside_default_gap():
    existing = [datetime(2026, 1, 1, 10, 0)]
    new_time = datetime(2026, 1, 1, 10, 45)  # 45 minutes later
    assert has_conflict(new_time, existing) is False


def test_conflict_respects_custom_gap():
    existing = [datetime(2026, 1, 1, 10, 0)]
    new_time = datetime(2026, 1, 1, 10, 45)
    assert has_conflict(new_time, existing, gap_minutes=60) is True


def test_is_in_the_past_true_for_earlier_time():
    now = datetime(2026, 6, 1, 12, 0)
    earlier = now - timedelta(hours=1)
    assert is_in_the_past(earlier, now=now) is True


def test_is_in_the_past_false_for_future_time():
    now = datetime(2026, 6, 1, 12, 0)
    later = now + timedelta(hours=1)
    assert is_in_the_past(later, now=now) is False
