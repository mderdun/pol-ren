"""Every page with ink carries a text layer, and the words in it map to
Unicode (a font without a ToUnicode map extracts as U+FFFD). Music fonts are
not counted: their glyphs have no Unicode meaning."""
from ..findings import Hit
from ..pdf import is_music_font


def check(pdf):
    for i, page in enumerate(pdf.doc):
        text = page.get_text("text").strip()
        ink = bool(page.get_drawings()) or bool(page.get_images())
        if ink and not text:
            yield Hit(key=f"p{i + 1}:no-text", page=i + 1,
                      values={"what": f"p.{i + 1} has marks but no text layer: the words are not searchable"})
    bad, total = {}, {}
    for pno, s in pdf.spans:
        font = s.get("font", "")
        if is_music_font(font):
            continue
        t = s.get("text", "")
        total[font] = total.get(font, 0) + len(t)
        bad[font] = bad.get(font, 0) + t.count("�")
    for font in sorted(bad):
        if total[font] and bad[font] / total[font] > 0.05:
            yield Hit(key=f"unicode:{font}", page=None,
                      values={"what": f"text in {font.split('+', 1)[-1]} does not map to Unicode "
                                      f"({bad[font]} of {total[font]} characters): it cannot be searched or copied"})
