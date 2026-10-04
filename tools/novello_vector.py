#!/usr/bin/env python3
"""Plate-and-paper treatment that keeps the page vector (see tools/novello.py
for the raster original).

    tools/novello_vector.py IN.pdf OUT.pdf [--strength 1.5] [--seed 1611] [--pages 1-2]

Every drawn mark on the page (staff lines, stems, beams, bar lines, slurs,
rules) becomes a polygon, and the polygon is reshaped as ink on soft paper
would reshape it. Type and music glyphs stay live text: they are set in the
pressed fonts (tools/make-pressed-fonts.sh), which carry the same treatment in
their outlines. With --text outline every glyph is instead outlined with
Ghostscript and treated here, as before the pressed fonts (slow, large files).
The treatment:
  - ink gain: each mark grows a little and its corners round off, more where
    the plate printed heavily (a broad, faint pressure field);
  - bleed: the edge wanders with a fine paper-fibre field, so it is soft and
    slightly ragged instead of mathematically clean;
  - pores: solid heads and beams get the odd small void where ink did not take.
Colours stay the house colours (black and the one red); the page stays white.
The output is vector throughout. Same seed, same page.
"""
import argparse, os, subprocess, tempfile
import numpy as np
import pymupdf
import shapely
from scipy import ndimage as ndi
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union, orient
from shapely import make_valid, segmentize

MM = 72 / 25.4

def field(w, h, cell, rng):
    """Smooth random field over the page, value ~[-1, 1], features `cell` pt."""
    nx, ny = int(w / cell) + 4, int(h / cell) + 4
    g = ndi.spline_filter(rng.standard_normal((nx, ny)), order=3)   # once, not per call
    def f(pts):
        pts = np.asarray(pts, float)
        v = ndi.map_coordinates(g, [pts[:, 0] / cell + 1, pts[:, 1] / cell + 1], order=3,
                                mode='nearest', prefilter=False)
        return np.clip(v / 1.5, -1, 1)
    return f

def bezier(p0, p1, p2, p3, n=8):
    t = np.linspace(0, 1, n + 1)[1:, None]
    P = [np.array(p) for p in (p0, p1, p2, p3)]
    return list(map(tuple, (1 - t) ** 3 * P[0] + 3 * (1 - t) ** 2 * t * P[1] + 3 * (1 - t) * t ** 2 * P[2] + t ** 3 * P[3]))

def rings_of(items):
    """Split a drawing's items into closed point lists (subpaths)."""
    rings, cur = [], []
    def close():
        nonlocal cur
        if len(cur) >= 3: rings.append(cur)
        cur = []
    for it in items:
        k = it[0]
        if k == 'l':
            a, b = tuple(it[1]), tuple(it[2])
            if cur and np.hypot(cur[-1][0] - a[0], cur[-1][1] - a[1]) > 1e-3: close()
            if not cur: cur = [a]
            cur.append(b)
        elif k == 'c':
            a = tuple(it[1])
            if cur and np.hypot(cur[-1][0] - a[0], cur[-1][1] - a[1]) > 1e-3: close()
            if not cur: cur = [a]
            cur += bezier(it[1], it[2], it[3], it[4])
        elif k == 're':
            close(); r = it[1]
            rings.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)])
        elif k == 'qu':
            close(); q = it[1]
            rings.append([tuple(q.ul), tuple(q.ur), tuple(q.lr), tuple(q.ll)])
    close()
    return rings

def parse_dash(s):
    """'[ on off ... ] phase' -> (pattern, phase) or None for a solid line."""
    if not s or s.strip().startswith('[]'): return None
    nums = s.replace('[', ' ').replace(']', ' ').split()
    vals = [float(x) for x in nums]
    pat, phase = vals[:-1], vals[-1]
    return (pat, phase) if pat and sum(pat) > 0 else None

def dashed(line, dash):
    """Split a line into its dashes, as the PDF stroke would draw them."""
    if dash is None: return [line]
    from shapely.ops import substring
    pat, phase = dash
    L, out, pos, i, on = line.length, [], -phase, 0, True
    while pos < L:
        step = pat[i % len(pat)]
        a, b = max(pos, 0), min(pos + step, L)
        if on and b > a: out.append(substring(line, a, b))
        pos += step; i += 1; on = not on
    return [o for o in out if o.length > 0] or [line]

