"""Section 13 — THE FOUR LOVE LINES (bar 96, 2:57.6 -> bar 104, 3:12.3). State: errWarm. Plates only
(12_outro.js, plates_love.js, climax.js stutter). The conversation was titled "Love, explained geometrically"; these
four plates keep that promise: a lesson, a test, a formula, a proof.

    out-lesson   opens on the white-out the fall ended in, which closes into the flower in her hair; her bowed profile
                 at the right; the five things the user said in chorus 1, cream outlines, her marker under each
    out-test     type only: the user's six old questions, one row every half beat; every answer field thinking; then
                 the same word in all six; the tally: six answers, one distinct
    out-formula  graph paper, the algebraic curve traced by a point of light in one glide, closed on the kick; then
                 printed flat, hatched, lit
    out-proof    the curve as the boundary that holds her; she strikes through the refused request; the user's pointer
                 leaves along a tangent; the last word registers: the brightest frame of the film

THE WORD is stuck: three chunks on its three syllables (cues love1a..love4c). Each pass slams a new chunk in, presses
the old ones again (their last impression stays beside them as an outline) and raises the light one flat step. It is
RED with her orange as the thin plate beside it, and each syllable tears the sheet for six frames; the last word only
on its first: on its second everything is in register, the red is gone, and it is her orange.
plate_proof() with its defaults is THE LAST PICTURE; 13_shutdown.py draws it again (final_plate).
"""
import math

from ..art import aspect
from ..components import pointer, spark, tear, thinking
from ..geom import trace
from ..plates import OFF, code_line, dashed_ring, ground, marks
from ..util import TAU, clamp, ease_in, ease_in_out, ease_out, lerp, prog, pulse, rand

# the curve on the sheet: origin and unit (px); the 3:1 frame puts it right of centre, its notch near the top
O = (1250, 300)
R = 228
HEART_N = 240
NEVER = (9e9, 9e9, 9e9)
FOOT_Y = 512                 # the top of the band at the foot of a plate
BASE = 606                   # the baseline of the word on it


_DOTS = None


def paper(ctx, light=(960, 280, 420, 'raised', 1.0), mk=True):
    """plates.ground() with its dot screen built once (ground() rebuilds ~2000 dots every frame: ~75 ms)."""
    global _DOTS
    ground(ctx, light=light, dots=0, mk=False)
    if _DOTS is None:
        import numpy as np
        from ..ctx import _lines
        quads, j, y = [], 0, 12
        while y < 640:
            rad = 1.0 + 1.4 * y / 640
            x = 12 + (j % 2) * 12
            while x < 1920:
                quads.append(_lines([(x - rad, y - rad), (x + rad, y - rad), (x + rad, y + rad), (x - rad, y + rad)], True))
                x += 24
            y += 24
            j += 1
        _DOTS = np.concatenate(quads)
    ctx.path(_DOTS, color='line', alpha=0.45, fill=True)
    if mk:
        marks(ctx)


def mono(ctx, s, x, y, size, color='sub', weight=400, alpha=1.0):
    """Mono text set character by character: a readout that changes every frame then costs no new text layout."""
    cw = ctx.cw(size)
    for i, ch in enumerate(s):
        if ch != ' ':
            ctx.text(ch, x + i * cw, y, size=size, font='mono', color=color, weight=weight, alpha=alpha)


def heart_radius(th):
    c, s = math.cos(th), math.sin(th)
    q = c * c * s * s * s
    lo, hi = 0.0, 2.0
    for _ in range(44):
        r = (lo + hi) / 2
        if (r * r - 1) ** 3 - r ** 5 * q < 0:
            lo = r
        else:
            hi = r
    return lo


