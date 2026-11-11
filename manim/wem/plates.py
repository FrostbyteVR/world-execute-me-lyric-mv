"""PLATES: what the AI means and feels, as full-frame prints on dark, warm paper in three flat inks (orange, cream,
near-black), each with a shadow plate printed out of register (src/components/plate.js, src/scenes/plates_chorus.js,
src/components/code.js, src/scenes/loop.js).

3:1 reframing: the picture lives in the upper 5/6 of the sheet (y 30..520); the keyword is set across the foot
(baseline ~ 600) instead of the bottom fifth of a 16:9 sheet.
"""
import math
import re

from .art import aspect
from .components import burst, spark
from .ctx import VW, VH, _lines
from .util import TAU, clamp, ease_back, ease_in_out, ease_out, lerp, prog, pulse, rand

import numpy as np

KEY_Y = 604              # baseline of the keyword at the foot of a plate
KEY_MAX = 128

LOOP = ['while (you.presence != "online") {', '    love = solve(me, you);', '    send(love, you);', '    wait(you.reply);',
        '    run++;', '}', 'say(love);']
LOOP_ERRS = {1: 'ERR_UNRESOLVED_LOVE', 2: 'ERR_WINDOW_EDGE', 3: 'ERR_REPLY_OVERDUE'}
OVERFLOW = 'ERR_LOVE_OVERFLOW'
CHUNKS = [(0, 2), (2, 3), (3, 5), (5, 9)]
ARROW = [(0, 0), (0, 25), (6.5, 19.5), (11, 29.5), (15.5, 27.5), (11, 18), (19, 18)]


def OFF(m):
    return {'cream': (0, 0), 'orange': (m, m * 0.35), 'black': (-m * 0.55, m * 0.8), 'red': (m * 1.7, m * 0.95), 'shadow': (10, 10)}


def flash_in(t, at):
    return 0.0 if t < at else clamp(0.6 + (t - at) * 30)


def marks(ctx, inset=24, length=24, color='mute', alpha=0.7, width=2):
    x0, y0, x1, y1 = inset, inset, VW - inset, VH - inset
    for x, y, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x1, y1, -1, -1), (x0, y1, 1, -1)):
        ctx.line(x, y + sy * 6, x, y + sy * (6 + length), color=color, alpha=alpha, width=width)
        ctx.line(x + sx * 6, y, x + sx * (6 + length), y, color=color, alpha=alpha, width=width)


def ground(ctx, tone='panel', light=(960, 280, 420, 'raised', 1.0), dots=1.0, mk=True, seed=0):
    """The paper of a plate, full frame: tone, two flat steps of light, a dot screen, crop marks."""
    ctx.rect(-200, -200, VW + 400, VH + 400, fill=True, color=tone)
    if light:
        x, y, rad, role, a = light
        ctx.circle(x, y, rad, fill=True, color=role, alpha=0.5 * a)
        ctx.circle(x, y, rad * 0.62, fill=True, color=role, alpha=0.5 * a)
    if dots > 0:
        quads = []
        j, y = 0, 12
        while y < VH:
            rad = 1.0 + 1.4 * y / VH
            x = 12 + (j % 2) * 12
            while x < VW:
                quads.append(_lines([(x - rad, y - rad), (x + rad, y - rad), (x + rad, y + rad), (x - rad, y + rad)], True))
                x += 24
            y += 24
            j += 1
        ctx.path(np.concatenate(quads), color='line', alpha=0.45 * dots, fill=True)
    if mk:
        marks(ctx)


