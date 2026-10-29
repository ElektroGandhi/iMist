"""Schedule validation and which action is due when (including across midnight)."""
from datetime import datetime

import pytest

from imist.schedule import due, validate

GOOD = {"days": [0, 1, 2, 3, 4], "start": "07:00", "end": "07:30", "light": "dark_blue", "mist": "interval"}
MONDAY = lambda hm: datetime(2026, 11, 2, *map(int, hm.split(":")))
SATURDAY = lambda hm: datetime(2026, 11, 7, *map(int, hm.split(":")))


def test_enabled_by_default():
    assert validate(GOOD)["enabled"] is True


def test_days_sorted_and_deduplicated():
    assert validate({**GOOD, "days": [4, 0, 0]})["days"] == [0, 4]


def test_light_off_allowed():
    assert validate({**GOOD, "light": "off"})["light"] == "off"


def test_unknown_fields_dropped():
    assert "x" not in validate({**GOOD, "x": 1})


def test_legacy_german_schedule_is_migrated():
    old = {"tage": [0], "von": "07:00", "bis": "07:30", "licht": "Dunkelblau", "nebel": "Intervall", "an": False}
    assert validate(old) == {"days": [0], "start": "07:00", "end": "07:30", "light": "dark_blue", "mist": "interval", "enabled": False}


@pytest.mark.parametrize("bad", [
    {"days": []}, {"days": [7]}, {"start": "24:00"}, {"start": "7:00"}, {"end": "07:00"},
    {"light": "purple"}, {"mist": "strong"},
])
def test_rejects(bad):
    with pytest.raises(ValueError):
        validate({**GOOD, **bad})


def test_due_on_and_off():
    plans = [validate(GOOD)]
    assert due(plans, MONDAY("07:00"))[0] == "on"
    assert due(plans, MONDAY("07:30"))[0] == "off"
    assert due(plans, MONDAY("07:01")) is None
    assert due(plans, SATURDAY("07:00")) is None


def test_paused_schedule_does_nothing():
    assert due([{**validate(GOOD), "enabled": False}], MONDAY("07:00")) is None


def test_across_midnight_ends_next_day():
    friday_night = [validate({**GOOD, "days": [4], "start": "23:00", "end": "01:00"})]
    assert due(friday_night, datetime(2026, 11, 6, 23, 0))[0] == "on"
    assert due(friday_night, SATURDAY("01:00"))[0] == "off"
    assert due(friday_night, datetime(2026, 11, 6, 1, 0)) is None


def test_start_wins_over_end_in_same_minute():
    chain = [validate({**GOOD, "start": "07:00", "end": "08:00"}),
             validate({**GOOD, "start": "08:00", "end": "09:00", "light": "red"})]
    assert due(chain, MONDAY("08:00"))[0] == "on"
