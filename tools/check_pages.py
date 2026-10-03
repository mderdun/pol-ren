#!/usr/bin/env python3
"""Page check: flag pages whose fill looks wrong after a build.

    tools/check_pages.py editions/<slug>/pdf/<file>.pdf ...

For each page, measures how far down the text block the ink reaches
(rendered at low resolution with pdftoppm). Warns about:
  - a short page (ink ends above 40% of the text block) that is followed
    by another page: usually a system or block pushed over by a spacing
    change, and the per-score breaks need resetting;
  - a page whose ink runs into the bottom margin (overfull).
Only pages with music are judged (prose pages end short by design before
a new part); the last page is not judged. Exit status is always 0;
this is a report, not a gate.
"""
import subprocess, sys, tempfile, os, glob
from PIL import Image

TOP, BOTTOM = 17 / 297, 1 - 23 / 297     # house text block (A4, mm)

def ink_rows(png):
    """(top, bottom) of the ink as fractions of the page, and whether the
    page carries music (rows of staff lines spanning most of the width)."""
    im = Image.open(png).convert('L'); w, h = im.size; px = im.load()
    rows, staff = [], 0
    for y in range(h):
        dark = sum(1 for x in range(0, w, 2) if px[x, y] < 160)
        if dark: rows.append(y)
        if dark > 0.3 * w: staff += 1
    if not rows: return None, None, False
    return rows[0] / h, rows[-1] / h, staff >= 10

def check(pdf):
    out = []
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(['pdftoppm', '-r', '20', '-png', pdf, f'{d}/p'], check=True)
        pages = sorted(glob.glob(f'{d}/p-*.png'))
        n = len(pages)
        for i, p in enumerate(pages, 1):
            top, bot, music = ink_rows(p)
            if top is None or not music or i == n:
                continue
            fill = (bot - TOP) / (BOTTOM - TOP)
            if fill < 0.40:
                out.append(f'  p.{i}: short page ({fill:.0%} of the text block) before p.{i+1}')
            if bot > BOTTOM + 0.012:
                out.append(f'  p.{i}: ink in the bottom margin')
    return out

if __name__ == '__main__':
    for pdf in sys.argv[1:]:
        warn = check(pdf)
        if warn:
            print(f'check {os.path.relpath(pdf)}:'); print('\n'.join(warn))
