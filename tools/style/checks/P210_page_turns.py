from ..findings import Hit
from ..registry import ROOT
from ..turns import break_lists, playing_through, read_musicxml, system_ends


def check(pdf):
    pages = [m for m in pdf.music_pages if any(len(s.staves) > 1 for s in m.systems)]
    if len(pages) < 2:
        return
    meta = getattr(pdf, "meta", {}) or {}
    xml = meta.get("musicxml") or ROOT / "editions" / pdf.slug / "pdf" / f"{pdf.slug}.musicxml"
    breaks = meta.get("breaks") if "breaks" in meta else break_lists(pdf.slug)
    try:
        data = read_musicxml(xml)
    except (OSError, FileNotFoundError):
        return
    counts = [sum(1 for s in m.systems if len(s.staves) > 1) for m in pages]
    ends = system_ends(breaks, data, sum(counts))
    if ends is None:
        return
    k = 0
    for i, m in enumerate(pages[:-1]):
        k += counts[i]
        nxt = pages[i + 1].number
        if m.number % 2 == 0 or nxt != m.number + 1:
            continue          # no leaf is turned between a verso and the facing recto
        bar = ends[k - 1]
        voices = playing_through(data, bar)
        if voices:
            yield Hit(key=f"turn-after-{bar}", page=m.number,
                      values={"page": m.number, "next": nxt, "bar": bar, "voices": ", ".join(voices),
                              "verb": "sings" if len(voices) == 1 else "sing"})