def drawing_geom(d):
    """Shapely geometry of one drawing: filled area, or a stroke's outline."""
    geoms = []
    if d.get('fill') is not None:
        polys = [Polygon(r).buffer(0) for r in rings_of(d['items']) if len(r) >= 3]
        polys = [p for p in polys if not p.is_empty]
        if polys:
            g = polys[0]
            for p in polys[1:]:
                g = g.symmetric_difference(p)          # even-odd: glyph counters
            geoms.append(g)
    if d.get('color') is not None and d.get('width'):
        wdt = d['width'] or 0.1
        caps = d.get('lineCap') or (0,)
        cap = {0: 'flat', 1: 'round', 2: 'square'}.get(caps[0] if isinstance(caps, (tuple, list)) else caps, 'flat')
        dash = parse_dash(d.get('dashes'))
        for it in d['items']:
            if it[0] == 'l':
                for seg in dashed(LineString([tuple(it[1]), tuple(it[2])]), dash):
                    geoms.append(seg.buffer(wdt / 2, cap_style=cap))
            elif it[0] == 'c':
                geoms.append(LineString([tuple(it[1])] + bezier(it[1], it[2], it[3], it[4])).buffer(wdt / 2, cap_style='flat'))
            elif it[0] == 're':
                r = it[1]
                geoms.append(Polygon([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1)]).exterior.buffer(wdt / 2))
    if not geoms: return None
    return unary_union(geoms) if len(geoms) > 1 else geoms[0]

def treat(geom, k, press, fib, wander, rng):
    if geom.is_empty: return geom
    c = geom.centroid
    gain = (0.016 * MM) * k * (1 + 0.6 * float(press(np.array([[c.x, c.y]]))[0]))
    g = geom.buffer(gain, join_style='round', resolution=4)
    # ink pools in tight inner corners: a small closing rounds them
    r = 0.025 * MM * k
    g = g.buffer(r, resolution=3).buffer(-r, resolution=3)
    g = segmentize(g, 0.25 * MM)
    def move(coords):
        pts = np.asarray(coords)
        d1 = fib(pts) * 0.016 * MM * k
        d2 = wander(pts) * 0.022 * MM * k
        d3 = fib(pts[:, ::-1] * 1.7) * 0.016 * MM * k
        return np.column_stack([pts[:, 0] + d2 + d1, pts[:, 1] + d3 - d2 * 0.5])
    def warp(p):
        if p.geom_type == 'Polygon':
            ext = move(p.exterior.coords)
            ints = [move(i.coords) for i in p.interiors]
            return make_valid(Polygon(ext, ints))
        if p.geom_type in ('MultiPolygon', 'GeometryCollection'):
            parts = [warp(q) for q in p.geoms if q.geom_type in ('Polygon', 'MultiPolygon')]
            try:
                return unary_union(parts)
            except Exception:                  # rare topology clash: keep the parts as they are
                return shapely.MultiPolygon([x for q in parts for x in (q.geoms if hasattr(q, 'geoms') else [q]) if x.geom_type == 'Polygon'])
        return p
    g = make_valid(warp(g))
    # pores in solid areas
    core = g.buffer(-0.12 * MM)
    if not core.is_empty and core.area > (0.3 * MM) ** 2:
        minx, miny, maxx, maxy = core.bounds
        n = rng.poisson(core.area / (2.2 * MM) ** 2 * k)
        holes = [Point(rng.uniform(minx, maxx), rng.uniform(miny, maxy)).buffer(rng.uniform(0.025, 0.05) * MM, resolution=3)
                 for _ in range(n)]
        holes = [hh for hh in holes if core.contains(hh.centroid)]
        if holes: g = g.difference(unary_union(holes))
    return g

def colour_key(d):
    col = d.get('fill') if d.get('fill') is not None else d.get('color')
    if col is None: return None
    r, gg, b = col
    if r > 0.45 and gg < 0.3 and b < 0.3: return 'red'
    if r > 0.9 and gg > 0.9 and b > 0.9: return 'white'
    return 'black'

def path_ops(geom, h):
    """PDF path operators for a geometry (y flipped to PDF space)."""
    polys = [geom] if geom.geom_type == 'Polygon' else [p for p in getattr(geom, 'geoms', []) if p.geom_type == 'Polygon']
    out = []
    for p in polys:
        p = orient(p.simplify(0.03, preserve_topology=True), 1.0)   # holes wind against their outline: nonzero fill keeps them
        for ring in [p.exterior] + list(p.interiors):
            # integers in hundredths of a point (the stream sets a 0.01 scale): the
            # same precision as before in fewer bytes. Points within 0.01 pt of the
            # line through their neighbours (0.03 pt) are dropped first (Douglas-Peucker),
            # far below what any printer can show.
            c = np.rint(np.asarray(ring.coords) * 100).astype(np.int64)
            c[:, 1] = int(round(h * 100)) - c[:, 1]
            if len(c) < 3: continue
            out.append('%d %d m ' % tuple(c[0]) + ' '.join('%d %d l' % tuple(q) for q in c[1:]) + ' h')
    return out

