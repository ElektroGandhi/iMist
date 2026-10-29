"""Sleep timer and weekly schedules.

Both run in Home Assistant, not on the device: the diffuser has no clock.
They are stored per device in .storage/imist.<entry_id> and survive restarts.
"""
from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_point_in_time, async_track_time_change
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from .const import COLORS, LIGHT_OFF, MIST_MODES, STORE_VERSION
from .device import ImistDevice
from .schedule import due, validate

_LOGGER = logging.getLogger(__name__)


class Scheduler:
    def __init__(self, hass: HomeAssistant, entry_id: str, device: ImistDevice) -> None:
        self.hass = hass
        self.device = device
        self._store: Store[dict] = Store(hass, STORE_VERSION, f"imist.{entry_id}")
        self.schedules: list[dict] = []
        self.timer_end: datetime | None = None
        self._timer_unsub: Callable[[], None] | None = None
        self._minute_unsub: Callable[[], None] | None = None

    async def start(self) -> None:
        data = await self._store.async_load() or {}
        stored = data.get("schedules", data.get("plaene", []))
        self.schedules = [validate(s) for s in stored]
        stored_end = data.get("timer_end", data.get("timer_ende"))
        end = dt_util.parse_datetime(stored_end) if stored_end else None
        if end and end > dt_util.utcnow():
            self._arm_timer(end)
        self._minute_unsub = async_track_time_change(self.hass, self._each_minute, second=0)

    def stop(self) -> None:
        for unsub in (self._minute_unsub, self._timer_unsub):
            if unsub:
                unsub()
        self._minute_unsub = self._timer_unsub = None

    def _save(self) -> None:
        self._store.async_delay_save(lambda: {
            "schedules": self.schedules,
            "timer_end": self.timer_end.isoformat() if self.timer_end else None,
        }, 1)

    # ---------- schedules ----------
    def set_schedules(self, schedules: list[dict]) -> None:
        self.schedules = [validate(s) for s in schedules]
        self._save()

    async def _each_minute(self, now: datetime) -> None:
        action = due(self.schedules, dt_util.as_local(now))
        if not action:
            return
        kind, s = action
        try:
            if kind == "on":
                light = LIGHT_OFF if s["light"] == "off" else COLORS[s["light"]][0]
                await self.device.set(mist=MIST_MODES[s["mist"]], light=light)
            else:
                await self.device.set(mist=MIST_MODES["off"], light=LIGHT_OFF)
            _LOGGER.info("Schedule %s–%s: %s", s["start"], s["end"], kind)
        except Exception as err:
            _LOGGER.warning("Schedule %s–%s (%s) not executed: %s", s["start"], s["end"], kind, err)

    # ---------- sleep timer ----------
    def set_timer(self, minutes: int | None) -> None:
        if self._timer_unsub:
            self._timer_unsub()
            self._timer_unsub = None
        self.timer_end = None
        if minutes:
            self._arm_timer(dt_util.utcnow() + timedelta(minutes=minutes))
        self._save()

    def _arm_timer(self, end: datetime) -> None:
        self.timer_end = end
        self._timer_unsub = async_track_point_in_time(self.hass, self._timer_expired, end)

    @callback
    def _timer_expired(self, _now: datetime) -> None:
        self._timer_unsub = None
        self.timer_end = None
        self._save()
        self.hass.async_create_task(self._switch_off())

    async def _switch_off(self) -> None:
        try:
            await self.device.set(mist=MIST_MODES["off"], light=LIGHT_OFF)
            _LOGGER.info("Sleep timer expired: off")
        except Exception as err:
            _LOGGER.warning("Sleep timer: switching off failed: %s", err)
