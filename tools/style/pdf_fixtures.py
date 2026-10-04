"""Small PDFs for the PDF checks' flag and pass examples (the `fixture:`
names in checks/P2xx-*.yaml). Each builder writes an A4 PDF unless it is
testing the page size, and may return `meta` for the check (page turns).

Staves are drawn as five lines 4.75 pt apart (staff size 19), systems of
four staves joined by a line at the left, as LilyPond prints them.
"""
from __future__ import annotations

from pathlib import Path

A4 = (595.28, 841.89)
SS = 4.75                     # staff space, pt
LEFT, RIGHT = 70.0, 536.0     # inside the 20 mm margins
RED = (154 / 255, 30 / 255, 30 / 255)


def _doc():
    import pymupdf
    return pymupdf.open()


def _page(doc, size=A4):
    return doc.new_page(width=size[0], height=size[1])


def _staff(page, top: float, x0=LEFT, x1=RIGHT):
    for k in range(5):
        y = top + k * SS
        page.draw_line((x0, y), (x1, y), color=(0, 0, 0), width=0.45)
    return top + 4 * SS


def _system(page, top: float, gaps: list[float], x0=LEFT, x1=RIGHT, extender_at: float | None = 3.0):
    """Staves with the given gaps (in spaces, line to line) between them;
    returns the bottom line of the last staff. A text line and an extender
    under each staff, extender_at spaces below it."""
    y = top
    tops = []
    for i in range(len(gaps) + 1):
        tops.append(y)
        bottom = _staff(page, y, x0, x1)
        page.insert_text((x0 + 10, bottom + 3.2 * SS), "sae -", fontsize=9)
        if extender_at is not None:
            ye = bottom + extender_at * SS
            page.draw_line((x0 + 60, ye), (x0 + 60 + 6 * SS, ye), color=(0, 0, 0), width=0.5)
        if i < len(gaps):
            y = bottom + gaps[i] * SS
    page.draw_line((x0, tops[0]), (x0, bottom), color=(0, 0, 0), width=0.6)    # systemic bar line
    return bottom


def _save(doc, path):
    doc.save(str(path))
    doc.close()


def _rename_font(path, old: str, new: str):
    """Give a base-14 font a house font's name (the checks read the name)."""
    import pymupdf
    doc = pymupdf.open(str(path))
    for page in doc:
        for xref, _, _, name, *_ in page.get_fonts(full=True):
            if name == old or name.endswith(old):
                doc.xref_set_key(xref, "BaseFont", f"/{new}")
    doc.saveIncr()
    doc.close()


# ---------------------------------------------------------------- colours, fonts

def house_colours(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 100), "Vox in Rama", fontsize=11, color=(0, 0, 0))
    p.insert_text((70, 120), "Antiphona", fontsize=11, color=RED)
    p.draw_line((70, 130), (520, 130), color=(0, 0, 0), width=1)
    p.draw_rect((70, 140, 120, 160), color=None, fill=(1, 1, 1))
    _save(doc, path)


def grey_text(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 100), "a grey note", fontsize=11, color=(0.5, 0.5, 0.5))
    _save(doc, path)


def blue_line(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 100), "text", fontsize=11)
    p.draw_line((70, 130), (520, 130), color=(0, 0, 1), width=1)
    _save(doc, path)


def red_music_glyph(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 100), "text", fontsize=11)
    p.insert_text((70, 140), "q", fontsize=20, color=RED, fontname="Cour")
    _save(doc, path)
    _rename_font(path, "Courier", "ABCDEF+Pressed-20")


def unembedded_font(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 100), "Helvetica, referenced only", fontsize=11)
    _save(doc, path)


def no_text(path):
    doc = _doc()
    p = _page(doc)
    _staff(p, 100)
    _save(doc, path)


def fallback_font(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 100), "x", fontsize=11, fontname="Cour")
    _save(doc, path)
    _rename_font(path, "Courier", "ABCDEF+DejaVuSans")


def pressed_font_names(path):
    doc = _doc()
    p = _page(doc)
    names = [("Helv", "Helvetica", "AAAAAA+JunicodePressed-Regular"), ("Cour", "Courier", "BBBBBB+Pressed-20"),
             ("TiRo", "Times-Roman", "CCCCCC+pressedchant"), ("Symb", "Symbol", "DDDDDD+TeXGyrePagella-Regular"),
             ("ZaDb", "ZapfDingbats", "EEEEEE+LMMono10-Regular")]
    for i, (short, _, _) in enumerate(names):
        p.insert_text((70, 100 + 20 * i), "abc", fontsize=11, fontname=short)
    _save(doc, path)
    for _, base, new in names:
        _rename_font(path, base, new)


def bold_font(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 100), "1.", fontsize=11, fontname="Cour")
    _save(doc, path)
    _rename_font(path, "Courier", "ABCDEF+JunicodePressed-Bold")


