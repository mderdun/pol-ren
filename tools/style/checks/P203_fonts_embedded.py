from ..findings import Hit


def check(pdf):
    for font, e in sorted(pdf.fonts.items()):
        if not e["embedded"]:
            ps = sorted(e["pages"])
            yield Hit(key=font, page=ps[0], values={"font": font, "pages": ", ".join(map(str, ps))})
