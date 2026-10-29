"""Wire protocol: build commands, parse state reports. No Home Assistant imports."""
from __future__ import annotations

from .const import COLORS, HEADER


def frame(mist: int, light: int) -> bytes:
    """Command bytes for one mist byte and one light byte."""
    return bytes([HEADER, mist, light])


def parse_reports(data: bytes) -> list[tuple[int, int]]:
    """All (mist, light) pairs in one notification.

    The device sends roughly ten reports per second and sometimes glues two
    together (``aa 00 18 aa 00 30``). Reading the characteristic returns 20 zero
    bytes, which is not a report.
    """
    pairs = []
    i = 0
    while i + 2 < len(data):
        if data[i] == HEADER:
            pairs.append((data[i + 1], data[i + 2]))
            i += 3
        else:
            i += 1
    return pairs


def nearest_color(rgb: tuple[int, int, int]) -> str:
    """The device knows eight fixed colors; map any RGB value to the closest one."""
    return min(COLORS, key=lambda k: sum((a - b) ** 2 for a, b in zip(COLORS[k][1], rgb)))
