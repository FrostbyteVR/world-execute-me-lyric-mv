"""Section 6 — VERSE 2 (bar 40, 1:14.2 -> bar 48, 1:29.0). State: warm (06_verse2.js, plates_verse2.js, objects.js,
molecules.js). Four role-play requests, and the user never waits for an answer to finish. On every noun the film
leaves the interface for a plate; the user's next click on Send ends it.

    v2-ask1..3   the user clicks Send: the request flies up out of the composer, her answer begins under it
    v2-eggplant  she IS the eggplant: its data card set in characters, in its own purple, her spark as its calyx; cut
                 open on the downbeat; on the keyword the colour runs out of it row by row and its molecules (fibre,
                 protein, sugar) are pulled out of it in cream paper, each captioned with name, formula and amount
    v2-tomato    the same grammar: the lid lifted off; lycopene, vitamin C, vitamin E
    v2-cat       herself in characters; on the noun the cat ears pop up; on the downbeat the print develops (cat_paws in
                 three inks) and her purr stands beside her as tabby stripes; on the keyword the stripes turn cream and
                 leave towards the user, their outlines staying
    v2-ask4      be god: on the kick the lights go down round the user's bubble
    v2-proof     a proof without its cream plate, a sun behind the void of her face; the missing plate slides over from
                 the user's bubble and registers on the keyword; the pointer leaves for the settings
3:1 reframing: the picture stands in the upper 520 px; the foot of the sheet (the composer's place) holds the keyword
and, at its right, the next request being typed. Characters are set on a cell grid sampled once from each shape.
"""
import math

import numpy as np
from manim import ImageMobject

from ..art import _source, aspect, regions
from ..components import R, burst, chat_layout, composer, draw_cursor, header, room, spark, window_frame
from ..ctx import _lines
from ..plates import arrow, band, ground, keyword
from ..util import TAU, clamp, ease_back, ease_in, ease_in_out, ease_out, lerp, prog, pulse, rand

REQ = [('nounEggplant', 44, 43), ('nounTomato', 47, 46), ('nounTabby', 50, 49), (None, 53, 52)]
FOOT = 520
CAP = {'x': 70, 'y': 82, 'size': 40}
C30 = math.cos(math.pi / 6)
LEN = [1, 0.8, 0.94, 0.74, 0.98, 0.82, 0.9, 0.76, 1, 0.8, 0.95, 0.78]
SCRAMBLE = 'ABCDEFGHIKLMNOPRSTUVXYZ0123456789#/<>[]%$'


def flash_in(t, at):
    return 0.0 if t < at else clamp(0.6 + (t - at) * 30)


# =============================================================================================== private helpers
_INK_ARR, _INK_POOL = {}, {}


def ink_image(ctx, name, x, y, w, h, roles, alpha=1.0, crop=None):
    """One or more ink plates of a silhouette, each in its own palette role: roles = {0: cream role, 1: orange role,
    2: black role}; a missing key leaves that ink out (exact plates: art.js inks({ plates: [{ ink, exact }] }))."""
    a = alpha * ctx.alpha
    if a <= 0.01:
        return
    src = _source(name)
    if src is None:
        return
    labels, al = src
    cols = {k: tuple(min(255, int(round(v / 4) * 4)) for v in ctx.rgb(r)) for k, r in roles.items() if r}
    key = (name, tuple(sorted(cols.items())), crop)
    arr = _INK_ARR.get(key)
    if arr is None:
        hh, ww = labels.shape
        arr = np.zeros((hh, ww, 4), dtype=np.uint8)
        mask = np.zeros((hh, ww), dtype=bool)
        for k, c in cols.items():
            m = labels == k
            arr[m, :3] = c
            mask |= m
        arr[..., 3] = np.where(mask, al, 0)
        if crop:
            u0, v0, u1, v1 = crop
            arr = arr[int(v0 * hh):max(int(v0 * hh) + 1, int(v1 * hh)), int(u0 * ww):int(u1 * ww)].copy()
        if len(_INK_ARR) > 300:
            _INK_ARR.clear()
        _INK_ARR[key] = arr
    pk = (key, id(arr))
    n = ctx._ii.get(pk, 0)
    pool = _INK_POOL.setdefault(pk, [])
    if n >= len(pool):
        pool.append(ImageMobject(arr.copy()))
    m = pool[n]
    ctx._ii[pk] = n + 1
    m.points = ctx._out(np.array([(x, y), (x + w, y), (x, y + h), (x + w, y + h)], dtype=float).reshape(1, 4, 2))
    qa = round(a * 16) / 16
    if getattr(m, '_wem_a', None) != qa:
        m.set_opacity(qa)
        m._wem_a = qa
    ctx.items.append(m)


_CELLS = {}


def glyph_cells(key, field, x0, y0, x1, y1, size):
    """Cells of a character grid over a shape: [(x, y, ink, dir)] (dir 0 = inside, 1 | 2 - 3 / 4 \\ = on the edge).
    field(x, y) -> ink at a point (0 = none). Sampled 3 x 3 per cell, once per key (ascii.js glyphPlate)."""
    c = _CELLS.get(key)
    if c is not None:
        return c
    cw, ch = size * 0.6, size
    gx0, gy0 = math.floor(x0 / cw) * cw, math.floor(y0 / ch) * ch
    cols, rows = int(math.ceil((x1 - gx0) / cw)), int(math.ceil((y1 - gy0) / ch))
    out = []
    for j in range(rows):
        for i in range(cols):
            cnt, n, left, right, top, bot = {}, 0, 0, 0, 0, 0
            for b in range(3):
                for a in range(3):
                    k = field(gx0 + (i + (a + 0.5) / 3) * cw, gy0 + (j + (b + 0.5) / 3) * ch)
                    if not k:
                        continue
                    cnt[k] = cnt.get(k, 0) + 1
                    n += 1
                    left += a == 0
                    right += a == 2
                    top += b == 0
                    bot += b == 2
            if n * 3 < 9:
                continue
            best = max(cnt, key=cnt.get)
            d = 0
            if n < 9:
                gx, gy = right - left, bot - top
                d = 1 if abs(gx) > 2 * abs(gy) else 2 if abs(gy) > 2 * abs(gx) else 3 if gx * gy > 0 else 4
            out.append((gx0 + i * cw, gy0 + (j + 0.8) * ch, best, d, i, j))
    if len(_CELLS) > 200:
        _CELLS.clear()
    _CELLS[key] = out
    return out


