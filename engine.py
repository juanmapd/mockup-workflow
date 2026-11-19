"""
PSD mockup compositing engine, no Photoshop required.

Builds on the psd-tools compositor (all blend modes, isolated and "pass through" groups, layer and vector
masks, clipping, fill layers, overlays and stroke) and adds:
  - Replacing Smart Object contents, honoring their transform (perspective) and custom warp
    (4x4 Bezier mesh).
  - Levels and Curves adjustment layers.
  - Drop Shadow, Inner Shadow, Outer Glow and Inner Glow effects (approximated).
Every instance of the same Smart Object (same unique_id) receives the new contents.
"""
import io
import os
import threading
import warnings

import cv2
import numpy as np
import psd_tools.composite as ptc
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import AdjustmentLayer, GroupMixin, SmartObjectLayer
from psd_tools.constants import Resource, Tag

warnings.filterwarnings('ignore')
_LOCK = threading.Lock()   # the compositor is patched at module level: one composite at a time
_CTX = {}


# ================================================================ design fitting
def tint_design(design, color):
    """Recolor the design (PIL RGBA) with a flat '#rrggbb' color, keeping its transparency."""
    if not color:
        return design
    c = color.lstrip('#')
    rgb = tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))
    flat = Image.new('RGBA', design.size, rgb + (255,))
    flat.putalpha(design.getchannel('A'))
    return flat


