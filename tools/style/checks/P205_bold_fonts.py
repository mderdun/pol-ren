import re

from ..findings import Hit

BOLD = re.compile(r"(Bold|Semibold|SemiBold|Demi|Black|Heavy|Medium|ExtraBold)", re.I)


def check(pdf):
    for font, e in sorted(pdf.fonts.items()):
        style = font.split("-", 1)[1] if "-" in font else ""
        if BOLD.search(style):
            ps = sorted(e["pages"])
            yield Hit(key=font, page=ps[0], values={"font": font, "pages": ", ".join(map(str, ps))})
