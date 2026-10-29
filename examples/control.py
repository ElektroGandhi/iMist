"""Control an iMist diffuser without Home Assistant.

    pip install bleak
    python control.py                     # print the live state for 10 seconds
    python control.py interval dark_blue  # set mist and light, then print the state

Mist: off, continuous, interval
Light: off, white, red, yellow, green, light_blue, dark_blue, pink, warm_white
"""
import asyncio
import sys

from bleak import BleakClient, BleakScanner

CHAR = "0000fff4-0000-1000-8000-00805f9b34fb"
MIST = {"off": 0x00, "continuous": 0x20, "interval": 0x40}
LIGHT = {"off": 0x00, "white": 0x08, "red": 0x18, "yellow": 0x30, "green": 0x20,
         "light_blue": 0x40, "dark_blue": 0x28, "pink": 0x38, "warm_white": 0x48}
NAMES = ({v: k for k, v in MIST.items()}, {v: k for k, v in LIGHT.items()})


last = None


def show(_char, data: bytearray) -> None:
    """The device reports ~10 times per second; print only changes."""
    global last
    for i in range(0, len(data) - 2, 3):
        if data[i] == 0xAA and bytes(data[i:i + 3]) != last:
            last = bytes(data[i:i + 3])
            mist, light = NAMES[0].get(data[i + 1], "?"), NAMES[1].get(data[i + 2], "?")
            print(f"{last.hex(' ')}  mist={mist:<10} light={light}")


async def main() -> None:
    device = await BleakScanner.find_device_by_name("AromaDiffuser", timeout=15)
    if device is None:
        sys.exit("No AromaDiffuser found. Is it switched on and not connected to a phone?")
    async with BleakClient(device) as client:
        await client.start_notify(CHAR, show)
        if len(sys.argv) == 3:
            command = bytes([0xAA, MIST[sys.argv[1]], LIGHT[sys.argv[2]]])
            print("sending", command.hex(" "))
            await client.write_gatt_char(CHAR, command, response=True)
        await asyncio.sleep(10 if len(sys.argv) < 3 else 2)


asyncio.run(main())