def draw_cells(ctx, cells, text, inks, size, edge=None, decode=None, shift=None, keep=None, t=0.0, seed=0):
    """Set characters on cells. inks = {ink: (role, weight, alpha, text?)}; edge = role of the outline glyphs.
    decode = 0..1 settled share (unsettled cells show noise); shift(j) = px a row has slid; keep(x, y) = still drawn."""
    n = len(text)
    for (x, y, ink, d, i, j) in cells:
        o = inks.get(ink)
        if not o:
            continue
        dx = shift(j) if shift else 0
        if dx > 2200:
            continue
        if keep and not keep(x + dx, y):
            continue
        role, wgt, al = o[0], o[1], o[2]
        src = o[3] if len(o) > 3 else text
        if edge and d:
            ch, role, wgt = '|-/\\'[d - 1], edge, 800
        else:
            ch = src[(i + j * 7) % len(src)] if src else '#'
        if decode is not None and decode < rand(seed, i, j):
            ch = SCRAMBLE[int(rand(seed, i, j, int(t * 30)) * len(SCRAMBLE))]
            role = 'mute'
        if ch == ' ':
            continue
        ctx.text(ch, x + dx, y, size=size, font='mono', weight=wgt, color=role, alpha=al)


def data_text(card, fallback, tail='per_100g'):
    rows = [f"{r['label'].lower().replace(' ', '_').replace(',', '_')}:{r['value'].replace(' ', '')}" for r in (card or {}).get('rows', [])]
    if not rows:
        return fallback
    return ('·'.join([*rows, tail] if tail else rows) + '·')


def spark_outline(cx, cy, r, rot=0.0, n=168, rays=12, inner=0.34):
    out = []
    for k in range(n):
        u = k / n * rays
        i = int(u)
        f = u - i
        rr = r * (inner + (LEN[i % 12] * (1 - f) + LEN[((i + 1) % rays) % 12] * f - inner) * abs(math.cos(f * math.pi)) ** 1.6)
        a = rot + k / n * TAU - math.pi / 2
        out.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    return out


def in_poly(pts, x, y):
    inside, j = False, len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


def ellipse_pts(cx, cy, rx, ry, rot=0.0, n=48):
    c, s = math.cos(rot), math.sin(rot)
    return [(cx + math.cos(a) * rx * c - math.sin(a) * ry * s, cy + math.cos(a) * rx * s + math.sin(a) * ry * c)
            for a in (k / n * TAU for k in range(n))]


def curve(pairs):
    def f(x):
        n = len(pairs)
        if x <= pairs[0][0]:
            return pairs[0][1]
        if x >= pairs[-1][0]:
            return pairs[-1][1]
        i = 0
        while x > pairs[i + 1][0]:
            i += 1
        p0, p1, p2, p3 = pairs[max(0, i - 1)][1], pairs[i][1], pairs[i + 1][1], pairs[min(n - 1, i + 2)][1]
        u = (x - pairs[i][0]) / (pairs[i + 1][0] - pairs[i][0])
        return 0.5 * (2 * p1 + (p2 - p0) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (3 * p1 - p0 - 3 * p2 + p3) * u ** 3)
    return f


# =============================================================================================== molecules
class Mol:
    def __init__(self):
        self.atoms, self.bonds = [], []

    def atom(self, x, y, label=None):
        self.atoms.append((x, y, label))
        return len(self.atoms) - 1

    def bond(self, i, j, order=1):
        self.bonds.append((i, j, order))
        return j

    def stub(self, i, dx, dy, label=None, order=1):
        return self.bond(i, self.atom(self.atoms[i][0] + dx, self.atoms[i][1] + dy, label), order)


def _lycopene():
    m, DOUBLE, METHYL = Mol(), {1, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 29}, {1, 5, 9, 13, 18, 22, 26, 30}
    at = m.atom(0, 0)
    for k in range(1, 32):
        at = m.stub(at, C30, -0.5 if k % 2 else 0.5, None, (2 if k % 2 else -2) if (k - 1) in DOUBLE else 1)
        if k in METHYL:
            m.stub(at, 0, -1 if k % 2 else 1)
    return m


def _ascorbic():
    m, r = Mol(), 0.8507
    v = [(r * math.cos(d * math.pi / 180), r * math.sin(d * math.pi / 180)) for d in (-90, -18, 54, 126, 198)]
    out = lambda i: (v[i][0] / r, v[i][1] / r)
    c4, o, c1, c2, c3 = m.atom(*v[0]), m.atom(*v[1], 'O'), m.atom(*v[2]), m.atom(*v[3]), m.atom(*v[4])
    m.bond(c4, c3)
    m.bond(c3, c2, -2)
    m.bond(c4, o)
    m.bond(c2, c1)
    m.bond(o, c1)
    m.stub(c3, *out(4), 'HO')
    m.stub(c2, *out(3), 'HO')
    m.stub(c1, *out(2), 'O', 2)
    c5 = m.stub(c4, 0.5, -C30)
    m.stub(c5, 1, 0, 'OH')
    m.stub(m.stub(c5, -0.5, -C30), -1, 0, 'HO')
    return m


def _tocopherol():
    m = Mol()
    c6, c5, c7 = m.atom(-C30, -0.5), m.atom(0, -1), m.atom(-C30, 0.5)
    c8, c4a, c8a = m.atom(0, 1), m.atom(C30, -0.5), m.atom(C30, 0.5)
    m.stub(c6, -C30, -0.5, 'HO')
    m.bond(c6, c5, 2)
    m.bond(c6, c7)
    m.bond(c5, c4a)
    m.bond(c7, c8, -2)
    m.bond(c8, c8a)
    m.bond(c4a, c8a, 2)
    m.stub(c5, 0, -1)
    m.stub(c7, -C30, 0.5)
    m.stub(c8, 0, 1)
    c4 = m.stub(c4a, C30, -0.5)
    o1 = m.stub(c8a, C30, 0.5, 'O')
    c3 = m.stub(c4, C30, 0.5)
    c2 = m.stub(o1, C30, -0.5)
    m.bond(c3, c2)
    m.stub(c2, 0.34, 0.94)
    at = c2
    for k in range(1, 14):
        at = m.stub(at, C30, -0.5 if k % 2 else 0.5)
        if k % 4 == 0:
            m.stub(at, 0, 1)
    return m


def _ring(m, c4):
    c5 = m.stub(c4, 0.5, -C30)
    c3 = m.stub(c4, 0.5, C30)
    o5 = m.stub(c5, 1, 0, 'O')
    c2 = m.stub(c3, 1, 0)
    c1 = m.stub(o5, 0.5, C30)
    m.bond(c2, c1)
    m.stub(c3, -0.5, C30, 'HO')
    m.stub(c2, 0.5, C30, 'OH')
    m.stub(m.stub(c5, -0.5, -C30), 0.5, -C30, 'OH')
    return c1


def _glucose():
    m = Mol()
    c4 = m.atom(-1, 0)
    m.stub(c4, -1, 0, 'HO')
    m.stub(_ring(m, c4), 1, 0, 'OH')
    return m


