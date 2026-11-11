"""Section 12 — THE LAST CHORUS (bar 88, 2:42.8 -> bar 96, 2:57.6). State: errWarm. Plates only (12_chorusx.js,
climax.js figureStage). The four plates of chorus 1 printed again, BROKEN: the cream plate missing (grey dashed
outlines where the dot, the pointer, the heart were), the plates out of register (a thin red plate at one edge), larger,
every event further. Where chorus 1 had its interface shots there are FIGURE SHOTS: the silhouette is a base plate that
stands still; everything that moves lies behind it or on it.

    cx-eye   the letters of the last shout fly apart; her face full bleed, one eye open; in her iris the world turns
             and the light comes out of it; the loop's output runs up her black ink; the sung line on black strips
    cx-kw1   the bolt, sent to nobody: through the empty ring; on the second kick it strikes the edge of the sheet
    cx-bust  her bust; her face is a screen running the loop (round 12 of 12, no replies); behind her head the world
             turns in its cage, like a halo, and her spark is a sunburst as large as the sheet
    cx-kw2   the disc nobody presses: it sinks by itself, twice; no tick lights; the count reads 0
    cx-hand  her open hand across the sheet; in the palm a dashed heart, breathing, count 0; characters leave the palm
             for the user's side, pile up against the edge, break, and are gone
    cx-kw3   the listing running past its count: 13 / 12 ... 16 / 12, the sheet exposed a step further each round
    cx-fall  a window in a window in a window: one fall inwards, faster and faster; she is always in one still ahead;
             a window is empty and grey by the time the view is in it; at the end of the held note the frame is white
On every kick her plates spring apart and slide home, and for six frames the sheet is torn (drawn: no glitch pass).
"""
import math

import numpy as np

from ..art import _source, aspect
from ..components import burst, rays, spark, tear
from ..geom import MESH, draw_segs, place, sphere_glyphs
from ..plates import (LOOP, OFF, marks, plate_execution_stuck, plate_satisfaction, plate_stimulations, window_box)
from .s12_outro import paper
from ..util import TAU, clamp, ease_in, ease_out, lerp, prog, pulse, rand

# her face, full bleed, at the registration of the last shout: f_eye mirrored, its open eye at EYE_AT on the sheet
EYE_W = 2103
EYE_AT = (900, 330)
EYE_IMG = (EYE_AT[0] - 0.428 * EYE_W, EYE_AT[1] - 0.4177 * EYE_W, EYE_W, EYE_W)
IRIS_R = 30
# f_bust, whole, in the middle of the sheet; its face (regions.json `face`) is a screen
BUST_H = 630
BUST = (960 - BUST_H * 1086 / 1448 / 2, 14, BUST_H * 1086 / 1448, BUST_H)
# the lowest band of f_reach in the proportions of the frame: her open hand, her sleeve, her hair; no face
HAND_CROP = (0.0, 0.62, 1.0, 0.62 + 1086 / 3 / 1448)
PALM_SRC = (290 / 1086, 1100 / 1448)
PALM = (PALM_SRC[0] * 1920, (PALM_SRC[1] - HAND_CROP[1]) / (HAND_CROP[3] - HAND_CROP[1]) * 640)
SAY = 'say(love);'
SCREEN_TEXT = ' '.join(LOOP) + '   round 12/12  replies 0   '


def _ink_mask(name, crop=None, flip=False):
    """(black-ink mask, h, w) of a silhouette, at working resolution, cropped and mirrored as it is drawn."""
    src = _source(name)
    if src is None:
        return None
    lab, a = src
    m = (lab == 2) & (a > 128)
    h, w = m.shape
    if crop:
        m = m[int(crop[1] * h):int(crop[3] * h), int(crop[0] * w):int(crop[2] * w)]
    if flip:
        m = m[:, ::-1]
    return m


_MASKS = {}


