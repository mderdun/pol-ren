from ..findings import Hit
from ..pdf import A4


def check(pdf):
    seen = set()
    for i, page in enumerate(pdf.doc):
        w, h = page.rect.width, page.rect.height
        if abs(w - A4[0]) > 1.5 or abs(h - A4[1]) > 1.5:
            size = (round(w), round(h))
            if size in seen:
                continue
            seen.add(size)
            yield Hit(key=f"{size[0]}x{size[1]}", page=i + 1, values={"page": i + 1, "w": w, "h": h})
