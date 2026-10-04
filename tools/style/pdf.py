"""The committed PDFs as the checks see them (PyMuPDF only; no TeX, no
poppler).

The house finish (tools/novello_vector.py) merges every drawn mark of a page
into one filled path, so staff lines cannot be read from the drawing
operators. They are found on a greyscale rendering instead:

- a staff line is a row whose longest dark run covers a quarter of the page
  width;
- five such lines, equally spaced, are a staff (the spacing is the staff
  space, ss);
- two consecutive staves belong to one system when a dark vertical line (the
  systemic bar line or the choir bracket at the left) joins them; staves that
  start at different x belong to different systems;
- an extender is a thin horizontal dark run, at least 2.5 ss long, below a
  staff and above the next one (ledger lines are shorter; ligature brackets
  hang above the staff they belong to).

All distances are reported in staff spaces, measured from line centre to line
centre, as in the Gould reading notes (docs/research/literature/
gould-behind-bars.md, house style 7).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path

from .registry import ROOT

DPI = 200
PT = DPI / 72.0                 # pixels per point
MM = 72 / 25.4                  # points per millimetre
A4 = (595.28, 841.89)
TEXT_LEFT, TEXT_RIGHT = 20 * MM, A4[0] - 20 * MM      # house style 2: 20 mm sides
DARK = 128


def _dark_table():
    return bytes((49 if i < DARK else 48) for i in range(256))


TBL = _dark_table()


@dataclass
class Staff:
    top: float          # y of the top line, px
    bottom: float       # y of the bottom line, px
    space: float        # staff space, px
    x0: int
    x1: int
    lines: list = field(default_factory=list)

    @property
    def x0_pt(self) -> float:
        return self.x0 / PT

    @property
    def x1_pt(self) -> float:
        return self.x1 / PT


@dataclass
class System:
    staves: list

    @property
    def gaps(self) -> list[float]:
        """Gaps between the staves, in staff spaces (line to line)."""
        out = []
        for a, b in zip(self.staves, self.staves[1:]):
            out.append((b.top - a.bottom) / ((a.space + b.space) / 2))
        return out

    @property
    def top(self) -> float:
        return self.staves[0].top

    @property
    def bottom(self) -> float:
        return self.staves[-1].bottom

    @property
    def space(self) -> float:
        return sum(s.space for s in self.staves) / len(self.staves)


class Raster:
    """One page rendered in greyscale, as rows of bytes ('1' dark, '0' light)."""

    def __init__(self, page, dpi: int = DPI):
        import pymupdf
        pix = page.get_pixmap(dpi=dpi, colorspace=pymupdf.csGRAY, alpha=False)
        self.w, self.h = pix.width, pix.height
        s = pix.samples
        stride = pix.stride
        self.rows = [s[y * stride:y * stride + self.w].translate(TBL) for y in range(self.h)]

    def longest_run(self, y: int) -> tuple[int, int]:
        best = max(self.rows[y].split(b"0"), key=len)
        return len(best), (self.rows[y].find(best) if best else -1)

    def dark(self, x: int, y: int) -> bool:
        return 0 <= y < self.h and 0 <= x < self.w and self.rows[y][x] == 49

    def column_run(self, x: int, y0: int, y1: int) -> float:
        """Share of dark pixels in column x between rows y0 and y1."""
        if y1 <= y0:
            return 1.0
        n = sum(1 for y in range(y0, y1) if self.rows[y][x] == 49)
        return n / (y1 - y0)

    def h_runs(self, y: int, minlen: int):
        """(x0, x1) of dark runs in row y at least minlen long."""
        row = self.rows[y]
        for m in re.finditer(rb"1{%d,}" % max(1, minlen), row):
            yield m.start(), m.end()


def _is_line(r: Raster, y: int) -> bool:
    """A staff-line row: one long dark run, or (where the finish or a
    knockout breaks the line) many dark pixels in long-ish runs."""
    L, _ = r.longest_run(y)
    if L >= 0.25 * r.w:
        return True
    return L >= 0.05 * r.w and r.rows[y].count(b"1") >= 0.4 * r.w


def _extent(r: Raster, y0: int, y1: int) -> tuple[int, int]:
    xs0, xs1 = [], []
    for y in range(y0, y1 + 1):
        runs = list(r.h_runs(y, int(0.02 * r.w)))
        if runs:
            xs0.append(runs[0][0])
            xs1.append(runs[-1][1])
    return (min(xs0), max(xs1)) if xs0 else (0, 0)


# staff space in pixels: staff sizes 13-22 pt give 3.25-5.5 pt, 9-15 px at
# 200 dpi; the bounds leave room for a cue staff and keep prose leading out
SPACE_MIN, SPACE_MAX = 5.0 * DPI / 200, 22.0 * DPI / 200


def find_staves(r: Raster) -> list[Staff]:
    lines = []
    y = 0
    flags = [_is_line(r, y) for y in range(r.h)]
    while y < r.h:
        if flags[y]:
            y0 = y
            while y + 1 < r.h and flags[y + 1]:
                y += 1
            x0, x1 = _extent(r, y0, y)
            lines.append(((y0 + y) / 2, x0, x1, y - y0 + 1))
        y += 1
    staves = []
    i = 0
    while i + 4 < len(lines):
        grp = lines[i:i + 5]
        gaps = [grp[k + 1][0] - grp[k][0] for k in range(4)]
        g = sum(gaps) / 4
        if (max(gaps) - min(gaps) <= max(1.5, 0.12 * g) and SPACE_MIN < g < SPACE_MAX
                and all(l[3] < g / 2 for l in grp)):
            xs0 = sorted(l[1] for l in grp)
            xs1 = sorted(l[2] for l in grp)
            staves.append(Staff(top=grp[0][0], bottom=grp[4][0], space=g, x0=xs0[2], x1=xs1[-1],
                                lines=[l[0] for l in grp]))
            i += 5
        else:
            i += 1
    return staves


def joined(r: Raster, a: Staff, b: Staff) -> bool:
    """Is there a solid vertical line from staff a down to staff b? The
    systemic bar line and the choir bracket at the left join the staves of a
    system, as do its solid section and final bar lines; nothing joins two
    systems, and the dashed Mensurstriche are too broken to count."""
    if abs(a.x1 - b.x1) > 2 * a.space:
        return False
    y0, y1 = int(a.bottom) + 2, int(b.top) - 1
    lo = max(0, min(a.x0, b.x0) - int(2.5 * a.space))
    hi = min(r.w, max(a.x1, b.x1) + 2)
    # the left edge first (cheap), then the rest of the width
    left = range(lo, min(hi, lo + int(0.3 * (hi - lo))))
    for xx in list(left) + list(range(left.stop, hi)):
        if r.dark(xx, (y0 + y1) // 2) and r.column_run(xx, y0, y1) >= 0.9:
            return True
    return False


def find_systems(r: Raster, staves: list[Staff]) -> list[System]:
    systems: list[System] = []
    for s in staves:
        if systems and joined(r, systems[-1].staves[-1], s):
            systems[-1].staves.append(s)
        else:
            systems.append(System([s]))
    return systems


def _stacked(r: Raster, y: int, x0: int, x1: int, space: float) -> bool:
    """A ledger line: another line of the same extent one staff space above
    or below (the next ledger line, or the staff's own bottom line for a short
    run)."""
    tol = max(2, int(0.15 * space))
    for dy in (-space, space):
        for yy in range(int(y + dy) - 2, int(y + dy) + 3):
            if not 0 <= yy < r.h:
                continue
            for a, b in r.h_runs(yy, int(0.8 * (x1 - x0))):
                if abs(a - x0) <= tol and abs(b - x1) <= tol:
                    return True
    return False


def _thickness(r: Raster, y: int, x0: int, x1: int) -> float:
    """Median vertical thickness (px) of the dark stroke through row y
    across the run: a beam is half a staff space thick, an extender a fifth."""
    vals = []
    for x in range(x0, x1, max(1, (x1 - x0) // 12)):
        a = y
        while r.dark(x, a - 1):
            a -= 1
        b = y
        while r.dark(x, b + 1):
            b += 1
        vals.append(b - a + 1)
    vals.sort()
    return vals[len(vals) // 2] if vals else 0


def extenders_below(r: Raster, st: Staff, limit_y: float) -> list[tuple[float, int, int]]:
    """Thin horizontal runs at least 2.5 ss long between staff st and limit_y:
    (y, x0, x1), y the centre of the run, px."""
    out = []
    minlen = int(2.5 * st.space)
    y = int(st.bottom + 0.4 * st.space)
    stop = int(min(limit_y, st.bottom + 6 * st.space))
    thick = max(2, int(0.3 * st.space))
    while y < stop:
        for x0, x1 in r.h_runs(y, minlen):
            if x1 < st.x0 - st.space or x0 > st.x1 + st.space:
                continue
            # thin: the rows a little above and below are light along most of
            # the run, and nothing as wide as a notehead sits on it (a ledger
            # line, or several touching, carries noteheads)
            mid = range(x0 + (x1 - x0) // 4, x1 - (x1 - x0) // 4)
            above = sum(r.dark(x, y - thick - 1) for x in mid)
            below = sum(r.dark(x, y + thick + 1) for x in mid)
            half = int(0.8 * st.space)
            third = range(x0 + (x1 - x0) // 3, x1 - (x1 - x0) // 3)
            near = sum(1 for x in third
                       if any(r.dark(x, yy) for yy in range(y - half, y - thick))
                       and any(r.dark(x, yy) for yy in range(y + thick + 1, y + half + 1)))
            if (above < 0.3 * len(mid) and below < 0.3 * len(mid) and near < 0.3 * max(1, len(third))
                    and _thickness(r, y, x0, x1) <= max(3, 0.3 * st.space)
                    and not _stacked(r, y, x0, x1, st.space)):
                # the centre of the run: rows below that are still dark along it
                yy = y
                while yy + 1 < stop and sum(r.dark(x, yy + 1) for x in mid) > 0.7 * len(mid):
                    yy += 1
                out.append(((y + yy) / 2, x0, x1))
        y += 1
    # one entry per extender (rows of one run)
    merged = []
    for e in sorted(out):
        if merged and abs(e[0] - merged[-1][0]) <= 2 and e[1] < merged[-1][2] and e[2] > merged[-1][1]:
            continue
        merged.append(e)
    return merged


@dataclass
class PageMusic:
    number: int
    staves: list
    systems: list
    raster: Raster


class PdfDoc:
    def __init__(self, path: Path, doc):
        self.path = Path(path)
        self.doc = doc
        try:
            self.rel = self.path.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            self.rel = self.path.name
        stem = self.path.stem
        self.kind = ("critical" if stem.endswith("-critical") else "performance" if stem.endswith("-performance")
                     else "guide")
        parts = Path(self.rel).parts
        self.slug = parts[1] if len(parts) > 2 and parts[0] in ("editions", "guides") else stem
        self._music: dict[int, PageMusic] = {}
        self.meta: dict = {}          # fixtures: the MusicXML and break list for P210

    @classmethod
    def open(cls, path: Path) -> "PdfDoc":
        import pymupdf
        return cls(path, pymupdf.open(str(path)))

    def __len__(self):
        return len(self.doc)

    def raster(self, pno: int) -> Raster:
        return self.music(pno).raster

    def music(self, pno: int) -> PageMusic:
        """Staves and systems of page pno (0-based)."""
        if pno not in self._music:
            r = Raster(self.doc[pno])
            st = find_staves(r)
            self._music[pno] = PageMusic(number=pno + 1, staves=st, systems=find_systems(r, st), raster=r)
        return self._music[pno]

    @cached_property
    def music_pages(self) -> list[PageMusic]:
        return [m for m in (self.music(i) for i in range(len(self.doc))) if m.staves]

    @cached_property
    def spans(self) -> list[tuple[int, dict]]:
        """(page number, span dict) for every text span (PyMuPDF 'dict')."""
        out = []
        for i, page in enumerate(self.doc):
            for b in page.get_text("dict")["blocks"]:
                for line in b.get("lines", []):
                    for s in line["spans"]:
                        out.append((i + 1, s))
        return out

    @cached_property
    def fonts(self) -> dict[str, dict]:
        """basefont (subset prefix removed) -> {ext, type, pages, embedded}."""
        out: dict[str, dict] = {}
        for i, page in enumerate(self.doc):
            for xref, ext, typ, name, *_ in page.get_fonts(full=True):
                base = name.split("+", 1)[1] if re.match(r"^[A-Z]{6}\+", name) else name
                e = out.setdefault(base, dict(ext=ext, type=typ, pages=set(), embedded=True))
                e["pages"].add(i + 1)
                if ext in ("n/a", "") and typ != "Type3":     # Type 3 glyphs live in the page
                    e["embedded"] = False
        return out


def is_music_font(name: str) -> bool:
    """LilyPond's music fonts (Emmentaler, feta) and their pressed copies."""
    n = name.split("+", 1)[-1]
    return bool(re.match(r"(Pressed-\d+|emmentaler|Emmentaler|feta|pressedchant|greciliae|gregorio|parmesan)", n))
