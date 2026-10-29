"""Schedule rules without Home Assistant imports (so they can be tested on their own)."""
from __future__ import annotations

import re
from datetime import datetime

from .const import COLORS, LEGACY_NAMES, MIST_MODES

TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def validate(entry: dict) -> dict:
    """Check one schedule coming from the panel and keep only known fields.

    Days are 0 (Monday) to 6 (Sunday). Names from releases before 0.4.0 are accepted.
    """
    days = sorted({int(d) for d in entry.get("days", entry.get("tage", []))})
    if not days or any(d < 0 or d > 6 for d in days):
        raise ValueError("days: 0 (Mon) to 6 (Sun), at least one")
    start = str(entry.get("start", entry.get("von", "")))
    end = str(entry.get("end", entry.get("bis", "")))
    for name, value in (("start", start), ("end", end)):
        if not TIME.match(value):
            raise ValueError(f"{name}: time as HH:MM")
    if start == end:
        raise ValueError("start and end are equal")
    light = entry.get("light", entry.get("licht"))
    light = LEGACY_NAMES.get(light, light)
    if light not in COLORS and light != "off":
        raise ValueError("light: unknown color")
    mist = entry.get("mist", entry.get("nebel"))
    mist = LEGACY_NAMES.get(mist, mist)
    if mist not in MIST_MODES:
        raise ValueError("mist: off, continuous or interval")
    return {"days": days, "start": start, "end": end, "light": light, "mist": mist,
            "enabled": bool(entry.get("enabled", entry.get("an", True)))}


def due(schedules: list[dict], now: datetime) -> tuple[str, dict] | None:
    """What to do in this minute: ("on", schedule), ("off", schedule) or None.

    A schedule across midnight (end < start) ends on the following day; then the
    day it started counts. If one schedule ends in the same minute another one
    starts, the start wins.
    """
    day, clock = now.weekday(), now.strftime("%H:%M")
    off = None
    for s in schedules:
        if not s.get("enabled"):
            continue
        if s["start"] == clock and day in s["days"]:
            return "on", s
        if s["end"] == clock:
            start_day = day if s["end"] > s["start"] else (day - 1) % 7
            if start_day in s["days"]:
                off = ("off", s)
    return off