def letter_page(path):
    doc = _doc()
    p = _page(doc, (612, 792))
    p.insert_text((70, 100), "text", fontsize=11)
    _save(doc, path)


# ---------------------------------------------------------------- staves

def gould_fail(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 70), "Vox in Rama", fontsize=11)
    b = _system(p, 100, [10, 10, 10])
    _system(p, b + 8 * SS, [10, 10, 10])
    _save(doc, path)


def gould_pass(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 70), "Vox in Rama", fontsize=11)
    b = _system(p, 100, [7, 7, 7])
    # ledger lines one and two spaces under the bottom staff: not extenders
    for k in (1, 2):
        p.draw_line((300, b + k * SS), (300 + 2 * SS, b + k * SS), color=(0, 0, 0), width=0.6)
    _system(p, b + 12 * SS, [7, 7, 7])
    _save(doc, path)


def wide_system(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 70), "x", fontsize=11)
    b = _system(p, 100, [7, 7, 7], x1=565)
    _system(p, b + 12 * SS, [7, 7, 7], x1=565)
    _save(doc, path)


def extender_close(path):
    doc = _doc()
    p = _page(doc)
    p.insert_text((70, 70), "x", fontsize=11)
    b = _system(p, 100, [7, 7, 7], extender_at=0.6)
    _system(p, b + 12 * SS, [7, 7, 7])
    _save(doc, path)


def _music_page(doc, systems: int, top=80.0):
    p = _page(doc)
    p.insert_text((70, 60), "x", fontsize=11)
    y = top
    for _ in range(systems):
        b = _system(p, y, [7, 7, 7])
        y = b + 12 * SS
    return p


def short_music_page(path):
    doc = _doc()
    _music_page(doc, 1)
    _music_page(doc, 3)
    _music_page(doc, 3)
    _save(doc, path)


def full_music_pages(path):
    doc = _doc()
    _music_page(doc, 3)
    _music_page(doc, 3)
    _music_page(doc, 3)
    _save(doc, path)


def _turn_xml(path: Path, rest_at_10: bool) -> Path:
    """Four voices, 20 bars of breves; bar 10 ends in a rest (or not) in
    every voice."""
    parts, list_ = [], []
    for i, name in enumerate(["Cantus", "Altus", "Tenor", "Bassus"], 1):
        list_.append(f'<score-part id="P{i}"><part-name>{name}</part-name></score-part>')
        ms = []
        for bar in range(1, 21):
            if bar == 10 and rest_at_10:
                body = ('<note><pitch><step>C</step><octave>4</octave></pitch><duration>4</duration></note>'
                        '<note><rest/><duration>4</duration></note>')
            else:
                body = '<note><pitch><step>C</step><octave>4</octave></pitch><duration>8</duration></note>'
            attrs = '<attributes><divisions>2</divisions><time><beats>2</beats><beat-type>1</beat-type></time></attributes>' \
                if bar == 1 else ""
            bl = '<barline location="right"><bar-style>light-heavy</bar-style></barline>' if bar == 20 else ""
            ms.append(f'<measure number="{bar}">{attrs}{body}{bl}</measure>')
        parts.append(f'<part id="P{i}">{"".join(ms)}</part>')
    xml = ('<?xml version="1.0"?><score-partwise><part-list>' + "".join(list_) + "</part-list>"
           + "".join(parts) + "</score-partwise>")
    out = path.with_suffix(".musicxml")
    out.write_text(xml, encoding="utf-8")
    return out


def _turns(path, rest):
    doc = _doc()
    _music_page(doc, 2)     # systems end at bars 5, 10
    _music_page(doc, 2)     # 15, 20
    _save(doc, path)
    return {"musicxml": _turn_xml(Path(path), rest), "breaks": [5, 10, 15]}


def turn_mid_phrase(path):
    return _turns(path, False)


def turn_at_rest(path):
    return _turns(path, True)


BUILDERS = {
    "house-colours": house_colours, "grey-text": grey_text, "blue-line": blue_line,
    "red-music-glyph": red_music_glyph, "unembedded-font": unembedded_font, "no-text": no_text,
    "fallback-font": fallback_font, "pressed-font-names": pressed_font_names, "bold-font": bold_font,
    "letter-page": letter_page, "gould-fail": gould_fail, "gould-pass": gould_pass, "wide-system": wide_system,
    "extender-close": extender_close, "short-music-page": short_music_page, "full-music-pages": full_music_pages,
    "turn-mid-phrase": turn_mid_phrase, "turn-at-rest": turn_at_rest,
}


def build(name: str, directory: Path, kind: str = "performance"):
    """Write fixture `name` as <directory>/<name>-<kind>.pdf; return (path, meta)."""
    path = Path(directory) / f"{name}-{kind}.pdf"
    meta = BUILDERS[name](path) or {}
    return path, meta