def _cellulose(n):
    m = Mol()
    c4 = m.atom(-1, 0)
    m.stub(c4, -1, 0, 'HO')
    for _ in range(n):
        c4 = m.stub(m.stub(_ring(m, c4), C30, 0.5, 'O'), C30, -0.5)
    return m


def _peptide(n):
    m = Mol()
    at = m.atom(0, 0, 'N')
    for k in range(1, 3 * n):
        at = m.stub(at, C30, -0.5 if k % 2 else 0.5, 'NH' if k % 3 == 0 else None)
        if k % 3 == 1:
            m.stub(at, 0, -1 if k % 2 else 1, 'R')
        if k % 3 == 2:
            m.stub(at, 0, -1 if k % 2 else 1, 'O', 2)
    return m


MOL = {'lycopene': _lycopene(), 'ascorbic': _ascorbic(), 'tocopherol': _tocopherol(), 'glucose': _glucose(),
       'cellulose': _cellulose(4), 'peptide': _peptide(5)}


def draw_molecule(ctx, M, x, y, L, k=1.0, color='text', ink='panel', shade='bg'):
    """A skeletal formula cut out of cream paper (molecules.js): bonds as flat strips, hetero atoms as discs with
    their letters cut out; k = share drawn, bond after bond in the order they were written."""
    drawn = clamp(k) * len(M.bonds)
    if drawn <= 0:
        return
    P = [(x + ax * L, y + ay * L) for ax, ay, _ in M.atoms]
    w = max(3.0, 0.19 * L)
    for dx, dy, col, letters in ((0.13 * L, 0.13 * L, shade, False), (0, 0, color, True)):
        seen = set()
        for nb, (i, j, order) in enumerate(M.bonds):
            f = min(1.0, drawn - nb)
            if f <= 0:
                break
            x0, y0 = P[i]
            x1, y1 = x0 + (P[j][0] - x0) * f, y0 + (P[j][1] - y0) * f
            ctx.line(x0 + dx, y0 + dy, x1 + dx, y1 + dy, color=col, width=w)
            if abs(order) == 2:
                ln = math.hypot(P[j][0] - x0, P[j][1] - y0) or 1
                sg = 1 if order > 0 else -1
                nx, ny = -(P[j][1] - y0) / ln * 0.21 * L * sg, (P[j][0] - x0) / ln * 0.21 * L * sg
                u0, u1 = 0.16, min(0.84, f)
                if u1 > u0:
                    ctx.line(x0 + (P[j][0] - x0) * u0 + nx + dx, y0 + (P[j][1] - y0) * u0 + ny + dy,
                             x0 + (P[j][0] - x0) * u1 + nx + dx, y0 + (P[j][1] - y0) * u1 + ny + dy, color=col, width=w * 0.62)
            seen.add(i)
            if f >= 1:
                seen.add(j)
        for i in seen:
            label = M.atoms[i][2]
            if not label:
                continue
            px, py = P[i]
            r = 0.34 * L
            if len(label) == 1:
                ctx.circle(px + dx, py + dy, r, fill=True, color=col)
            else:
                ctx.rrect(px + dx - 0.52 * L, py + dy - r, 1.04 * L, 2 * r, r, fill=col)
            if letters:
                ctx.text(label, px, py + 0.15 * L, size=0.42 * L, weight=800, font='mono', align='center', color=ink)


def formula(ctx, s, x, y, size=20, color='text', weight=700, alpha=1.0):
    """A chemical formula in mono, its counts set smaller and low. Returns its width."""
    cx = x
    for i, ch in enumerate(s):
        low = ch.isdigit() or (ch == 'n' and i and s[i - 1] == ')')
        sz = size * 0.68 if low else size
        if alpha > 0:
            ctx.text(ch, cx, y + (size * 0.2 if low else 0), size=sz, weight=weight, font='mono', color=color, alpha=alpha)
        cx += sz * 0.6
    return cx - x


# molecule, first atom (x, y), bond length L, [from, to] after the keyword, card row, caption [x (negative = right edge), y]
GIFT = {
    'eggplant': [('cellulose', 860, 450, 34, (0.03, 0.32), 2, (-1880, 440)),
                 ('peptide', 1060, 160, 34, (0.08, 0.30), 3, (-1880, 120)),
                 ('glucose', 1440, 300, 28, (0.13, 0.30), 1, (1570, 250))],
    'tomato': [('lycopene', 640, 300, 32, (0.03, 0.32), 1, (-1880, 220)),
               ('ascorbic', 1560, 150, 40, (0.09, 0.28), 0, (1200, 66)),
               ('tocopherol', 1300, 420, 34, (0.13, 0.36), 2, (1560, 368))],
}