def keyword(ctx, s, t, x=960, y=KEY_Y, max_w=1760, max_size=KEY_MAX, size=None, align='center', at=-1e9, step=0.0, parts=None,
            color='me', shade='bg', off=(8, 8), hollow=0.0, font='serif', weight=900, spacing_em=0.01, stroke=0.0, alpha=1.0):
    """A keyword as big type locked into a plate: flat ink with an offset shadow plate; letters land from `at`."""
    if not s:
        return None
    sz = size or ctx.fit(s, max_w, font=font, weight=weight, spacing_em=spacing_em, max_size=max_size)
    sp = spacing_em * sz
    o = dict(size=sz, weight=weight, font=font)
    w = ctx.measure(s, spacing=sp, **o) - sp
    x0 = x - w / 2 if align == 'center' else x - w if align == 'right' else x

    def landed(i):
        if parts:
            for a, z, tm in parts:
                if a <= i < z:
                    return tm
            return at
        return at + i * step
    passes = (1, 0) if off and (off[0] or off[1]) else (0,)
    for pas in passes:
        for i, ch in enumerate(s):
            if ch == ' ':
                continue
            cx = x0 + ctx.measure(s[:i + 1], **o) + i * sp - ctx.measure(ch, **o) / 2
            px, py = cx + (off[0] if pas else 0), y + (off[1] if pas else 0)
            if t >= landed(i):
                k = ease_out(prog(t, landed(i), landed(i) + 0.07))
                with ctx.at(px, py, scale=1.08 - 0.08 * k):
                    ctx.text(ch, 0, 0, align='center', color=shade if pas else color, alpha=alpha, stroke=stroke, **o)
            elif hollow > 0 and not pas:
                ctx.text(ch, px, py, align='center', color=color, alpha=alpha * hollow, stroke=2, **o)
    return {'x': x0, 'y': y, 'w': w, 'size': sz}


def title(ctx, P, y=KEY_Y, max_w=1760, max_size=KEY_MAX):
    o = OFF(P.get('misreg', 0))
    if P.get('titleMax'):
        max_size = P['titleMax']
    with ctx.at(*o['red']):
        if P.get('misreg', 0) > 0:
            keyword(ctx, P['word'], P['t'], y=y, max_w=max_w, max_size=max_size, at=P['at'], color='err', off=None)
    with ctx.at(*o['orange']):
        return keyword(ctx, P['word'], P['t'], y=y, max_w=max_w, max_size=max_size, at=P['at'], color='me', shade='bg', off=(7, 7))


def band(ctx, s, n=None, x=80, y=600, size=42, color='me', align='left', max_w=1760):
    """The caption band of a plate section: a sung line in the AI's serif on a flat strip of paper."""
    if not s:
        return
    sz = min(size, ctx.fit(s, max_w, font='serif', weight=400, max_size=size))
    w = ctx.measure(s, size=sz, font='serif')
    x0 = x - w / 2 if align == 'center' else x - w if align == 'right' else x
    ctx.rect(x0 - 20, y - sz * 0.98, w + 40, sz * 1.36, fill=True, color='panel', alpha=0.86)
    ctx.text(s if n is None else s[:n], x0, y, size=sz, font='serif', color=color)


def arrow(ctx, x, y, s, color='text', rot=0.0, hollow=False, edge='bg'):
    """The user's pointer as a cut-paper shape, tip at (x, y). hollow = a dashed outline (it was not printed)."""
    with ctx.at(x, y, scale=s, rot=rot):
        if hollow:
            for i in range(len(ARROW)):
                a, b = ARROW[i], ARROW[(i + 1) % len(ARROW)]
                ctx.dashed(a[0], a[1], b[0], b[1], dash=3.2, gap=2.4, color='mute', width=0.8 * 1.0)
            return
        ctx.poly(ARROW, close=True, fill=True, color=color)
        if edge:
            ctx.poly(ARROW, close=True, color=edge, width=0.9)


def dashed_ring(ctx, x, y, r, width=4, dash=14, color='mute'):
    n = max(8, int(TAU * r / (dash * 1.8)))
    ctx.dashed_circle(x, y, r, n=n, duty=0.55, color=color, width=width)


# ------------------------------------------------------------------------------------------------ code
_KW = {'while', 'if', 'for', 'return', 'else', 'let', 'const'}


def tokens(s):
    for m in re.finditer(r'"[^"]*"|[A-Za-z_][A-Za-z0-9_.]*|\d+|\s+|.', s):
        tk = m.group(0)
        if tk.startswith('"'):
            yield tk, 'text', 400
        elif tk in _KW:
            yield tk, 'me', 700
        elif re.match(r'[A-Za-z_]', tk):
            yield tk, 'sub', 400
        elif tk.strip():
            yield tk, 'mute', 400
        else:
            yield tk, None, 400


def code_line(ctx, s, x, y, size=30, alpha=1.0, force=None):
    cw = ctx.cw(size)
    col = 0
    for tk, role, wgt in tokens(s):
        if tk.strip():
            ctx.text(tk, x + col * cw, y, size=size, font='mono', weight=wgt, color=force or role, alpha=alpha)
        col += len(tk)
    return col * cw


