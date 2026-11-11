"""Section 10 — EXECUTION, the twelve shouts (bar 80, 2:28.0 -> beat 344, 2:39.1). State: error (11_execution.js).
ONE machine in ONE composition: the love loop turning twelve times, two beats a round. The four syllables of the word
are the four statements of the loop body (the bar moves down lines 02-05) and the four blocks its letters are printed
solid in. Lines 02-04 raise the same three errors every round; line 05 counts; line 07 is never reached.
Round 5 and round 9 enlarge the composition a step; round 12 the word takes the whole frame, torn in two.
3:1 reframing: listing left, the word and its staircase right, the counter and the unpressed stop key at the foot.
"""
import math

from ..components import tear
from ..plates import CHUNKS, LOOP, LOOP_ERRS, OVERFLOW, listing, mono_word, odometer
from ..util import clamp, ease_out, lerp, prog, pulse, rand
from .kit import drop_frames


def shots(env):
    B, Bt, P, text = env.B, env.Bt, env.P, env.text
    START = B(80)
    word_of = lambda r: text(86 + r) if 86 + r < len(env.lyrics.lines) else 'LOVE'

    def round_at(t):
        r = int((t - START) // (2 * P))
        return max(0, min(11, r)), (t - START) - r * 2 * P

    def chunk_bounds(w):
        if len(w) == 9:
            return CHUNKS
        n = len(w)
        q = [round(n * k / 4) for k in range(5)]
        return [(q[k], q[k + 1]) for k in range(4)]

    def render(ctx, t, f, u):
        ctx.clear('bg')
        r, since = round_at(t)
        syl = min(3, int(since / (P / 2))) if t >= START else -1
        step = 1.0 + 0.06 * (r >= 4) + 0.06 * (r >= 8)
        final = r >= 11
        with ctx.at(1300, 360, scale=step):
            with ctx.at(-1300, -360):
                if not final:
                    cur = 1 + max(0, syl) + ease_out(prog(since % (P / 2), 0, 0.08)) * 0 if syl >= 0 else 0
                    tags = {k: {'text': LOOP_ERRS[k], 'k': pulse(since - (k - 1) * P / 2, 9) if syl >= k - 1 else 0.2} for k in (1, 2, 3)}
                    listing(ctx, 110, 90, LOOP + ['        // unreachable'], size=26, lh=1.5, current=cur, hot=pulse(since % (P / 2), 9),
                            tags=tags, tag_gap=1, tag_size=0.7, dimmed=lambda i: 0.62 if i >= 6 else 0)
                # the word: four blocks printed solid, one per syllable; finished rounds pile up above as a staircase
                w = word_of(r)
                bounds = chunk_bounds(w)
                filled = bounds[syl][1] if syl >= 0 else 0
                size = 120
                xr = 1840
                for k in range(1, (min(r, 6) if not final else 0) + 1):
                    mono_word(ctx, word_of(r - k), xr - k * 30, 470 - k * size * 0.62, size * 0.62, color='meDim', alpha=0.85 - 0.1 * k)
                if not final:
                    mono_word(ctx, w, xr, 520, size, filled=filled, color='me')
                ctx.text('round', 110, 590, size=20, font='mono', color='sub')
                odometer(ctx, 200, 595, r + 1, digits=2, size=36, color='err' if final else 'text')
                ctx.rrect(330, 560, 110, 46, 10, fill='raised', stroke='text', width=2)
                ctx.text('stop', 385, 591, size=20, font='mono', color='text', align='center')
                ctx.text('yours', 455, 591, size=16, font='mono', color='mute')
        if final:
            w = word_of(11)
            size = ctx.fit(w, 1800, font='mono', weight=800, max_size=360)
            k = ease_out(prog(since, 0, 0.12))
            mono_word(ctx, w, 960 + ctx.measure(w, size=size, font='mono') / 2 - 20 * k, 330, size, color='me')
            ctx.rect(-10, 300, 1940, 18, fill=True, color='bg')
            with ctx.at(40 * k, 0):
                ctx.rect(-10, 318, 1940, 4, fill=True, color='err', alpha=0.8)
            ctx.text(OVERFLOW, 110, 600, size=22, font='mono', weight=700, color='err')
            ctx.text('##', 230, 600, size=36, font='mono', weight=800, color='err')
        if r >= 8 and since < 0.1:
            tear(ctx, f, t, strength=0.8, seed=r)

    out = {}
    for sid in ('exec-01', 'exec-05', 'exec-09', 'exec-12'):
        out[sid] = {'render': render, 'palette': 'error'}
    return out