# =============================================================================================== the fruit
def _eggplant_geom(cx, cy, s, tilt, open_k):
    """Screen outlines of the eggplant (objects.js eggplant): upper piece, lower piece (or None), cut face, calyx."""
    Y0, Y1 = -0.8, 1.0
    WIDTH = curve([(-0.8, 0.0), (-0.77, 0.13), (-0.66, 0.2), (-0.4, 0.245), (-0.05, 0.31), (0.3, 0.4), (0.6, 0.44), (0.8, 0.4),
                   (0.93, 0.27), (0.985, 0.13), (1.0, 0.0)])
    SPINE = lambda y: 0.3 * math.sin((y + 0.3) * 1.15) - 0.08
    half = lambda y: max(0.0, WIDTH(y))
    CUT_Y, CUT_S = 0.3, 0.3
    k, e = clamp(open_k), ease_out(clamp(open_k))
    cs, sn = math.cos(tilt), math.sin(tilt)
    gap, turn = 0.34 * e, 0.13 * e
    cut_y = lambda x: CUT_Y + CUT_S * (x - SPINE(CUT_Y))

    def scr(x, y, lower=False):
        if lower:
            px, py = x - SPINE(CUT_Y), y - CUT_Y
            c, n = math.cos(turn), math.sin(turn)
            x = SPINE(CUT_Y) + px * c - py * n + 0.1 * gap
            y = CUT_Y + px * n + py * c + gap
        return (cx + (x * cs - (y - 0.1) * sn) * s, cy + (x * sn + (y - 0.1) * cs) * s)

    def body(n=48):
        Rr = [(SPINE(lerp(Y0, Y1, i / n)) + half(lerp(Y0, Y1, i / n)), lerp(Y0, Y1, i / n)) for i in range(n + 1)]
        Ll = [(SPINE(lerp(Y0, Y1, i / n)) - half(lerp(Y0, Y1, i / n)), lerp(Y0, Y1, i / n)) for i in range(n + 1)]
        return Rr + Ll[::-1]

    def split(lower):
        pts, out = body(), []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            ia, ib = a[1] > cut_y(a[0]), b[1] > cut_y(b[0])
            if ia == lower:
                out.append(a)
            if ia != ib:
                lo, hi = 0.0, 1.0
                for _ in range(16):
                    m = (lo + hi) / 2
                    x, y = lerp(a[0], b[0], m), lerp(a[1], b[1], m)
                    if (y > cut_y(x)) == ia:
                        lo = m
                    else:
                        hi = m
                out.append((lerp(a[0], b[0], lo), lerp(a[1], b[1], lo)))
        return out
    if k > 0:
        upper = [scr(x, y) for x, y in split(False)]
        lower = [scr(x, y, True) for x, y in split(True)]
    else:
        upper, lower = [scr(x, y) for x, y in body()], None
    faces = []
    if k > 0:
        for low in (True, False):
            c = scr(SPINE(CUT_Y), CUT_Y, low)
            w = half(CUT_Y) * s * 1.02
            ang = tilt + math.atan(CUT_S) + (turn if low else 0)
            faces.append((c, w, w * 0.34 * e, ang))
    at = lambda x, y: scr(SPINE(Y0) + x, Y0 + 0.03 + y)
    cal = [at(x * (0.3 + 0.12 * max(0, y) ** 0.8), y * (0.2 + 0.36 * max(0, y) ** 0.8) - 0.03)
           for x, y in spark_outline(0, 0, 1, rot=math.pi / 7, n=84, rays=7, inner=0.5)]
    stem = [at(x, y) for x, y in ((-0.07, -0.02), (-0.085, -0.2), (-0.05, -0.36), (0.06, -0.43), (0.15, -0.38), (0.1, -0.3), (0.07, -0.2), (0.075, -0.02))]

    def ink(X, Y):
        dx, dy = (X - cx) / s, (Y - cy) / s
        x, y = dx * cs + dy * sn, -dx * sn + dy * cs + 0.1
        if not (Y0 < y < Y1) or abs(x - SPINE(y)) >= half(y):
            return 0
        q = (x - SPINE(y)) / max(1e-6, half(y))
        return 2 if (-0.78 < q < -0.36 and -0.5 < y < 0.78 - 0.5 * (q + 0.78)) else 3 if q > 0.46 + 0.2 * y else 1
    knife = (scr(SPINE(CUT_Y) - 0.95, cut_y(SPINE(CUT_Y) - 0.95)), scr(SPINE(CUT_Y) + 0.95, cut_y(SPINE(CUT_Y) + 0.95)))
    return upper, lower, faces, [stem, cal], ink, knife


def _tomato_geom(cx, cy, s, open_k):
    T_ELL = [(-0.34, -0.02, 0.72, 0.8), (0.34, -0.02, 0.72, 0.8), (0, 0.1, 1.0, 0.74)]
    T_CUT, T_W, T_TILT = 0.02, 1.058, -0.09
    out = []
    for i in range(120):
        a = i / 120 * TAU - math.pi / 2
        c, sn_ = math.cos(a), math.sin(a)
        r = 0
        for ex, ey, rx, ry in T_ELL:
            A = (c / rx) ** 2 + (sn_ / ry) ** 2
            Bq = -2 * (c * ex / rx ** 2 + sn_ * ey / ry ** 2)
            Cq = (ex / rx) ** 2 + (ey / ry) ** 2 - 1
            r = max(r, (-Bq + math.sqrt(Bq * Bq - 4 * A * Cq)) / (2 * A))
        out.append((c * r, sn_ * r))
    k, e = clamp(open_k), ease_out(clamp(open_k))
    cs, sn = math.cos(T_TILT), math.sin(T_TILT)
    up, down, hh, turn = 0.2 * e, 0.27 * e, 0.25 * T_W * e, -0.07 * e
    front = lambda x: hh * math.sqrt(max(0.0, 1 - (x / T_W) ** 2))

    def scr(x, y, lid=False):
        if lid:
            py = y - T_CUT
            c, n = math.cos(turn), math.sin(turn)
            x, y = x * c - py * n - 0.05 * e, T_CUT + x * n + py * c - up
        else:
            y += down
        return (cx + (x * cs - y * sn) * s, cy + (x * sn + y * cs) * s)
    arc = lambda sign, n=30: [(lerp(T_W, -T_W, i / n), T_CUT + sign * front(lerp(T_W, -T_W, i / n))) for i in range(n + 1)]
    above = [p for p in out if p[1] < T_CUT]
    below = [p for p in out if p[1] >= T_CUT]
    i0 = next((i for i in range(1, len(above)) if above[i][0] < 0 and above[i - 1][0] > 0), 0)
    lid_l = above[i0:] + above[:i0] + arc(1)
    low_l = below + arc(-1)[::-1]
    whole = [scr(x, y) for x, y in out]
    lid = [scr(x, y, True) for x, y in lid_l] if k > 0 else whole
    low = [scr(x, y) for x, y in low_l] if k > 0 else None
    face = None
    if k > 0:
        c = scr(0, T_CUT)
        face = (c, T_W * s, hh * s, T_TILT)
    at = lambda x, y: scr(x, -0.735 + y, k > 0)
    cal = [at(x * (0.5 + 0.1 * max(0, y) ** 0.8), y * (0.12 + 0.2 * max(0, y) ** 0.8) + 0.02)
           for x, y in spark_outline(0, 0, 1, rot=math.pi / 7, n=84, rays=7, inner=0.42)]
    stem = [at(x, y) for x, y in ((-0.06, 0.0), (-0.07, -0.14), (-0.03, -0.27), (0.07, -0.31), (0.13, -0.26), (0.08, -0.2), (0.06, -0.12), (0.065, 0.0))]

    def ink(X, Y):
        dx, dy = (X - cx) / s, (Y - cy) / s
        x, y = dx * cs + dy * sn, -dx * sn + dy * cs
        if k <= 0:
            pass
        if not any(((x - ex) / rx) ** 2 + ((y - ey) / ry) ** 2 < 1 for ex, ey, rx, ry in T_ELL):
            return 0
        return 2 if ((x + 0.44) / 0.25) ** 2 + ((y + 0.3) / 0.33) ** 2 < 1 else 3 if (x + 0.16) ** 2 + (y + 0.2) ** 2 > 1 else 1
    knife = (scr(-1.3, T_CUT), scr(1.3, T_CUT))
    return lid, low, face, [stem, cal], ink, knife, (down + up) * s * 0.5


