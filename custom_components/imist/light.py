"""Light: the device has eight fixed colors. Any HA color is mapped to the nearest one."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_EFFECT, ATTR_RGB_COLOR, ColorMode, LightEntity, LightEntityFeature
from homeassistant.const import CONF_ADDRESS

from .const import COLORS, LIGHT_OFF, UNIQUE_ID_LIGHT
from .entity import ImistEntity
from .protocol import nearest_color

KEY_TO_BYTE = {key: byte for key, (byte, _) in COLORS.items()}
BYTE_TO_KEY = {byte: key for key, byte in KEY_TO_BYTE.items()}


async def async_setup_entry(hass, entry, async_add_entities) -> None:
    async_add_entities([ImistLight(entry.runtime_data.device, entry.data[CONF_ADDRESS], UNIQUE_ID_LIGHT, "light")])


class ImistLight(ImistEntity, LightEntity):
    _attr_color_mode = ColorMode.RGB
    _attr_supported_color_modes = {ColorMode.RGB}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = list(COLORS)

    @property
    def is_on(self) -> bool | None:
        if self.device.light is None:
            return None
        return self.device.light != LIGHT_OFF

    @property
    def effect(self) -> str | None:
        return BYTE_TO_KEY.get(self.device.light)

    @property
    def rgb_color(self) -> tuple[int, int, int] | None:
        key = BYTE_TO_KEY.get(self.device.light) or BYTE_TO_KEY.get(self.device.last_color)
        return COLORS[key][1] if key else None

    async def async_turn_on(self, **kwargs: Any) -> None:
        if kwargs.get(ATTR_EFFECT) in KEY_TO_BYTE:
            byte = KEY_TO_BYTE[kwargs[ATTR_EFFECT]]
        elif ATTR_RGB_COLOR in kwargs:
            byte = KEY_TO_BYTE[nearest_color(tuple(kwargs[ATTR_RGB_COLOR]))]
        else:
            byte = self.device.last_color
        await self.device.set(light=byte)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.device.set(light=LIGHT_OFF)
