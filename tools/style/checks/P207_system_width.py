from ..findings import Hit
from ..pdf import TEXT_LEFT, TEXT_RIGHT

TOL = 4.0          # pt: the finish lets a line end wander, and build.sh allows 490 - 482 pt


def check(pdf):
    for m in pdf.music_pages:
        x0 = min(s.x0_pt for s in m.staves)
        x1 = max(s.x1_pt for s in m.staves)
        if x1 > TEXT_RIGHT + TOL:
            yield Hit(key=f"p{m.number}:right", page=m.number,
                      values={"page": m.number, "side": "past the right edge of", "x": x1, "lo": TEXT_LEFT, "hi": TEXT_RIGHT})
        if x0 < TEXT_LEFT - TOL:
            yield Hit(key=f"p{m.number}:left", page=m.number,
                      values={"page": m.number, "side": "before the left edge of", "x": x0, "lo": TEXT_LEFT, "hi": TEXT_RIGHT})