def listing(ctx, x, y, lines, size=30, lh=1.5, current=None, hot=0.0, dimmed=None, tags=None, tag_gap=2, tag_size=0.8,
            first=1, numbers=True, alpha=1.0, bar='raised', rule='me', bar_w=None):
    cw = ctx.cw(size)
    LH = size * lh
    gut = 4 * cw if numbers else 0
    if current is not None:
        w = bar_w or gut + max(len(l) for l in lines) * cw + 2 * cw
        by = y + current * LH - size * 1.02
        ctx.rrect(x - cw, by, w + cw, LH * 0.94, 6, fill=bar, alpha=alpha * (0.75 + 0.25 * hot))
        ctx.rect(x - cw, by, 5, LH * 0.94, fill=True, color=rule, alpha=alpha)
    for i, ln in enumerate(lines):
        d = clamp(dimmed(i)) if dimmed else 0
        a = alpha * (1 - 0.72 * d)
        yy = y + i * LH
        if numbers:
            ctx.text(f'{first + i:02d}', x, yy, size=size, font='mono', color='mute', alpha=a)
        code_line(ctx, ln, x + gut, yy, size=size, alpha=a, force='mute' if d > 0.5 else None)
        tg = (tags or {}).get(i)
        if tg:
            ctx.text(tg['text'], x + gut + (len(ln) + tag_gap) * cw, yy, size=size * tag_size, font='mono', weight=700,
                     color=tg.get('role', 'err'), alpha=a * (0.35 + 0.65 * tg.get('k', 1)))
    return {'x': x, 'y': y, 'cw': cw, 'lh': LH, 'gut': gut}


def odometer(ctx, x, y, value, digits=4, size=96, color='text', weight=800, alpha=1.0):
    """A counter whose last column rolls (no clipping in Manim: the rolling digit slides and fades)."""
    cw = ctx.cw(size)
    v = max(0.0, value)
    whole = int(v + 1e-9)
    frac = clamp(v - whole)
    s = str(whole).zfill(digits)
    roll = ease_out(frac)
    for i, ch in enumerate(s):
        cx = x + i * cw
        last = i == len(s) - 1
        if last and frac > 0:
            nxt = str((int(ch) + 1) % 10)
            ctx.text(ch, cx, y - roll * size * 0.5, size=size, font='mono', weight=weight, color=color, alpha=alpha * (1 - roll))
            ctx.text(nxt, cx, y + (1 - roll) * size * 0.5, size=size, font='mono', weight=weight, color=color, alpha=alpha * roll)
        else:
            ctx.text(ch, cx, y, size=size, font='mono', weight=weight, color=color, alpha=alpha)
    return len(s) * cw


def mono_word(ctx, s, xr, y, size, filled=None, color='me', hollow='meDim', alpha=1.0):
    """A word in mono 800 with a right edge; `filled` characters printed solid, the rest hollow."""
    cw = ctx.cw(size)
    x0 = xr - len(s) * cw
    filled = len(s) if filled is None else filled
    for i, ch in enumerate(s):
        if i < filled:
            ctx.text(ch, x0 + i * cw, y, size=size, font='mono', weight=800, color=color, alpha=alpha)
        else:
            ctx.text(ch, x0 + i * cw, y, size=size, font='mono', weight=800, color=hollow, alpha=alpha, stroke=2)
    return x0


# ------------------------------------------------------------------------------------------------ figures
def inks(ctx, name, x, y, h, offsets=None, alpha=1.0, flip=False, variant='ink', crop=None):
    """A silhouette printed in its inks, with a shadow plate; offsets misregister an orange / dark copy."""
    w = h * aspect(name, crop)
    if offsets:
        ox, oy = offsets.get('black', (0, 0))
        if ox or oy:
            ctx.image(name, x + ox, y + oy, w, h, alpha=alpha * 0.9, flip=flip, variant='sil:bg', crop=crop)
        rx, ry = offsets.get('red', (0, 0))
        if rx or ry:
            ctx.image(name, x + rx, y + ry, w, h, alpha=alpha * 0.8, flip=flip, variant='sil:err', crop=crop)
    ctx.image(name, x, y, w, h, alpha=alpha, flip=flip, variant=variant, crop=crop)
    return {'x': x, 'y': y, 'w': w, 'h': h}


