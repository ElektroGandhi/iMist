"""Diagnostics download (Settings → Devices → iMist → Download diagnostics)."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .websocket import status


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry) -> dict[str, Any]:
    data = status(hass, entry)
    data["address"] = data["address"][:8] + ":xx:xx:xx"
    data["options"] = dict(entry.options)
    return data
