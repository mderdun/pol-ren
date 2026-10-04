#!/usr/bin/env python3
"""Give the spare height of each music page to the staff gaps inside its
systems (Ross 69), keeping the gap between systems the widest (Gould 488).

    tools/stretch_systems.py NAME.prsys NAME.syslog STAFFSIZE OUT.scm OUT.prskip

NAME.prsys is written by LaTeX (pol-ren.cls): "S page n" for each system n
of the score on page `page`, "P page slack" for the height a page leaves
unused at natural spacing. NAME.syslog is written by LilyPond (pol-ren.ily,
PR_SYSLOG): one "score system" line per staff of each system, in the order
lilypond-book numbers the systems. On the next build:
  OUT.scm (LilyPond, PR_STRETCH): ((score . system) . extra staff spaces),
    added below the lyrics of every staff of that system but the last;
  OUT.prskip (LaTeX): \\prsysskip{n}{X pt}, added before system n.

Per page, every gap takes the same addition: each staff gap inside a system
and each gap between two systems. A four-voice system has three staff gaps
to one system gap, so the staves take three quarters of the spare height
(Ross: the staff gaps "always", at three to six times the share of the
system gaps), while the gap between systems grows as much as any gap inside
them and stays the widest gap on the page (Gould 488). A gap takes at most
MAX_GAP staff spaces; what is left stays where LaTeX puts it. The page that
ends the score takes no more than the page before it, so a short last page
does not spread its systems further than the rest, and two facing music
pages take the same spacing (the tighter of the two). Content only grows by
less than the slack, so page breaks do not move; tools/build.sh checks that.
Exit status 0 if there is anything to add, 1 if not.
"""
import sys
from collections import OrderedDict

MAX_GAP = 3.0          # staff spaces added to one gap, at most
SAFETY = 3.0           # pt of each page's slack left alone


def main():
    prsys, syslog, size, out, outskip = sys.argv[1:6]
    ss = float(size) / 4.0                            # staff space, pt
    slack, onpage = {}, OrderedDict()
    for line in open(prsys, encoding='utf-8', errors='replace'):
        p = line.split()
        if len(p) == 3 and p[0] == 'P':
            slack[p[1]] = float(p[2].rstrip('pt'))
        elif len(p) == 3 and p[0] == 'S':
            onpage.setdefault(p[1], []).append(int(p[2]))
    staves = OrderedDict()
    for line in open(syslog):
        p = line.split()
        if len(p) == 2:
            k = (int(p[0]), int(p[1]))
            staves[k] = staves.get(k, 0) + 1
    keys = list(staves)
    nsys = max((n for ns in onpage.values() for n in ns), default=0)
    if nsys == 0:
        return 1
    if nsys != len(keys):
        print(f'  stretch: {nsys} systems in LaTeX, {len(keys)} in LilyPond; spacing left as it is')
        return 1
    pages = list(onpage)
    room = {}                                         # page -> staff spaces a gap
    for page in pages:
        ns = onpage[page]
        gaps = sum(staves[keys[n - 1]] - 1 for n in ns)
        s = slack.get(page, 0.0) - SAFETY
        if gaps == 0 or s <= 0:
            room[page] = 0.0
            continue
        room[page] = min(s / (gaps + len(ns) - 1) / ss, MAX_GAP)
    for i, page in enumerate(pages):                  # the last page: no looser than the one before
        if max(onpage[page]) == nsys and i > 0:
            room[page] = min(room[page], room[pages[i - 1]])

    def partner(page):                                # the facing page (2|3, 4|5 ...)
        if not page.isdigit() or int(page) < 2:
            return None
        p = int(page)
        return str(p + 1 if p % 2 == 0 else p - 1)
    extra, skip = {}, {}
    for page in pages:
        e = room[page]
        q = partner(page)
        if q in room:
            e = min(e, room[q])
        for i, n in enumerate(onpage[page]):
            extra[keys[n - 1]] = round(e, 3)
            if i > 0:
                skip[n] = round(e * ss, 2)
    items = [(k, v) for k, v in extra.items() if v > 0.05]
    with open(out, 'w') as f:
        f.write('(' + ' '.join(f'(({k[0]} . {k[1]}) . {v})' for k, v in items) + ')\n')
    with open(outskip, 'w') as f:
        for n, v in skip.items():
            if v > 0.2:
                f.write(f'\\prsysskip{{{n}}}{{{v}pt}}\n')
    if items:
        print('  stretch: ' + ', '.join(f'p.{pg} +{extra.get(keys[onpage[pg][0] - 1], 0):.2f}'
                                         for pg in pages) + ' staff spaces a gap')
    return 0 if items else 1


if __name__ == '__main__':
    sys.exit(main())
