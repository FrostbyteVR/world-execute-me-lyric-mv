"""The character silhouettes (assets/character/*.png) as flat three-ink prints, recoloured by palette ROLE.

As in src/engine/art.js, each picture is separated ONCE into its three inks (cream, orange, near-black) and every
treatment only recolours, drops or crops those plates; the art is never redrawn. The result is a small RGBA array
that ctx.image() hands to a pooled ImageMobject (cached per palette colour, so a palette blend costs nothing after
its first frame).

variants:
    'ink'        the three inks in palette roles: cream -> text, orange -> me, black -> panel
    'ob'         orange and black only: the cream plate missing (the proof sheets of verse 2)
    'grey'       the three inks as greys (the `off` state keeps no colour)
    'sil:ROLE'   the whole figure as one flat matte in a palette role
    'dots:ROLE'  a dot screen of the figure in one role (the screen her figure becomes when she is alone)
"""
import os

import numpy as np
from PIL import Image

from .data import ROOT

INK_RGB = np.array([[244, 224, 198], [220, 114, 63], [36, 26, 21]], dtype=float)
MAX_SIDE = {'f_eye': 720}
_SRC = {}
_OUT = {}
REGIONS = None


def regions():
    global REGIONS
    if REGIONS is None:
        import json
        try:
            REGIONS = json.load(open(os.path.join(ROOT, 'assets/character/regions.json'), encoding='utf-8'))
        except OSError:
            REGIONS = {}
    return REGIONS


def _source(name):
    """(labels, alpha) at working resolution: labels 0 cream, 1 orange, 2 black."""
    s = _SRC.get(name)
    if s is not None:
        return s
    p = os.path.join(ROOT, 'assets/character', f'{name}.png')
    if not os.path.exists(p):
        _SRC[name] = None
        return None
    im = Image.open(p).convert('RGBA')
    side = MAX_SIDE.get(name, 520)
    k = side / max(im.size)
    im = im.resize((max(1, round(im.size[0] * k)), max(1, round(im.size[1] * k))), Image.LANCZOS)
    a = np.asarray(im, dtype=float)
    rgb, alpha = a[..., :3], a[..., 3]
    d = ((rgb[..., None, :] - INK_RGB[None, None]) ** 2).sum(-1)
    labels = d.argmin(-1).astype(np.uint8)
    alpha = np.where(alpha < 16, 0, np.minimum(255, alpha * 1.01)).astype(np.uint8)
    _SRC[name] = (labels, alpha)
    return _SRC[name]


def _q(c):
    return tuple(min(255, int(round(v / 4) * 4)) for v in c)


def art_pixels(env, name, variant, pal, crop=None):
    src = _source(name)
    if src is None:
        return None
    labels, alpha = src
    if variant == 'grey':
        cols = [_q(pal['text']), _q(pal['mute']), _q(pal['panel'])]
    elif variant.startswith('glass:'):
        c = pal.get(variant.split(':')[1], pal['mute'])
        d = tuple(cv + (pv - cv) * 0.55 for cv, pv in zip(c, pal['panel']))
        cols = [_q(c), _q(c), _q(d)]
    elif variant.startswith('sil:') or variant.startswith('dots:'):
        c = _q(pal.get(variant.split(':')[1], pal['text']))
        cols = [c, c, c]
    else:
        cols = [_q(pal['text']), _q(pal['me']), _q(pal['panel'])]
        if pal.sat < 0.99:   # the palette keeps only part of the colour: so does the art
            g = [sum(c) / 3 for c in cols]
            cols = [_q(tuple(gv + (cv - gv) * pal.sat for cv in c)) for c, gv in zip(cols, g)]
    key = (name, variant, tuple(cols), crop)
    out = _OUT.get(key)
    if out is not None:
        return out
    h, w = labels.shape
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    lut = np.array(cols, dtype=np.uint8)
    arr[..., :3] = lut[labels]
    a = alpha.copy()
    if variant == 'ob':
        a = np.where(labels == 0, 0, a).astype(np.uint8)
    if variant.startswith('dots:'):
        yy, xx = np.mgrid[0:h, 0:w]
        cell = max(4, h // 60)
        cx, cy = (xx % cell) - cell / 2, (yy % cell) - cell / 2
        lum = np.array([0.95, 0.6, 0.2])[labels]
        rad = (cell / 2) * np.sqrt(lum)
        a = np.where(cx * cx + cy * cy <= rad * rad, a, 0).astype(np.uint8)
    arr[..., 3] = a
    if crop:
        u0, v0, u1, v1 = crop
        arr = arr[int(v0 * h):int(v1 * h), int(u0 * w):int(u1 * w)].copy()
    _OUT[key] = arr
    if len(_OUT) > 400:
        _OUT.pop(next(iter(_OUT)))
    return arr


def aspect(name, crop=None):
    src = _source(name)
    if src is None:
        return 0.75
    h, w = src[0].shape
    if crop:
        return (crop[2] - crop[0]) * w / max(1e-6, (crop[3] - crop[1]) * h)
    return w / h
