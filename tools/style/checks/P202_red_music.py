from ..colours import name_of
from ..findings import Hit
from ..pdf import is_music_font


def check(pdf):
    bad: dict = {}
    for pno, s in pdf.spans:
        if not is_music_font(s.get("font", "")) or not s.get("text", "").strip(" "):
            continue
        c = s.get("color", 0)
        if name_of(((c >> 16) & 255, (c >> 8) & 255, c & 255)) == "rubric":
            font = s["font"].split("+", 1)[-1]
            bad.setdefault(font, set()).add(pno)
    for font, pages in sorted(bad.items()):
        ps = sorted(pages)
        yield Hit(key=font, page=ps[0], values={"font": font, "pages": ", ".join(map(str, ps))})