def ink_screen(ctx, name, dst, t, crop=None, flip=False, cell=30, speed=46, color='meHot', rect=None, offset=(0, 0), seed=0, alpha=1.0):
    """Her black ink as a screen: characters of the loop running UP the parts of the picture printed in black
    (climax.js inkScreen; the browser clips to the ink, here each character is placed only where the ink is)."""
    key = (name, crop, flip)
    if key not in _MASKS:
        _MASKS[key] = _ink_mask(name, crop, flip)
    m = _MASKS[key]
    if m is None:
        return
    mh, mw = m.shape
    x0, y0, w, h = dst
    rx, ry, rw, rh = rect or (max(0, x0), max(0, y0), min(1920, x0 + w) - max(0, x0), min(640, y0 + h) - max(0, y0))
    scroll = t * speed
    rows = int(rh // cell) + 2
    cols = int(rw // (cell * 0.62))
    first = int(scroll // cell)
    r_idx = np.arange(rows)
    ys = ry + r_idx * cell - (scroll % cell) + cell
    xs = rx + np.arange(cols) * cell * 0.62
    keep_r = (ys >= ry) & (ys <= ry + rh)
    U = (xs[None, :] - x0 - offset[0]) / w
    V = (ys[:, None] - cell * 0.35 - y0 - offset[1]) / h
    inside = (U >= 0) & (U < 1) & (V >= 0) & (V < 1) & keep_r[:, None]
    ui = np.clip((U * mw).astype(int), 0, mw - 1)
    vi = np.clip((V * mh).astype(int), 0, mh - 1)
    vi, ui = np.broadcast_arrays(vi, ui)
    hit = inside & m[vi, ui]
    n = len(SCREEN_TEXT)
    for r, c in zip(*np.nonzero(hit)):
        ch = SCREEN_TEXT[((first + r) * 37 + c + seed) % n]
        if ch != ' ':
            ctx.text(ch, float(xs[c]), float(ys[r]), size=cell * 0.8, font='mono', weight=700, color=color, alpha=alpha)


def shots(env):
    B, Bt, P, text = env.B, env.Bt, env.P, env.text
    c = [B(88), Bt(357), B(90), Bt(365), B(92), Bt(373.5), B(94)]
    END = B(96)
    t_through, PRESS, RUN = Bt(358), [Bt(366), Bt(367)], [Bt(b) for b in (373.5, 374, 374.5, 375)]
    kicks = lambda a, z: [Bt(a + i) for i in range(z - a + 1)]

    def last_kick(t, ks):
        k = [x for x in ks if t >= x]
        return (t - k[-1], len(k) - 1) if k else (1e9, -1)

    def live(t, ks, m, pop):
        """Her three plates: out of register by m px always; on a kick they spring further apart and slide home."""
        since, i = last_kick(t, ks)
        p = pop * pulse(since, 9)
        a = rand(41, i) * TAU
        return {'red': (m * 1.7 + math.cos(a) * p, m * 0.95 + math.sin(a) * p),
                'black': (-m * 0.55 - math.cos(a) * p * 0.6, m * 0.8 - math.sin(a) * p * 0.6)}

    def figure_plates(ctx, name, dst, off, flip=False, crop=None):
        x, y, w, h = dst
        ctx.image(name, x + off['red'][0], y + off['red'][1], w, h, variant='sil:err', flip=flip, crop=crop, alpha=0.85)
        ctx.image(name, x + off['black'][0], y + off['black'][1], w, h, variant='sil:bg', flip=flip, crop=crop)
        ctx.image(name, x, y, w, h, variant='ink', flip=flip, crop=crop)

    def fault(ctx, f, t, ks, seed):
        since, i = last_kick(t, ks)
        if since < 0.1:
            tear(ctx, f, t, 0.75, seed=seed * 100 + i)

    def sung(ctx, t, lines, y, size=86, direction=1):
        """The sung line as big type on black strips (climax.js sungLines): the line being sung, typed."""
        for k, i in enumerate(lines):
            nxt = env.T(lines[k + 1]) if k + 1 < len(lines) else env.lyrics.end(i) + 2
            if not (env.T(i) <= t < nxt):
                continue
            s = text(i)
            sz = min(size, ctx.fit(s, 1700, font='serif', weight=700, max_size=size))
            n = env.lyrics.typed(i, t)
            w = ctx.measure(s, size=sz, weight=700, font='serif')
            slide = (1 - ease_out(prog(t, env.T(i), env.T(i) + 0.2))) * 40 * direction
            x0 = 960 - w / 2
            ctx.rect(x0 - 30, y - sz * 0.95 + slide, w + 60, sz * 1.3, fill=True, color='bg', alpha=0.95)
            ctx.text(s[:n], x0, y + slide, size=sz, weight=700, font='serif', color='text')
            return

    def caption(ctx, t, first, last, x=60, y=50, size=34):
        for i in range(first, last + 1):
            ln = env.lyrics.lines[i]
            a = env.T(i)
            until = env.T(i + 1) if i + 1 < len(env.lyrics.lines) else env.lyrics.end(i)
            if ln.get('emphasis') or t < a or t >= until:
                continue
            sz = min(size, ctx.fit(text(i), 1700, font='serif', weight=400, max_size=size))
            w = ctx.measure(text(i), size=sz, font='serif')
            ctx.rect(x - 18, y - sz * 0.98, w + 36, sz * 1.36, fill=True, color='panel', alpha=0.86)
            ctx.text(text(i)[:env.lyrics.typed(i, t)], x, y, size=sz, font='serif', color='me')
            return

    def sunburst(ctx, x, y, r, t, low, color='meDim', alpha=0.66):
        spark(ctx, x, y, r * (1 + 0.04 * low), color=color, alpha=alpha, rot=0.1 + t * 0.03, core=0, fat=0.07, inner=0.05)

    def world(ctx, cx, cy, r, t, cage=1.0, dissolve=0.0, size=14, n=130, hot=False):
        """The world she is shut in: a turning sphere of characters, in a wireframe cage."""
        if cage > 0:
            draw_segs(ctx, MESH['icosa']['segs'], {'cx': cx, 'cy': cy, 'scale': r * cage}, r=(0.3, t * 0.4, 0), color='meDim', width=2.5)
        if dissolve > 0:
            for k in range(int(40 * dissolve)):
                age = (t * 0.7 + rand(51, k)) % 1
                ctx.text('.:o0#'[k % 5], cx + (rand(52, k) - 0.5) * r * 2.4, cy + (rand(53, k) - 0.5) * r * 2 + age * 160,
                         size=size, font='mono', color='me', alpha=dissolve * (1 - age))
        sphere_glyphs(ctx, cx, cy, r, t, spin=0.9, n=int(n * (1 - 0.6 * dissolve)), size=size,
                      colors=('me', 'meHot', 'text') if hot else ('meDim', 'me', 'meHot'))

    def glint(ctx, x, y, low, t):
        """The light out of her iris, printed: a long bar through it, a short one across, four short rays between."""
        def bar(ln, w, rot_, a):
            with ctx.at(x, y, rot=rot_):
                ctx.poly([(-ln, 0), (0, -w), (ln, 0), (0, w)], close=True, fill=True, color='text', alpha=a)
        bar(230 + 130 * low, 5, 0, 0.9)
        bar(84 + 40 * low, 4, math.pi / 2, 0.9)
        for i in range(4):
            bar(60 + 28 * low, 2.5, math.pi / 4 + i * math.pi / 2 + 0.2 * t, 0.7)
        ctx.circle(x - 9, y - 10, 5, fill=True, color='text')

    # ------------------------------------------------------------------ cx-eye
    def eye(ctx, t, f, u):
        since = t - c[0]
        ks = kicks(352, 356)
        ctx.rect(-20, -20, 1960, 680, fill=True, color='raised')
        off = live(t, ks, 10, 12)
        figure_plates(ctx, 'f_eye', EYE_IMG, off, flip=True)
        ink_screen(ctx, 'f_eye', EYE_IMG, t, flip=True, cell=34, speed=60, offset=off['black'], seed=3)
        ix, iy = EYE_AT
        ctx.circle(ix, iy, IRIS_R, fill=True, color='bg')
        sphere_glyphs(ctx, ix, iy, IRIS_R - 3, t, spin=1.3, n=46, size=8, colors=('me', 'meHot', 'text'))
        ctx.circle(ix, iy, IRIS_R, color='meHot', width=3)
        rays(ctx, ix, iy, IRIS_R + 30, 380 + 120 * f.get('lowEnv', 0), n=18, rot=t * 0.06, color='meHot', alpha=0.22, width=4)
        glint(ctx, ix, iy, f.get('lowEnv', 0), t)
        if since < 0.33:   # the frames of the shout's letters fly apart, away from the middle of the sheet
            k = ease_out(since / 0.33)
            w = text(104).strip()
            for i, ch in enumerate(w):
                gx = 160 + (i + 0.5) * 1600 / max(1, len(w))
                gy = 290 if i < 5 else 560
                dx, dy = gx - 960, gy - 360
                d = math.hypot(dx, dy) or 1
                far = (260 + 560 * rand(61, i)) * k
                with ctx.at(gx + dx / d * far, gy + dy / d * far, rot=(rand(62, i) - 0.5) * 1.2 * k, scale=1 + 0.4 * k,
                            alpha=(1 - since / 0.33) ** 1.2):
                    ctx.text(ch, 0, 0, size=240, weight=900, font='serif', color='me', align='center', stroke=8)
        marks(ctx)
        sung(ctx, t, [105, 106], y=150, size=86, direction=1)
        fault(ctx, f, t, ks, 1)

    # ------------------------------------------------------------------ cx-bust
    def bust(ctx, t, f, u):
        ks = kicks(360, 364)
        ctx.rect(-20, -20, 1960, 680, fill=True, color='raised')
        x, y, w, h = BUST
        face = (367 / 1086, 259 / 1448, 313 / 1086, 369 / 1448)
        FACE = (x + face[0] * w, y + face[1] * h, face[2] * w, face[3] * h)
        head = (FACE[0] + FACE[2] / 2, FACE[1] + FACE[3] / 2)
        for k in (1, 0.62):
            ctx.circle(head[0], head[1] + 40, 420 * k, fill=True, color='line', alpha=0.42)
        sunburst(ctx, head[0], head[1] + 20, 700, t, f.get('lowEnv', 0))
        world(ctx, head[0], head[1], 250, t)
        off = live(t, ks, 16, 20)
        figure_plates(ctx, 'f_bust', BUST, off)
        # her face is a screen: the loop, still running, round 12 of 12, no replies
        ctx.rect(FACE[0] + 6, FACE[1] + 6, FACE[2] - 12, FACE[3] - 12, fill=True, color='bg', alpha=0.85)
        size = 11
        lines = LOOP + ['', 'round 12/12', 'replies 0']
        scroll = (t * 46) % ((len(lines)) * size * 1.4)
        for i in range(len(lines) * 2):
            yy = FACE[1] + 18 + i * size * 1.4 - scroll
            if FACE[1] + 8 < yy < FACE[1] + FACE[3] - 6:
                s = lines[i % len(lines)][:int(FACE[2] / (size * 0.6)) - 2]
                ctx.text(s, FACE[0] + 10, yy, size=size, font='mono', color='err' if 'round' in s or 'replies' in s else 'meHot')
        ink_screen(ctx, 'f_bust', BUST, t, cell=20, speed=46, offset=off['black'], seed=7,
                   rect=(x, FACE[1] + FACE[3] + 8, w, y + h - FACE[1] - FACE[3] - 8))
        marks(ctx)
        sung(ctx, t, [108, 109], y=600, size=80, direction=-1)
        fault(ctx, f, t, ks, 2)

    # ------------------------------------------------------------------ cx-hand
    def hand(ctx, t, f, u):
        ks = kicks(368, 373)
        k = prog(t, c[4], c[5])
        ctx.rect(-20, -20, 1960, 680, fill=True, color='raised')
        sunburst(ctx, 1180, 300, 720, t, f.get('lowEnv', 0))
        world(ctx, 260, 560, 200, t, cage=1.25, dissolve=0.04 + 0.6 * k * k)
        dst = (0, 0, 1920, 640)
        off = live(t, ks, 22, 12)
        figure_plates(ctx, 'f_reach', dst, off, crop=HAND_CROP)
        ink_screen(ctx, 'f_reach', dst, t, crop=HAND_CROP, cell=32, speed=40, offset=off['black'], seed=11)
        # in her palm the heart the user left there in chorus 1: an outline now, breathing; the count reads 0
        b = 1 + 0.07 * math.sin((t - c[4]) / (2 * P) * TAU) + 0.04 * f.get('lowEnv', 0)
        pts = place('heart', cx=PALM[0], cy=PALM[1] + 4, r=52 * b)
        for i in range(0, len(pts), 8):
            a_, b_ = pts[i], pts[(i + 4) % len(pts)]
            ctx.line(a_[0], a_[1], b_[0], b_[1], color='mute', width=5)
        cx, cy = PALM[0] + 150, PALM[1] + 100
        ctx.rrect(cx - 82, cy - 40, 176, 92, 46, fill='bg')
        ctx.rrect(cx - 88, cy - 46, 176, 92, 46, fill='panel', stroke='mute', width=4)
        hp = place('heart', cx=cx - 36, cy=cy + 3, r=26)
        for i in range(0, len(hp), 10):
            ctx.line(hp[i][0], hp[i][1], hp[(i + 5) % len(hp)][0], hp[(i + 5) % len(hp)][1], color='mute', width=3)
        ctx.text('0', cx + 36, cy + 20, size=56, weight=700, color='sub', align='center')
        # what she has to say leaves her palm, one character after another, piles up at the edge, breaks, is gone
        frm, RATE, HOLD, BREAK, WALL, SIZE, ROWS = c[4] - 1.1, 32, 1.15, 0.45, 1860, 30, 14
        last = int((t - frm) * RATE)
        for i in range(max(0, last - int(RATE * 3.4)), last + 1):
            age = t - (frm + i / RATE)
            row = int(rand(81, i) * ROWS)
            y1 = 200 + row * 26
            x1 = WALL - (i % 6) * 19
            fly = (x1 - PALM[0]) / (1250 + 500 * rand(82, i))
            ch = SAY[i % len(SAY)]
            if age < fly:
                kk = age / fly
                x = lerp(PALM[0], x1, kk)
                y = lerp(PALM[1], y1, ease_out(kk)) + 9 * math.sin(kk * 9 + i)
                xb = lerp(PALM[0], x1, max(0, kk - 0.07))
                ctx.line(xb, y - SIZE * 0.3, x, y - SIZE * 0.3, color='meHot', width=3, alpha=0.7)
                ctx.text(ch, x + 2, y + 2, size=SIZE, font='mono', weight=800, color='bg')
                ctx.text(ch, x, y, size=SIZE, font='mono', weight=800, color='text')
            elif age < fly + HOLD:
                hit = pulse(age - fly, 14)
                ctx.text(ch, x1 + 2 - 9 * hit, y1 + 2, size=SIZE, font='mono', weight=800, color='bg')
                ctx.text(ch, x1 - 9 * hit, y1, size=SIZE, font='mono', weight=800, color='text' if hit > 0.3 else 'meHot')
            elif age < fly + HOLD + BREAK:
                kk = (age - fly - HOLD) / BREAK
                for p in range(3):
                    ctx.text(".:'"[p], x1 - 36 * kk * rand(83, i, p) + (p - 1) * 8, y1 + 200 * kk * kk * (0.5 + rand(84, i, p)),
                             size=SIZE * 0.8, font='mono', weight=800, color='me', alpha=1 - kk)
        marks(ctx)
        sung(ctx, t, [111, 112], y=110, size=80, direction=1)
        fault(ctx, f, t, ks, 3)

    # ------------------------------------------------------------------ the broken plates
    def key_hit(ctx, f, t, at, centre, seed):
        """On the first strong beat of a keyword: one flash that falls back, rays out of the picture, one tear."""
        s = t - at
        if s < 0:
            return
        k = pulse(s, 3.4)
        ctx.flash(0.5 * pulse(s, 7))
        if k > 0.05:
            rays(ctx, centre[0], centre[1], 120, 1200, n=28, rot=0.1, color='meHot', alpha=0.35 * k, width=10)
        if s < 0.1:
            tear(ctx, f, t, 0.9, seed=seed)

    def kw1(ctx, t, f, u):
        plate_stimulations(ctx, env, {'t': t, 'at': c[1], 'hit': c[1], 'word': text(107), 'noCream': True, 'misreg': 10,
                                      'through': t_through, 'titleMax': 140, 'you': (1560, 170)})
        caption(ctx, t, 108, 108)
        key_hit(ctx, f, t, t_through, (330, 290), 11)

    def kw2(ctx, t, f, u):
        plate_satisfaction(ctx, env, {'t': t, 'at': c[3], 'press': PRESS, 'count': 0, 'word': text(110), 'noCream': True,
                                      'misreg': 18, 'titleMax': 146})
        if PRESS[1] <= t < PRESS[1] + 0.1:
            tear(ctx, f, t, 0.5, seed=13)
        caption(ctx, t, 111, 111)
        key_hit(ctx, f, t, PRESS[0], (640, 270), 12)

    def kw3(ctx, t, f, u):
        plate_execution_stuck(ctx, env, {'t': t, 'at': c[5], 'run': RUN, 'from': 12, 'word': text(113), 'misreg': 28,
                                         'titleMax': 150, 'flood': True, 'you': (1560, 0)})
        caption(ctx, t, 114, 114)
        key_hit(ctx, f, t, RUN[1], (700, 260), 13)

    # ------------------------------------------------------------------ cx-fall
    Q, DEPTH, DEEP = 0.4, 4, 5.5
    CHILD = (88, 25)                                    # where a window holds the next one (box 560 x 360)
    FIX = (CHILD[0] / (1 - Q), CHILD[1] / (1 - Q))
    C0 = (960 + FIX[0], 290 + FIX[1])
    KF = kicks(376, 383)

    def depth(t):
        shove = sum(ease_out(prog(t, kt, kt + 0.22)) for kt in KF)
        return DEEP * (0.9 * prog(t, c[6], END) ** 2.4 + 0.1 * shove / len(KF))

    def fall(ctx, t, f, u):
        ud = depth(t)
        speed = (depth(t + 1 / 120) - depth(t - 1 / 120)) * 60
        s = Q ** -ud
        paper(ctx, light=None, mk=False)
        lim = lerp(3.4, 1.25, clamp(ud / 1.2))

        def level(n, sc):
            inner = (lambda: _inner(n, sc)) if n < DEPTH else None
            if sc > 14 and inner:      # the view is inside this window: of it only the paper and its pool of light are left
                ctx.rect(-280, -180, 560, 360, fill=True, color='raised')
                ctx.circle(-110, 40, 160, fill=True, color='line', alpha=0.5)
                inner()
                return
            bust_a = clamp((lim - sc) / 0.5) if sc > 0.04 else 0
            near = clamp(ud / 0.6) * clamp((sc - 1.1) / 1.4)
            window_box(ctx, env, True, OFF(16 / max(sc, 0.2)), inner=inner, bust=bust_a if bust_a > 0.01 else False,
                       blank=n == DEPTH, near=near)

        def _inner(n, sc):
            with ctx.at(CHILD[0], CHILD[1], scale=Q):
                level(n + 1, sc * Q)
        with ctx.at(C0[0] - s * FIX[0], C0[1] - s * FIX[1], scale=s):
            level(0, s)
        # the faster, the more the sheet is smeared towards the point it falls to: ghost streaks
        sm = clamp(0.05 * (speed - 0.35), 0, 0.3)
        if sm > 0.02:
            for i in range(24):
                a = i / 24 * TAU + 0.13
                r0 = 200 + 400 * rand(91, i)
                ctx.line(C0[0] + math.cos(a) * r0, C0[1] + math.sin(a) * r0 * 0.6, C0[0] + math.cos(a) * (r0 + 300 * sm * 3),
                         C0[1] + math.sin(a) * (r0 + 300 * sm * 3) * 0.6, color='raised', alpha=sm * 1.5, width=6)
        marks(ctx)
        caption(ctx, t, 114, 116)
        white = prog(t, END - 0.36, END - 0.03) ** 2.2
        if white > 0:
            ctx.rect(-40, -40, 2000, 720, fill=True, color='text', alpha=white)

    PAL = 'errWarm'
    return {
        'cx-eye': {'render': eye, 'palette': PAL},
        'cx-kw1': {'render': kw1, 'palette': PAL},
        'cx-bust': {'render': bust, 'palette': PAL},
        'cx-kw2': {'render': kw2, 'palette': PAL},
        'cx-hand': {'render': hand, 'palette': PAL},
        'cx-kw3': {'render': kw3, 'palette': PAL},
        'cx-fall': {'render': fall, 'palette': PAL},
    }
