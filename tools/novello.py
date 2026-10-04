#!/usr/bin/env python3
"""Experiment: print an edition as if from engraved plates on soft paper,
in the manner of a late-Victorian octavo (Novello and the like).

    tools/novello.py IN.pdf OUT.pdf [--pages 1-2] [--dpi 600] [--paper] [--seed N]

The page is rasterised and the ink is treated, not the music:
  - ink gain: every mark spreads a little into the paper, more on its edges
    than its middle, so thin lines thicken and corners round off;
  - bleed: the spread is uneven, driven by a paper-fibre noise field, so
    edges are soft and slightly ragged rather than mathematically clean;
  - inking: plate pressure varies across the page in broad, faint patches;
    solid heads and beams show the odd pale pore where ink did not take;
  - paper (optional): a faint warm tone and grain. Off by default, since the
    house allows only black, white and the one red.
Red ink is kept red; it gets the same bleed. The result is a raster PDF.
Same seed, same page: the texture is generative but repeatable.
"""
import argparse, subprocess, tempfile, glob, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

RED = np.array([0x9A, 0x1E, 0x1E], np.float32) / 255

def noise(shape, scale, rng, octaves=3):
    """Smooth value noise in [0,1], features about `scale` px across."""
    h, w = shape
    out = np.zeros(shape, np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        s = max(2, int(scale / 2 ** o))
        g = rng.random((h // s + 3, w // s + 3), dtype=np.float32)
        up = ndi.zoom(g, s, order=3)[:h, :w]
        out += amp * up; tot += amp; amp *= 0.5
    out /= tot
    return (out - out.min()) / (np.ptp(out) + 1e-9)

def treat(rgb, dpi, rng, paper, strength=1.0):
    a = rgb.astype(np.float32) / 255
    ink = 1 - a.min(axis=2)                       # 0 paper .. 1 full ink
    redness = np.clip((a[..., 0] - a[..., 1]) * 2.5, 0, 1) * (ink > 0.05)
    px = dpi / 25.4                               # pixels per mm
    k = strength
    # warp: the plate and paper are not perfectly flat; edges wander a little
    h, w = ink.shape
    dy = (noise(ink.shape, 1.2 * px, rng, 2) - 0.5) * 0.06 * px * k
    dx = (noise(ink.shape, 1.2 * px, rng, 2) - 0.5) * 0.06 * px * k
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    ink = ndi.map_coordinates(ink, [yy + dy, xx + dx], order=1, mode='nearest')
    del yy, xx, dy, dx
    fib = noise(ink.shape, 0.25 * px, rng, 2)     # paper fibre, ~0.25 mm
    # ink gain and bleed: blur the ink, then re-threshold against the fibres
    spread = ndi.gaussian_filter(ink, 0.06 * px * k)
    thr = 0.40 - 0.06 * k + 0.22 * k * (fib - 0.5)   # fibres pull ink unevenly
    hard = np.clip((spread - thr) / 0.12 + 0.5, 0, 1)
    out = np.maximum(hard, ink * 0.85)            # never lose a printed mark
    out = ndi.gaussian_filter(out, 0.025 * px)    # soften the new edge
    halo = ndi.gaussian_filter(ink, 0.16 * px) * 0.10 * k   # faint wick into the paper
    out = np.maximum(out, halo)
    # plate pressure: broad faint patches; pores in solid areas
    press = 0.90 + 0.10 * noise(ink.shape, 18 * px, rng, 2)
    solid = ndi.binary_erosion(ink > 0.8, iterations=max(1, int(0.08 * px)))
    pores = (rng.random(ink.shape, dtype=np.float32) < 0.0025) & solid
    pores = ndi.binary_dilation(pores, iterations=max(1, int(0.03 * px)))
    out = out * press * np.where(pores, 0.72, 1.0)
    # colour: black ink is a very dark warm black; red stays the house red
    red = ndi.gaussian_filter(redness, 0.05 * px)
    inkcol = (1 - red)[..., None] * np.array([0.07, 0.06, 0.06], np.float32) + red[..., None] * RED
    base = np.ones_like(a)
    if paper:
        tone = np.array([0.985, 0.968, 0.930])
        grain = 1 - 0.025 * noise(ink.shape, 0.6 * px, rng, 2)[..., None]
        base = base * tone * grain
    res = base * (1 - out[..., None]) + inkcol * out[..., None]
    return (np.clip(res, 0, 1) * 255).astype(np.uint8)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('inp'); ap.add_argument('out')
    ap.add_argument('--pages'); ap.add_argument('--dpi', type=int, default=450)
    ap.add_argument('--paper', action='store_true'); ap.add_argument('--strength', type=float, default=1.2); ap.add_argument('--seed', type=int, default=1611)
    a = ap.parse_args()
    with tempfile.TemporaryDirectory() as d:
        cmd = ['pdftoppm', '-r', str(a.dpi), '-png']
        if a.pages:
            f, _, l = a.pages.partition('-'); cmd += ['-f', f, '-l', l or f]
        subprocess.run(cmd + [a.inp, f'{d}/p'], check=True)
        outs = []
        for i, f in enumerate(sorted(glob.glob(f'{d}/p-*.png'))):
            rng = np.random.default_rng(a.seed + i)
            img = treat(np.array(Image.open(f).convert('RGB')), a.dpi, rng, a.paper, a.strength)
            o = f'{d}/n-{i:03d}.jpg'
            Image.fromarray(img).save(o, quality=92, dpi=(a.dpi, a.dpi))
            outs.append(o)
        import img2pdf
        with open(a.out, 'wb') as fh:
            fh.write(img2pdf.convert(outs))

if __name__ == '__main__':
    main()
