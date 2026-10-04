"""Text colours from the text layer, drawing colours (stroke and fill) from
the page's vector paths. Raster images (a facsimile) are not judged: they
reproduce a source."""
from ..colours import from_unit, hexstr, name_of
from ..findings import Hit


def check(pdf):
    bad: dict = {}
    for pno, s in pdf.spans:
        c = s.get("color", 0)
        rgb = ((c >> 16) & 255, (c >> 8) & 255, c & 255)
        if name_of(rgb) is None:
            bad.setdefault(("text", hexstr(rgb)), set()).add(pno)
    for i, page in enumerate(pdf.doc):
        for d in page.get_drawings():
            for k in ("color", "fill"):
                v = d.get(k)
                if v is None:
                    continue
                rgb = from_unit(v)
                if name_of(rgb) is None:
                    bad.setdefault(("drawing", hexstr(rgb)), set()).add(i + 1)
    for (what, col), pages in sorted(bad.items()):
        ps = sorted(pages)
        yield Hit(key=f"{what}:{col}", page=ps[0],
                  values={"what": what, "colour": col, "pages": ", ".join(map(str, ps))})
