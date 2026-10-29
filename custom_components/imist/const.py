"""Constants for the iMist aroma diffuser integration.

Everything protocol-related was measured on a real device, see docs/PROTOCOL.md.
"""

DOMAIN = "imist"
VERSION = "0.4.0"

# GATT layout: one vendor service with one characteristic for commands AND state reports
SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
CHAR_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"

# Command and state report share one format: aa MM LL
HEADER = 0xAA

MIST_MODES = {"off": 0x00, "continuous": 0x20, "interval": 0x40}

LIGHT_OFF = 0x00
# key: (byte, RGB for Home Assistant). Order = order of the LIGHT button on the device.
COLORS = {
    "white": (0x08, (255, 255, 255)),
    "red": (0x18, (255, 0, 0)),
    "yellow": (0x30, (255, 255, 0)),
    "green": (0x20, (0, 255, 0)),
    "light_blue": (0x40, (0, 200, 255)),
    "dark_blue": (0x28, (0, 0, 255)),
    "pink": (0x38, (255, 0, 180)),
    "warm_white": (0x48, (255, 236, 210)),
}

# Names used before 0.4.0 (German). Accepted when reading stored schedules.
LEGACY_NAMES = {
    "Weiß": "white", "Rot": "red", "Gelb": "yellow", "Grün": "green", "Hellblau": "light_blue",
    "Dunkelblau": "dark_blue", "Pink": "pink", "Weiß 2": "warm_white",
    "Aus": "off", "Dauer": "continuous", "Intervall": "interval",
}

# Unique-ID suffixes are kept from the first release so existing entities survive updates.
UNIQUE_ID_LIGHT = "licht"
UNIQUE_ID_MIST = "nebel"

RECONNECT_DELAY = 30  # seconds

# Options
CONF_PANEL = "panel"
LEGACY_CONF_PANEL = "seite"

# Sidebar panel and storage
STATIC_URL = "/imist_static"
PANEL_ELEMENT = "imist-panel"
STORE_VERSION = 1
TIMER_MINUTES = (30, 60, 120, 240)
