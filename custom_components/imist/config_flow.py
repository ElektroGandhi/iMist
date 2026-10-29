"""Setup via Bluetooth discovery or by picking from the list; options for the panel."""
from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak, async_discovered_service_info
from homeassistant.config_entries import ConfigEntry, ConfigFlow, ConfigFlowResult, OptionsFlow
from homeassistant.const import CONF_ADDRESS
from homeassistant.core import callback

from .const import CONF_PANEL, DOMAIN, LEGACY_CONF_PANEL, SERVICE_UUID

NAME = "AromaDiffuser"


def _title(address: str) -> str:
    return f"iMist {address[-5:]}"


class ImistConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._discovery: BluetoothServiceInfoBleak | None = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return ImistOptionsFlow()

    async def async_step_bluetooth(self, discovery_info: BluetoothServiceInfoBleak) -> ConfigFlowResult:
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        self._discovery = discovery_info
        self.context["title_placeholders"] = {"name": discovery_info.name or NAME}
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        assert self._discovery is not None
        if user_input is not None:
            return self.async_create_entry(title=_title(self._discovery.address),
                                           data={CONF_ADDRESS: self._discovery.address})
        self._set_confirm_only()
        return self.async_show_form(
            step_id="bluetooth_confirm",
            description_placeholders={"name": self._discovery.name or NAME,
                                      "address": self._discovery.address})

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=_title(address), data={CONF_ADDRESS: address})
        configured = self._async_current_ids(include_ignore=False)
        found = {
            info.address: f"{info.name} ({info.address})"
            for info in async_discovered_service_info(self.hass, connectable=True)
            if info.name == NAME and SERVICE_UUID in info.service_uuids and info.address not in configured
        }
        if not found:
            return self.async_abort(reason="no_devices_found")
        return self.async_show_form(
            step_id="user", data_schema=vol.Schema({vol.Required(CONF_ADDRESS): vol.In(found)}))


class ImistOptionsFlow(OptionsFlow):
    """Show or hide the sidebar panel."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        current = self.config_entry.options.get(CONF_PANEL, self.config_entry.options.get(LEGACY_CONF_PANEL, False))
        return self.async_show_form(step_id="init", data_schema=vol.Schema({
            vol.Required(CONF_PANEL, default=current): bool,
        }))
