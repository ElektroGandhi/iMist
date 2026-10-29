"""Websocket commands for the sidebar panel: status, sleep timer, schedules."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import bluetooth, websocket_api
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, TIMER_MINUTES, VERSION


def status(hass: HomeAssistant, entry) -> dict[str, Any]:
    data = entry.runtime_data
    address = entry.data[CONF_ADDRESS]
    info = bluetooth.async_last_service_info(hass, address.upper(), connectable=True)
    entities = {e.entity_id.split(".")[0]: e.entity_id
                for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)}
    return {
        # device diagnostics first: its keys must never overwrite the fields below
        **data.device.diagnostics(),
        "title": entry.title,
        "address": address,
        "version": VERSION,
        "rssi": info.rssi if info else None,
        "light_entity": entities.get("light"),
        "mist_entity": entities.get("select"),
        "timer_end": data.scheduler.timer_end.isoformat() if data.scheduler.timer_end else None,
        "timer_minutes": list(TIMER_MINUTES),
        "schedules": data.scheduler.schedules,
    }


def _entry(hass: HomeAssistant, connection, msg):
    entry = hass.config_entries.async_get_entry(msg["entry_id"])
    if entry is None or entry.domain != DOMAIN or not hasattr(entry, "runtime_data"):
        connection.send_error(msg["id"], "not_found", "Device not found or not loaded")
        return None
    return entry


@callback
def async_register(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_status)
    websocket_api.async_register_command(hass, ws_timer)
    websocket_api.async_register_command(hass, ws_schedules)


@websocket_api.websocket_command({vol.Required("type"): "imist/status", vol.Required("entry_id"): str})
@callback
def ws_status(hass, connection, msg):
    if entry := _entry(hass, connection, msg):
        connection.send_result(msg["id"], status(hass, entry))


@websocket_api.websocket_command({
    vol.Required("type"): "imist/timer", vol.Required("entry_id"): str,
    vol.Required("minutes"): vol.Any(None, vol.All(int, vol.Range(min=1, max=24 * 60))),
})
@callback
def ws_timer(hass, connection, msg):
    if entry := _entry(hass, connection, msg):
        entry.runtime_data.scheduler.set_timer(msg["minutes"])
        connection.send_result(msg["id"], status(hass, entry))


@websocket_api.websocket_command({
    vol.Required("type"): "imist/schedules", vol.Required("entry_id"): str,
    vol.Required("schedules"): [dict],
})
@callback
def ws_schedules(hass, connection, msg):
    if entry := _entry(hass, connection, msg):
        try:
            entry.runtime_data.scheduler.set_schedules(msg["schedules"])
        except (ValueError, KeyError, TypeError) as err:
            connection.send_error(msg["id"], "invalid_format", str(err))
            return
        connection.send_result(msg["id"], status(hass, entry))