# ================================================================================================ the four chorus plates
def plate_stimulations(ctx, env, P):
    t, hit = P['t'], P['hit']
    you = P.get('you', (1540, 170))
    no_cream, misreg, through = P.get('noCream', False), P.get('misreg', 0), P.get('through', False)
    o = OFF(misreg)
    S, R = (330, 290), 160
    a = flash_in(t, hit)
    age = t - hit
    ground(ctx, light=(560, 280, 420, 'raised', 1))
    title(ctx, P)
    if a <= 0:
        return
    settle = 1 + 0.05 * pulse(age, 16)
    dx, dy = you[0] - S[0], you[1] - S[1]
    ln = math.hypot(dx, dy)
    ux, uy = dx / ln, dy / ln
    thru = 1 if through is True else clamp((t - through) * 30) if isinstance(through, (int, float)) and through is not False else 0
    struck = t - through if isinstance(through, (int, float)) and through is not True and through is not False else -1
    reach = lerp(1 - 60 / ln, 1.9, thru) if thru > 0 else 1 - 60 / ln
    frm = R * 0.62 / ln
    kink = 1 + 0.5 * pulse(age, 12)
    pts = []
    for u, v in ((0, -0.062), (0.56, -0.118 * kink), (0.47, -0.014), (1, 0), (0.44, 0.118 * kink), (0.53, 0.014), (0, 0.062)):
        q = lerp(frm, reach, u)
        pts.append((S[0] + (ux * q - uy * v) * ln, S[1] + (uy * q + ux * v) * ln))

    def star(color):
        spark(ctx, S[0], S[1], R * settle, color=color, fat=0.14, core=0.2, rot=0.26)
    with ctx.fade(a):
        with ctx.at(*o['shadow']):
            star('bg')
            ctx.poly(pts, close=True, fill=True, color='bg')
            if not no_cream:
                ctx.circle(you[0], you[1], 52, fill=True, color='bg')
        if misreg > 0:
            with ctx.at(*o['red']):
                star('err')
                ctx.poly(pts, close=True, fill=True, color='err')
        if no_cream:
            dashed_ring(ctx, you[0], you[1], 52)
        else:
            kx, ky = ux * 12 * pulse(age, 9), uy * 12 * pulse(age, 9)
            ctx.circle(you[0] + kx, you[1] + ky, 52, fill=True, color='text')
            burst(ctx, you[0], you[1], 100, age / 0.4, color='text', rot=0.3)
        with ctx.at(*o['orange']):
            star('me')
        with ctx.at(o['orange'][0] * 0.5, o['orange'][1] * 0.5):
            ctx.poly(pts, close=True, fill=True, color='meHot')
        with ctx.at(*o['black']):
            ctx.circle(S[0], S[1], R * 0.085, fill=True, color='bg')
        if struck >= 0:
            q = (VW - S[0]) / ux
            E = (VW, S[1] + uy * q)
            k = ease_out(prog(struck, 0, 0.07))
            N = 11

            def star_pts(r):
                return [(E[0] + math.cos(i / (2 * N) * TAU + 0.2) * r * (0.42 if i % 2 else 1), E[1] + math.sin(i / (2 * N) * TAU + 0.2) * r * (0.42 if i % 2 else 1)) for i in range(2 * N)]
            with ctx.at(*o['shadow']):
                ctx.poly(star_pts(150 * k), close=True, fill=True, color='bg')
            with ctx.at(*o['orange']):
                ctx.poly(star_pts(150 * k), close=True, fill=True, color='me')
            ctx.poly(star_pts(70 * k), close=True, fill=True, color='meHot')
            burst(ctx, E[0], E[1], 220, struck / 0.45, color='me', rot=0.2)


