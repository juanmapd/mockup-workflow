#!/usr/bin/env python3
"""
CLI: replace the Smart Object of a PSD mockup with an image and export to PNG (no Photoshop needed).

  python mockup.py [mockup.psd] [design.png] [result.png] [--fit contain|cover|stretch] [--check]

The default paths are on ~/Desktop (see --help).
--check composites the mockup with its original content and compares it with the composite Photoshop saved.
"""
import argparse
import os

import numpy as np
from PIL import Image
from psd_tools import PSDImage

import engine
from version import APP_NAME, __version__

D = os.path.expanduser('~/Desktop')
ap = argparse.ArgumentParser(description=f'{APP_NAME}: place a design on a PSD mockup without Photoshop.',
                             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
ap.add_argument('--version', action='version', version=f'{APP_NAME} {__version__}')
ap.add_argument('psd', nargs='?', default=os.path.join(D, 'mockup.psd'), help='PSD mockup')
ap.add_argument('design', nargs='?', default=os.path.join(D, 'dise\u00f1o.png'), help='design image')
ap.add_argument('out', nargs='?', default=os.path.join(D, 'resultado.png'), help='output PNG')
ap.add_argument('--fit', choices=['contain', 'cover', 'stretch'], default='contain',
                help='how the design fits the Smart Object canvas')
ap.add_argument('--check', action='store_true',
                help='render the original content and compare it with the composite saved by Photoshop')
a = ap.parse_args()

if a.check:
    img, _ = engine.render(a.psd, None)
    ref = np.asarray(PSDImage.open(a.psd).topil().convert('RGB'), np.float32)
    diff = np.abs(ref - np.asarray(img, np.float32))
    print(f'Mean error {diff.mean():.2f}/255 · p99 {np.percentile(diff, 99):.1f} · '
          f'pixels >10: {(diff.max(2) > 10).mean() * 100:.2f}%')
else:
    img, _ = engine.render(a.psd, Image.open(a.design), a.fit)
    img.save(a.out)
    print('Done ->', a.out)
