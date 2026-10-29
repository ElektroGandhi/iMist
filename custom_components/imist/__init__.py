"""iMist aroma diffuser over Bluetooth Low Energy."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from homeassistant.components import bluetooth, frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import CONF_PANEL, DOMAIN, LEGACY_CONF_PANEL, PANEL_ELEMENT, STATIC_URL, VERSION
from .device import ImistDevice
from .scheduler import Scheduler
from .websocket import async_register

PLATFORMS = [Platform.LIGHT, Platform.SELECT]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


@dataclass
class ImistData:
    device: ImistDevice
    scheduler: Scheduler


type ImistConfigEntry = ConfigEntry[ImistData]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_register(hass)
    await hass.http.async_register_static_paths([
        StaticPathConfig(STATIC_URL, str(Path(__file__).parent / "frontend"), cache_headers=False)])
    return True


def _panel_path(entry: ConfigEntry) -> str:
    return f"imist-{entry.entry_id[-6:].lower()}"


def panel_enabled(entry: ConfigEntry) -> bool:
    return entry.options.get(CONF_PANEL, entry.options.get(LEGACY_CONF_PANEL, False))


async def async_setup_entry(hass: HomeAssistant, entry: ImistConfigEntry) -> bool:
    address = entry.data[CONF_ADDRESS].upper()
    # Not in range is not an error: entities stay unavailable until the device shows up.
    device = ImistDevice(bluetooth.async_ble_device_from_address(hass, address, connectable=True))
    scheduler = Scheduler(hass, entry.entry_id, device)
    entry.runtime_data = ImistData(device, scheduler)

    @callback
    def _seen(info: bluetooth.BluetoothServiceInfoBleak, _change) -> None:
        device.seen(info.device)

    entry.async_on_unload(bluetooth.async_register_callback(
        hass, _seen, {"address": address, "connectable": True},
        bluetooth.BluetoothScanningMode.PASSIVE))

    await scheduler.start()
    entry.async_on_unload(scheduler.stop)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_create_background_task(hass, device.start(), "imist_connect")

    if panel_enabled(entry):
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=_panel_path(entry),
            webcomponent_name=PANEL_ELEMENT,
            module_url=f"{STATIC_URL}/imist-panel.js?v={VERSION}",
            sidebar_title="Diffusor" if hass.config.language.startswith("de") else "Diffuser",
            sidebar_icon="mdi:weather-fog",
            config={"entry_id": entry.entry_id},
            require_admin=False,
        )
        entry.async_on_unload(lambda: frontend.async_remove_panel(hass, _panel_path(entry)))

    entry.async_on_unload(entry.add_update_listener(_options_updated))
    return True


async def _options_updated(hass: HomeAssistant, entry: ImistConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ImistConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        await entry.runtime_data.device.stop()
    return ok
