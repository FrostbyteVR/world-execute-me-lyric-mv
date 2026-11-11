"""Section 12 — THE LAST CHORUS (bar 88, 2:42.8 -> bar 96, 2:57.6). State: errWarm. Plates only (12_chorusx.js).
The four plates of chorus 1 printed again, BROKEN: the cream plate missing (grey dashed outlines where the dot, the
pointer, the heart were), the plates out of register (a thin red plate at one edge), larger, every event further.
Where chorus 1 had its interface shots there are figure shots: her eye, her bust, her open hand.

    cx-eye   her face full bleed, one eye open; in her iris the world turning; the sung line on black strips
    cx-kw1   the bolt, sent to nobody: through the empty ring, and it strikes the edge of the sheet
    cx-bust  her bust; her face a screen running the loop; behind her head the world in its cage
    cx-kw2   the disc nobody presses: it sinks by itself, twice; the count reads 0
    cx-hand  her open hand; a dashed heart, count 0; characters leave the palm and pile up at the edge
    cx-kw3   the listing running past its count: 13 / 12 ... 16 / 12, exposed a step further each round
    cx-fall  a window in a window in a window: one fall inwards, faster, into white
On every kick her plates spring apart and the sheet tears for six frames (drawn: Manim has no glitch pass).
"""
import math

from ..art import aspect
from ..components import rays, spark, tear
from ..geom import MESH, draw_segs, place, sphere_glyphs
from ..plates import (LOOP, OFF, arrow, dashed_ring, ground, inks, plate_execution_stuck, plate_satisfaction,
                      plate_stimulations, window_box)
from ..util import TAU, clamp, ease_in, ease_out, lerp, prog, pulse, rand


