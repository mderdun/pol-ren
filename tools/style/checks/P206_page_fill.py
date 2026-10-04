"""tools/check_pages.py on the committed PDF, rendered with PyMuPDF at the
same 20 dpi instead of pdftoppm (so CI needs no poppler)."""
import re

from ..findings import Hit


def check(pdf):
    import pymupdf

    from tools.check_pages import ink_rows_px, judge
    music = {m.number for m in pdf.music_pages}
    measured = []
    for i, page in enumerate(pdf.doc):
        pix = page.get_pixmap(dpi=20, colorspace=pymupdf.csGRAY, alpha=False)
        w, h, s, stride = pix.width, pix.height, pix.samples, pix.stride
        top, bot, _, body = ink_rows_px(w, h, lambda x, y: s[y * stride + x])
        # at 20 dpi the finished staff lines are too light for check_pages'
        # own test for a music page; the staves found at 200 dpi decide
        measured.append((top, bot, (i + 1) in music, body))
    for line in judge(measured):
        m = re.match(r"\s*p\.(\d+): (.*)", line)
        page = int(m.group(1)) if m else None
        text = m.group(2) if m else line.strip()
        yield Hit(key=re.sub(r"\d+%", "", text), page=page, values={"what": f"p.{page}: {text}"})
