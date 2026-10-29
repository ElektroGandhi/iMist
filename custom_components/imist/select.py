"""Mist: off, continuous or interval."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.const import CONF_ADDRESS

from .const import MIST_MODES, UNIQUE_ID_MIST
from .entity import ImistEntity

BYTE_TO_KEY = {byte: key for key, byte in MIST_MODES.items()}


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([ImistMist(entry.runtime_data.device, entry.data[CONF_ADDRESS], UNIQUE_ID_MIST, "mist")])


class ImistMist(ImistEntity, SelectEntity):
    _attr_options = list(MIST_MODES)

    @property
    def current_option(self) -> str | None:
        return BYTE_TO_KEY.get(self.device.mist)

    async def async_select_option(self, option: str) -> None:
        await self.device.set(mist=MIST_MODES[option])
