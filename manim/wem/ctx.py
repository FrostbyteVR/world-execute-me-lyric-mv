"""The drawing context handed to every shot: the Canvas-2D API of src/engine/draw.js, on top of Manim mobjects.

Shots draw in a fixed VIRTUAL frame of 1920 x 640 px (the 3:1 shape of the 960 x 320 display, at twice its
resolution, so the type sizes of the browser film carry over). 100 virtual px = 1 Manim unit; the Manim frame
is 19.2 x 6.4 units. y grows DOWNWARDS, as on a canvas.

A frame is rebuilt from scratch every time (as in the browser: no frame depends on the one before it). To keep
that affordable in Manim, every mobject comes out of a pool and is re-shaped in place instead of being created:

    ctx.line / poly / rect / rrect / circle / ...   pooled VMobjects (points set directly as cubic Beziers)
    ctx.text                                         pooled Text glyphs, one Pango layout per distinct string
    ctx.image                                        pooled ImageMobjects (character art), corners set directly

Transforms (ctx.at, ctx.camera) and opacity nest as on a canvas: `with ctx.at(x, y, rot=.., scale=.., alpha=..):`.
"""
import math
from contextlib import contextmanager

import numpy as np
from manim import VMobject, ImageMobject, Text, ManimColor

from .data import mix_pal, parse_hex
from .util import clamp

VW, VH = 1920, 640
UNIT = 100.0                      # virtual px per Manim unit
EM_FONT_SIZE = 72.0               # Manim font_size whose em is exactly 1 unit (measured: 100 -> 1.3888 units)
KAPPA = 0.5522847498

FAMILY = {'mono': 'JetBrains Mono', 'serif': 'Source Serif 4', 'sans': 'Inter'}
_CJK = None


def cjk_family():
    """A CJK face Pango actually has (the warning line and the count cards): Noto first, else any CJK family."""
    global _CJK
    if _CJK is None:
        import manimpango
        have = set(manimpango.list_fonts())
        _CJK = next((f for f in ('Noto Sans CJK TC', 'Noto Sans TC', 'Noto Sans CJK JP', 'Source Han Sans TC', 'WenQuanYi Zen Hei',
                                 'Microsoft JhengHei', 'PingFang TC', 'IPAGothic') if f in have), 'Sans')
    return _CJK
WEIGHT = {100: 'THIN', 200: 'ULTRALIGHT', 300: 'LIGHT', 400: 'NORMAL', 500: 'MEDIUM', 600: 'SEMIBOLD',
          700: 'BOLD', 800: 'ULTRABOLD', 900: 'HEAVY'}

_COL = {}


def mcolor(rgb):
    key = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
    c = _COL.get(key)
    if c is None:
        c = _COL[key] = ManimColor.from_rgb(tuple(v / 255 for v in key))
    return c


def _mat(a=1.0, b=0.0, c=0.0, d=1.0, e=0.0, f=0.0):
    """Canvas-style affine [a c e; b d f; 0 0 1]."""
    return np.array([[a, c, e], [b, d, f], [0.0, 0.0, 1.0]])


def _arc(cx, cy, r, a0, a1, rx=None):
    """Cubic Bezier quads (n, 4, 2) for an arc (canvas angles: y down, clockwise positive)."""
    rx = r if rx is None else rx
    span = a1 - a0
    n = max(1, int(math.ceil(abs(span) / (math.pi / 2) - 1e-9)))
    out = np.empty((n, 4, 2))
    da = span / n
    h = 4 / 3 * math.tan(da / 4)
    for i in range(n):
        t0, t1 = a0 + i * da, a0 + (i + 1) * da
        c0, s0, c1, s1 = math.cos(t0), math.sin(t0), math.cos(t1), math.sin(t1)
        out[i, 0] = (cx + rx * c0, cy + r * s0)
        out[i, 1] = (cx + rx * (c0 - h * s0), cy + r * (s0 + h * c0))
        out[i, 2] = (cx + rx * (c1 + h * s1), cy + r * (s1 - h * c1))
        out[i, 3] = (cx + rx * c1, cy + r * s1)
    return out


def _lines(pts, close=False):
    p = np.asarray(pts, dtype=float)
    if close and len(p) > 1 and not np.allclose(p[0], p[-1]):
        p = np.vstack([p, p[:1]])
    a, b = p[:-1], p[1:]
    out = np.empty((len(a), 4, 2))
    out[:, 0] = a
    out[:, 1] = a + (b - a) / 3
    out[:, 2] = a + 2 * (b - a) / 3
    out[:, 3] = b
    return out