def fit_design(design, cw, ch, mode='contain'):
    """Fit the design (PIL RGBA) to the Smart Object's inner canvas (cw x ch)."""
    dw, dh = design.size
    if mode == 'stretch':
        return design.resize((cw, ch), Image.LANCZOS)
    s = (min if mode == 'contain' else max)(cw / dw, ch / dh)
    nw, nh = max(1, round(dw * s)), max(1, round(dh * s))
    scaled = design.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('RGBA', (cw, ch), (0, 0, 0, 0))
    if mode == 'contain':
        canvas.alpha_composite(scaled, ((cw - nw) // 2, (ch - nh) // 2))
    else:
        l, t = (nw - cw) // 2, (nh - ch) // 2
        canvas.alpha_composite(scaled.crop((l, t, l + cw, t + ch)))
    return canvas


# ================================================================ Smart Object geometry
def _bezier_basis(t):
    t = np.asarray(t, np.float64)
    return np.stack([(1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t ** 2 * (1 - t), t ** 3], -1)


def _reparam(c, t):
    """Relative position (0..1) along a 1D Bezier curve with control points c, for each t."""
    x = _bezier_basis(t) @ np.asarray(c, np.float64)
    span = x[-1] - x[0]
    return t if abs(span) < 1e-6 else np.clip((x - x[0]) / span, 0, 1)


def _so_warp_desc(so):
    """Active Smart Object warp: the quilt warp (quiltWarp) if present and custom, otherwise the classic one."""
    data = so._config.data if so._config is not None else {}
    quilt = data.get(b'quiltWarp')
    if quilt is not None and getattr(quilt.get(b'warpStyle'), 'enum', None) == b'warpCustom':
        return quilt, True
    return data.get(b'warp') or {}, False


CYLINDER_SAG = 1.11   # ellipse scale, tuned against Photoshop composites (coffee cup: error 10.5 -> 2.6)


def _cylinder_geometry(warp, box, cw, ch, g=64):
    """
    Photoshop "Cylinder" warp (approximated; Adobe does not document the model).
    warpValues = [top, bottom, right, left, top ellipse, bottom ellipse, wrap].
    The content is projected onto half a cylinder (sinusoidal compression towards the edges) and each row bends
    along an ellipse that goes from the top one to the bottom one. The transform box encloses the result.
    """
    top, bot, right, left, e_top, e_bot, wrap = (list(warp[b'warpValues']) + [1.0] * 7)[:7]
    W, H = (right - left) or cw, (bot - top) or ch
    t = np.linspace(0, 1, g + 1)
    U, V = np.meshgrid(t, t)
    wrap = min(max(float(wrap), 0.05), 1.0)
    xs = W * (1 - np.cos(np.pi * U * wrap)) / (1 - np.cos(np.pi * wrap))
    sag = ((1 - V) * e_top + V * e_bot) * CYLINDER_SAG * W / 2 * np.sin(np.pi * U)
    pts = np.stack([xs, H * V + sag], -1)
    (rx0, ry0), (rx1, ry1) = pts.reshape(-1, 2).min(0), pts.reshape(-1, 2).max(0)
    Hm = cv2.getPerspectiveTransform(np.float32([[rx0, ry0], [rx1, ry0], [rx1, ry1], [rx0, ry1]]), box)
    dst = cv2.perspectiveTransform(pts.reshape(-1, 1, 2).astype(np.float32), Hm).reshape(pts.shape)
    return [(np.stack([U * cw, V * ch], -1), dst)]


def _so_geometry(so, cw, ch, samples=48):
    """
    List of patches (src, dst): point grids in content pixels and their position in the document.
    None if the Smart Object has no custom warp (a homography is enough).
    """
    box = np.float32(so.transform_box).reshape(4, 2)
    warp, quilt = _so_warp_desc(so)
    style = getattr(warp.get(b'warpStyle'), 'enum', b'warpNone')
    if style == b'warpCylinder' and warp.get(b'warpValues') is not None:
        return _cylinder_geometry(warp, box, cw, ch), style
    if style != b'warpCustom':
        return None, style
    env = warp[b'customEnvelopeWarp']
    mesh = env[b'meshPoints']
    xs, ys = np.float64(list(mesh[b'Hrzn'])), np.float64(list(mesh[b'Vrtc']))
    b = warp.get(b'bounds', {})
    bl, bt = float(b.get(b'Left', 0)), float(b.get(b'Top ', 0))
    bw = float(b.get(b'Rght', cw)) - bl
    bh = float(b.get(b'Btom', ch)) - bt
    if quilt:
        slx = np.float64(list(env[b'quiltSliceX'][b'quiltSliceX']))
        sly = np.float64(list(env[b'quiltSliceY'][b'quiltSliceY']))
        ox, oy = bl, bt
    else:
        slx, sly = np.float64([bl, bl + bw]), np.float64([bt, bt + bh])
    nx, ny = 3 * (len(slx) - 1) + 1, 3 * (len(sly) - 1) + 1
    if xs.size != nx * ny:
        return None, b'warpUnsupportedMesh'
    P = np.stack([xs, ys], -1).reshape(ny, nx, 2)
    if not quilt:
        # The classic mesh lives in the original placement space: its origin is the corner of the corners.
        corners = P[[0, 0, -1, -1], [0, -1, -1, 0]]
        ox, oy = corners[:, 0].min(), corners[:, 1].min()
        slx, sly = slx - bl + ox, sly - bt + oy
    n_patches = (len(slx) - 1) * (len(sly) - 1)
    g = max(6, int(samples / max(1, np.sqrt(n_patches))))
    t = np.linspace(0, 1, g + 1)
    B = _bezier_basis(t)
    surf = []
    for py in range(len(sly) - 1):
        for px in range(len(slx) - 1):
            ctrl = P[3 * py:3 * py + 4, 3 * px:3 * px + 4]
            pts = np.einsum('vi,uj,ijk->vuk', B, B, ctrl)
            # equivalent position in the content (slices are in placement coordinates)
            tu, tv = t, t
            if quilt:
                # Photoshop walks each patch by the mean position of its guides, not uniformly:
                # with handles away from 1/3 and 2/3 the content does not slide along the mesh.
                tu = _reparam(ctrl[:, :, 0].mean(0), t)
                tv = _reparam(ctrl[:, :, 1].mean(1), t)
            sx = (slx[px] + tu * (slx[px + 1] - slx[px]) - ox) / bw * cw
            sy = (sly[py] + tv * (sly[py + 1] - sly[py]) - oy) / bh * ch
            gx, gy = np.meshgrid(np.clip(sx, 0, cw), np.clip(sy, 0, ch))
            surf.append((np.stack([gx, gy], -1), pts))
    if quilt:
        # In a quilt warp the transform box encloses the already warped mesh.
        allp = P.reshape(-1, 2)
        rx0, ry0 = allp.min(0)
        rx1, ry1 = allp.max(0)
    else:
        rx0, ry0, rx1, ry1 = ox, oy, ox + bw, oy + bh
    Hm = cv2.getPerspectiveTransform(np.float32([[rx0, ry0], [rx1, ry0], [rx1, ry1], [rx0, ry1]]), box)
    patches = [(src, cv2.perspectiveTransform(pts.reshape(-1, 1, 2).astype(np.float32), Hm).reshape(pts.shape))
               for src, pts in surf]
    return patches, style


def _warp_content(content, so, W, H):
    """Project the Smart Object content (PIL RGBA) onto the document. Returns (rgb, alpha, style); rgb/alpha float32 HxW."""
    c = np.asarray(content, np.float32) / 255.0
    ch, cw = c.shape[:2]
    pre = c.copy()
    pre[..., :3] *= pre[..., 3:4]
    geom, style = _so_geometry(so, cw, ch)
    if geom is None:
        src = np.float32([[0, 0], [cw, 0], [cw, ch], [0, ch]])
        M = cv2.getPerspectiveTransform(src, np.float32(so.transform_box).reshape(4, 2))
        out = cv2.warpPerspective(pre, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    else:
        out = np.zeros((H, W, 4), np.float32)
        for src, dst in geom:
            _mesh_warp(pre, src, dst, out)
    out = np.clip(out, 0, 1)
    a = out[..., 3]
    rgb = np.where(a[..., None] > 1e-6, out[..., :3] / np.maximum(a[..., None], 1e-6), 0)
    return np.clip(rgb, 0, 1), a, style


def _mesh_warp(pre, src, dst, out):
    """Triangle mesh warp: each grid cell is transformed with an affine map (writes into out)."""
    H, W = out.shape[:2]
    n = src.shape[0] - 1
    for i in range(n):
        for j in range(n):
            for tri in (((i, j), (i, j + 1), (i + 1, j + 1)), ((i, j), (i + 1, j + 1), (i + 1, j))):
                s = np.float32([src[p] for p in tri])
                d = np.float32([dst[p] for p in tri])
                x0, y0 = np.floor(d.min(0)).astype(int) - 1
                x1, y1 = np.ceil(d.max(0)).astype(int) + 2
                x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
                if x1 <= x0 or y1 <= y0:
                    continue
                M = cv2.getAffineTransform(s, d - np.float32([x0, y0]))
                patch = cv2.warpAffine(pre, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                                       borderMode=cv2.BORDER_REPLICATE)
                mask = np.zeros((y1 - y0, x1 - x0), np.uint8)
                cv2.fillConvexPoly(mask, np.round((d - [x0, y0]) * 16).astype(np.int32), 1, cv2.LINE_8, 4)
                m = mask.astype(bool)
                out[y0:y1, x0:x1][m] = patch[m]
    return out


# ================================================================ smart filters
FILTER_NAMES = {b'GsnB': 'Gaussian Blur', b'MtnB': 'Motion Blur', b'BxBl': 'Box Blur'}


def smart_filters(layer):
    """Smart filters of a Smart Object layer: [(key, name, params, enabled)]."""
    data = None
    for tag in (Tag.SMART_OBJECT_LAYER_DATA1, Tag.SMART_OBJECT_LAYER_DATA2):
        d = layer.tagged_blocks.get_data(tag) if layer.tagged_blocks else None
        if d is not None:
            data = getattr(d, 'data', d)
            break
    ff = data.get(b'filterFX') if hasattr(data, 'get') else None
    if not ff or not bool(ff.get(b'enab', True)):
        return []
    out = []
    for f in ff.get(b'filterFXList') or []:
        fl = f.get(b'Fltr')
        key = getattr(fl, 'classID', b'') or b''
        name = FILTER_NAMES.get(key) or str(f.get(b'Nm  ') or key).strip(" '\x00.")
        params = {k.decode(errors='ignore').strip(): float(v) for k, v in (fl.items() if hasattr(fl, 'items') else [])
                  if isinstance(v, (int, float)) or hasattr(v, 'value')}
        out.append((key, name, params, bool(f.get(b'enab', True))))
    return out


def filter_label(f):
    """Human-readable filter label, e.g. 'Gaussian Blur 3 px' or 'Motion Blur 10 px, 45°'."""
    key, name, p, _ = f
    if key in (b'GsnB', b'BxBl') and p.get('Rds'):
        return f'{name} {p["Rds"]:g} px'
    if key == b'MtnB' and p.get('Dstn'):
        return f'{name} {p["Dstn"]:g} px, {p.get("Angl", 0):g}°'
    return name


def _apply_smart_filters(layer, rgb, a, warn):
    """Apply the layer's blur smart filters to the already projected layer (document space)."""
    filters = [f for f in smart_filters(layer) if f[3]]
    if not filters:
        return rgb, a
    pre = np.concatenate([rgb * a[..., None], a[..., None]], -1).astype(np.float32)
    for key, name, p, _ in filters:
        if key == b'GsnB':
            r = p.get('Rds', 0)
            if r > 0:
                pre = cv2.GaussianBlur(pre, (0, 0), sigmaX=r)
        elif key == b'BxBl':
            r = int(round(p.get('Rds', 0)))
            if r > 0:
                pre = cv2.blur(pre, (2 * r + 1, 2 * r + 1))
        elif key == b'MtnB':
            dist, ang = int(round(p.get('Dstn', 0))), np.deg2rad(p.get('Angl', 0))
            if dist > 1:
                k = np.zeros((2 * dist + 1, 2 * dist + 1), np.float32)
                c = dist
                dx, dy = np.cos(ang), -np.sin(ang)
                for t in np.linspace(-dist / 2, dist / 2, 2 * dist + 1):
                    k[int(round(c + t * dy)), int(round(c + t * dx))] = 1
                pre = cv2.filter2D(pre, -1, k / k.sum())
        else:
            warn(f'smart filter "{name}" on "{layer.name}" is not supported; skipped')
    a2 = pre[..., 3]
    rgb2 = np.where(a2[..., None] > 1e-6, pre[..., :3] / np.maximum(a2[..., None], 1e-6), 0)
    return np.clip(rgb2, 0, 1), np.clip(a2, 0, 1)


# ================================================================ adjustments
def _spline_lut(points):
    """0..255 LUT from (input, output) points using a natural cubic spline (like Photoshop)."""
    pts = sorted({int(x): int(y) for x, y in points}.items())
    x = np.float64([p[0] for p in pts])
    y = np.float64([p[1] for p in pts])
    xs = np.arange(256, dtype=np.float64)
    if len(x) < 3:
        return np.clip(np.interp(xs, x, y), 0, 255) / 255.0
    n = len(x)
    h = np.diff(x)
    A = np.zeros((n, n))
    r = np.zeros(n)
    A[0, 0] = A[-1, -1] = 1
    for i in range(1, n - 1):
        A[i, i - 1], A[i, i], A[i, i + 1] = h[i - 1], 2 * (h[i - 1] + h[i]), h[i]
        r[i] = 3 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])
    c = np.linalg.solve(A, r)
    idx = np.clip(np.searchsorted(x, xs) - 1, 0, n - 2)
    dx = xs - x[idx]
    b = (y[idx + 1] - y[idx]) / h[idx] - h[idx] * (2 * c[idx] + c[idx + 1]) / 3
    d = (c[idx + 1] - c[idx]) / (3 * h[idx])
    val = y[idx] + b * dx + c[idx] * dx ** 2 + d * dx ** 3
    val = np.where(xs < x[0], y[0], np.where(xs > x[-1], y[-1], val))
    return np.clip(val, 0, 255) / 255.0


def _apply_lut(col, lut):
    return np.interp(col, np.linspace(0, 1, 256), lut).astype(np.float32)


def _levels_lut(rec):
    v = np.arange(256, dtype=np.float64)
    lo, hi = rec.input_floor, max(rec.input_ceiling, rec.input_floor + 1)
    x = np.clip((v - lo) / (hi - lo), 0, 1) ** (1.0 / max(rec.gamma / 100.0, 0.01))
    return np.clip(rec.output_floor + x * (rec.output_ceiling - rec.output_floor), 0, 255) / 255.0


def _adjust(layer, col, warn):
    """Apply an adjustment layer to a color array (H,W,3). Returns None if it is not supported."""
    kind = layer.kind
    out = col.copy()
    if kind == 'levels':
        recs = list(layer.data)
        for ch in range(3):
            if ch + 1 < len(recs):
                out[..., ch] = _apply_lut(out[..., ch], _levels_lut(recs[ch + 1]))
        if recs:
            out = _apply_lut(out, _levels_lut(recs[0]))
        return out
    if kind == 'curves':
        d = layer.data
        items = [(it.channel_id, it.points) for it in (d.extra or [])]
        if not items and d.data:
            items = list(enumerate(d.data))
        master = None
        for cid, pts in items:
            if getattr(d, 'is_map', False):
                continue
            lut = _spline_lut([(i, o) for o, i in pts])      # Photoshop stores (output, input)
            if cid == 0:
                master = lut
            elif 1 <= cid <= 3:
                out[..., cid - 1] = _apply_lut(out[..., cid - 1], lut)
        if master is not None:
            out = _apply_lut(out, master)
        return out
    if kind == 'brightnesscontrast':
        d = layer.data
        b, c = getattr(d, 'brightness', 0) / 100.0, getattr(d, 'contrast', 0) / 100.0
        return np.clip((out - 0.5) * (1 + c) + 0.5 + b * 0.5, 0, 1)
    warn(f'adjustment "{layer.name}" ({kind}) is not supported; skipped')
    return None


# ================================================================ effects
def _effect_color(desc):
    c = desc.get(b'Clr ') if desc else None
    try:
        return np.float32([c[b'Rd  '], c[b'Grn '], c[b'Bl  ']]) / 255.0
    except Exception:
        return np.float32([0, 0, 0])


def _shift_blur(a, dx, dy, size):
    h, w = a.shape
    s = cv2.warpAffine(a, np.float32([[1, 0, dx], [0, 1, dy]]), (w, h), borderMode=cv2.BORDER_CONSTANT)
    if size > 0:
        s = cv2.GaussianBlur(s, (0, 0), sigmaX=max(size / 2.0, 0.5))
    return s


# ================================================================ extended compositor
class _Compositor(ptc.Compositor):
    def __init__(self, viewport, color=1.0, alpha=0.0, isolated=False, layer_filter=None, force=False):
        super().__init__(viewport, color, alpha, isolated, layer_filter, force)
        self._isolated = isolated

    # --- layers
    def apply(self, layer, clip_compositing=False):
        if self._layer_filter is not None and not self._layer_filter(layer):
            return
        if not clip_compositing and layer.clipping:
            return
        if isinstance(layer, AdjustmentLayer):
            return self._apply_adjustment(layer)
        replaced = isinstance(layer, SmartObjectLayer) and _replaced(layer)
        if not replaced and not isinstance(layer, GroupMixin) and \
                ptc._intersect(self._viewport, layer.bbox) == (0, 0, 0, 0):
            return

        knockout = bool(layer.tagged_blocks.get_data(Tag.KNOCKOUT_SETTING, 0))
        if isinstance(layer, GroupMixin):
            color, shape, alpha = self._get_group(layer, knockout)
        else:
            color, shape, alpha = self._get_object(layer)
        if layer.has_clip_layers():
            color = self._apply_clip_layers(layer, color, alpha)

        shape_mask, opacity_mask = self._get_mask(layer)
        shape_const, opacity_const = self._get_const(layer)
        shape = shape * shape_mask
        alpha = alpha * shape_mask * opacity_mask * opacity_const
        fx = _effects(layer)
        if 'ColorOverlay' in fx:
            # Like Photoshop: the overlay replaces the layer color BEFORE compositing it. psd-tools composited it
            # on top afterwards, and the original color (e.g. white text at 40%) lightened the result.
            e, d = fx['ColorOverlay']
            from psd_tools.composite.blend import BLEND_FUNC
            ov = np.broadcast_to(_effect_color(d), color.shape[:2] + (3,)).astype(np.float32)
            base = color if color.shape[2] == 3 else np.repeat(color, 3, axis=2)
            mixed = BLEND_FUNC.get(_fx_mode(e, d), lambda b, s: s)(base, ov)
            k = float(e.opacity) / 100.0
            color = (base * (1 - k) + mixed * k).astype(np.float32)

        for name in ('DropShadow', 'OuterGlow'):
            if name in fx:
                self._outer_effect(name, fx[name], shape, opacity_const * opacity_mask, shape_const)
        self._apply_source(color, shape * shape_const, alpha * shape_const, layer.blend_mode, knockout)
        for name in ('InnerShadow', 'InnerGlow'):
            if name in fx:
                self._inner_effect(name, fx[name], shape, alpha)
        if 'ColorOverlay' not in fx:
            self._apply_color_overlay(layer, color, shape, alpha)
        self._apply_pattern_overlay(layer, color, shape, alpha)
        self._apply_gradient_overlay(layer, color, shape, alpha)
        if (self._force and layer.has_vector_mask()) or (not layer.has_pixels() and ptc.has_fill(layer)):
            self._apply_stroke_effect(layer, color, shape_mask, alpha)
        else:
            self._apply_stroke_effect(layer, color, shape, alpha)

    def _get_group(self, layer, knockout):
        # Same as psd-tools but with the whole viewport: a Smart Object's new content may extend beyond the
        # rectangle the original content occupied.
        color_b, alpha_b = (self._color_0, self._alpha_0) if knockout else (self._color, self._alpha)
        return ptc.composite(layer, color_b, alpha_b, self._viewport, layer_filter=self._layer_filter, force=self._force)

    def _get_object(self, layer):
        if isinstance(layer, SmartObjectLayer) and _replaced(layer):
            rgb, a = _CTX['warped'][id(layer)]
            vp = self._viewport
            full = (0, 0, _CTX['W'], _CTX['H'])
            color = ptc.paste(vp, full, rgb, 1.0)
            shape = ptc.paste(vp, full, a[..., None])
            return color, shape, shape * 1.0
        return super()._get_object(layer)

    # --- adjustments
    def _apply_adjustment(self, layer):
        col = self._color
        if col.shape[2] == 1:
            col = np.repeat(col, 3, axis=2)
        new = _adjust(layer, col, _CTX['warn'])
        if new is None:
            return
        shape_mask, opacity_mask = self._get_mask(layer)
        _, opacity_const = self._get_const(layer)
        k = np.broadcast_to(np.asarray(shape_mask, np.float32) * opacity_mask * opacity_const,
                            col.shape[:2] + (1,)).astype(np.float32)
        self._color = col + (new - col) * k
        if self._color_0.shape[2] == 1:
            self._color_0 = np.repeat(self._color_0, 3, axis=2)
        if not self._isolated:
            # In a "pass through" group the adjustment affects everything below it.
            self._shape_g = ptc._union(self._shape_g, k)
            self._alpha_g = ptc._union(self._alpha_g, k)

    # --- effects
    def _effect_source(self, desc, e):
        rgb = _effect_color(desc)
        return np.broadcast_to(rgb, (self.height, self.width, 3)).astype(np.float32)

    def _outer_effect(self, name, item, shape, opacity, fill):
        e, d = item
        a = np.asarray(shape, np.float32)
        a = np.broadcast_to(a, (self.height, self.width, 1))[..., 0].astype(np.float32)
        size = float(d.get(b'blur', 0) or 0)
        if name == 'DropShadow':
            ang = np.deg2rad(_CTX['angle'] if d.get(b'uglg') else float(d.get(b'lagl', 90)))
            dist = float(d.get(b'Dstn', 0) or 0)
            s = _shift_blur(a, -dist * np.cos(ang), dist * np.sin(ang), size)
        else:
            s = np.clip(_shift_blur(a, 0, 0, size) * 2, 0, 1)
        s = s * (float(e.opacity) / 100.0) * opacity
        if d.get(b'layerConceals', True) or name == 'OuterGlow':
            s = s * (1 - a * fill)
        s = s[..., None].astype(np.float32)
        self._apply_source(self._effect_source(d, e), s, s, _fx_mode(e, d))

    def _inner_effect(self, name, item, shape, alpha):
        e, d = item
        a = np.broadcast_to(np.asarray(shape, np.float32), (self.height, self.width, 1))[..., 0].astype(np.float32)
        size = float(d.get(b'blur', 0) or 0)
        if name == 'InnerShadow':
            ang = np.deg2rad(_CTX['angle'] if d.get(b'uglg') else float(d.get(b'lagl', 90)))
            dist = float(d.get(b'Dstn', 0) or 0)
            k = _shift_blur(1 - a, -dist * np.cos(ang), dist * np.sin(ang), size)
        else:
            k = np.clip((1 - _shift_blur(a, 0, 0, size)) * 2, 0, 1)
        k = (k * a)[..., None].astype(np.float32)
        op = float(e.opacity) / 100.0
        self._apply_source(self._effect_source(d, e), k, np.asarray(alpha) * k * op, _fx_mode(e, d))


def _fx_mode(e, d):
    """Blend mode of an effect, as the key the compositor understands (e.g. b'Mltp')."""
    from psd_tools.composite.blend import BLEND_FUNC
    m = getattr(d.get(b'Md  '), 'enum', None)
    return m if m in BLEND_FUNC else e.blend_mode


SUPPORTED_FX = {'DropShadow', 'InnerShadow', 'OuterGlow', 'InnerGlow', 'ColorOverlay', 'GradientOverlay',
                'PatternOverlay', 'Stroke'}


def _effects(layer):
    fx = {}
    if layer.has_effects() and layer.effects.enabled:
        for e in layer.effects:
            if e.enabled:
                name = type(e).__name__
                fx[name] = (e, e.value)
                if name not in SUPPORTED_FX:
                    _CTX['warn'](f'effect {name} on "{layer.name}" is not supported; skipped')
    return fx


def _replaced(layer):
    return id(layer) in _CTX.get('warped', {})


# ================================================================ public API
def _so_groups(psd):
    groups = {}
    for l in psd.descendants():
        if l.kind == 'smartobject':
            groups.setdefault(l.smart_object.unique_id, []).append(l)
    return groups


def _rep_name(names):
    # Layer names that hint at "put your design here" (English and Spanish, since many mockups ship that way).
    pref = [n for n in names if any(k in n.lower() for k in ('design', 'dise\u00f1o', 'diseno', 'here', 'aqu\u00ed', 'place'))]
    rest = [n for n in names if 'dupl' not in n.lower() and "don't edit" not in n.lower()]
    return (pref or rest or names)[0].strip()


def inspect(psd_path):
    """PSD size and its unique Smart Objects (grouped by unique_id)."""
    psd = PSDImage.open(psd_path)
    smart = []
    for uid, layers in _so_groups(psd).items():
        so = layers[0].smart_object
        inner = None
        try:
            if so.data:
                inner = list(PSDImage.open(io.BytesIO(so.data)).size) if so.filetype in (b'8BPS', b'8BPB', '8bps', '8bpb') \
                    else list(Image.open(io.BytesIO(so.data)).size)
        except Exception:
            inner = None
        smart.append({'uid': uid, 'name': _rep_name([l.name for l in layers]), 'names': [l.name for l in layers],
                      'visible': any(l.is_visible() for l in layers), 'file': so.filename, 'inner': inner})
    smart.sort(key=lambda s: not s['visible'])
    return {'size': list(psd.size), 'smartObjects': smart}


BLEND_NAMES = {'NORMAL': 'Normal', 'PASS_THROUGH': 'Pass Through', 'MULTIPLY': 'Multiply', 'SCREEN': 'Screen',
               'OVERLAY': 'Overlay', 'SOFT_LIGHT': 'Soft Light', 'HARD_LIGHT': 'Hard Light', 'DARKEN': 'Darken',
               'LIGHTEN': 'Lighten', 'COLOR_BURN': 'Color Burn', 'COLOR_DODGE': 'Color Dodge',
               'LINEAR_BURN': 'Linear Burn', 'LINEAR_DODGE': 'Linear Dodge (Add)', 'DIFFERENCE': 'Difference',
               'EXCLUSION': 'Exclusion', 'HUE': 'Hue', 'SATURATION': 'Saturation', 'COLOR': 'Color',
               'LUMINOSITY': 'Luminosity', 'VIVID_LIGHT': 'Vivid Light', 'LINEAR_LIGHT': 'Linear Light',
               'PIN_LIGHT': 'Pin Light', 'HARD_MIX': 'Hard Mix', 'SUBTRACT': 'Subtract', 'DIVIDE': 'Divide',
               'DISSOLVE': 'Dissolve'}
EFFECT_NAMES = {'DropShadow': 'Drop Shadow', 'InnerShadow': 'Inner Shadow', 'OuterGlow': 'Outer Glow',
                'InnerGlow': 'Inner Glow', 'ColorOverlay': 'Color Overlay', 'GradientOverlay': 'Gradient Overlay',
                'PatternOverlay': 'Pattern Overlay', 'Stroke': 'Stroke', 'BevelEmboss': 'Bevel & Emboss',
                'Satin': 'Satin'}
KIND_NAMES = {'pixel': 'Pixel', 'group': 'Group', 'smartobject': 'Smart Object', 'type': 'Type', 'shape': 'Shape',
              'solidcolorfill': 'Solid Color', 'gradientfill': 'Gradient Fill', 'patternfill': 'Pattern Fill',
              'levels': 'Levels', 'curves': 'Curves', 'brightnesscontrast': 'Brightness/Contrast'}
WARP_NAMES = {b'warpNone': 'none', b'warpCylinder': 'cylinder', b'warpArc': 'arc', b'warpFlag': 'flag',
              b'warpWave': 'wave', b'warpBulge': 'bulge', b'warpArch': 'arch'}


def blend_name(mode):
    """Photoshop's English name for a psd-tools BlendMode."""
    return BLEND_NAMES.get(mode.name, mode.name.replace('_', ' ').title())
SUPPORTED_ADJ = {'levels', 'curves', 'brightnesscontrast'}


def _layer_info(l, depth, path):
    fx = [EFFECT_NAMES.get(type(e).__name__, type(e).__name__) for e in l.effects if e.enabled] \
        if l.has_effects() and l.effects.enabled else []
    filters = [filter_label(f) for f in smart_filters(l) if f[3]] if l.kind == 'smartobject' else []
    notes = []
    if l.kind not in KIND_NAMES and not l.is_group():
        notes.append('type not rendered')
    elif isinstance(l, AdjustmentLayer) and l.kind not in SUPPORTED_ADJ:
        notes.append('adjustment not rendered')
    if any(f[0] not in FILTER_NAMES for f in (smart_filters(l) if l.kind == 'smartobject' else []) if f[3]):
        notes.append('filter not rendered')
    return {
        'name': l.name, 'type': KIND_NAMES.get(l.kind, l.kind), 'depth': depth, 'group': path,
        'visible': bool(l.visible), 'blend': blend_name(l.blend_mode),
        'opacity': round(l.opacity / 255 * 100), 'fill': round(l.tagged_blocks.get_data(Tag.BLEND_FILL_OPACITY, 255) / 255 * 100)
        if l.tagged_blocks else 100,
        'clipping': bool(l.clipping), 'mask': bool(l.has_mask() or l.has_vector_mask()),
        'effects': fx, 'filters': filters, 'warnings': notes,
    }


def layer_list(psd):
    """All PSD layers (top to bottom, as in Photoshop) with their properties."""
    out = []

    def walk(group, depth, path):
        for l in reversed(list(group)):
            out.append(_layer_info(l, depth, path))
            if l.is_group():
                walk(l, depth + 1, f'{path}/{l.name}' if path else l.name)
    walk(psd, 0, '')
    return out


def _so_details(layers):
    """Warp, instances, transparency, effects, filters and clipped layers above a Smart Object."""
    vis = [l for l in layers if l.is_visible()] or layers
    so = vis[0].smart_object
    warp, quilt = _so_warp_desc(so)
    style = getattr(warp.get(b'warpStyle'), 'enum', b'warpNone')
    deform = ('quilt' if quilt else 'custom mesh') if style == b'warpCustom' else \
        WARP_NAMES.get(style, style.decode(errors='ignore'))
    box = np.float32(so.transform_box).reshape(4, 2)
    rect = abs(box[0, 1] - box[1, 1]) < 1 and abs(box[2, 1] - box[3, 1]) < 1 and abs(box[0, 0] - box[3, 0]) < 1
    instances = []
    for l in layers:
        siblings = list(l.parent) if l.parent is not None else []
        i = siblings.index(l) if l in siblings else -1
        clipped = []
        for c in siblings[i + 1:] if i >= 0 else []:
            if not c.clipping:
                break
            clipped.append({'name': c.name, 'blend': blend_name(c.blend_mode), 'visible': bool(c.visible)})
        info = _layer_info(l, 0, '')
        instances.append({'name': l.name, 'visible': bool(l.is_visible()), 'opacity': info['opacity'],
                          'fill': info['fill'], 'blend': info['blend'], 'mask': info['mask'],
                          'effects': info['effects'], 'filters': info['filters'], 'clippedLayers': clipped})
    return {'warp': deform, 'perspective': 'rectangular' if rect else 'perspective', 'instances': instances}


def analyze(psd_path):
    """
    Traits of each Smart Object for the mockup profile: inner canvas aspect ratio, luminance of the surface
    the design goes on (to recommend a light or dark logo) and whether the sample content covers the whole
    canvas (design with background) or not (transparent logo).
    The surface is measured by compositing the mockup with an empty design, inside each object's projected shape.
    """
    from fractions import Fraction
    psd = PSDImage.open(psd_path)
    W, H = psd.size
    groups = _so_groups(psd)
    empty = Image.new('RGBA', (4, 4), (0, 0, 0, 0))
    base, _ = render(psd_path, log=lambda m: None, assignments={u: {'design': empty} for u in groups})
    lum = np.asarray(base.convert('L'), np.float32) / 255.0
    out = []
    for uid, layers in groups.items():
        vis = [l for l in layers if l.is_visible()] or layers
        so = vis[0].smart_object
        try:
            cw, ch = _inner_size(so)
            sample = np.asarray(_inner_original(so), np.float32) / 255.0
            alpha = sample[..., 3]
            coverage = float((alpha > 0.5).mean())
            # Luminance of the sample content: its author already picked a color that works on that surface.
            sample_lum = float((sample[..., :3] @ np.float32([0.299, 0.587, 0.114]) * alpha).sum() / alpha.sum()) \
                if alpha.sum() > 0 else None
            _, shape, _ = _warp_content(Image.new('RGBA', (cw, ch), (255, 255, 255, 255)), so, W, H)
            inside = shape > 0.5
            lay = vis[0]
            if lay.has_mask() and not lay.mask.disabled and lay.mask.topil() is not None:   # actual visible area
                m = np.full((H, W), lay.mask.background_color / 255.0, np.float32)
                x0, y0, x1, y1 = lay.mask.bbox
                mk = np.asarray(lay.mask.topil().convert('L'), np.float32) / 255.0
                cx0, cy0, cx1, cy1 = max(x0, 0), max(y0, 0), min(x1, W), min(y1, H)
                if cx1 > cx0 and cy1 > cy0:
                    m[cy0:cy1, cx0:cx1] = mk[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
                if (inside & (m > 0.5)).sum() > 0.05 * inside.sum():
                    inside &= m > 0.5
            region = lum[inside]
        except Exception:
            cw, ch, coverage, region, sample_lum = 0, 0, 0.0, np.array([]), None
        surface = float(np.median(region)) if region.size else 0.5
        with_bg = coverage > 0.9
        if with_bg:
            logo = 'original'                      # full-bleed piece (poster, label): keep its colors
        elif sample_lum is not None and coverage > 0.003 and abs(sample_lum - 0.5) > 0.12:
            logo = 'light' if sample_lum > 0.5 else 'dark'
        else:
            logo = 'light' if surface < 0.5 else 'dark'
        ratio = Fraction(cw, ch).limit_denominator(16) if cw and ch else None
        out.append({
            'uid': uid, 'name': _rep_name([l.name for l in layers]), 'inner': [cw, ch],
            'aspect': round(cw / ch, 4) if ch else None, 'ratio': f'{ratio.numerator}:{ratio.denominator}' if ratio else '',
            'surface': round(surface, 3), 'coverage': round(coverage, 3), 'withBackground': with_bg,
            'sample': round(sample_lum, 3) if sample_lum is not None else None, 'logo': logo, **_so_details(layers),
            'visible': any(l.is_visible() for l in layers),
        })
    return {'size': list(psd.size), 'objects': out, 'layers': layer_list(psd)}


def preview(psd_path, max_side=900):
    psd = PSDImage.open(psd_path)
    img = psd.topil() or psd.composite()
    img = img.convert('RGB')
    img.thumbnail((max_side, max_side), Image.LANCZOS)
    return img


def _inner_size(so):
    data = io.BytesIO(so.data)
    try:
        return PSDImage.open(data).size
    except Exception:
        data.seek(0)
        return Image.open(data).size


def _inner_original(so):
    data = io.BytesIO(so.data)
    try:
        return PSDImage.open(data).composite().convert('RGBA')
    except Exception:
        data.seek(0)
        return Image.open(data).convert('RGBA')


def prepare_design(design, cw, ch, fit='contain', tint=None, rotate=0):
    """Rotate, recolor and fit a design (PIL) to a Smart Object's inner canvas."""
    d = design.convert('RGBA')
    if rotate % 360:
        d = d.rotate(-(rotate % 360), expand=True)   # clockwise
    return fit_design(tint_design(d, tint), cw, ch, fit)


def render(psd_path, design=None, fit='contain', uids=None, log=print, tint=None, rotate=0, assignments=None):
    """
    Composite the mockup and return (PIL RGB, warnings).

    - assignments: {uid: {'design': PIL, 'fit', 'tint', 'rotate'}}. Each Smart Object gets its own design;
      the ones not listed (or with design None) keep their original content.
    - Without assignments (simple mode): `design` goes to the Smart Objects in `uids` (None = all). If
      design is None the original content is used (to validate against Photoshop).
    """
    warnings_out = []

    def warn(msg):
        if msg not in warnings_out:
            warnings_out.append(msg)
            log('warning: ' + msg)

    psd = PSDImage.open(psd_path)
    W, H = psd.size
    groups = _so_groups(psd)
    if not groups:
        raise ValueError('The PSD contains no Smart Objects')
    if assignments is None:
        if isinstance(uids, str):
            uids = [uids]
        targets = [u for u in groups if (not uids or u in uids)]
        if not targets:
            raise ValueError('The selected Smart Object no longer exists in the PSD')
        assignments = {u: {'design': design, 'fit': fit, 'tint': tint, 'rotate': rotate, 'original': design is None}
                       for u in targets}
    else:
        unknown = [u for u in assignments if u not in groups]
        for u in unknown:
            warn('a linked Smart Object no longer exists in the PSD; ignored')
        assignments = {u: a for u, a in assignments.items() if u in groups and a.get('design') is not None}

    warped = {}
    for uid, a in assignments.items():
        layers = [l for l in groups[uid] if l.is_visible()]
        if not layers:
            continue
        so = layers[0].smart_object
        cw, ch = _inner_size(so)
        if a.get('original'):
            content = _inner_original(so)
        else:
            content = prepare_design(a['design'], cw, ch, a.get('fit', 'contain'), a.get('tint'), int(a.get('rotate') or 0))
        log(f'Smart Object "{_rep_name([l.name for l in groups[uid]])}": inner canvas {cw}x{ch}, '
            f'{len(layers)} instance(s), fit {a.get("fit", "contain")}')
        for l in layers:
            rgb, al, style = _warp_content(content, l.smart_object, W, H)
            if style not in (b'warpNone', b'warpCustom', b'warpCylinder'):
                warn(f'"{l.name}" uses the {style.decode(errors="ignore")} warp; only the perspective is applied')
            rgb, al = _apply_smart_filters(l, rgb, al, warn)
            warped[id(l)] = (rgb.astype(np.float32), al.astype(np.float32))

    gres = psd.image_resources.get_data(Resource.GLOBAL_ANGLE)
    with _LOCK:
        _CTX.clear()
        _CTX.update(W=W, H=H, warped=warped, warn=warn, angle=float(gres) if gres is not None else 90.0)
        original = ptc.Compositor
        ptc.Compositor = _Compositor
        try:
            color, _, alpha = ptc.composite(psd, color=1.0, alpha=0.0)
        finally:
            ptc.Compositor = original
            _CTX.clear()
    if color.shape[2] == 1:
        color = np.repeat(color, 3, axis=2)
    rgb = color[..., :3] * alpha + (1 - alpha)          # white background where the PSD is transparent
    out = Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB')
    return out, warnings_out