def shots(env):
    B, Bt, P, text = env.B, env.Bt, env.P, env.text
    c = [B(88), Bt(357), B(90), Bt(365), B(92), Bt(373.5), B(94)]
    END = B(96)
    t_through, PRESS, RUN = Bt(358), [Bt(366), Bt(367)], [Bt(b) for b in (373.5, 374, 374.5, 375)]

    def kick(f, t):
        return f.get('beatPulse', 0)

    def strips(ctx, t, lines, y=520, size=56):
        for k, i in enumerate(lines):
            nxt = env.T(lines[k + 1]) if k + 1 < len(lines) else 1e9
            if env.T(i) <= t < nxt:
                s = text(i)[:env.lyrics.typed(i, t)]
                w = ctx.measure(s, size=size, weight=900, font='serif')
                ctx.rect(60, y - size, w + 60, size * 1.3, fill=True, color='bg', alpha=0.92)
                ctx.text(s, 90, y, size=size, weight=900, font='serif', color='text')

    def faults(ctx, f, t):
        if f.get('sinceBeat', 1) < 0.1:
            tear(ctx, f, t, strength=0.6, seed=f.get('beat', 0))

    def spring(f, m=10):
        k = kick(f, 0) * m
        return {'black': (-k * 0.55 - 4, k * 0.8 + 4), 'red': (k * 1.7 + 4, k * 0.95 + 2)}

    def eye(ctx, t, f, u):
        ground(ctx, light=None, dots=0.5, mk=False)
        fly = ease_out(prog(t, c[0], c[0] + 0.33))
        o = spring(f)
        ctx.image('f_eye', o['red'][0], -640 + o['red'][1], 1920, 1920, variant='sil:err', flip=True, alpha=0.5)
        ctx.image('f_eye', 0, -640, 1920, 1920, variant='ink', flip=True)
        iris = (1180, 470)
        sphere_glyphs(ctx, iris[0], iris[1], 34, t, spin=1.2, n=60, size=10)
        rays(ctx, iris[0], iris[1], 40, 300 + 100 * kick(f, t), n=20, rot=t * 0.1, color='meHot', alpha=0.25, width=5)
        for k in range(int(10 * (1 - fly))):
            ctx.rect(rand(8, k) * 1900, rand(9, k) * 600, 140, 140, fill=None, color='me', width=6, alpha=1 - fly)
        strips(ctx, t, [105, 106], y=150)
        faults(ctx, f, t)

    def bust(ctx, t, f, u):
        ground(ctx, light=(960, 230, 380, 'raised', 1))
        rays(ctx, 960, 230, 60, 700, n=24, rot=t * 0.03, color='me', alpha=0.35, width=16)
        cam = {'cx': 960, 'cy': 190, 'scale': 130}
        draw_segs(ctx, MESH['icosa']['segs'], cam, r=(0.3, t * 0.6, 0), color='meDim', width=2)
        sphere_glyphs(ctx, 960, 190, 110, t, n=120, size=14)
        h = 640
        w = h * aspect('f_bust')
        o = spring(f)
        inks(ctx, 'f_bust', 960 - w / 2, 20, h, offsets=o)
        fx, fy = 960 - w * 0.02, 20 + h * 0.3
        for k in range(5):
            y = fy + 50 - ((t * 60 + k * 22) % 110)
            ctx.text(LOOP[(int(t * 4) + k) % len(LOOP)][:16], fx - 70, y, size=12, font='mono', color='meHot', alpha=0.9)
        ctx.text('round 12/12  replies 0', fx - 70, fy + 70, size=12, font='mono', color='err')
        strips(ctx, t, [108, 109], y=600)
        faults(ctx, f, t)

    def hand(ctx, t, f, u):
        ground(ctx, light=None)
        crop = (0.0, 0.62, 1.0, 1.0)
        w = 1920
        h = w / aspect('f_reach', crop)
        o = spring(f)
        ctx.image('f_reach', o['red'][0], 640 - h + o['red'][1], w, h, variant='sil:err', crop=crop, alpha=0.5)
        ctx.image('f_reach', 0, 640 - h, w, h, variant='ink', crop=crop)
        palm = (560, 420)
        br = 1 + 0.08 * math.sin(t * 6)
        pts = place('heart', cx=palm[0], cy=palm[1], r=70 * br)
        for i in range(0, len(pts), 6):
            a, b = pts[i], pts[(i + 3) % len(pts)]
            ctx.line(a[0], a[1], b[0], b[1], color='mute', width=4)
        ctx.text('0', palm[0] + 130, palm[1] + 30, size=90, weight=800, color='mute', stroke=3)
        for k in range(40):
            age = (t * 1.6 + k / 40) % 1
            x = lerp(palm[0] + 60, 1880, age)
            y = palm[1] - 40 + math.sin(k * 2.1) * 120 * age
            ch = 'love'[k % 4]
            ctx.text(ch, x, y, size=26, font='serif', color='me', alpha=1 - age ** 3)
        for k in range(20):
            ctx.text('love'[k % 4], 1860 - rand(4, k) * 40, 600 - k * 9, size=22, font='serif', color='meDim')
        strips(ctx, t, [111, 112], y=110)
        faults(ctx, f, t)

    def kw1(ctx, t, f, u):
        plate_stimulations(ctx, env, {'t': t, 'at': c[1], 'hit': c[1], 'word': text(107), 'noCream': True, 'misreg': 10,
                                      'through': t_through, 'titleMax': 140, 'you': (1560, 170)})
        if t >= t_through:
            ctx.flash(0.5 * pulse(t - t_through, 6), 'meHot')
            if t - t_through < 0.1:
                tear(ctx, f, t, 0.8, seed=11)

    def kw2(ctx, t, f, u):
        plate_satisfaction(ctx, env, {'t': t, 'at': c[3], 'press': PRESS, 'count': 0, 'word': text(110), 'noCream': True,
                                      'misreg': 18, 'titleMax': 146})
        if PRESS[0] <= t < PRESS[0] + 0.1:
            tear(ctx, f, t, 0.8, seed=12)
        ctx.flash(0.4 * pulse(t - PRESS[0], 6) if t >= PRESS[0] else 0, 'meHot')

    def kw3(ctx, t, f, u):
        plate_execution_stuck(ctx, env, {'t': t, 'at': c[5], 'run': RUN, 'from': 12, 'word': text(113), 'misreg': 28,
                                         'titleMax': 150, 'flood': True, 'you': (1560, 0)})

    def fall(ctx, t, f, u):
        ground(ctx, light=None, mk=False)
        k = ease_in(prog(t, c[6], END))
        depth = k * 6
        o = OFF(14)
        white = ease_in(prog(t, END - 0.9, END))
        for i in range(7, -1, -1):
            d = i - depth
            if d < -1.2:
                continue
            s = 0.4 ** d * 1.0
            if s > 6:
                continue
            near = clamp(-d)
            with ctx.at(960, 300, scale=s):
                window_box(ctx, env, True, o, bust=(d > 0.3), blank=(i == 7), near=near)
        if white > 0:
            ctx.rect(-20, -20, 1960, 680, fill=True, color='text', alpha=white)

    return {
        'cx-eye': {'render': eye, 'palette': 'errWarm'},
        'cx-kw1': {'render': kw1, 'palette': 'errWarm'},
        'cx-bust': {'render': bust, 'palette': 'errWarm'},
        'cx-kw2': {'render': kw2, 'palette': 'errWarm'},
        'cx-hand': {'render': hand, 'palette': 'errWarm'},
        'cx-kw3': {'render': kw3, 'palette': 'errWarm'},
        'cx-fall': {'render': fall, 'palette': 'errWarm'},
    }