class _TextShape:
    """One Pango layout of a string: its glyph outlines in em units, origin = left ink edge on the baseline."""

    def __init__(self, s, family, weight, italic):
        probe = 'H' + s
        kw = dict(font=family, font_size=EM_FONT_SIZE, weight=WEIGHT.get(weight, 'NORMAL'))
        if italic:
            kw['slant'] = 'ITALIC'
        m = Text(probe, **kw)
        glyphs = list(m.submobjects)
        base = glyphs[0].get_bottom()[1] if glyphs else 0.0
        glyphs = glyphs[1:]
        self.ok = bool(glyphs)
        if not self.ok:
            self.width = 0.0
            return
        left = min(g.get_left()[0] for g in glyphs)
        right = max(g.get_right()[0] for g in glyphs)
        self.width = right - left
        self.pts = []
        for g in glyphs:
            p = g.points[:, :2].copy()
            p[:, 0] -= left
            p[:, 1] = base - p[:, 1]           # y down, baseline = 0
            self.pts.append(p)
        self.centers = [float(np.mean(p[:, 0])) if len(p) else 0.0 for p in self.pts]
        # which character each glyph is (for letter spacing): non-space characters in order
        idx = [i for i, ch in enumerate(s) if not ch.isspace()]
        self.char_index = idx if len(idx) == len(self.pts) else list(range(len(self.pts)))
        self.proto = m
        self.proto.submobjects = []