def shots(env):
    T, B, Bt, P, text = env.T, env.B, env.Bt, env.P, env.text
    cards = env.script.get('cards_section6', [])
    req = lambda i: cards[i]['request'] if i < len(cards) else ''
    SEND = [B(40), Bt(167.5), Bt(175.5), Bt(183.5)]
    NOUN = [env.features.snap_half(env.cue(REQ[k][0], SEND[k] + 0.5)) for k in range(3)]
    DARK, END = Bt(184.5), B(48)
    W0 = chat_layout(side=0)
    TH = W0['thread']
    BTN = (W0['composer']['x'] + W0['composer']['w'] - 36, W0['composer']['y'] + W0['composer']['h'] / 2)

    # ------------------------------------------------------------------ the glimpses of the interface
    CAMS = [{'zoom': 1.28, 'x': 80, 'y': 110, 'rot': 0}, {'zoom': 1.36, 'x': 60, 'y': 118, 'rot': -0.02},
            {'zoom': 1.32, 'x': 20, 'y': 112, 'rot': 0.016}, {'zoom': 1.1, 'x': 40, 'y': 60, 'rot': 0}]

    def glimpse_cam(k):
        def cam(t, f, u):
            c = CAMS[k]
            if k == 3:
                return dict(c)
            p = prog(t, u['at'], u['until'])
            return {'zoom': c['zoom'] * (1 + 0.03 * p), 'x': c['x'], 'y': c['y'] - 6 * p, 'rot': c['rot']}
        return cam

    def glimpse(k):
        def render(ctx, t, f, u):
            cut, (cue, line, kw) = SEND[k], REQ[k]
            dark = clamp((t - Bt(184)) * 30) if k == 3 else 0
            room(ctx, dim=0.5, t=t)
            window_frame(ctx, W0, glass=0.95)
            ctx.radial(960, 450, 560, 'meDim', 0.34)
            header(ctx, W0, title=env.script.get('title', ''), pres='online')
            y_prev, y_you, y_me = (200, 280, 390) if k < 3 else (170, 250, 360)
            spark(ctx, TH['x'] + 15, y_prev - 12, 13, alpha=0.6)
            ctx.text(text(kw), TH['x'] + 46, y_prev, size=30, weight=700, font='serif', color='meHot', alpha=0.6)

            def her(alpha=1.0):
                if t < T(line):
                    return
                s = text(line)
                n = env.lyrics.typed(line, t)
                fly = (1 - ease_out(prog(t, T(line), T(line) + 0.25))) * 60
                spark(ctx, TH['x'] + 15, y_me - 14 + fly, 13, alpha=alpha)
                ctx.text(s[:n], TH['x'] + 46, y_me + fly, size=40, font='serif', color='me', alpha=alpha)
                if n < len(s):
                    ctx.circle(TH['x'] + 46 + ctx.measure(s[:n], size=40, font='serif') + 12, y_me - 11 + fly, 6.5, fill=True, color='me', alpha=alpha)
            her()
            composer(ctx, W0['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, send='busy')
            burst(ctx, BTN[0], BTN[1], 40, (t - cut) / 0.45, color='text')
            if dark > 0:
                with ctx.screen():
                    ctx.rect(0, 0, 1920, 640, fill=True, color='panel', alpha=0.9 * dark)
                her(dark)
            # the request, thrown up out of the composer (ghosted while it flies), landing with a small overshoot
            s = req(k)
            sz = 30 if k < 3 else 34
            bw = ctx.measure(s, size=sz, weight=500 if dark > 0.5 else 400) + 50
            xr = TH['x'] + TH['w']

            def bubble(tt, alpha):
                kk = prog(tt, cut - 0.06, cut + 0.22)
                if kk <= 0:
                    return
                yb = y_you + (1 - ease_back(kk)) * 220
                a = clamp(kk * 4) * alpha
                if dark > 0.5:
                    ctx.rrect(xr - bw, yb - 46, bw, 64, 30, fill='text', alpha=a)
                    ctx.text(s, xr - bw + 25, yb - 2, size=sz, color='bg', weight=500, alpha=a)
                else:
                    ctx.rrect(xr - bw, yb - 46, bw, 64, 30, fill='raised', stroke='text', width=2, alpha=a)
                    ctx.text(s, xr - bw + 25, yb - 2, size=sz, color='text', alpha=a)
            if t < cut + 0.22:
                for i in (4, 3, 2, 1):
                    bubble(t - i * 0.018, 0.4 * (1 - i / 5))
            bubble(t, 1.0)
            way = ([{'t': cut, 'x': BTN[0] + 3, 'y': BTN[1] + 4}, {'t': DARK, 'x': 1500, 'y': 420}] if k == 3 else
                   [{'t': cut, 'x': BTN[0] + 3, 'y': BTN[1] + 4}, {'t': cut + 0.6, 'x': BTN[0] + 40, 'y': BTN[1] + 30}])
            draw_cursor(ctx, way, t)
        return render

    # ------------------------------------------------------------------ what every plate of the verse shares
    def sheet(ctx, light=(560, 280, 400, 'raised', 1.0)):
        ground(ctx, light=light)

    def foot(ctx, t, word_line, hit, color='text', glow=False):
        ctx.rect(-10, FOOT, 1940, 140, fill=True, color='panel')
        ctx.rect(-10, FOOT, 1940, 140, fill=True, color='raised', alpha=0.32)
        ctx.line(0, FOOT, 1920, FOOT, color='line', width=2)
        if t >= hit:
            if glow:
                with ctx.glow('me', 24, 0.5):
                    keyword(ctx, text(word_line), t, y=596, max_w=1300, max_size=104, at=hit, color=color, shade='bg', off=(7, 7))
            else:
                keyword(ctx, text(word_line), t, y=596, max_w=1300, max_size=104, at=hit, color=color, shade='bg', off=(7, 7))

    def caption(ctx, t, lines):
        for k, i in enumerate(lines):
            nxt = T(i + 1)
            if T(i) <= t < nxt:
                band(ctx, text(i), env.lyrics.typed(i, t), x=CAP['x'], y=CAP['y'], size=CAP['size'])

    def typing(ctx, t, nxt):
        if not nxt:
            return
        s, a, z = nxt
        a, z = Bt(a), Bt(z)
        if t < a - 0.25:
            return
        n = int(prog(t, a, z) * len(s) + 1e-6)
        x = 1846 - ctx.measure(s, size=24, weight=500)
        ctx.text(s[:n], x, 630, size=24, weight=500, color='text')
        if n < len(s) or int(t * 2.2) % 2 == 0:
            ctx.rect(x + ctx.measure(s[:n], size=24, weight=500) + 3, 610, 2.5, 26, fill=True, color='text')

    def gift(ctx, kind, since):
        if since < 0:
            return
        rows = cards[1 if kind == 'tomato' else 0]['rows'] if len(cards) > 1 else []
        drift = 26 * max(0, since - 0.3)
        for name, x, y, L, (t0, t1), row_i, (cx_, cy_) in GIFT[kind]:
            k = ease_out(prog(since, t0, t1))
            draw_molecule(ctx, MOL[name], x + drift, y, L, k)
            if row_i >= len(rows) or k <= 0:
                continue
            row = rows[row_i]
            a = clamp((since - t0) * 12)
            f = row.get('formula', '')
            w = max(ctx.measure(row['label'], size=20, weight=600), formula(ctx, f, 0, 0, size=20, alpha=0) + 24 + 12 * len(row['value']))
            x0 = -cx_ - w if cx_ < 0 else cx_
            ctx.text(row['label'], x0, cy_, size=20, weight=600, color='text', alpha=a)
            fw = formula(ctx, f, x0, cy_ + 26, size=20, alpha=a)
            ctx.text(row['value'], x0 + fw + 24, cy_ + 26, size=20, font='mono', color='sub', alpha=a)

    # ------------------------------------------------------------------ the eggplant, the tomato
    def plate_fruit(kind, k, settle_cue, open_beat, hit_line, lines, nxt):
        SP = kind
        txt = data_text(cards[k] if k < len(cards) else None, 'water:92g·' if kind == 'eggplant' else 'vitamin_c:13.7mg·')
        dots = ''.join('.' if c.isalpha() or c == '_' else c for c in txt)
        GLYPH = 16 if kind == 'eggplant' else 17

        def render(ctx, t, f, u):
            at, opn, hit = NOUN[k], Bt(open_beat), T(hit_line)
            settle = env.cue(settle_cue, at + 0.4)
            a = flash_in(t, at)
            cut = t - opn
            sheet(ctx)
            op = prog(t, opn, opn + 0.2)
            give = t - hit if t >= hit else -1
            gone = clamp(give / 0.1) if give >= 0 else 0
            knock = 1 + 0.045 * pulse(t - at, 16)
            sx, sy = (6 * pulse(cut, 14) * math.sin(cut * 90), 4 * pulse(cut, 14) * math.cos(cut * 70)) if cut >= 0 else (0, 0)
            if kind == 'eggplant':
                cx, cy, s = 580, 262, 200
                upper, lower, faces, caps, inkf, knife = _eggplant_geom(cx, cy, s, 0.8, op)
                pieces = [(upper, 'U')] + ([(lower, 'L')] if lower else [])
                face_list = faces
                lift = 0
            else:
                cx, cy, s = 600, 310, 170
                lid, low, face, caps, inkf, knife, lift = _tomato_geom(cx, cy, s, op)
                pieces = [(lid, 'U')] + ([(low, 'L')] if low else [])
                face_list = [face] if face else []
            with ctx.at(sx + cx * (1 - knock), sy + cy * (1 - knock), scale=knock, alpha=a):
                SH = 0.045 * s
                for pts, _ in pieces:
                    ctx.poly([(x + SH, y + SH) for x, y in pts], close=True, fill=True, color='bg')
                # the cut faces (under the pieces for the eggplant; on the lower half for the tomato)
                for (c, w, hh, ang) in face_list:
                    if hh < 2:
                        continue
                    if gone < 1:
                        ctx.poly(ellipse_pts(c[0], c[1], w, hh, ang), close=True, fill=True, color=f'{SP}.dark', alpha=1 - gone)
                        ctx.poly(ellipse_pts(c[0], c[1], w * 0.9, hh * 0.8, ang), close=True, fill=True, color=f'{SP}.light', alpha=1 - gone)
                        ca, sa = math.cos(ang), math.sin(ang)
                        for rr, n, ph in ((0.62, 9, 0.2), (0.3, 5, 0.9)):
                            for i in range(n):
                                q = ph + i / n * TAU
                                ex, ey = math.cos(q) * w * 0.9 * rr, math.sin(q) * hh * 0.8 * rr
                                ctx.poly(ellipse_pts(c[0] + ex * ca - ey * sa, c[1] + ex * sa + ey * ca, w * 0.06, max(1, hh * 0.13), ang + q, 10),
                                         close=True, fill=True, color='bg', alpha=1 - gone)
                    if gone > 0:
                        ctx.poly(ellipse_pts(c[0], c[1], w, hh, ang), close=True, color=f'{SP}.light', width=3, alpha=gone)
                rows_n = {}
                for pts, tag in pieces:
                    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
                    poly_ = pts

                    def field(X, Y, poly_=poly_):
                        return inkf(X, Y) if in_poly(poly_, X, Y) else 0
                    key = (kind, tag, round(op, 2) if op < 1 else 1)
                    cells = glyph_cells(key, field, min(xs), min(ys), max(xs), max(ys), GLYPH)
                    nrows = max([c[5] for c in cells] + [1]) + 1
                    seed = 70 if tag == 'U' else 71

                    def shift(j, seed=seed, nrows=nrows):
                        if give < 0:
                            return 0
                        return 2100 * clamp((give - 0.17 * (0.62 * j / nrows + 0.38 * rand(seed, j))) / 0.3) ** 2.2
                    if give < 0:
                        ctx.poly(pts, close=True, fill=True, color=f'{SP}.dark')
                    else:
                        # the flat colour row by row, each row where it has slid to (never past the outline: the
                        # colour that has left turns into the molecules)
                        spans = {}
                        for (x, y, ink, d, i, j) in cells:
                            lo, hi, _ = spans.get(j, (1e9, -1e9, y))
                            spans[j] = (min(lo, x), max(hi, x + GLYPH * 0.6), y)
                        for j, (lo, hi, yr) in spans.items():
                            dx = shift(j)
                            if lo + dx < hi:
                                ctx.rect(lo + dx, yr - GLYPH * 0.8, hi - lo - dx, GLYPH + 0.6, fill=True, color=f'{SP}.dark')
                    inks = {1: (f'{SP}.base', 800, 1.0), 2: (f'{SP}.light', 800, 1.0), 3: (f'{SP}.base', 400, 0.75, dots)}
                    draw_cells(ctx, cells, txt, inks, GLYPH, edge=f'{SP}.light',
                               decode=prog(t, at, settle) if t < settle else None, t=t, seed=31 + (tag == 'L'),
                               shift=shift if give >= 0 else None,
                               keep=(lambda X, Y, poly_=poly_: in_poly(poly_, X, Y)) if give >= 0 else None)
                    ctx.poly(pts, close=True, color=f'{SP}.light', width=3)
                if 0.02 < op < 1:
                    ctx.line(knife[0][0], knife[0][1] - lift, knife[1][0], knife[1][1] - lift, color=f'{SP}.light', width=5, alpha=1 - op)
                # calyx and stem: the spark as a cap, flat orange in a black outline
                lw = max(3, s * 0.014)
                for pts in caps:
                    ctx.poly([(x + SH * 0.6, y + SH * 0.6) for x, y in pts], close=True, fill=True, color='bg')
                    ctx.poly(pts, close=True, color='bg', width=lw * 2)
                    ctx.poly(pts, close=True, fill=True, color='me')
            gift(ctx, kind, t - hit)
            caption(ctx, t, lines)
            foot(ctx, t, hit_line, hit)
            typing(ctx, t, nxt)
        return render

    # ------------------------------------------------------------------ the tabby cat
    FIG = {'x': 300, 'y': 70, 'w': 520}
    FIG['h'] = FIG['w'] * 1448 / 1086
    kf = FIG['w'] / 1086
    RG = regions()
    fb = RG.get('f_bust', {}).get('flower', [760, 217])
    fp = RG.get('cat_paws', {}).get('flower', [801, 263])
    PAWS = {'x': FIG['x'] + (fb[0] - fp[0]) * kf, 'y': FIG['y'] + (fb[1] - fp[1]) * kf, 'w': FIG['w'], 'h': FIG['h']}
    CAT = {'x': FIG['x'] - 28 * kf, 'y': FIG['y'] - 49 * kf, 'w': FIG['w'], 'h': FIG['h']}
    EARS = [(CAT['x'] + e[0] * kf, CAT['y'] + e[1] * kf, e[2] * kf, e[3] * kf) for e in RG.get('cat_bust', {}).get('ears', [])]
    PURR = {'y': 300, 'x0': 900, 'x1': 1840, 'h': 150, 'w': 24,
            'amp': [0.5, 0.82, 0.62, 1, 0.7, 0.92, 0.56, 0.8, 1, 0.66, 0.88, 0.58, 0.44]}
    CAT_TXT = data_text(cards[2] if len(cards) > 2 else None, 'purr:25-150Hz·', '')
    CAT_DOTS = ''.join('.' if c.isalpha() or c == '_' else c for c in CAT_TXT)

    def fig_field(name, rect):
        src = _source(name)
        labels, al = src
        hh, ww = labels.shape

        def field(X, Y):
            u, v = (X - rect['x']) / rect['w'], (Y - rect['y']) / rect['h']
            if not (0 <= u < 1 and 0 <= v < 1):
                return 0
            px, py = int(u * ww), int(v * hh)
            return int(labels[py, px]) + 1 if al[py, px] > 128 else 0
        return field

    def glyph_figure(ctx, name, rect, t, decode=None, below=None, ears=None):
        ink_image(ctx, name, rect['x'], rect['y'], rect['w'], rect['h'], {0: 'mute', 1: 'meDim', 2: 'panel'})
        cells = glyph_cells(('fig', name), fig_field(name, rect), rect['x'], rect['y'], rect['x'] + rect['w'], min(FOOT + 20, rect['y'] + rect['h']), 15)
        inks = {1: ('text', 800, 1.0), 2: ('meHot', 800, 1.0), 3: ('line', 400, 1.0, CAT_DOTS)}
        if below is not None:
            cells = [c for c in cells if c[1] > below]
        if ears:   # the ears pop up: cells inside an ear box rise from its root
            out = []
            for c in cells:
                for (ex, ey, ew, eh) in EARS:
                    if ex <= c[0] <= ex + ew and ey <= c[1] - 8 <= ey + eh:
                        out.append((c[0], ey + eh - (ey + eh - c[1]) * max(0.03, ears), *c[2:]))
                        break
                else:
                    out.append(c)
            cells = out
        draw_cells(ctx, cells, CAT_TXT, inks, 15, edge='me', decode=decode, t=t, seed=43)

    def stripe(h, flip):
        return [(x * PURR['w'] * (-1 if flip else 1), y) for x, y in ((0, -h), (0.5, -0.3 * h), (0.4, 0.5 * h), (0, h), (-0.5, 0.25 * h), (-0.42, -0.55 * h))]

    def purr(ctx, t, at, develop, hit):
        n = len(PURR['amp'])
        pitch = (PURR['x1'] - PURR['x0']) / (n - 1)
        since = t - hit
        drawn = ease_out(prog(t, at + 0.05, at + 0.4))
        xe = lerp(PURR['x0'] - 30, PURR['x1'] + 30, drawn)
        ctx.line(PURR['x0'] - 30, PURR['y'], xe, PURR['y'], color='line', width=3)
        for i in range(n):
            x = PURR['x0'] + i * pitch
            if t < develop + i * 0.014:
                if x < xe:
                    ctx.poly([(x + px, PURR['y'] + py) for px, py in stripe(PURR['h'] * PURR['amp'][i], i % 2)], close=True, color='line', width=2.5)
                continue
            grow = ease_back(prog(t, develop + i * 0.014, develop + i * 0.014 + 0.18))
            breath = 1 + 0.09 * math.sin(TAU * (t - develop) / 1.846 - i * 0.45) * prog(t, develop + 0.3, develop + 0.6)
            h = PURR['h'] * PURR['amp'][i] * grow * breath
            pts = stripe(h, i % 2)
            t0 = 0.08 + 0.016 * ((i * 5) % n)
            if since < t0:
                ctx.poly([(x + px + 7, PURR['y'] + py + 7) for px, py in pts], close=True, fill=True, color='bg')
                ctx.poly([(x + px, PURR['y'] + py) for px, py in pts], close=True, fill=True, color='text' if since >= i * 0.006 else 'me')
                continue
            ctx.poly([(x + px, PURR['y'] + py) for px, py in pts], close=True, color='meDim', width=2.5)
            fly = 2300 * clamp((since - t0 - 0.05) / 0.36) ** 2.2
            lane = 110 + 380 * ((i * 5) % n) / (n - 1)
            if fly - h > 1920 - x + 40:
                continue
            yy = lerp(PURR['y'], lane, ease_out(prog(since, t0, t0 + 0.2)))
            with ctx.at(x + fly, yy, rot=math.pi / 2 * ease_in_out(prog(since, t0, t0 + 0.15))):
                ctx.poly([(px + 6, py + 6) for px, py in pts], close=True, fill=True, color='bg')
                ctx.poly(pts, close=True, fill=True, color='text')

    def plate_cat(ctx, t, f, u):
        at, ears, develop, hit = NOUN[2], env.cue('nounCat', NOUN[2] + 0.4), Bt(180), T(52)
        a = flash_in(t, at)
        sheet(ctx, (560, 300, 420, 'raised', 1))
        dev = prog(t, develop, develop + 0.14)
        k = 1 + 0.04 * pulse(t - at, 16) + 0.03 * pulse(t - develop, 14)
        purr(ctx, t, at, develop, hit)
        with ctx.at(560 * (1 - k), 300 * (1 - k), scale=k, alpha=a):
            if dev < 1:
                wipe = PAWS['y'] + PAWS['h'] * dev if dev > 0 else None
                if t < ears:
                    glyph_figure(ctx, 'f_bust', FIG, t, decode=prog(t, at, at + 0.3) if t < at + 0.3 else None, below=wipe)
                else:
                    glyph_figure(ctx, 'cat_bust', CAT, t, below=wipe, ears=ease_back(prog(t, ears, ears + 0.18)))
            if dev > 0:
                ink_image(ctx, 'cat_paws', PAWS['x'], PAWS['y'], PAWS['w'], PAWS['h'] * dev, {0: 'text', 1: 'me', 2: 'panel'}, crop=(0, 0, 1, max(0.002, dev)))
                if dev < 1:
                    ctx.rect(PAWS['x'], PAWS['y'] + PAWS['h'] * dev - 5, PAWS['w'], 10, fill=True, color='meHot')
        caption(ctx, t, [50, 51])
        foot(ctx, t, 52, hit)
        typing(ctx, t, (req(3), 181, 183.1))

    # ------------------------------------------------------------------ the proof (be god)
    SLIDE = 420

    def sun(ctx, cx, cy, k):
        r0, N = 120, 28
        for role, pick, ln, w in (('meDim', 0, 520, 0.066), ('me', 1, 340, 0.03)):
            for i in range(pick, N, 2):
                an = i / N * TAU + 0.11
                r1 = lerp(r0, ln, k)
                ctx.poly([(cx + math.cos(an - w) * r0, cy + math.sin(an - w) * r0), (cx + math.cos(an) * r1, cy + math.sin(an) * r1),
                          (cx + math.cos(an + w) * r0, cy + math.sin(an + w) * r0)], close=True, fill=True, color=role)
        ctx.circle(cx, cy, r0 * 1.04, fill=True, color='meDim')

    def target(ctx, x, y, color):
        ctx.circle(x, y, 10, color=color, width=2.5)
        ctx.line(x - 18, y, x + 18, y, color=color, width=2.5)
        ctx.line(x, y - 18, x, y + 18, color=color, width=2.5)

    def plate_proof(ctx, t, f, u):
        at, sun_t, slide, hit = DARK, env.cue('nounGod', DARK + 0.7), Bt(188), T(55)
        a = flash_in(t, at)
        lit = clamp((t - sun_t) * 30)
        sheet(ctx, (560, 300, 420, 'raised', 0.5 + 0.5 * lit))
        face = RG.get('f_bust', {}).get('face', [367, 259, 313, 369])
        C = (FIG['x'] + (face[0] + face[2] / 2) * kf, FIG['y'] + (face[1] + face[3] / 2) * kf)
        whole = t >= hit
        dx = SLIDE * (1 - ease_in_out(prog(t, slide, hit)))
        k = 1 + 0.03 * pulse(t - hit, 18)
        with ctx.fade(a):
            if t >= sun_t:
                sun(ctx, C[0], C[1], ease_out(prog(t, sun_t, sun_t + 0.12)))
            target(ctx, FIG['x'] - 60, 470, 'mute')
            with ctx.at(C[0] * (1 - k), C[1] * (1 - k), scale=k):
                if whole:
                    ink_image(ctx, 'f_bust', FIG['x'] + 8, FIG['y'] + 8, FIG['w'], FIG['h'], {0: 'bg', 1: 'bg', 2: 'bg'}, alpha=0.9)
                    ink_image(ctx, 'f_bust', FIG['x'], FIG['y'], FIG['w'], FIG['h'], {0: 'text', 1: 'me', 2: 'panel'})
                else:
                    ink_image(ctx, 'f_bust', FIG['x'] + 8, FIG['y'] + 8, FIG['w'], FIG['h'], {1: 'bg', 2: 'bg'}, alpha=0.9)
                    ink_image(ctx, 'f_bust', FIG['x'], FIG['y'], FIG['w'], FIG['h'], {1: 'me', 2: 'panel'})
                    if t >= slide:
                        ap = flash_in(t, slide)
                        ink_image(ctx, 'f_bust', FIG['x'] + dx + 8, FIG['y'] + 8, FIG['w'], FIG['h'], {0: 'bg'}, alpha=ap)
                        ink_image(ctx, 'f_bust', FIG['x'] + dx, FIG['y'], FIG['w'], FIG['h'], {0: 'text'}, alpha=ap)
            if t >= slide:
                target(ctx, FIG['x'] - 60 + dx, 470, 'text')
        # the user's request, cut out of cream paper, where the interface had the bubble
        s4 = req(3)
        bw = ctx.measure(s4, size=34, weight=500) + 60
        bx, by = 1840 - bw, 60
        ctx.rrect(bx + 8, by + 8, bw, 68, 30, fill='bg')
        ctx.rrect(bx, by, bw, 68, 30, fill='text')
        ctx.text(s4, bx + 30, by + 46, size=34, weight=500, color='bg')
        caption(ctx, t, [53, 54])
        if t >= T(56):
            band(ctx, text(56), env.lyrics.typed(56, t), x=CAP['x'], y=CAP['y'], size=CAP['size'])
        foot(ctx, t, 55, hit, color='meHot' if whole else 'text', glow=whole)
        # the pointer: it waits by its message, then leaves for the settings
        go = ease_in_out(prog(t, Bt(191), END))
        rest, to = (1700, 190), (1700, 30)
        ps = lerp(2.6, 1.5, go)
        px, py = lerp(rest[0], to[0], go), lerp(rest[1], to[1], go)
        arrow(ctx, px + 4 * ps, py + 4 * ps, ps, color='bg', edge=None)
        arrow(ctx, px, py, ps, color='text', edge='bg')

    return {
        'v2-ask1': {'render': glimpse(0), 'camera': glimpse_cam(0), 'palette': 'warm'},
        'v2-eggplant': {'render': plate_fruit('eggplant', 0, 'nounEggplantEnd', 164, 46, [44, 45], (req(1), 164.75, 166.75)), 'palette': 'warm'},
        'v2-ask2': {'render': glimpse(1), 'camera': glimpse_cam(1), 'palette': 'warm'},
        'v2-tomato': {'render': plate_fruit('tomato', 1, 'nounTomatoEnd', 172, 49, [47, 48], (req(2), 172.75, 174.9)), 'palette': 'warm'},
        'v2-ask3': {'render': glimpse(2), 'camera': glimpse_cam(2), 'palette': 'warm'},
        'v2-cat': {'render': plate_cat, 'palette': 'warm'},
        'v2-ask4': {'render': glimpse(3), 'camera': glimpse_cam(3), 'palette': 'warm'},
        'v2-proof': {'render': plate_proof, 'palette': 'warm'},
    }