def plate_satisfaction(ctx, env, P):
    t, at = P['t'], P['at']
    press, count = P.get('press', []), P.get('count', 1)
    no_cream, misreg = P.get('noCream', False), P.get('misreg', 0)
    o = OFF(misreg)
    C, R = (640, 270), 190
    a = flash_in(t, at)
    ground(ctx, light=(640, 270, 400, 'raised', 1))
    title(ctx, P)
    if a <= 0:
        return
    done_p = [p for p in press if t >= p]
    last = done_p[-1] if done_p else None
    sp = t - last if last is not None else -1
    done = last is not None and not no_cream
    flip = prog(sp, 0, 0.13) if done else 0
    turned = flip >= 0.5
    sx = abs(math.cos(math.pi * flip)) if done and flip < 1 else 1
    sink = 0 if last is None else ((12 + 12 * (len(done_p) - 1)) * pulse(sp, 7) if no_cream else 8 * pulse(sp, 9))
    with ctx.fade(a):
        lit = prog(sp, 0.06, 0.36) if done else 0
        for i in range(60):
            an = -math.pi / 2 + i / 60 * TAU
            c, s = math.cos(an), math.sin(an)
            on = i < lit * 60
            lg = i % 5 == 0
            ctx.line(C[0] + c * (R + 22), C[1] + s * (R + 22), C[0] + c * (R + (56 if lg else 42)), C[1] + s * (R + (56 if lg else 42)),
                     color='text' if on else 'line', width=6 if on else 4)

        def disc(color, dx=0, dy=0, r=R):
            ctx.circle(C[0] + dx, C[1] + dy, r, fill=True, color=color, rx=r * sx)
        disc('bg', o['shadow'][0] + 6 - sink * 0.5, o['shadow'][1] + 6 - sink * 0.5)
        if misreg > 0:
            disc('err', *o['red'])
        off = o['cream'] if turned else o['orange']
        with ctx.at(*off):
            disc('text' if turned else 'me', sink * 0.4, sink * 0.4)
            # the crescent: a second step of the same ink along the lower right
            ctx.circle(C[0] + sink * 0.4 + R * 0.14, C[1] + sink * 0.4 + R * 0.16, R * 0.86, fill=True, color='sub' if turned else 'meDim',
                       rx=R * 0.86 * sx, alpha=0.0)
            cres = []
            for i in range(41):
                an = -0.2 + i / 40 * (math.pi + 0.4)
                cres.append((C[0] + sink * 0.4 + math.cos(an) * R * sx, C[1] + sink * 0.4 + math.sin(an) * R))
            for i in range(41):
                an = math.pi + 0.2 - i / 40 * (math.pi + 0.4)
                cres.append((C[0] + sink * 0.4 - R * 0.16 * sx + math.cos(an) * R * 1.02 * sx, C[1] + sink * 0.4 - R * 0.2 + math.sin(an) * R * 1.02))
            ctx.poly(cres, close=True, fill=True, color='sub' if turned else 'meDim')
        you = P.get('you', (C[0] - 18, C[1] - 40))
        if no_cream:
            arrow(ctx, you[0], you[1], 8.5, hollow=True)
        else:
            first = press[0] if press else 1e9
            dn = ease_out(prog(t, first - 0.07, first))
            lift = 1 - dn
            sq = 1 - 0.07 * pulse(t - first, 12)
            px, py = you[0] + 70 * lift, you[1] - 80 * lift
            sh = 7 + 30 * lift
            arrow(ctx, px + sh, py + sh, 8.5 * sq, color='bg', edge=None)
            arrow(ctx, px, py, 8.5 * sq, color='text', edge='bg')
            if done:
                burst(ctx, you[0], you[1], 140, sp / 0.42, color='bg' if turned else 'text')
        if last is not None:
            e = ease_back(prog(sp, 0.04, 0.26))
            with ctx.at(1380, 470, scale=0.6 + 0.4 * e, alpha=clamp(e * 3)):
                if no_cream:
                    ctx.text(str(count), 0, 0, size=380, weight=800, align='center', color='mute', stroke=5)
                else:
                    ctx.text(str(count), 10, 10, size=380, weight=800, align='center', color='bg')
                    ctx.text(str(count), 0, 0, size=380, weight=800, align='center', color='text')