class Ctx:
    def __init__(self, env):
        self.env = env
        self.cfg = env.cfg
        self.palettes = env.palettes
        self.pal = self.palettes['off']
        self.state_pal = None
        self.W, self.H = VW, VH
        self._shapes = {}
        self._vpool, self._vi = [], 0
        self._tpool, self._ti = {}, {}
        self._ipool, self._ii = {}, {}
        self._art = {}
        self.items = []
        self.M = _mat()
        self.alpha = 1.0
        self.fx = {}
        self._glow = None
        self.t = 0.0
        self.f = {}

    # ---- frame -------------------------------------------------------------------------------------------
    def reset_frame(self):
        self._vi = 0
        self._ti = {}
        self._ii = {}

    def begin(self, t, f, fx):
        """Start a layer: an empty item list, the identity transform."""
        self.items = []
        self.M = _mat()
        self.alpha = 1.0
        self._glow = None
        self.t, self.f, self.fx = t, f, fx
        self.state_pal = None
        return self.items

    # ---- palette -----------------------------------------------------------------------------------------
    def resolve_pal(self, spec):
        if isinstance(spec, str):
            return self.palettes.get(spec, self.palettes['on'])
        if isinstance(spec, (tuple, list)):
            k = spec[2] if spec[2] == spec[2] else 0
            return mix_pal(self.resolve_pal(spec[0]), self.resolve_pal(spec[1]), clamp(k))
        return spec if spec is not None else self.pal

    def set_pal(self, spec):
        self.pal = self.resolve_pal(spec)
        return self.pal

    @contextmanager
    def with_pal(self, spec):
        keep = self.pal
        self.set_pal(spec)
        try:
            yield
        finally:
            self.pal = keep

    def rgb(self, name):
        if name is None:
            return None
        if isinstance(name, tuple):
            return name
        c = self.pal.get(name)
        if c is None:
            c = parse_hex(name) if isinstance(name, str) and name.startswith('#') else None
        if c is None:
            spot = name.split('.') if isinstance(name, str) else None
            if spot and len(spot) == 2 and spot[0] in self.env.spot:
                c = self.env.spot[spot[0]].get(spot[1])
        return c if c is not None else self.pal['text']

    # ---- transforms --------------------------------------------------------------------------------------
    @contextmanager
    def at(self, x, y, rot=0.0, scale=1.0, sx=None, sy=None, alpha=1.0):
        keepM, keepA = self.M, self.alpha
        sx = scale if sx is None else sx
        sy = scale if sy is None else sy
        c, s = math.cos(rot), math.sin(rot)
        self.M = self.M @ _mat(1, 0, 0, 1, x, y) @ _mat(c, s, -s, c, 0, 0) @ _mat(sx, 0, 0, sy, 0, 0)
        self.alpha = self.alpha * max(0.0, alpha)
        try:
            yield
        finally:
            self.M, self.alpha = keepM, keepA

    @contextmanager
    def transform(self, a, b, c, d, e=0.0, f=0.0):
        """A general affine (canvas transform(a, b, c, d, e, f)) for what is drawn inside."""
        keep = self.M
        self.M = self.M @ _mat(a, b, c, d, e, f)
        try:
            yield
        finally:
            self.M = keep

    @contextmanager
    def screen(self):
        """Draw in screen space (no camera, no transforms) inside."""
        keep = self.M
        self.M = self.base_M.copy() if getattr(self, 'base_M', None) is not None else _mat()
        try:
            yield
        finally:
            self.M = keep

    @contextmanager
    def fade(self, alpha):
        keep = self.alpha
        self.alpha *= max(0.0, alpha)
        try:
            yield
        finally:
            self.alpha = keep

    def camera(self, x=0.0, y=0.0, zoom=1.0, rot=0.0):
        """Pan (camera moves right / down), zoom about the screen centre, rotate. Acts on what is drawn after it."""
        c, s = math.cos(rot), math.sin(rot)
        self.M = (self.M @ _mat(1, 0, 0, 1, VW / 2, VH / 2) @ _mat(c, s, -s, c, 0, 0) @ _mat(zoom, 0, 0, zoom, 0, 0)
                  @ _mat(1, 0, 0, 1, -VW / 2 - x, -VH / 2 - y))

    def scale_now(self):
        return math.sqrt(abs(np.linalg.det(self.M[:2, :2])))

    def to_screen(self, x, y):
        p = self.M @ np.array([x, y, 1.0])
        return p[0], p[1]

    def _out(self, quads):
        """(n, 4, 2) local px -> (4n, 3) Manim points."""
        q = quads.reshape(-1, 2)
        M = self.M
        x = q[:, 0] * M[0, 0] + q[:, 1] * M[0, 1] + M[0, 2]
        y = q[:, 0] * M[1, 0] + q[:, 1] * M[1, 1] + M[1, 2]
        out = np.empty((len(q), 3))
        out[:, 0] = x / UNIT - VW / 2 / UNIT
        out[:, 1] = VH / 2 / UNIT - y / UNIT
        out[:, 2] = 0.0
        return out

    # ---- pooled mobjects ---------------------------------------------------------------------------------
    def _vm(self):
        if self._vi >= len(self._vpool):
            self._vpool.append(VMobject())
        m = self._vpool[self._vi]
        self._vi += 1
        return m

    def _emit(self, quads, fill=None, fill_a=0.0, stroke=None, stroke_a=0.0, width=0.0, glow=True):
        if self._glow and glow:
            gc, gr, ga = self._glow
            self._halo(quads, gc, gr, ga, closed=fill is not None)
        m = self._vm()
        m.points = self._out(quads)
        s = self.scale_now()
        if fill is not None and fill_a > 0.003:
            m.set_fill(mcolor(fill), opacity=min(1.0, fill_a), family=False)
        else:
            m.set_fill(opacity=0.0, family=False)
        if stroke is not None and stroke_a > 0.003 and width > 0:
            m.set_stroke(mcolor(stroke), width=width * s, opacity=min(1.0, stroke_a), family=False)
        else:
            m.set_stroke(width=0, opacity=0.0, family=False)
        self.items.append(m)
        return m

    def _halo(self, quads, rgb, radius, a, closed):
        """A soft glow approximated by wide translucent strokes (Manim's Cairo camera has no blur)."""
        s = self.scale_now()
        for w, k in ((radius * 1.4, 0.10), (radius * 0.75, 0.16), (radius * 0.35, 0.22)):
            m = self._vm()
            m.points = self._out(quads)
            m.set_fill(opacity=0.0, family=False)
            m.set_stroke(mcolor(rgb), width=max(1.0, w * s), opacity=min(1.0, a * k * self.alpha), family=False)
            self.items.append(m)

    @contextmanager
    def glow(self, color, radius, alpha=1.0):
        """Everything drawn inside gets a halo in `color` (radius in virtual px)."""
        keep = self._glow
        self._glow = (self.rgb(color), radius, alpha) if alpha > 0.01 else None
        try:
            yield
        finally:
            self._glow = keep

    # ---- primitives --------------------------------------------------------------------------------------
    def clear(self, color='bg'):
        keep = self.M
        self.M = _mat()
        self._emit(_lines([(-40, -40), (VW + 40, -40), (VW + 40, VH + 40), (-40, VH + 40)], True), fill=self.rgb(color), fill_a=self.alpha, glow=False)
        self.M = keep

    def line(self, x1, y1, x2, y2, color='text', alpha=1.0, width=2.0):
        a = alpha * self.alpha
        if a <= 0.003:
            return
        self._emit(_lines([(x1, y1), (x2, y2)]), stroke=self.rgb(color), stroke_a=a, width=width)

    def poly(self, pts, color='text', alpha=1.0, width=2.0, close=False, fill=False):
        a = alpha * self.alpha
        if a <= 0.003 or len(pts) < 2:
            return
        q = _lines(pts, close or fill)
        if fill:
            self._emit(q, fill=self.rgb(color), fill_a=a)
        else:
            self._emit(q, stroke=self.rgb(color), stroke_a=a, width=width)

    def rect(self, x, y, w, h, color='text', alpha=1.0, width=2.0, fill=False):
        self.poly([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], color=color, alpha=alpha, width=width, close=True, fill=fill)

    def rrect(self, x, y, w, h, r, fill='raised', stroke=None, alpha=1.0, width=1.5, fill_alpha=1.0, stroke_alpha=1.0, shadow=0.0):
        a = alpha * self.alpha
        if a <= 0.003 or w <= 0 or h <= 0:
            return
        r = max(0.0, min(r, w / 2, h / 2))
        if r < 0.5:
            q = _lines([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True)
        else:
            q = np.concatenate([
                _lines([(x + r, y), (x + w - r, y)]), _arc(x + w - r, y + r, r, -math.pi / 2, 0),
                _lines([(x + w, y + r), (x + w, y + h - r)]), _arc(x + w - r, y + h - r, r, 0, math.pi / 2),
                _lines([(x + w - r, y + h), (x + r, y + h)]), _arc(x + r, y + h - r, r, math.pi / 2, math.pi),
                _lines([(x, y + h - r), (x, y + r)]), _arc(x + r, y + r, r, math.pi, 1.5 * math.pi)])
        if shadow > 0 and fill:
            for i, (d, k) in enumerate(((22, 0.10), (12, 0.14), (5, 0.18))):
                sq = q.copy()
                sq[..., 1] += 8 * shadow
                cx, cy = x + w / 2, y + h / 2
                sq[..., 0] = cx + (sq[..., 0] - cx) * (1 + d * shadow / max(w, 1))
                sq[..., 1] = cy + 8 * shadow + (sq[..., 1] - cy - 8 * shadow) * (1 + d * shadow / max(h, 1))
                self._emit(sq, fill=(0, 0, 0), fill_a=a * k * shadow, glow=False)
        self._emit(q, fill=self.rgb(fill) if fill else None, fill_a=a * fill_alpha,
                   stroke=self.rgb(stroke) if stroke else None, stroke_a=a * stroke_alpha, width=width)

    def circle(self, x, y, r, color='text', alpha=1.0, width=2.0, fill=False, a0=0.0, a1=math.tau, rx=None):
        a = alpha * self.alpha
        if a <= 0.003 or r <= 0:
            return
        q = _arc(x, y, r, a0, a1, rx)
        if fill:
            if abs(a1 - a0) < math.tau - 1e-6:
                q = np.concatenate([q, _lines([q[-1, 3], (x, y), q[0, 0]])])
            self._emit(q, fill=self.rgb(color), fill_a=a)
        else:
            self._emit(q, stroke=self.rgb(color), stroke_a=a, width=width)

    def path(self, quads, color='text', alpha=1.0, width=2.0, fill=False):
        """Raw cubic Bezier quads (n, 4, 2), for shapes built by the components."""
        a = alpha * self.alpha
        if a <= 0.003 or len(quads) == 0:
            return
        if fill:
            self._emit(np.asarray(quads), fill=self.rgb(color), fill_a=a)
        else:
            self._emit(np.asarray(quads), stroke=self.rgb(color), stroke_a=a, width=width)

    def grad_rect(self, x, y, w, h, stops, direction='v', steps=12):
        """Linear gradient: stops [(pos 0..1, role, alpha), ...], drawn as `steps` bands."""
        for i in range(steps):
            k0, k1 = i / steps, (i + 1) / steps
            km = (k0 + k1) / 2
            for j in range(len(stops) - 1):
                if stops[j][0] <= km <= stops[j + 1][0]:
                    p0, r0, a0 = stops[j]
                    p1, r1, a1 = stops[j + 1]
                    u = 0 if p1 == p0 else (km - p0) / (p1 - p0)
                    c0, c1 = self.rgb(r0), self.rgb(r1)
                    rgb = tuple(c0[n] + (c1[n] - c0[n]) * u for n in range(3))
                    al = a0 + (a1 - a0) * u
                    break
            else:
                continue
            if al <= 0.003:
                continue
            if direction == 'v':
                self.rect(x, y + h * k0, w, h * (k1 - k0) + 0.5, color=rgb, alpha=al, fill=True)
            else:
                self.rect(x + w * k0, y, w * (k1 - k0) + 0.5, h, color=rgb, alpha=al, fill=True)

    def radial(self, x, y, r, role, alpha, rings=6):
        """Soft radial light: stacked translucent discs (approximates the canvas radial gradient)."""
        if alpha <= 0.003:
            return
        for i in range(rings):
            self.circle(x, y, r * (1 - i / rings), color=role, alpha=alpha * 0.32, fill=True)

    def brackets(self, r, length=22, color='mute', alpha=1.0, width=2.0, k=1.0):
        l = length * k
        x, y, w, h = r['x'], r['y'], r['w'], r['h']
        for pts in ([(x, y + l), (x, y), (x + l, y)], [(x + w - l, y), (x + w, y), (x + w, y + l)],
                    [(x + w, y + h - l), (x + w, y + h), (x + w - l, y + h)], [(x + l, y + h), (x, y + h), (x, y + h - l)]):
            self.poly(pts, color=color, alpha=alpha, width=width)

    def dashed(self, x1, y1, x2, y2, dash=12, gap=9, phase=0.0, **kw):
        L = math.hypot(x2 - x1, y2 - y1)
        if L <= 0:
            return
        ux, uy = (x2 - x1) / L, (y2 - y1) / L
        d = -(phase % (dash + gap))
        while d < L:
            a, b = max(0, d), min(L, d + dash)
            if b > a:
                self.line(x1 + ux * a, y1 + uy * a, x1 + ux * b, y1 + uy * b, **kw)
            d += dash + gap

    def dashed_circle(self, x, y, r, n=24, duty=0.6, rot=0.0, **kw):
        for i in range(n):
            a0 = rot + i / n * math.tau
            self.circle(x, y, r, a0=a0, a1=a0 + duty * math.tau / n, **kw)

    def trail(self, n, dt, fn, strength=0.5):
        for i in range(n, -1, -1):
            w = 1.0 if i == 0 else strength * (1 - i / (n + 1))
            with self.fade(w):
                fn(i * dt)

    # ---- text --------------------------------------------------------------------------------------------
    def _shape(self, s, font, weight, italic):
        fam = FAMILY.get(font, cjk_family() if font.startswith(('tc', 'kr', 'meme')) else FAMILY['sans'])
        key = (s, fam, weight, italic)
        sh = self._shapes.get(key)
        if sh is None:
            sh = self._shapes[key] = _TextShape(s, fam, weight, italic)
        return key, sh

    def measure(self, s, size=24, weight=400, font='sans', spacing=0.0, italic=False):
        if not s:
            return 0.0
        if font == 'mono':
            return len(s) * (size * 0.6 + spacing)
        _, sh = self._shape(s, font, weight, italic)
        # a trailing / leading space has no ink: count it at a quarter em, as the canvas would give it room
        pad = (len(s) - len(s.lstrip(' ')) + len(s) - len(s.rstrip(' '))) * 0.27 if s.strip() else len(s) * 0.27
        return (sh.width + pad) * size + len(s) * spacing

    def cw(self, size):
        return size * 0.6

    def fit(self, s, max_w, font='serif', weight=700, spacing_em=0.0, max_size=2000, italic=False):
        w100 = self.measure(s, size=100, weight=weight, font=font, spacing=spacing_em * 100, italic=italic)
        return min(max_size, max_w / max(w100, 1e-6) * 100)

    def wrap(self, s, max_w, **opts):
        out = []
        for para in str(s).split('\n'):
            line = ''
            for word in para.split(' '):
                nxt = f'{line} {word}' if line else word
                if line and self.measure(nxt, **opts) > max_w:
                    out.append(line)
                    line = word
                else:
                    line = nxt
            out.append(line)
        return out

    def text(self, s, x, y, size=24, weight=400, color='text', alpha=1.0, align='left', spacing=0.0, font='sans',
             stroke=0.0, italic=False):
        """Text with its BASELINE at y (canvas convention). align: left | center | right."""
        a = alpha * self.alpha
        if a <= 0.003 or not s or not str(s).strip():
            return
        s = str(s)
        key, sh = self._shape(s, font, weight, italic)
        if not sh.ok:
            return
        lead = (len(s) - len(s.lstrip(' '))) * 0.27 * size
        w = self.measure(s, size=size, weight=weight, font=font, spacing=spacing, italic=italic)
        if font == 'mono':  # mono: the advance grid, not the ink box
            ink = sh.width * size + (len(s.strip()) - 1) * spacing
            lead = (len(s) - len(s.lstrip(' '))) * (size * 0.6 + spacing) + max(0.0, (len(s.strip()) * (size * 0.6 + spacing) - spacing - ink) / 2)
        x0 = x - (w / 2 if align == 'center' else w if align == 'right' else 0) + lead
        # pooled Text instance for this layout
        n = self._ti.get(key, 0)
        pool = self._tpool.setdefault(key, [])
        if n >= len(pool):
            m = sh.proto.copy()
            m.submobjects = [VMobject() for _ in sh.pts]
            pool.append(m)
        m = pool[n]
        self._ti[key] = n + 1
        col = mcolor(self.rgb(color))
        sc = self.scale_now()
        for g, p, ci in zip(m.submobjects, sh.pts, sh.char_index):
            q = p * size
            q[:, 0] += x0 + ci * spacing
            q[:, 1] += y
            g.points = self._out(q.reshape(-1, 4, 2))
            if stroke > 0:
                g.set_fill(opacity=0.0, family=False)
                g.set_stroke(col, width=stroke * sc, opacity=min(1.0, a), family=False)
            else:
                g.set_fill(col, opacity=min(1.0, a), family=False)
                g.set_stroke(width=0, opacity=0.0, family=False)
        if self._glow:
            gc, gr, ga = self._glow
            for g in m.submobjects:
                h = self._vm()
                h.points = g.points.copy()
                h.set_fill(opacity=0.0, family=False)
                h.set_stroke(mcolor(gc), width=max(1.0, gr * 0.5 * sc), opacity=min(1.0, ga * 0.18 * self.alpha), family=False)
                self.items.append(h)
        self.items.append(m)
        return w

    # ---- images ------------------------------------------------------------------------------------------
    def image(self, name, x, y, w, h, alpha=1.0, flip=False, variant='ink', rot=0.0, crop=None):
        """Character art (assets/character) into the rect x, y, w, h. variant: see art.py."""
        a = alpha * self.alpha
        if a <= 0.01:
            return
        from .art import art_pixels
        arr = art_pixels(self.env, name, variant, self.pal, crop)
        if arr is None:
            return
        key = (name, variant, id(arr))
        n = self._ii.get(key, 0)
        pool = self._ipool.setdefault(key, [])
        if n >= len(pool):
            pool.append(ImageMobject(arr.copy()))
        m = pool[n]
        self._ii[key] = n + 1
        x0, x1 = (x + w, x) if flip else (x, x + w)
        if rot:
            cx, cy = x + w / 2, y + h / 2
            c, s = math.cos(rot), math.sin(rot)
            rp = lambda px, py: (cx + (px - cx) * c - (py - cy) * s, cy + (px - cx) * s + (py - cy) * c)
            corners = [rp(x0, y), rp(x1, y), rp(x0, y + h), rp(x1, y + h)]
        else:
            corners = [(x0, y), (x1, y), (x0, y + h), (x1, y + h)]
        q = np.array(corners, dtype=float).reshape(1, 4, 2)
        m.points = self._out(q)
        qa = round(a * 16) / 16
        if getattr(m, '_wem_a', None) != qa:
            m.set_opacity(qa)
            m._wem_a = qa
        self.items.append(m)

    # ---- effects that the engine applies to the whole frame ------------------------------------------------
    def flash(self, v, color=None):
        if v > self.fx.get('flash', 0):
            self.fx['flash'] = v
            self.fx['flashColor'] = self.rgb(color) if color else None
