"""Tests of the compositing engine that do not need a PSD."""
import os

import numpy as np
import pytest
from PIL import Image

import engine


def design(w=200, h=100):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    img.paste(Image.new('RGBA', (w, h), (255, 255, 255, 255)), (0, 0))
    return img


@pytest.mark.parametrize('mode', ['contain', 'cover', 'stretch'])
def test_fit_design_respects_the_inner_canvas(mode):
    out = engine.fit_design(design(), 300, 300, mode)
    assert out.size == (300, 300)


def test_contain_centers_and_leaves_a_transparent_margin():
    out = np.asarray(engine.fit_design(design(200, 100), 300, 300, 'contain'))
    alpha = out[..., 3]
    assert alpha[0, 150] == 0 and alpha[150, 150] == 255      # bands above and below, content in the middle
    rows = np.nonzero(alpha[:, 150])[0]
    assert rows.min() == 75 and rows.max() == 224             # 150 px tall, centered


def test_cover_llena_todo_el_lienzo():
    alpha = np.asarray(engine.fit_design(design(200, 100), 300, 300, 'cover'))[..., 3]
    assert alpha.min() == 255


def test_tint_cambia_el_color_y_conserva_la_transparencia():
    src = Image.new('RGBA', (10, 10), (0, 0, 0, 0))
    src.putpixel((5, 5), (255, 255, 255, 128))
    out = engine.tint_design(src, '#1c2030')
    assert out.getpixel((5, 5)) == (0x1c, 0x20, 0x30, 128)
    assert out.getpixel((0, 0))[3] == 0
    assert engine.tint_design(src, None) is src


def test_curva_identidad_no_cambia_nada():
    lut = engine._spline_lut([(0, 0), (128, 128), (255, 255)])
    assert np.allclose(lut * 255, np.arange(256), atol=0.5)


def test_curva_en_s_aumenta_el_contraste():
    lut = engine._spline_lut([(0, 0), (64, 40), (192, 215), (255, 255)])
    assert lut[64] * 255 < 64 and lut[192] * 255 > 192


class Rec:
    def __init__(self, lo=0, hi=255, olo=0, ohi=255, gamma=100):
        self.input_floor, self.input_ceiling, self.output_floor, self.output_ceiling, self.gamma = lo, hi, olo, ohi, gamma


def test_levels():
    assert np.allclose(engine._levels_lut(Rec()) * 255, np.arange(256), atol=0.5)
    lut = engine._levels_lut(Rec(lo=25, hi=230))
    assert lut[25] == 0 and lut[230] == 1


@pytest.mark.skipif(not os.environ.get('MW_TEST_PSD'), reason='set MW_TEST_PSD=path/to.psd for the fidelity test')
def test_fidelity_against_photoshop():
    """Renders the PSD with its original content and compares it with the composite saved by Photoshop."""
    from psd_tools import PSDImage
    path = os.environ['MW_TEST_PSD']
    img, _ = engine.render(path, None, log=lambda m: None)
    ref = np.asarray(PSDImage.open(path).topil().convert('RGB'), np.float32)
    err = np.abs(ref - np.asarray(img, np.float32)).mean()
    assert err < 1.0, f'mean error {err:.2f}/255'


class FakeEnum:
    def __init__(self, v):
        self.enum = v


def test_cylinder_warp_curves_and_compresses_the_edges():
    import numpy as np
    warp = {b'warpStyle': FakeEnum(b'warpCylinder'), b'warpValues': [0, 100, 200, 0, -0.5, -0.5, 1.0]}
    box = np.float32([[0, 0], [200, 0], [200, 100], [0, 100]])
    (src, dst), = engine._cylinder_geometry(warp, box, 200, 100, g=8)
    row = dst[0]
    steps = np.diff(row[:, 0])
    assert steps[0] < steps[len(steps) // 2]          # more compressed at the edge than in the middle
    assert row[len(row) // 2, 1] < row[0, 1]          # the top row curves (middle higher up)
    assert dst[..., 0].min() >= -0.5 and dst[..., 0].max() <= 200.5   # inside the transform box


def test_uniform_mesh_reparametrization_is_identity():
    import numpy as np
    t = np.linspace(0, 1, 11)
    assert np.allclose(engine._reparam([0, 1, 2, 3], t), t)


@pytest.mark.skipif(not os.environ.get('MW_TEST_PSD'), reason='set MW_TEST_PSD=path/to.psd')
def test_analysis_and_one_design_per_object():
    """Analyzes the PSD and composites a different design in each Smart Object."""
    path = os.environ['MW_TEST_PSD']
    info = engine.analyze(path)
    assert info['objects'] and all(o['logo'] in ('light', 'dark', 'original') for o in info['objects'])
    colors = [(255, 0, 0, 255), (0, 0, 255, 255)]
    assignments = {o['uid']: {'design': Image.new('RGBA', (50, 50), colors[i % 2])} for i, o in enumerate(info['objects'])}
    img, _ = engine.render(path, assignments=assignments, log=lambda m: None)
    assert img.size == tuple(info['size'])


@pytest.mark.skipif(not os.environ.get('MW_TEST_PSD'), reason='set MW_TEST_PSD=path/to.psd')
def test_layer_list_and_object_details():
    info = engine.analyze(os.environ['MW_TEST_PSD'])
    assert info['layers'] and all('name' in l and 'blend' in l for l in info['layers'])
    assert all('warp' in o and o['instances'] for o in info['objects'])
