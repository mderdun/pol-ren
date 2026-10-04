from ..findings import Hit

MARGIN = 0.1       # staff spaces: measurement noise at 200 dpi


def check(pdf):
    for m in pdf.music_pages:
        systems = m.systems
        for i in range(len(systems) - 1):
            a, b = systems[i], systems[i + 1]
            inner = max(a.gaps + b.gaps, default=None)
            if inner is None:
                continue          # single staves (chant): nothing to compare
            gap = (b.top - a.bottom) / ((a.space + b.space) / 2)
            if gap <= inner + MARGIN:
                yield Hit(key=f"p{m.number}:s{i + 1}", page=m.number,
                          values={"page": m.number, "a": i + 1, "b": i + 2, "gap": gap, "inner": inner})
