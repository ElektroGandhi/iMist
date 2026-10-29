"""Bluetooth connection to the diffuser.

The device reports its state about ten times per second, so the connection is
kept open and Home Assistant always shows the real state, including button
presses on the device itself.
"""
from __future__ import annotations

import asyncio
import logging
import time
from collections import deque
from collections.abc import Callable
from datetime import datetime, timezone

from bleak.backends.device import BLEDevice
from bleak_retry_connector import BleakClientWithServiceCache, establish_connection

from .const import CHAR_UUID, COLORS, MIST_MODES, RECONNECT_DELAY, SERVICE_UUID
from .protocol import frame, parse_reports

_LOGGER = logging.getLogger(__name__)


class ImistDevice:
    def __init__(self, ble_device: BLEDevice | None) -> None:
        self.ble_device = ble_device
        self._client: BleakClientWithServiceCache | None = None
        self._lock = asyncio.Lock()
        self._listeners: list[Callable[[], None]] = []
        self._active = True
        self._retry: asyncio.TimerHandle | None = None
        self.mist: int | None = None
        self.light: int | None = None
        self.last_color = COLORS["white"][0]
        # diagnostics
        self.connected_since: datetime | None = None
        self.disconnects: deque[float] = deque(maxlen=200)
        self.last_report: float | None = None  # time.monotonic()
        self.raw: str | None = None
        self.last_error: str | None = None

    @property
    def connected(self) -> bool:
        return self._client is not None and self._client.is_connected

    # ---------- listeners ----------
    def subscribe(self, callback: Callable[[], None]) -> Callable[[], None]:
        self._listeners.append(callback)
        return lambda: self._listeners.remove(callback)

    def _notify(self) -> None:
        for callback in list(self._listeners):
            callback()

    # ---------- connection ----------
    def seen(self, ble_device: BLEDevice) -> None:
        """New advertisement: remember the device and connect if we were waiting for it."""
        first = self.ble_device is None
        self.ble_device = ble_device
        if first and self._active and not self._retry:
            asyncio.get_running_loop().create_task(self.start())

    async def start(self) -> None:
        if self.ble_device is None:
            return
        try:
            async with self._lock:
                await self._connect()
        except Exception as err:  # radio is flaky, try again later
            self.last_error = str(err)
            _LOGGER.debug("Connection failed: %s", err)
            self._schedule_retry()

    async def _connect(self) -> BleakClientWithServiceCache:
        if self.connected:
            return self._client
        if self.ble_device is None:
            raise RuntimeError("Device not in range")
        client = await establish_connection(
            BleakClientWithServiceCache, self.ble_device, self.ble_device.name or "iMist",
            disconnected_callback=self._on_disconnect,
        )
        if client.services.get_service(SERVICE_UUID) is None:
            services = ", ".join(s.uuid for s in client.services)
            await client.disconnect()
            raise RuntimeError(f"Service {SERVICE_UUID} missing. Device offers: {services}")
        await client.start_notify(CHAR_UUID, self._on_report)
        self._client = client
        self.connected_since = datetime.now(timezone.utc)
        self.last_error = None
        self._notify()
        return client

    def _on_disconnect(self, _client) -> None:
        if self._client is not None:
            self.disconnects.append(time.time())
        self._client = None
        self.connected_since = None
        self._notify()
        self._schedule_retry()

    def _schedule_retry(self) -> None:
        if not self._active or self._retry:
            return
        loop = asyncio.get_running_loop()

        def _go() -> None:
            self._retry = None
            loop.create_task(self.start())

        self._retry = loop.call_later(RECONNECT_DELAY, _go)

    async def stop(self) -> None:
        self._active = False
        if self._retry:
            self._retry.cancel()
            self._retry = None
        if self._client:
            client, self._client = self._client, None
            await client.disconnect()

    # ---------- state ----------
    def _on_report(self, _char, data: bytearray) -> None:
        reports = parse_reports(bytes(data))
        if not reports:
            return
        self.last_report = time.monotonic()
        self.raw = frame(*reports[-1]).hex(" ")
        mist, light = reports[-1]
        if (mist, light) != (self.mist, self.light):
            self.mist, self.light = mist, light
            if light:
                self.last_color = light
            self._notify()

    def diagnostics(self) -> dict:
        now = time.time()
        return {
            "connected": self.connected,
            "connected_since": self.connected_since.isoformat() if self.connected_since else None,
            "disconnects_24h": sum(1 for t in self.disconnects if now - t < 86400),
            "last_report_s": round(time.monotonic() - self.last_report, 1) if self.last_report else None,
            "raw": self.raw,
            "mist_byte": self.mist,
            "light_byte": self.light,
            "last_error": self.last_error,
        }

    async def set(self, mist: int | None = None, light: int | None = None) -> None:
        new_mist = mist if mist is not None else (self.mist or MIST_MODES["off"])
        new_light = light if light is not None else (self.light or 0)
        async with self._lock:
            client = await self._connect()
            _LOGGER.debug("Sending %s", frame(new_mist, new_light).hex(" "))
            await client.write_gatt_char(CHAR_UUID, frame(new_mist, new_light), response=True)
        # show the target state until the device reports back
        self.mist, self.light = new_mist, new_light
        if new_light:
            self.last_color = new_light
        self._notify()