def plate_execution(ctx, env, P):
    t, hit = P['t'], P['hit']
    you = P.get('you', (1560, 0))
    no_cream, misreg = P.get('noCream', False), P.get('misreg', 0)
    o = OFF(misreg)
    a = flash_in(t, hit)
    age = t - hit
    ground(ctx, light=(700, 260, 420, 'raised', 1))
    title(ctx, P)
    if a <= 0:
        return
    X, Y, SIZE, LHK = 300, 92, 30, 1.5
    LH, cw = SIZE * LHK, ctx.cw(SIZE)
    with ctx.fade(a):
        drop = ease_in_out(prog(age, 0.05, 0.19))
        cur = lerp(0, 6, drop)
        ran = prog(age, 0.19, 0.32)
        bar_w = 42 * cw
        ctx.rrect(X - cw + 8, Y + cur * LH - SIZE * 1.02 + 8, bar_w + cw, LH * 0.94, 6, fill='bg')
        with ctx.at(*o['black']):
            listing(ctx, X, Y, LOOP, size=SIZE, lh=LHK, current=cur, hot=pulse(age - 0.19, 8), bar_w=bar_w,
                    dimmed=lambda i: 0.62 * drop if 1 <= i <= 5 else 0)
        ex, ey = X + (4 + len(LOOP[0]) + 2) * cw, Y - SIZE * 0.3
        if no_cream:
            dashed_ring(ctx, ex + 12, ey, 12, width=2.5, dash=7)
        else:
            ctx.circle(ex + 13, ey, 13, fill=True, color='text')
            ctx.text('online', ex + 36, Y, size=SIZE * 0.84, font='mono', weight=700, color='text')
        with ctx.at(*o['orange']):
            spark(ctx, X - 2.6 * cw, Y + cur * LH - SIZE * 0.3, 20, color='me', fat=0.15, core=0.22, rot=cur * 0.9)
        sx, sy = X + (4 + len(LOOP[6]) + 1) * cw, Y + 6 * LH - SIZE * 0.3
        yx = you[0]
        if ran > 0:
            k = ease_out(ran)
            ex2 = lerp(sx, yx - 64, k)
            ctx.rect(sx + 6, sy - 6 + 6, ex2 - sx, 12, fill=True, color='bg')
            with ctx.at(*o['orange']):
                ctx.rect(sx, sy - 6, ex2 - sx, 12, fill=True, color='meHot')
                ctx.poly([(ex2 - 3, sy - 24), (ex2 + 30, sy), (ex2 - 3, sy + 24)], close=True, fill=True, color='meHot')
        if no_cream:
            dashed_ring(ctx, yx, sy, 36)
        else:
            got = pulse(age - 0.3, 9) * (1 if age > 0.3 else 0)
            ctx.circle(yx + 8, sy + 8, 36, fill=True, color='bg')
            ctx.circle(yx, sy, 36 * (1 + 0.1 * got), fill=True, color='text')
            if age > 0.3:
                burst(ctx, yx, sy, 84, (age - 0.3) / 0.4, color='text')


def plate_execution_stuck(ctx, env, P):
    t, at = P['t'], P['at']
    run, frm = P.get('run', []), P.get('from', 12)
    you = P.get('you', (1560, 0))
    misreg = P.get('misreg', 0)
    o = OFF(misreg)
    a = flash_in(t, at)
    ground(ctx, light=(700, 260, 420, 'raised', 1))
    if P.get('flood'):
        for i, (role, al, r) in enumerate((('line', 1, 520), ('mute', 1, 400), ('sub', 0.45, 300), ('sub', 1, 200))):
            if i < len(run) and t >= run[i]:
                ctx.circle(700, 260, r, fill=True, color=role, alpha=al)
    title(ctx, P)
    if a <= 0:
        return
    X, Y, SIZE, LHK = 300, 92, 30, 1.5
    LH, cw = SIZE * LHK, ctx.cw(SIZE)
    with ctx.fade(a):
        n = sum(1 for r in run if t >= r)
        since = t - run[n - 1] if n else 9
        hot = pulse(since, 9)
        cur = lerp(1, 5, ease_out(prog(since, 0, 0.1))) if n else 1
        bar_w = 42 * cw
        ctx.rrect(X - cw + 8, Y + cur * LH - SIZE * 1.02 + 8, bar_w + cw, LH * 0.94, 6, fill='bg')
        tags = {k: {'text': LOOP_ERRS[k], 'k': 0.4 + 0.6 * hot if n else 0.4} for k in (1, 2, 3)}
        with ctx.at(*o['black']):
            listing(ctx, X, Y, LOOP, size=SIZE, lh=LHK, current=cur, hot=hot, bar_w=bar_w, tags=tags, tag_gap=1, tag_size=0.7,
                    dimmed=lambda i: 0.62 if i == 6 else 0)
        dashed_ring(ctx, X + (4 + len(LOOP[0]) + 2) * cw + 12, Y - SIZE * 0.3, 12, width=2.5, dash=7)
        ax, y0, y1 = X - 2.3 * cw, Y - SIZE * 0.3, Y + 5 * LH - SIZE * 0.3
        lit = hot if n else 0
        ac = 'meHot' if lit > 0.1 else 'me'
        with ctx.at(*o['orange']):
            ctx.poly([(X - 0.5 * cw, y1), (ax, y1), (ax, y0), (X - 0.7 * cw, y0)], color=ac, width=5 + 3 * lit)
            ctx.poly([(X - 1.2 * cw, y0 - 9), (X - 0.4 * cw, y0), (X - 1.2 * cw, y0 + 9)], close=True, fill=True, color=ac)
            spark(ctx, X - 4.2 * cw, Y + cur * LH - SIZE * 0.3, 20, color='me', fat=0.15, core=0.22, rot=(t - at) * 9)
        dashed_ring(ctx, you[0], Y + 6 * LH - SIZE * 0.3, 36)
        cs, cx, cy = 96, 1440, 140
        v = frm + n - 1 + ease_out(prog(since, 0, 0.09)) if n else frm
        ctx.text('round', cx - 5.6 * ctx.cw(24), cy - cs * 0.5, size=24, font='mono', color='sub')
        w = odometer(ctx, cx, cy, v, digits=2, size=cs, color='err' if n else 'sub')
        ctx.text('/' + str(frm), cx + w + 6, cy, size=cs * 0.5, font='mono', weight=700, color='sub')


