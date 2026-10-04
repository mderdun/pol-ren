#!/usr/bin/env python3
"""Experiment: bake the plate-and-paper finish into a copy of Junicode, so that
type is textured by the font itself and stays live text in the PDF.

    tools/texture_font.py IN.otf OUT.otf [--size 11] [--strength 1.5] [--seed 1611]

Each glyph outline is reshaped as tools/novello_vector.py reshapes a mark on
the page (ink gain, rounded corners, an edge that wanders with a paper-fibre
field, the odd pore), at the given design size in points. The result is a new
font family, "Junicode Pressed". Junicode is under the SIL Open Font License
1.1, which allows modified versions provided they stay under the OFL and are
not sold on their own; the copyright notice and licence are kept, and the
family is renamed so that it is never mistaken for Peter Baker's original.
"""
import argparse, sys, os
import numpy as np
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from shapely.geometry import Polygon
from shapely.ops import unary_union, orient

sys.path.insert(0, os.path.dirname(__file__))
import novello_vector as nv

class FlatPen(BasePen):
    """Collects contours as point lists, flattening curves."""
    def __init__(self, glyphset):
        super().__init__(glyphset); self.contours = []; self.cur = []
    def _moveTo(self, p): self.cur = [p]
    def _lineTo(self, p): self.cur.append(p)
    def _curveToOne(self, p1, p2, p3):
        p0 = self.cur[-1]
        for t in np.linspace(0, 1, 9)[1:]:
            self.cur.append(tuple((1-t)**3*np.array(p0) + 3*(1-t)**2*t*np.array(p1) + 3*(1-t)*t**2*np.array(p2) + t**3*np.array(p3)))
    def _closePath(self):
        if len(self.cur) >= 3: self.contours.append(self.cur)
        self.cur = []
    _endPath = _closePath

def outline(glyph, glyphset, tt=False):
    pen = FlatPen(glyphset); glyph.draw(pen)
    polys = [Polygon(c) for c in pen.contours]
    polys = [p for p in polys if p.is_valid or p.buffer(0).area > 0]
    if not polys: return None
    # outer contours run counter-clockwise in CFF, clockwise in TrueType
    signed = [(p, Polygon(p.exterior).exterior.is_ccw != tt) for p in polys]
    pos = unary_union([p.buffer(0) for p, ccw in signed if ccw])
    neg = unary_union([p.buffer(0) for p, ccw in signed if not ccw])
    if pos.is_empty: pos, neg = neg, pos
    return pos.difference(neg) if not neg.is_empty else pos

def draw(geom, pen, tol=0.5, tt=False):
    polys = [geom] if geom.geom_type == 'Polygon' else [g for g in getattr(geom, 'geoms', []) if g.geom_type == 'Polygon']
    for p in polys:
        p = orient(p.simplify(tol, preserve_topology=True), -1.0 if tt else 1.0)   # outer ccw (PostScript), cw (TrueType)
        for ring in [p.exterior] + list(p.interiors):
            c = [(round(x), round(y)) for x, y in ring.coords[:-1]]
            if len(c) < 3: continue
            pen.moveTo(c[0])
            for q in c[1:]: pen.lineTo(q)
            pen.closePath()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--size', type=float, default=11.0)
    ap.add_argument('--strength', type=float, default=1.5)
    ap.add_argument('--seed', type=int, default=1611)
    ap.add_argument('--tolerance', type=float, default=0.03,
                    help='outline simplification at the design size, in points (as on the page)')
    ap.add_argument('--family', default='Junicode Pressed')
    ap.add_argument('--rename', help='the original family name to replace (default: from the name table)')
    a = ap.parse_args()
    font = TTFont(a.inp)
    upm = font['head'].unitsPerEm
    s = a.size / upm                     # font units -> points at the design size
    gs = font.getGlyphSet()
    tt = 'glyf' in font
    if tt:
        # TrueType (the Gregorio chant font): hinting refers to the old points, so it goes
        for t in ('cvt ', 'fpgm', 'prep', 'hdmx', 'LTSH', 'VDMX'):
            if t in font: del font[t]
    else:
        cff = font['CFF '].cff; top = cff.topDictIndex[0]
        cff.desubroutinize()      # every outline is redrawn; the old subroutines would only ride along
        cs = top.CharStrings
    new = {}
    rng = np.random.default_rng(a.seed)
    span = 3 * upm * s                   # noise fields over a 3-em square
    press = nv.field(span, span, 50 * nv.MM, rng)
    fib = nv.field(span, span, 0.22 * nv.MM, rng)
    wander = nv.field(span, span, 1.1 * nv.MM, rng)
    from shapely import affinity
    done = 0
    for name in font.getGlyphOrder():
        g = gs[name]
        geom = outline(g, gs, tt)
        if geom is None or geom.is_empty: continue
        # to points, shifted into the noise fields; each glyph samples its own patch
        ox, oy = rng.uniform(0.2, 1.8) * upm * s, rng.uniform(0.2, 1.8) * upm * s
        pt = affinity.affine_transform(geom, [s, 0, 0, s, ox + upm * s * 0.5, oy + upm * s * 0.5])
        pt = nv.treat(pt, a.strength, press, fib, wander, rng)
        back = affinity.affine_transform(pt, [1 / s, 0, 0, 1 / s, -(ox + upm * s * 0.5) / s, -(oy + upm * s * 0.5) / s])
        width = font['hmtx'][name][0]
        if tt:
            pen = TTGlyphPen(None)
            draw(back, pen, a.tolerance / s, tt=True)
            new[name] = pen.glyph()
        else:
            pen = T2CharStringPen(width, gs)
            draw(back, pen, a.tolerance / s)
            cs[name] = pen.getCharString(private=cs[name].private, globalSubrs=cs[name].globalSubrs)
        done += 1
    if tt:   # after the loop: the glyph set reads the old outlines until then
        glyf = font['glyf']
        for name, gl in new.items():
            glyf[name] = gl
            gl.recalcBounds(glyf)
            font['hmtx'][name] = (font['hmtx'][name][0], getattr(gl, 'xMin', 0))
    # names: a different family, same copyright and licence. The original
    # family name is replaced wherever it occurs (Junicode Exp -> Junicode
    # Pressed Exp; Junicode-Exp -> JunicodePressed-Exp; Emmentaler-20 -> Pressed-20),
    # so every style keeps a distinct name.
    old = a.rename or font['name'].getDebugName(16) or font['name'].getDebugName(1).split()[0].split('-')[0]
    def ren(t):
        return t.replace(old.replace(' ', ''), a.family.replace(' ', '')) if ' ' not in t and '-' in t \
            else t.replace(old, a.family)
    for rec in font['name'].names:
        if rec.nameID in (1, 4, 6, 16):
            rec.string = ren(rec.toUnicode())
        elif rec.nameID == 3:
            rec.string = ren(font['name'].getDebugName(6)) + ';pol-ren'
    if not tt:
        cff.fontNames = [ren(n) for n in cff.fontNames]
        if hasattr(top, 'FullName'): top.FullName = ren(top.FullName)
        if hasattr(top, 'FamilyName'): top.FamilyName = ren(top.FamilyName)
    font.save(a.out)
    print(f'{done} glyphs textured -> {a.out}')

if __name__ == '__main__':
    main()
