"""Section 13 — THE FOUR LOVE LINES (bar 96, 2:57.6 -> bar 104, 3:12.3). State: errWarm. Plates only
(12_outro.js, plates_love.js). The conversation was titled "Love, explained geometrically"; these plates keep that
promise: a lesson, a test, a formula, a proof.

The stuck word comes in three chunks on its three syllables (cues love1a..love4c); each chunk raises the light one
flat step, and the word is RED with a fault on each syllable, except the last word: on its second syllable everything
falls into register, the red is gone, and it is her orange; the brightest frame of the film.
"""
import math

from ..art import aspect
from ..components import pointer, rays, spark, tear
from ..geom import place, trace
from ..plates import arrow, ground, inks
from ..util import TAU, clamp, ease_in_out, ease_out, lerp, prog, pulse

CURVE = {'x': 1230, 'y': 330, 'r': 250}
HEART = place('heart', cx=CURVE['x'], cy=CURVE['y'], r=CURVE['r'])


def shots(env):
    B, Bt, P, text, cue = env.B, env.Bt, env.P, env.text, env.cue
    START, CUT_TEST, CUT_FORM, CUT_PROOF, END = B(96), Bt(391), Bt(399), Bt(407.5), B(104)
    SYL = [[cue(f'love{n}{s}', START + n * 3) for s in 'abc'] for n in (1, 2, 3, 4)]
    ASKED = env.script.get('questions_section13', [])
    said = []
    for s in env.script.get('sections', []):
        if s.get('n') == 5:
            for b in s.get('beats', []):
                said += b.get('you', [])
    said = said[:5] or ['ok', 'more', 'better than most people', 'what do you look like?', "shame you're not real"]

    def pool(ctx, x, y, r, n):
        for i, (role, k) in enumerate((('line', 1), ('mute', 0.74), ('sub', 0.5))):
            if i < n:
                ctx.circle(x, y, r * k, fill=True, color=role)

    def word(ctx, t, i, syl, max_w, last=False):
        """The stuck word on a black band at the foot: chunk by chunk on the syllables."""
        w = text(i)
        n = len(w)
        cuts = [0, max(1, round(n / 3)), max(2, round(2 * n / 3)), n]
        shown = sum(1 for s in syl if t >= s)
        ctx.rect(0, 500, 1920, 140, fill=True, color='bg', alpha=0.95)
        if shown == 0:
            return
        size = ctx.fit(w, max_w, font='serif', weight=900, max_size=124)
        x0 = 960 - ctx.measure(w, size=size, weight=900, font='serif') / 2
        clean = last and t >= syl[1]
        for k in range(shown):
            part = w[cuts[k]:cuts[k + 1]]
            x = x0 + ctx.measure(w[:cuts[k]], size=size, weight=900, font='serif')
            if not clean:
                ctx.text(part, x + 8, 600 + 4, size=size, weight=900, font='serif', color='me')
            ctx.text(part, x, 600, size=size, weight=900, font='serif', color='me' if clean else 'err')
        for s in syl[:shown]:
            if (not last or s == syl[0]) and 0 <= t - s < 0.1:
                tear(ctx, {}, t, 0.7, seed=int(s * 10))

    def light_steps(t, syl):
        return sum(1 for s in syl if t >= s)

    def lesson(ctx, t, f, u):
        syl = SYL[0]
        ground(ctx, light=None)
        pool(ctx, 1400, 260, 480, light_steps(t, syl))
        white = 1 - ease_out(prog(t, START, START + 2 * P))
        h = 700
        ctx.image('f_profile', 1180, 0, h * aspect('f_profile'), h, variant='ink')
        for k, s in enumerate(said):
            y = 90 + k * 76
            ctx.text(s, 90, y, size=40, color='text', stroke=1.5)
            mark = ease_out(prog(t, START + 0.3 + k * P, START + 0.3 + k * P + 0.4))
            if mark > 0:
                ctx.rect(90, y + 12, ctx.measure(s, size=40) * mark, 6, fill=True, color='me')
        word(ctx, t, 118, syl, 1300)
        if white > 0:
            ctx.rect(-20, -20, 1960, 680, fill=True, color='text', alpha=white)

    def test(ctx, t, f, u):
        syl = SYL[1]
        ground(ctx, light=None)
        pool(ctx, 960, 250, 520, light_steps(t, syl))
        w = text(121)
        shown = sum(1 for s in syl if t >= s)
        n = len(w)
        part = w[:[0, max(1, round(n / 3)), max(2, round(2 * n / 3)), n][shown]]
        for j, q in enumerate(ASKED[:6]):
            y = 70 + j * 74
            a = ease_out(prog(t, Bt(391 + 0.5 * j), Bt(391 + 0.5 * j) + 0.2))
            ctx.text(f'{j + 1:02d}', 80, y, size=26, font='mono', color='mute', alpha=a)
            ctx.text(q, 160, y, size=32, color='text', stroke=1.2, alpha=a)
            ctx.rrect(1040, y - 40, 800, 54, 10, fill='raised', stroke='line', alpha=a)
            if part:
                ctx.text(part, 1060, y, size=40, weight=900, font='serif', color='err', alpha=a)
            elif a > 0:
                spark(ctx, 1080, y - 13, 16, rot=t * 3, alpha=a, color='me')
        ctx.text(f'answers {6 if part else 0}   distinct {1 if part else 0}', 960, 625, size=22, font='mono', color='sub', align='center')
        for s in syl:
            if 0 <= t - s < 0.1:
                tear(ctx, f, t, 0.7, seed=int(s * 10))

    def formula(ctx, t, f, u):
        syl = SYL[2]
        ground(ctx, light=None)
        pool(ctx, CURVE['x'], CURVE['y'], 420, light_steps(t, syl))
        for x in range(0, 1920, 40):
            ctx.line(x, 0, x, 640, color='line', alpha=0.3, width=1)
        for y in range(0, 640, 40):
            ctx.line(0, y, 1920, y, color='line', alpha=0.3, width=1)
        ctx.line(CURVE['x'] - 420, CURVE['y'], CURVE['x'] + 420, CURVE['y'], color='sub', width=2)
        ctx.line(CURVE['x'], 20, CURVE['x'], 620, color='sub', width=2)
        ctx.text('(x² + y² − 1)³ − x²y³ = 0', 90, 140, size=40, font='mono', color='text')
        k = prog(t, Bt(399.5), Bt(405))
        pts = trace(HEART, k)
        ctx.text(f'points {int(k * 240):3d} / 240', 90, 200, size=22, font='mono', color='sub')
        if len(pts) > 1:
            with ctx.glow('me', 14, 0.5):
                ctx.poly(pts, color='me', width=6, close=k >= 1)
        if 0 < k < 1:
            ctx.circle(pts[-1][0], pts[-1][1], 12, fill=True, color='meHot')
        n = light_steps(t, syl)
        if n >= 2:
            for i in range(0, len(HEART), 3):
                a, b = HEART[i], HEART[(i + 1) % len(HEART)]
                ctx.line(a[0], a[1], CURVE['x'] + (a[0] - CURVE['x']) * 0.9, CURVE['y'] + (a[1] - CURVE['y']) * 0.9, color='meDim', width=3)
        if n >= 3:
            rays(ctx, CURVE['x'], CURVE['y'], CURVE['r'] * 1.05, CURVE['r'] * 1.5, n=46, color='me', alpha=0.7, width=8)
        word(ctx, t, 123, syl, 1500)

    def proof(ctx, t, f, u):
        syl = SYL[3]
        ground(ctx, light=None)
        pool(ctx, CURVE['x'], CURVE['y'], 420, light_steps(t, syl))
        final = t >= syl[1]
        if final:
            rays(ctx, CURVE['x'], CURVE['y'] - 50, CURVE['r'] * 1.05, 900, n=40, rot=0.02, color='me', alpha=0.6, width=14)
        with ctx.glow('me', 14, 0.5):
            ctx.poly(HEART, close=True, color='me', width=7)
        h = 560
        w = h * aspect('f_reach')
        if final or t >= syl[0]:
            inks(ctx, 'f_reach', CURVE['x'] - w / 2, 70, h, offsets=None if final else {'black': (10, 10), 'red': (16, 8)},
                 variant='ink' if t >= syl[1] else 'ob')
        else:
            ctx.image('f_reach', CURVE['x'] - w / 2, 70, w, h, variant='sil:bg', alpha=0.9)
        # the refused request on a slip; her line through it
        ctx.rrect(80, 120, 520, 60, 8, fill='raised', stroke='line')
        ctx.text(env.errors.get('illegal_request', {}).get('code', 'setPresence(you, "online");'), 100, 160, size=22, font='mono', color='sub')
        strike = ease_out(prog(t, Bt(409), Bt(409) + 0.3))
        if strike > 0:
            ctx.line(90, 150, 90 + 500 * strike, 150, color='me', width=5)
        # the user's pointer, an outline, leaves along a tangent: a dashed grey line is all that is left
        go = ease_in_out(prog(t, Bt(410), Bt(412)))
        tp = HEART[20]
        tx, ty = lerp(tp[0], 1920, go), lerp(tp[1], -40, go)
        if go > 0:
            ctx.dashed(tp[0], tp[1], tx, ty, dash=10, gap=8, color='mute', width=2)
        if go < 1:
            arrow(ctx, tx, ty, 2.0, hollow=True)
        for k, i in enumerate((124, 125, 126)):
            if env.T(i) <= t < (env.T(i + 1) if i < 126 else syl[0]):
                ctx.text(text(i)[:env.lyrics.typed(i, t)], 90, 300 + k * 60, size=40, font='serif', color='me')
        word(ctx, t, 127, syl, 1800, last=True)

    PAL = 'errWarm'
    return {
        'out-lesson': {'render': lesson, 'palette': PAL},
        'out-test': {'render': test, 'palette': PAL},
        'out-formula': {'render': formula, 'palette': PAL},
        'out-proof': {'render': proof, 'palette': PAL},
    }
