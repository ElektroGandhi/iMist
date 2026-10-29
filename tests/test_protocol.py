"""Frames and reports exactly as measured on the device (docs/PROTOCOL.md)."""
import pytest

from imist.const import COLORS, MIST_MODES
from imist.device import ImistDevice
from imist.protocol import frame, nearest_color, parse_reports


@pytest.mark.parametrize(("mist", "light", "expected"), [
    ("off", "red", "aa 00 18"),
    ("interval", "dark_blue", "aa 40 28"),
    ("continuous", None, "aa 20 00"),
])
def test_frame(mist, light, expected):
    light_byte = COLORS[light][0] if light else 0
    assert frame(MIST_MODES[mist], light_byte).hex(" ") == expected


def test_parse_single_report():
    assert parse_reports(bytes.fromhex("aa0018")) == [(0x00, 0x18)]


def test_parse_glued_reports():
    assert parse_reports(bytes.fromhex("aa0018aa0030")) == [(0x00, 0x18), (0x00, 0x30)]


def test_zero_block_from_read_is_not_a_report():
    assert parse_reports(bytes(20)) == []


@pytest.mark.parametrize(("rgb", "key"), [
    ((250, 10, 10), "red"), ((0, 0, 200), "dark_blue"), ((20, 210, 240), "light_blue"), ((255, 255, 255), "white"),
])
def test_nearest_color(rgb, key):
    assert nearest_color(rgb) == key


def test_color_bytes_are_unique():
    bytes_ = [b for b, _ in COLORS.values()]
    assert len(bytes_) == len(set(bytes_)) == 8


def test_diagnostics_never_shadow_status_fields():
    # 0.3.0 shipped a bug where diagnostics overwrote light/mist entity ids in the status
    status_fields = {"title", "address", "version", "rssi", "light_entity", "mist_entity",
                     "timer_end", "timer_minutes", "schedules"}
    assert not status_fields & set(ImistDevice(None).diagnostics())
