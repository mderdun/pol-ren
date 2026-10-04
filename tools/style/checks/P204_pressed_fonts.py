import re

from ..findings import Hit

PRESSED = re.compile(r"^(JunicodePressed(?:-\w+)?|Pressed-\d+|pressedchant)$")
# house style 5a names these as not yet pressed
UNPRESSED_OK = re.compile(r"^(TeXGyrePagella(?:-\w+)?|LMMono\d*(?:-\w+)?)$")


def check(pdf):
    for font, e in sorted(pdf.fonts.items()):
        if PRESSED.match(font) or UNPRESSED_OK.match(font):
            continue
        if font.startswith("Junicode"):
            hint = "the unpressed Junicode: was the PDF built with NOVELLO=0?"
        elif re.match(r"(emmentaler|Emmentaler|feta|greciliae)", font):
            hint = "an unpressed music font: rebuild with tools/make-pressed-fonts.sh"
        else:
            hint = "probably a fallback for a glyph the house fonts lack"
        ps = sorted(e["pages"])
        yield Hit(key=font, page=ps[0], values={"font": font, "pages": ", ".join(map(str, ps)), "hint": hint})