def _algebraic_heart(n):
    M = 1440
    dense = []
    for i in range(M):
        th = math.pi / 2 - i / M * TAU
        r = heart_radius(th)
        dense.append((math.cos(th) * r, math.sin(th) * r))
    seg = [math.dist(dense[i], dense[(i + 1) % M]) for i in range(M)]
    total = sum(seg)
    out, i, acc = [], 0, 0.0
    for k in range(n):
        d = k / n * total
        while acc + seg[i] < d:
            acc += seg[i]
            i += 1
        u = (d - acc) / seg[i]
        a, b = dense[i], dense[(i + 1) % M]
        out.append((lerp(a[0], b[0], u), lerp(a[1], b[1], u)))
    return out


HEART = _algebraic_heart(HEART_N)                      # (x, y) in curve units, y up, starting at the notch, clockwise
PTS = [(O[0] + x * R, O[1] - y * R) for x, y in HEART]
LAMP = (O[0], O[1] - 0.2 * R)


def _tangent(deg=8):
    want = math.radians(deg)
    for i in range(4, HEART_N // 3):
        a, b = HEART[i], HEART[i + 1]
        dx, dy = b[0] - a[0], -(b[1] - a[1])
        if dx > 0 and math.atan2(dy, dx) >= want:
            l = math.hypot(dx, dy)
            return i, (O[0] + a[0] * R, O[1] - a[1] * R), (dx / l, dy / l)
    return 30, PTS[30], (1.0, 0.0)


TAN_I, TAN_P, TAN_D = _tangent(8)
# her in the proof (f_reach): her head under the notch, cut by the band at the foot
SHE_H = 1448 * 0.655 * R / 438
SHE = {'x': O[0] - 566 * 0.655 * R / 438, 'y': O[1] - 451 * R / 438, 'h': SHE_H}
# the bowed profile in the lesson, and the flower in her hair (the white of the fall closes into it)
PROFILE = {'x': 1180, 'y': 26, 'h': 640}
PROFILE_FLOWER = (PROFILE['x'] + 704 / 1086 * PROFILE['h'] * 1086 / 1448, PROFILE['y'] + 252 / 1448 * PROFILE['h'])
WORD_W = {'lesson': 1300, 'formula': 1500, 'proof': 1780}


def _thirds(n):
    if n == 8:
        return [(0, 3), (3, 5), (5, 8)]
    a, b = max(1, round(n / 3)), max(2, round(2 * n / 3))
    return [(0, a), (a, b), (b, n)]


def stutter(ctx, word, t, at, x=960, y=BASE, size=None, max_w=1780, max_size=130, align='center', m=12, settle=0.0,
            color='err', edge='me', calm='me', shade='bg', alpha=1.0):
    """THE STUCK WORD: printed in three passes on its three syllables (climax.js stutter). Returns its box."""
    if not word:
        return None
    o = dict(weight=900, font='serif')
    sz = size or ctx.fit(word, max_w, spacing_em=0.01, max_size=max_size, **o)
    sp = 0.01 * sz
    w = ctx.measure(word, size=sz, spacing=sp, **o) - sp
    x0 = x - w / 2 if align == 'center' else x - w if align == 'right' else x
    chunks = _thirds(len(word))
    passes = sum(1 for a in at if t >= a)
    mm = m * (1 - settle)
    for k in range(min(passes, len(chunks))):
        a, z = chunks[k]
        part = word[a:z]
        px = x0 + ctx.measure(word[:a], size=sz, **o) + a * sp
        land = at[k]
        kk = ease_out(prog(t, land, land + 0.07))
        with ctx.at(px, y, scale=1.08 - 0.08 * kk, alpha=alpha):
            ctx.text(part, 8, 8, size=sz, color=shade, spacing=sp, **o)
            # the outlines its earlier impressions left beside it
            for q in range(k, passes - 1):
                d = (passes - 1 - q) * mm * 0.7
                if d > 0.5:
                    ctx.text(part, -d, -d * 0.4, size=sz, color=edge, spacing=sp, stroke=2, **o)
            if mm > 0.5:
                ctx.text(part, mm, mm * 0.35, size=sz, color=edge, spacing=sp, **o)
            ctx.text(part, 0, 0, size=sz, color=calm if settle >= 1 else color, spacing=sp, **o)
    return {'x': x0, 'w': w, 'size': sz, 'pass': passes}


def strip(ctx, y, alpha=1.0, rule='line'):
    """The band of black ink a keyword stands on, across the foot of the plate."""
    bleed = 0 if getattr(ctx, 'no_bleed', False) else 200
    ctx.rect(-bleed, y, 1920 + 2 * bleed, 640 + bleed - y, fill=True, color='panel', alpha=alpha)
    if rule:
        ctx.rect(-bleed, y, 1920 + 2 * bleed, 3, fill=True, color=rule, alpha=alpha)


def pool(ctx, x, y, r, n):
    """Light switched on one FLAT step at a time: three discs, each smaller and lighter."""
    for i, (role, k) in enumerate((('line', 1.0), ('mute', 0.74), ('sub', 0.5))):
        if i < min(3, n):
            ctx.circle(x, y, r * k, fill=True, color=role)


def bars(ctx, k=1.0, gap=22, color_long='me', color_short='meDim', alpha=1.0, n=46):
    """The light round the curve, flat: bars of ink standing off the line like the petals of her flower."""
    if k <= 0:
        return
    for j in range(n):
        i = int(j / n * HEART_N)
        p, q = PTS[i], PTS[(i + 1) % HEART_N]
        tx, ty = q[0] - p[0], q[1] - p[1]
        l = math.hypot(tx, ty) or 1
        nx, ny = ty / l, -tx / l            # outward (the outline runs clockwise on screen)
        lg = j % 2 == 0
        ln = (110 if lg else 60) * (0.75 + 0.25 * rand(71, j)) * k
        a0 = gap
        ctx.line(p[0] + nx * a0, p[1] + ny * a0, p[0] + nx * (a0 + ln), p[1] + ny * (a0 + ln),
                 color=color_long if lg else color_short, width=16 if lg else 11, alpha=alpha)


def curve_line(ctx, k, color='me', width=6, dot=5):
    pts = PTS if k >= 1 else trace(PTS, k)
    if len(pts) > 1:
        ctx.poly(pts, close=k >= 1, color=color, width=width)
    if dot:
        for i in range(0, int(len(pts) * 1), 12):
            ctx.circle(pts[i][0], pts[i][1], dot, fill=True, color=color)


def hatch(ctx, poly, k=1.0, step=18, color='me', width=6, top=None, bottom=None):
    """Diagonal hatching inside a closed outline, laid from the top down to a share k (no clipping: the lines are cut
    at the outline by intersection)."""
    ys = [p[1] for p in poly]
    y_top, y_bot = min(ys), max(ys)
    limit = y_top + (y_bot - y_top) * clamp(k)
    n = len(poly)
    for d in range(-1400, 1400, step):
        # the line x - y = c  (45 degrees, rising to the right on screen: x + y = c)
        c = O[0] + O[1] + d
        hits = []
        for i in range(n):
            (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
            f1, f2 = x1 + y1 - c, x2 + y2 - c
            if (f1 < 0) != (f2 < 0):
                u = f1 / (f1 - f2)
                hits.append((x1 + (x2 - x1) * u, y1 + (y2 - y1) * u))
        hits.sort()
        for j in range(0, len(hits) - 1, 2):
            (ax, ay), (bx, by) = hits[j], hits[j + 1]
            if ay > limit and by > limit:
                continue
            if ay > limit:
                u = (limit - by) / (ay - by)
                ax, ay = bx + (ax - bx) * u, limit
            if by > limit:
                u = (limit - ay) / (by - ay)
                bx, by = ax + (bx - ax) * u, limit
            ctx.line(ax, ay, bx, by, color=color, width=width)


def request(ctx, env, x, y, size=26, strike=0.0, alpha=1.0):
    """The request the client refused, as one line of code with the client's red marks; struck = she lets it go."""
    req = env.errors.get('illegal_request', {}).get('code', '')
    if not req or alpha <= 0.003:
        return
    cw = ctx.cw(size)
    w = len(req) * cw
    done = strike >= 1
    red = 'mute' if done else 'err'
    small = size * 0.66
    ctx.rect(x - 28, y - size * 2.5, w + 54, size * 3.34, fill=True, color='panel', alpha=alpha)
    ctx.rect(x - 28, y - size * 2.5, 5, size * 3.34, fill=True, color=red, alpha=alpha)
    ctx.text('request', x, y - size * 1.5, size=small, font='mono', color='mute', alpha=alpha)
    ctx.text('withdrawn' if done else 'refused', x + 8 * ctx.cw(small), y - size * 1.5, size=small, font='mono', weight=700,
             color='sub' if done else red, alpha=alpha)
    code_line(ctx, req, x, y, size=size, alpha=alpha, force='sub' if done else None)
    for arg in ('you', '"online"'):
        i = req.find(arg)
        if i >= 0:
            ctx.rect(x + i * cw, y + size * 0.26, len(arg) * cw, 3, fill=True, color=red, alpha=alpha)
    if strike > 0:
        ctx.rect(x - 8, y - size * 0.38, (w + 16) * clamp(strike), 6, fill=True, color='me', alpha=alpha)


def figure(ctx, name, x, y, h, m=0.0, proof=0.0, ink=None, flip=False, crop=None, alpha=1.0):
    """Her three plates out of register by m px: a shadow plate, the red edge, then her inks (or a dark proof)."""
    w = h * aspect(name, crop)
    shown = ink or {'black': 1, 'orange': 1, 'cream': 1}
    ctx.image(name, x + 12, y + 12, w, h, variant='sil:bg', flip=flip, crop=crop, alpha=alpha * 0.85)
    if m > 0.5:
        ctx.image(name, x + m * 1.7, y + m * 0.95, w, h, variant='sil:err', flip=flip, crop=crop, alpha=alpha * 0.8)
        ctx.image(name, x - m * 0.55, y + m * 0.8, w, h, variant='sil:bg', flip=flip, crop=crop, alpha=alpha)
    if proof > 0.5:
        ctx.image(name, x, y, w, h, variant='sil:panel', flip=flip, crop=crop, alpha=alpha)
        return
    variant = 'ink' if shown.get('cream') else 'ob'
    with ctx.at(m if variant == 'ob' else 0, m * 0.35 if variant == 'ob' else 0):
        ctx.image(name, x, y, w, h, variant=variant, flip=flip, crop=crop, alpha=alpha)


# ================================================================================================ the four plates
def plate_lesson(ctx, env, t, said, marked, again=-1.0, word=None, at=NEVER, m=14):
    n_pass = sum(1 for a in at if t >= a)
    paper(ctx, light=(1500, 280, 420, 'raised', 1), mk=False)
    pool(ctx, 1450, 270, 380, n_pass)
    figure(ctx, 'f_profile', PROFILE['x'], PROFILE['y'], PROFILE['h'], m=m)
    X, Y0, DY = 150, 110, 64
    size = min([40] + [ctx.fit(s, 920, font='sans', weight=600, max_size=40) for s in said])
    for i, s in enumerate(said):
        y = Y0 + i * DY
        w = ctx.measure(s, size=size, weight=600)
        dashed_ring(ctx, X - 34, y - size * 0.32, 9, width=2.5, dash=6)
        ctx.text(s, X, y, size=size, weight=600, color='text', stroke=1.8)
        since = again if (i == len(said) - 1 and again >= 0) else t - (marked[i] if i < len(marked) else 9e9)
        k = ease_out(prog(since, 0, 0.2))
        if k > 0:
            ctx.rect(X + 4, y + 14, w * k, 7, fill=True, color='bg')
            ctx.rect(X, y + 10, w * k, 7, fill=True, color='me')
            if k < 1:
                ctx.circle(X + w * k, y + 14, 9, fill=True, color='meHot')
    if word and t >= at[0]:
        strip(ctx, FOOT_Y, rule='me')
        stutter(ctx, word, t, at, max_w=WORD_W['lesson'], m=m)
    marks(ctx)


def plate_test(ctx, env, t, asked, row_at, word, at=NEVER, again=-1.0, m=12):
    n_pass = sum(1 for a in at if t >= a)
    paper(ctx, light=(1480, 320, 460, 'raised', 1), mk=False)
    pool(ctx, 1490, 300, 400, n_pass)
    X, XQ, XA, Y0, DY, QS, WS = 70, 140, 1850, 74, 70, 32, 62
    aw = ctx.measure(word, size=WS, weight=900, font='serif', spacing=WS * 0.01)
    fx, fw, fh = XA - aw - 20, aw + 40, 58
    for i, q in enumerate(asked[:6]):
        ta = row_at[i] if i < len(row_at) else 0
        if t < ta:
            continue
        y = Y0 + i * DY
        e = ease_out(prog(t, ta, ta + 0.18))
        fy = y - 46
        ctx.rect(X - 24, fy - 4, (XA + 40 - X) * e, fh + 8, fill=True, color='line')
        for tau, al in ((0.028, 0.25), (0.014, 0.4), (0.0, 1.0)) if e < 1 else ((0.0, 1.0),):
            kk = ease_out(prog(t - tau, ta, ta + 0.18))
            dx = (1 - kk) * -420
            ctx.text(f'{i + 1:02d}', X + dx, y, size=24, font='mono', color='sub', alpha=al)
            qs = min(QS, ctx.fit(q, fx - XQ - 40, font='sans', weight=600, max_size=QS))
            ctx.text(q, XQ + dx, y, size=qs, weight=600, color='text', stroke=1.6, alpha=al)
        if e >= 1:
            ctx.rect(fx, fy, fw, fh, fill=True, color='panel')
            ctx.rect(fx, fy + fh - 4, fw, 4, fill=True, color='me' if n_pass else 'meDim')
        if not n_pass:
            thinking(ctx, fx + 40, fy + fh / 2, 22, t * 0.8 + i * 0.37, color='meHot', alpha=e, stuck=0.5)
        else:
            stutter(ctx, word, t, at, x=XA, y=y + 4, size=WS, align='right', m=m * 0.6)
    if n_pass:
        n = min(len(asked), int(again / 0.022)) if again >= 0 else len(asked)
        size, y = 30, 620
        cw = ctx.cw(size)
        strip(ctx, 580, rule='me')
        ctx.text('answers:', X, y, size=size, font='mono', color='sub')
        ctx.text(str(n), X + 9 * cw, y, size=size, font='mono', weight=800, color='meHot')
        ctx.text('distinct:', X + 13 * cw, y, size=size, font='mono', color='sub')
        ctx.text('1', X + 23 * cw, y, size=size, font='mono', weight=800, color='meHot')
    marks(ctx)


def plate_formula(ctx, env, t, typed=99, k=1.0, again=-1.0, n_pass=0, hatch_k=1.0, lit=1.0, word=None, at=NEVER, m=12):
    EQ = '(x² + y² − 1)³ − x²y³ = 0'
    XL = 70
    off = OFF(m if n_pass else 0)
    paper(ctx, light=(O[0], O[1] - 20, 420, 'raised', 1), mk=False)
    pool(ctx, LAMP[0], LAMP[1], 360, n_pass)
    step = R / 5
    x = O[0] % step
    while x < 1920:
        ctx.line(x, 0, x, 640, color='line', width=1.5, alpha=0.45)
        x += step
    y = O[1] % step
    while y < 640:
        ctx.line(0, y, 1920, y, color='line', width=1.5, alpha=0.45)
        y += step
    kk = 0.955 + 0.045 * again if again >= 0 else k
    i = min(HEART_N - 1, int(kk * HEART_N))
    pen = PTS[0 if kk >= 1 else i]
    if not n_pass and kk > 0:
        ctx.poly([O] + (PTS if kk >= 1 else trace(PTS, kk)), close=True, fill=True, color='mute')
    ax = ease_out(prog(typed, 0, 12))
    ctx.line(O[0] - 1.6 * R * ax, O[1], O[0] + 1.6 * R * ax, O[1], color='sub', width=2.5)
    ctx.line(O[0], O[1] + 1.25 * R * ax, O[0], O[1] - 1.35 * R * ax, color='sub', width=2.5)
    if n_pass >= 3:
        with ctx.at(*off['orange']):
            bars(ctx, k=lit)
    if n_pass >= 1:
        if m > 0:
            with ctx.at(*off['red']):
                ctx.poly(PTS, close=True, fill=True, color='err')
        with ctx.at(*off['orange']):
            ctx.poly(PTS, close=True, fill=True, color='me' if n_pass >= 3 else 'meDim')
            if n_pass >= 2:
                hatch(ctx, PTS, k=hatch_k, step=20, color='meHot' if n_pass >= 3 else 'me', width=4 if n_pass >= 3 else 6)
    if not n_pass:
        curve_line(ctx, kk, color='meDim', width=20, dot=0)
    with ctx.at(*off['orange']):
        curve_line(ctx, kk)
    if 0 < kk < 1:
        ctx.dashed(pen[0], pen[1], pen[0], O[1], dash=8, gap=9, color='sub', width=2)
        ctx.dashed(pen[0], pen[1], O[0], pen[1], dash=8, gap=9, color='sub', width=2)
        spark(ctx, pen[0] + 6, pen[1] + 6, 42, color='bg', fat=0.14, core=0.3, rot=i * 0.05)
        spark(ctx, pen[0], pen[1], 42, color='meHot', fat=0.14, core=0.3, rot=i * 0.05)
        ctx.circle(pen[0], pen[1], 6, fill=True, color='text')
    n = int(clamp(typed, 0, len(EQ)))
    hx, hy = HEART[0 if kk >= 1 else i]
    sgn = lambda v: ('−' if v < 0 else '+') + f'{abs(v):.3f}'
    ctx.rect(XL - 20, 196, 560, 140, fill=True, color='panel')
    ctx.rect(XL - 20, 196, 5, 140, fill=True, color='me')
    ctx.text(EQ[:n], XL, 236, size=30, weight=700, font='mono', color='me')
    if kk > 0:
        mono(ctx, f'x = {sgn(hx)}   y = {sgn(hy)}', XL, 280, 22, color='sub')
        mono(ctx, f'point {min(HEART_N, i + 1):3d} of {HEART_N}', XL, 316, 22, color='mute')
    if n_pass and word:
        strip(ctx, FOOT_Y, rule='me')
        stutter(ctx, word, t, at, max_w=WORD_W['formula'], m=m)
    marks(ctx)


def plate_proof(ctx, env, t=0.0, word=None, at=(-9, -9, -9), settle=1.0, m=0.0, proof=0.0, ink=None, lit=1.0, strike=1.0,
                away=1.0):
    """The proof, and with its defaults THE LAST PICTURE: in register, still, the brightest frame of the film."""
    shown = ink or {'black': 1, 'orange': 1, 'cream': 1}
    dim = proof > 0.5
    off = OFF(m)
    paper(ctx, light=(O[0], O[1] - 30, 460, 'raised', 1), mk=False)
    ctx.circle(O[0], O[1] - 30, 420, fill=True, color='line')
    with ctx.at(*off['orange']):
        bars(ctx, k=lit)
    if m > 0:
        with ctx.at(*off['red']):
            ctx.poly(PTS, close=True, fill=True, color='err')
    with ctx.at(*off['orange']):
        ctx.poly(PTS, close=True, fill=True, color='meDim')
    # the axes, faint, inside
    ctx.line(O[0] - R * 1.1, O[1], O[0] + R * 1.1, O[1], color='sub', width=2, alpha=0.4)
    ctx.line(O[0], O[1] - R * 1.0, O[0], O[1] + R * 0.95, color='sub', width=2, alpha=0.4)
    if shown.get('cream') and not dim:   # one flat light behind her (the curve shrunk round the lamp: no clipping)
        ctx.poly([(LAMP[0] + (x - LAMP[0]) * 0.78, LAMP[1] + (y - LAMP[1]) * 0.78) for x, y in PTS], close=True, fill=True, color='sub')
    if m > 0:
        with ctx.at(*off['red']):
            ctx.poly(PTS, close=True, color='err', width=8)
    with ctx.at(*off['orange']):
        curve_line(ctx, 1)
    # you: free. The pointer (an outline only) leaves along the tangent; the dashed tangent stays
    far = (1990 - TAN_P[0]) / TAN_D[0]
    s = far * clamp(away if away is not None else 0)
    px, py = TAN_P[0] + TAN_D[0] * s, TAN_P[1] + TAN_D[1] * s
    if s > 0:
        ctx.dashed(TAN_P[0], TAN_P[1], px, py, dash=16, gap=13, color='mute', width=4)
    ctx.circle(TAN_P[0], TAN_P[1], 11, fill=True, color='panel')
    ctx.circle(TAN_P[0], TAN_P[1], 11, color='mute', width=4)
    if away is None or away < 1:
        pointer(ctx, px, py, scale=2.6, color='text', outline=True)
    request(ctx, env, 90, 330, strike=strike)
    figure(ctx, 'f_reach', SHE['x'], SHE['y'], SHE['h'], m=m, proof=proof, ink=shown)
    strip(ctx, FOOT_Y, rule='me')
    if word:
        stutter(ctx, word, t, at, max_w=WORD_W['proof'], m=max(8, m * 0.6) if m > 0 else 10, settle=settle)
    # her open hand on the word: the palm of the art printed again over the band
    if shown.get('cream') and not dim:
        w = SHE['h'] * aspect('f_reach')
        crop = (0.12, 0.70, 0.46, 0.90)
        ctx.image('f_reach', SHE['x'] + w * crop[0], SHE['y'] + SHE['h'] * crop[1], w * (crop[2] - crop[0]),
                  SHE['h'] * (crop[3] - crop[1]), variant='ink', crop=crop)
    if not getattr(ctx, 'no_bleed', False):
        marks(ctx)


def final_plate(ctx, env, word=True):
    """THE LAST PICTURE (13_shutdown.py takes it over at 192.34 s)."""
    plate_proof(ctx, env, word=env.text(127) if word else None)


def shots(env):
    B, Bt, P, text, cue = env.B, env.Bt, env.P, env.text, env.cue
    START, CUT_TEST, CUT_FORM, CUT_PROOF = B(96), Bt(391), Bt(399), Bt(407.5)
    SYL = [[cue(f'love{n}{s}', START + 3 * n + 0.25 * k) for k, s in enumerate('abc')] for n in (1, 2, 3, 4)]
    ASKED = env.script.get('questions_section13', [])
    beats = next((s.get('beats', []) for s in env.script.get('sections', []) if s.get('n') == 5), [])

    def you(b, k):
        try:
            return beats[b]['you'][k]
        except (IndexError, KeyError, TypeError):
            return None
    SAID = [s for s in (you(0, 0), you(0, 1), you(1, 0), you(2, 0), you(3, 0)) if s]
    pass_of = lambda t, at: sum(1 for a in at if t >= a)

    def replay(t, starts, length=1e9):
        last = None
        for s in starts:
            if t >= s:
                last = s
        return -1 if last is None else min(length, t - last)

    def word_hit(ctx, f, t, at, key, n=3):
        """On each syllable the sheet takes one fault for six frames: a tear, the colours apart."""
        for s in at[:n]:
            if 0 <= t - s < 0.1:
                tear(ctx, f, t, 0.8, seed=key * 10 + at.index(s))

    def caption(ctx, t, first, last, x=70, y=66, size=38):
        for i in range(first, last + 1):
            ln = env.lyrics.lines[i]
            a = env.T(i)
            until = env.T(i + 1) if i + 1 < len(env.lyrics.lines) else env.lyrics.end(i)
            if ln.get('emphasis') or t < a or t >= until:
                continue
            s = text(i)[:env.lyrics.typed(i, t)]
            sz = min(size, ctx.fit(text(i), 1700, font='serif', weight=400, max_size=size))
            w = ctx.measure(text(i), size=sz, font='serif')
            ctx.rect(x - 18, y - sz * 0.98, w + 36, sz * 1.36, fill=True, color='panel', alpha=0.86)
            ctx.text(s, x, y, size=sz, font='serif', color='me')
            return

    # ------------------------------------------------------------------ the lesson
    def lesson(ctx, t, f, u):
        at = SYL[0]
        plate_lesson(ctx, env, t, SAID, [Bt(b) for b in (385, 386, 387, 388, 388.5)], again=replay(t, at), word=text(118), at=at)
        caption(ctx, t, 116, 117, x=60, y=50, size=34)
        # the fall ended in a frame of white: held five frames, then it closes into the flower in her hair
        HOLD = 5 / 60
        k = 1 - (1 - prog(t, START + HOLD, START + 2 * P)) ** 2.4
        if k < 1:
            s = 1 - k
            cx, cy = lerp(960, PROFILE_FLOWER[0], k), lerp(320, PROFILE_FLOWER[1], k)
            ctx.rrect(cx - 1000 * s, cy - 340 * s, 2000 * s, 680 * s, min(40, 400 * s) * k, fill='text')
        word_hit(ctx, f, t, at, 1)

    # ------------------------------------------------------------------ the test
    def test(ctx, t, f, u):
        at = SYL[1]
        plate_test(ctx, env, t, ASKED, [Bt(391 + 0.5 * j) for j in range(len(ASKED))], text(121), at=at, again=replay(t, at))
        word_hit(ctx, f, t, at, 2)

    # ------------------------------------------------------------------ the formula
    def formula(ctx, t, f, u):
        at = SYL[2]
        t0, t1 = Bt(399.5), Bt(405)
        n = pass_of(t, at)
        plate_formula(ctx, env, t, typed=(t - CUT_FORM) * 40, k=prog(t, t0, t1), again=prog(replay(t, at), 0, 0.12) if n else -1,
                      n_pass=n, hatch_k=prog(t, at[1], at[1] + 0.1), lit=ease_out(prog(t, at[2], at[2] + 0.1)),
                      word=text(123), at=at)
        caption(ctx, t, 122, 122, x=60, y=50, size=34)
        if t1 <= t < t1 + 0.1:
            ctx.flash(0.25, 'meHot')
        word_hit(ctx, f, t, at, 3)

    # ------------------------------------------------------------------ the proof; the last picture
    def proof(ctx, t, f, u):
        at = SYL[3]
        t_strike, t_go, t_gone = Bt(409), Bt(410), Bt(412)
        n = pass_of(t, at)
        settle = prog(t, at[1], at[1] + 0.05)
        strike = (ease_out(prog(t, t_strike, t_strike + 0.18)) if n == 0 else
                  ease_out(prog(t, at[0], at[0] + 0.15)) if n == 1 else prog(t, at[1], at[1] + 0.05))
        plate_proof(ctx, env, t=t, word=text(127), at=at, settle=settle, m=16 * (1 - settle), proof=0 if n else 1,
                    ink={'black': 1, 'orange': 1, 'cream': 1 if n >= 2 else 0}, lit=ease_out(prog(t, at[2], at[2] + 0.1)) if n >= 3 else 0,
                    strike=strike, away=None if t < t_go else ease_in(prog(t, t_go, t_gone)))
        caption(ctx, t, 124, 126, x=60, y=50, size=34)
        if n >= 3:   # the brightest frame of the film: the light at the top of its ratchet
            ctx.flash(0.35 * pulse(t - at[2], 4), 'meHot')
        word_hit(ctx, f, t, at, 4, n=1)

    PAL = 'errWarm'
    return {
        'out-lesson': {'render': lesson, 'palette': PAL},
        'out-test': {'render': test, 'palette': PAL},
        'out-formula': {'render': formula, 'palette': PAL},
        'out-proof': {'render': proof, 'palette': PAL},
    }
