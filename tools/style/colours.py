"""The house palette (house style 5): black, white and one red, #9A1E1E."""
from __future__ import annotations

PALETTE = {"black": (0, 0, 0), "white": (255, 255, 255), "rubric": (154, 30, 30)}
TOL = 2          # in 0-255 units: rounding in PDF writers and LilyPond's 3-digit fractions


def name_of(rgb255) -> str | None:
    for n, c in PALETTE.items():
        if all(abs(a - b) <= TOL for a, b in zip(rgb255, c)):
            return n
    return None


def from_unit(vals) -> tuple:
    vals = list(vals)
    if len(vals) == 1:                       # grey
        vals = vals * 3
    if len(vals) == 4:                       # CMYK
        c, m, y, k = vals
        vals = [(1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k)]
    return tuple(round(255 * float(v)) for v in vals[:3])


def hexstr(rgb255) -> str:
    return "#" + "".join(f"{v:02X}" for v in rgb255)