def write_page(doc, page, layers):
    """One content stream for the page: each colour filled once (nonzero, so
    overlapping marks add up rather than cancel)."""
    parts = []
    for rgb, ops in layers:
        if ops:
            parts.append('%.4f %.4f %.4f rg\n' % rgb + '\n'.join(ops) + '\nf\n')
    xref = doc.get_new_xref()
    doc.update_object(xref, '<<>>')
    doc.update_stream(xref, ''.join(parts).encode())
    page.set_contents(xref)

def do_page(args):
    path, i, strength, seed = args
    src = pymupdf.open(path); sp = src[i]
    w, h = sp.rect.width, sp.rect.height
    rng = np.random.default_rng(seed + i)
    press = field(w, h, 50 * MM, rng)
    fib = field(w, h, 0.22 * MM, rng)
    wander = field(w, h, 1.1 * MM, rng)
    layers = {'black': [], 'red': []}
    for dr in sp.get_drawings():
        key = colour_key(dr)
        if key in (None, 'white'): continue
        g = drawing_geom(dr)
        if g is None or g.is_empty: continue
        g = treat(g, strength, press, fib, wander, rng)
        layers[key] += path_ops(g, h)
    return w, h, layers

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--strength', type=float, default=1.5)
    ap.add_argument('--seed', type=int, default=1611)
    ap.add_argument('--pages')
    ap.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--text', choices=['keep', 'outline'], default='keep',
                    help='keep: type is left as live text (set in the pressed fonts, which carry '
                         'their own texture) and only drawn marks are treated; outline: every '
                         'glyph is outlined and treated here (slow, large files)')
    a = ap.parse_args()
    from multiprocessing import Pool
    with tempfile.TemporaryDirectory() as d:
        if a.text == 'outline':
            outl = os.path.join(d, 'outl.pdf')
            subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-dNoOutputFonts', '-sDEVICE=pdfwrite',
                            f'-sOutputFile={outl}', a.inp], check=True)
            base = a.inp
        else:
            # drawn marks come from the page itself; the base page is the same page
            # with its vector graphics removed, i.e. the type (and any images) alone
            outl = a.inp
            base = os.path.join(d, 'text.pdf')
            subprocess.run(['gs', '-q', '-dNOPAUSE', '-dBATCH', '-dFILTERVECTOR', '-sDEVICE=pdfwrite',
                            f'-sOutputFile={base}', a.inp], check=True)
        n = len(pymupdf.open(outl))
        pages = range(n)
        if a.pages:
            f, _, l = a.pages.partition('-'); pages = range(int(f) - 1, int(l or f))
        jobs = [(outl, i, a.strength, a.seed) for i in pages]
        with Pool(min(a.jobs, len(jobs))) as pool:
            results = pool.map(do_page, jobs)
        dst = pymupdf.open()
        orig = pymupdf.open(a.inp)
        basedoc = pymupdf.open(base)
        for i, (w, h, layers) in zip(pages, results):
            dp = dst.new_page(width=w, height=h)
            ink = 'q 0.01 0 0 0.01 0 0 cm\n' + ''.join('%.4f %.4f %.4f rg\n' % rgb + '\n'.join(ops) + '\nf\n'
                          for rgb, ops in [((0, 0, 0), layers['black']),
                                           ((0x9A / 255, 0x1E / 255, 0x1E / 255), layers['red'])] if ops) + 'Q\n'
            # The original page rides along, clipped to nothing: it draws no ink but
            # keeps the text searchable and selectable, as in the plain PDF.
            # (keep: the type-only page is shown as it is, under the treated ink.)
            dp.show_pdf_page(dp.rect, basedoc, i)
            xref = dp.get_contents()[0]
            under = dst.xref_stream(xref)
            clip = b'q 0 0 0 0 re W n\n' if a.text == 'outline' else b'q\n'
            dst.update_stream(xref, clip + under + b'\nQ\n' + ink.encode())
            for link in orig[i].get_links():
                link.pop('xref', None)
                try: dp.insert_link(link)
                except Exception: pass
        if len(pages) == len(orig):          # a partial run (--pages) has no outline
            dst.set_toc(orig.get_toc(simple=False))
        dst.set_metadata(orig.metadata)
        dst.save(a.out, garbage=4, deflate=True, use_objstms=1, compression_effort=100)

if __name__ == '__main__':
    main()
