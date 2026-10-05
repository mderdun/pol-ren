from ..findings import Hit
from ..pdf import extenders_below

LIMIT = 1.0        # staff spaces (Grier 167)


def check(pdf):
    for m in pdf.music_pages:
        for i, st in enumerate(m.staves):
            nxt = m.staves[i + 1].top if i + 1 < len(m.staves) else m.raster.h
            close = [(y - st.bottom) / st.space for y, _, _ in extenders_below(m.raster, st, nxt)]
            close = [d for d in close if d <= LIMIT]
            if close:
                yield Hit(key=f"p{m.number}:staff{i + 1}", page=m.number,
                          values={"page": m.number, "staff": i + 1, "dist": min(close)})