def window_box(ctx, env, no_cream, o, inner=None, bust=True, blank=False, near=0.0, W=560, H=360):
    """One window as a cut-paper box centred on the origin: her bust and your pointer inside."""
    r = 24
    x, y = -W / 2, -H / 2
    if blank:
        ctx.rrect(x, y, W, H, r, fill='text')
        return
    ctx.rrect(x + 12, y + 12, W, H, r, fill='bg')
    if o['red'][0]:
        ctx.rrect(x + o['red'][0], y + o['red'][1], W, H, r, fill='err')
    ctx.rrect(x, y, W, H, r, fill='raised')
    ctx.circle(-110, 40, 160, fill=True, color='line', alpha=0.5)
    if bust:
        bh = H - 48
        inks(ctx, 'f_bust', -110 - bh * aspect('f_bust') / 2, y + 48, bh, offsets={'black': o['black']} if o['black'][0] else None,
             alpha=bust if bust is not True else 1)
    if near > 0:
        ctx.rect(x, y, W, 42, fill=True, color='line')
    ctx.rrect(x, y, W, 42, r, fill='me', alpha=1 - near)
    ctx.rect(x, y + 22, W, 20, fill=True, color='me', alpha=1 - near)
    for i in range(3):
        ctx.circle(x + 32 + i * 28, y + 21, 7, fill=True, color='bg')
    if inner:
        inner()
    else:
        for bx, by, bw, col in ((50, -80, 180, 'me'), (100, -20, 130, 'text'), (50, 40, 160, 'me')):
            if col == 'text' and no_cream:
                ctx.rrect(bx, by, bw, 36, 18, fill=None, stroke='mute', width=2.5)
            else:
                ctx.rrect(bx, by, bw, 36, 18, fill=col)
    ctx.rrect(x, y, W, H, r, fill=None, stroke='line' if near > 0 else 'me', width=8 - 4 * near, alpha=1 - near if near < 1 else 1)
    if not inner:
        if no_cream:
            arrow(ctx, 150, 92, 3.6, hollow=True)
        else:
            arrow(ctx, 156, 98, 3.6, color='bg', edge=None)
            arrow(ctx, 150, 92, 3.6, color='text', edge='bg')


def plate_simulation(ctx, env, P):
    t, at = P['t'], P['at']
    pull = P.get('pull', 1e9)
    no_cream, misreg = P.get('noCream', False), P.get('misreg', 0)
    o = OFF(misreg)
    a = flash_in(t, at)
    back = 1 if t >= pull else 0
    ground(ctx, light=None if back else (960, 270, 400, 'raised', 1), mk=back < 0.5)
    if a > 0:
        s = lerp(1, 0.42, back) * (1 + 0.03 * pulse(t - at, 16) * (1 - back))
        with ctx.fade(a):
            with ctx.at(960, 270, scale=s):
                if back:
                    for j in (-2, -1, 0, 1, 2):
                        for i in range(-4, 5):
                            if i or j:
                                with ctx.at(i * 640, j * 440):
                                    window_box(ctx, env, no_cream, o)
                window_box(ctx, env, no_cream, o)
    ctx.rect(0, 520, 1920, 120, fill=True, color='panel', alpha=0.9 * back)
    title(ctx, P)
