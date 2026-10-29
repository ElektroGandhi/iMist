"""Shared base: one device, state comes from the device itself."""
from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.entity import Entity

from .const import DOMAIN
from .device import ImistDevice


class ImistEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, device: ImistDevice, address: str, unique_suffix: str, translation_key: str) -> None:
        self.device = device
        self._attr_unique_id = f"{address}_{unique_suffix}"
        self._attr_translation_key = translation_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, address)},
            connections={(CONNECTION_BLUETOOTH, address)},
            name="iMist Aroma Diffuser", manufacturer="iMist", model="AromaDiffuser (BLE fff0)")

    @property
    def available(self) -> bool:
        return self.device.connected and self.device.light is not None

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.device.subscribe(self.async_write_ha_state))
