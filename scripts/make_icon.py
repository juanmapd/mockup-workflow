#!/usr/bin/env python3
"""Generate the app icon (assets/icon-1024.png, assets/MockupWorkflow.icns) and the Demo flow designs:
static/demo-design.png (logo) and static/demo-monogram.svg + .png (white "MW" monogram).
Usage: python scripts/make_icon.py   (needs fonttools: requirements-dev.txt)"""
import os
import shutil
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ASSETS = os.path.join(ROOT, 'assets')
S = 1024


# "Layers" glyph (24-unit grid): a rhombus and two identical layers cut by a constant gap, all with sharp
# edges. They are the same polygons the UI uses (static/app.js, "logo" icon) and the splash screen.
GLYPH = [
    [(3, 7.5), (12, 3), (21, 7.5), (12, 12)],
    [(3, 12), (6.2, 10.4), (12, 13.3), (17.8, 10.4), (21, 12), (12, 16.5)],
    [(3, 16.5), (6.2, 14.9), (12, 17.8), (17.8, 14.9), (21, 16.5), (12, 21)],
]


def draw_glyph(size, color=(255, 255, 255, 255), inset=0.0):
    """The glyph on a square canvas of `size` px (with an `inset` px margin), supersampled for crisp edges."""
    k = 4
    g = Image.new('RGBA', (size * k, size * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(g)
    sc = (size - 2 * inset) * k / 18          # the glyph spans x 3..21 -> 18 units
    ox = inset * k - 3 * sc
    oy = (size * k - 18 * sc) / 2 - 3 * sc    # y 3..21, centered
    for poly in GLYPH:
        d.polygon([(ox + x * sc, oy + y * sc) for x, y in poly], fill=color)
    return g.resize((size, size), Image.LANCZOS)


def draw():
    x0, y0, x1, y1, radius = 100, 100, 924, 924, 185
    body = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(body)
    for i in range(y1 - y0):   # vertical indigo gradient
        t = i / (y1 - y0 - 1)
        d.line([(x0, y0 + i), (x1, y0 + i)], fill=(int(92 - 22 * t), int(86 - 25 * t), int(246 - 20 * t), 255))
    mask = Image.new('L', (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=255)
    icon = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    icon.paste(body, (0, 0), mask)
    shadow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle((x0, y0 + 18, x1, y1 + 18), radius=radius, fill=(20, 18, 60, 90))
    icon = Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(22)), icon)
    glyph = draw_glyph(560)
    icon.alpha_composite(glyph, ((S - 560) // 2, (S - 560) // 2))
    return icon


DEMO_FONT = '/System/Library/Fonts/Avenir Next.ttc'   # index 0: Avenir Next Bold


def draw_demo():
    """
    Demo flow design: the white layers glyph with "Mockup Workflow" below it, no background and a wide
    transparent margin so it breathes inside any Smart Object.
    """
    W, H = 2400, 2000
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    glyph = draw_glyph(820)
    d = ImageDraw.Draw(out)
    text = 'Mockup Workflow'
    size = 210
    while True:   # shrink the type until the text fits in 85% of the canvas width
        font = ImageFont.truetype(DEMO_FONT, size, index=0)
        l, t, r, b = d.textbbox((0, 0), text, font=font)
        if r - l <= 0.85 * W or size <= 40:
            break
        size -= 5
    gap = 70
    block = glyph.getbbox()[3] - glyph.getbbox()[1] + gap + (b - t)
    y0 = (H - block) // 2 - glyph.getbbox()[1]
    out.alpha_composite(glyph, ((W - glyph.width) // 2, y0))
    d.text(((W - (r - l)) // 2 - l, y0 + glyph.getbbox()[3] + gap - t), text, font=font, fill=(255, 255, 255, 255))
    return out


MONO_W, MONO_H, MONO_CAP = 1600, 1000, 560     # monogram canvas and cap height, in px
MONO_FIT = 0.8                                 # max share of the canvas width the letters may take


def monogram_layout(text='MW'):
    """Letter outlines (Avenir Next Bold) centered on the canvas: (SVG d, font size, x origin, baseline)."""
    from fontTools.pens.boundsPen import BoundsPen
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont
    font = TTFont(DEMO_FONT, fontNumber=0)
    gs, cmap = font.getGlyphSet(), font.getBestCmap()
    names = [cmap[ord(c)] for c in text]
    cap = font['OS/2'].sCapHeight or font['head'].unitsPerEm * 0.7
    # word width from each letter's advance plus the actual bounds of the last one (font units)
    adv = [gs[n].width for n in names]
    bp = BoundsPen(gs)
    gs[names[-1]].draw(bp)
    bp0 = BoundsPen(gs)
    gs[names[0]].draw(bp0)
    ink_units = sum(adv[:-1]) + bp.bounds[2] - bp0.bounds[0]   # from the first letter's left edge to the last's right edge
    scale = min(MONO_CAP / cap, MONO_FIT * MONO_W / ink_units)   # wide letters (W) shrink to keep a margin
    ink = ink_units * scale
    x0 = (MONO_W - ink) / 2 - bp0.bounds[0] * scale
    base = (MONO_H + cap * scale) / 2
    pen = SVGPathPen(gs)
    x = x0
    for n, a in zip(names, adv):
        gs[n].draw(TransformPen(pen, (scale, 0, 0, -scale, x, base)))
        x += a * scale
    return pen.getCommands(), font['head'].unitsPerEm * scale, x0, base


def draw_monogram():
    """White "MW" monogram: SVG with the letters converted to paths (no font dependency) and its PNG."""
    d, size, x0, base = monogram_layout()
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {MONO_W} {MONO_H}" width="{MONO_W}" height="{MONO_H}">\n'
           f'  <title>Mockup Workflow, MW monogram</title>\n  <path fill="#ffffff" d="{d}"/>\n</svg>\n')
    k = 2
    img = Image.new('RGBA', (MONO_W * k, MONO_H * k), (0, 0, 0, 0))
    font = ImageFont.truetype(DEMO_FONT, round(size * k), index=0)
    ImageDraw.Draw(img).text((x0 * k, base * k), 'MW', font=font, fill=(255, 255, 255, 255), anchor='ls')
    return svg, img.resize((MONO_W, MONO_H), Image.LANCZOS)


def main():
    os.makedirs(ASSETS, exist_ok=True)
    png = os.path.join(ASSETS, 'icon-1024.png')
    draw().save(png)
    iconset = os.path.join(ASSETS, 'icon.iconset')
    shutil.rmtree(iconset, ignore_errors=True)
    os.makedirs(iconset)
    img = Image.open(png)
    for s in (16, 32, 128, 256, 512):
        img.resize((s, s), Image.LANCZOS).save(os.path.join(iconset, f'icon_{s}x{s}.png'))
        img.resize((s * 2, s * 2), Image.LANCZOS).save(os.path.join(iconset, f'icon_{s}x{s}@2x.png'))
    subprocess.run(['iconutil', '-c', 'icns', iconset, '-o', os.path.join(ASSETS, 'MockupWorkflow.icns')], check=True)
    shutil.rmtree(iconset)
    draw_demo().save(os.path.join(ROOT, 'static', 'demo-design.png'))
    svg, png = draw_monogram()
    with open(os.path.join(ROOT, 'static', 'demo-monogram.svg'), 'w', encoding='utf-8') as f:
        f.write(svg)
    png.save(os.path.join(ROOT, 'static', 'demo-monogram.png'))
    print('Icon written to assets/ and demo designs to static/ (demo-design.png, demo-monogram.svg/.png)')


if __name__ == '__main__':
    main()
