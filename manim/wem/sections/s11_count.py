"""Section 11 — COUNT and THE LAST SHOUT (beat 344, 2:39.1 -> bar 88, 2:42.8). State: error (11_count.js).

COUNT: the loop is interrupted (^C) and the same call is tried in six languages, one card per number ON the beat it is
sung on. Every frame is dark. A huge numeral in her serif; the number word in its own script; the call; replies 0 / n.
Each card arrives by one terminal move within 0.12 s: cursor drop, newline push, carriage return, column print,
punch-in, row interleave.
THE LAST SHOUT: the word in her serif, two rows that fill the frame; behind its letters her face, her open eye.
(The browser film makes every letter a window onto f_eye; Manim has no masks, so the face shows dimly through a
dark field and the letters carry her colour.)
"""
import math

from ..art import aspect
from ..components import R
from ..util import clamp, ease_out, lerp, prog, pulse

LANGS = [('de', 'Deutsch', 'eins'), ('es', 'español', 'dos'), ('fr', 'français', 'trois'), ('ko', '한국어', '넷'),
         ('sv', 'svenska', 'fem'), ('zh', '中文', '六')]


def shots(env):
    Bt, P, text = env.Bt, env.P, env.text
    t_shout = env.shot('last-shout')['at'] if env.shot('last-shout') else Bt(350)

    def card(n):
        def render(ctx, t, f, u):
            ctx.clear('bg')
            at = Bt(344 + n)
            age = t - at
            k = ease_out(clamp(age / 0.12))
            # the move that brings the card in, as an offset of the whole card
            dx, dy, alpha = 0, 0, 1
            if n == 0:
                bar = lerp(0, 640, k)
                if k < 1:
                    ctx.rect(0, bar - 6, 1920, 12, fill=True, color='text', alpha=0.8)
            elif n == 1:
                dy = (1 - k) * 640
            elif n == 2:
                dx = (1 - k) * 1920
            elif n == 3:
                alpha = k
            code, name, word = LANGS[n]
            left = n % 2 == 0
            with ctx.at(dx, dy, alpha=alpha):
                cs = 22
                ctx.text('^C', 60, 50, size=cs, font='mono', color='err', weight=700)
                prefix = '> for (lang of ['
                x = 60 + ctx.cw(cs) * 3
                ctx.text(prefix, x, 50, size=cs, font='mono', color='sub')
                x += ctx.cw(cs) * len(prefix)
                for i, (c, _, _) in enumerate(LANGS):
                    col = 'text' if i == n else 'mute'
                    ctx.text(c, x, 50, size=cs, font='mono', color=col, weight=700 if i == n else 400)
                    if i < n:
                        ctx.line(x - 2, 42, x + ctx.cw(cs) * 2 + 2, 42, color='mute', width=2)
                    x += ctx.cw(cs) * (4 if i < 5 else 2)
                ctx.text(']) say(love, lang);', x, 50, size=cs, font='mono', color='sub')
                sc = 1.6 - 0.6 * ease_out(clamp(age / 0.1)) if n == 4 else 1.0
                with ctx.at(960, 470, scale=sc):
                    ctx.text(str(n + 1), 0, 0, size=460, weight=900, font='serif', color='me', align='center')
                wx = 420 if left else 1500
                fam = 'tcSans' if code in ('ko', 'zh') else 'serif'
                ctx.text(word, wx, 380, size=110, weight=700, font=fam, color='text', align='center')
                ctx.text(f'say(love, "{name}")', 1500 if left else 420, 380, size=28, font='mono' if code not in ('ko', 'zh') else 'tcSans',
                         color='sub', align='center')
                ctx.text('replies ', 860, 600, size=26, font='mono', color='sub')
                ctx.text('0', 860 + ctx.cw(26) * 8, 600, size=26, font='mono', color='err', weight=700)
                ctx.text(f' / {n + 1}', 860 + ctx.cw(26) * 9, 600, size=26, font='mono', color='sub')
            if n == 5 and age < 0.12:
                for row in range(6):
                    off = (1 - k) * 1920 * (1 if row % 2 else -1)
                    ctx.rect(off, row * 107, 1920, 107, fill=True, color='bg', alpha=0.9)
        return render

    def shout(ctx, t, f, u):
        ctx.clear('bg')
        i = env.shot('last-shout')['lines'][0] if env.shot('last-shout') and env.shot('last-shout')['lines'] else 104
        w = text(i).strip()
        a, b = w[:5], w[5:]
        groups = [(0, 2), (2, 3), (3, 5), (5, len(w))]
        times = [t_shout + k * P / 4 for k in range(4)]
        lit = sum(1 for tt in times if t >= tt)
        ctx.image('f_eye', 0, -640, 1920, 1920, variant='ink', flip=True, alpha=0.08 + 0.06 * lit)
        rows = [(a, 0), (b, 5)]
        for r, (s, off) in enumerate(rows):
            if not s:
                continue
            size = ctx.fit(s, 1800, font='serif', weight=900, max_size=300)
            x = 960 - ctx.measure(s, size=size, weight=900, font='serif') / 2
            y = 290 + r * 300
            for c, ch in enumerate(s):
                gi = next(g for g, (p, q) in enumerate(groups) if p <= c + off < q) if any(p <= c + off < q for p, q in groups) else 3
                on = lit > gi
                cw_ = ctx.measure(ch, size=size, weight=900, font='serif')
                ctx.text(ch, x, y, size=size, weight=900, font='serif', color='meHot' if on else 'meDim', alpha=1 if on else 0.4)
                x += cw_
        if lit >= 4:
            ctx.circle(1180, 470, 26, fill=True, color='text')
            ctx.circle(1180, 470, 12, fill=True, color='bg')

    out = {}
    for n, sid in enumerate(('count-1-de', 'count-2-es', 'count-3-fr', 'count-4-ko', 'count-5-sv', 'count-6-zh')):
        out[sid] = {'render': card(n), 'palette': 'error'}
    out['last-shout'] = {'render': shout, 'palette': 'error'}
    return out
