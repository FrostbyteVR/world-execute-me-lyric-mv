"""Section 3 — VERSE 1 (beat 63, 0:29.4 -> bar 24, 0:44.65). State: on (03_verse1.js).
The AI answers the question with mathematics, drawn on the page of the conversation itself. What "I am" is ORANGE,
what it gives "you" is CREAM, and the cream things are made by the user's own cursor.

    v1-points   the spark's twelve tips scatter into a point set; cream edges give it DIMENSION
    v1-circle   the lattice's silhouette relaxes into a circle; the cursor runs its CIRCUMFERENCE
    v1-sine     the circle unrolls into a sine wave; the cursor sits on it, a TANGENT under it
    v1-limit    the wave is damped towards a line; the user presses Stop: that line is the LIMIT
3:1 reframing: the figures sit in the middle of a wide page; the lyric is set top left, the gifts at the right.
"""
import math

from ..components import (R, chat_layout, composer, draw_cursor, header, pill, pointer, room, spark, spark_tips,
                          window_frame)
from ..geom import MESH, big, draw_segs, hull_outline, morph, on_path, place, project, rot
from ..util import TAU, clamp, ease_in_out, ease_out, lerp, prog, pulse, rand
from .kit import ai_line
from .s02_title import HANDOFF


def fmt(v):
    return ('' if v < 0 else ' ') + f'{v:.2f}'


def shots(env):
    T, H, B, Bt, P, text = env.T, env.H, env.B, env.Bt, env.P, env.text
    L = chat_layout(side=0)
    START, hit_dim, cut_circle, t_hand = Bt(63), T(14), H(15), T(16)
    hit_circ, cut_sine, t_sit, hit_tan = T(17), H(18), T(19), T(20)
    cut_limit, hit_lim, END = H(21), T(23), B(24)
    SWEEP = 0.68
    C = {'x': HANDOFF['cx'], 'y': HANDOFF['cy']}
    R_CUBE, R_CIRCLE = 140, 160
    CUBE = MESH['cube']
    AXIS = [next(c for c in range(3) if abs(CUBE['verts'][i][c] - CUBE['verts'][j][c]) > 0.1) for i, j in CUBE['edges']]
    cam = {'cx': C['x'], 'cy': C['y'], 'scale': R_CUBE}

    def spin(t):
        k = ease_out(prog(t, START, START + 1.2))
        return [0.36 * k, 0.5 * (t - START) * k, 0]
    TIPS = [((x - C['x']) / R_CUBE, (y - C['y']) / R_CUBE, 0) for x, y in spark_tips(HANDOFF['cx'], HANDOFF['cy'], HANDOFF['r'], HANDOFF['rot'])]
    cube_hull = hull_outline([project(rot(v, *spin(cut_circle)), cam)[:2] for v in CUBE['verts']])
    circle = place('circle', cx=C['x'], cy=C['y'], r=R_CIRCLE)
    G = R(L['win']['x'] + 2, L['head']['y'] + L['head']['h'] + 2, L['win']['w'] - 4, L['composer']['y'] - L['head']['y'] - L['head']['h'] - 14)

    def hand_angle(t):
        return -math.pi / 2 + TAU / (4 * P) * (min(t, hit_circ) - t_hand) + TAU * ease_in_out(prog(t, hit_circ, hit_circ + SWEEP))

    def sine_geo(t):
        k = ease_in_out(prog(t, cut_sine, cut_sine + 0.75))
        Rc, ccx = lerp(R_CIRCLE, 90, k), lerp(C['x'], 260, k)
        th = hand_angle(cut_sine) + TAU / (2 * P) * (t - cut_sine)
        X0, X1, kx = ccx + Rc + 60, 1800, TAU / 440
        return {'k': k, 'Rc': Rc, 'ccx': ccx, 'ccy': C['y'], 'th': th, 'X0': X0, 'X1': X1, 'kx': kx,
                'yAt': lambda x: C['y'] + Rc * math.sin(th - kx * (x - X0)),
                'slope': lambda x: -Rc * kx * math.cos(th - kx * (x - X0))}

    def stage(ctx, t, busy=True, title_at=START + P):
        room(ctx, dim=0.42, t=t)
        window_frame(ctx, L, glass=0.94)
        title = env.script.get('title', '')
        n = int(clamp((t - title_at) * 22, 0, len(title)))
        header(ctx, L, title=title[:n] if n > 0 else 'New conversation', pres='online')
        x = G['x'] + (C['x'] - G['x']) % 40
        while x < G['x'] + G['w']:
            ctx.line(x, G['y'], x, G['y'] + G['h'], color='line', alpha=0.5 if round((x - C['x']) / 40) % 5 == 0 else 0.22, width=1)
            x += 40
        y = G['y'] + (C['y'] - G['y']) % 40
        while y < G['y'] + G['h']:
            ctx.line(G['x'], y, G['x'] + G['w'], y, color='line', alpha=0.5 if round((y - C['y']) / 40) % 5 == 0 else 0.22, width=1)
            y += 40
        ctx.radial(C['x'], C['y'], 420, 'meDim', 0.14)
        return composer(ctx, L['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, send='busy' if busy else 'idle')

    def say(ctx, t, a, b, x=110, y=120, size=30):
        ai_line(ctx, env, a, t, x, y, size=size, hold=9)
        if b is not None:
            ai_line(ctx, env, b, t, x, y + size * 1.36, size=size, hold=9, color='me')

    def gift(ctx, i, t, at, cx, cy, max_w, max_size=110):
        age = t - at
        if age < 0:
            return
        s = text(i)
        size = ctx.fit(s, max_w, font='serif', weight=900, max_size=max_size)
        sp = size * 0.02
        x = cx - (ctx.measure(s, size=size, weight=900, font='serif', spacing=sp) - sp) / 2
        for k, ch in enumerate(s):
            w = ctx.measure(ch, size=size, weight=900, font='serif')
            e = ease_out(prog(age, k * 0.022, k * 0.022 + 0.16))
            if e > 0 and ch != ' ':
                with ctx.at(x + w / 2, cy, scale=1.9 - 0.9 * e):
                    ctx.text(ch, 0, 0, size=size, weight=900, font='serif', align='center', color='text', alpha=e)
            x += w + sp

    # ------------------------------------------------------------------ points -> DIMENSION
    def points(ctx, t, f, u):
        stage(ctx, t)
        loose = ease_out(prog(t, START, START + 1.0))
        gather = ease_in_out(prog(t, T(13), hit_dim - 0.03))
        s = spin(t)
        group_t = lambda ax: hit_dim + ax * (P / 2)
        pts = []
        for i, tip in enumerate(TIPS):
            w = [(rand(66, i, c) - 0.5) * 2.5 + 0.16 * math.sin(t * (0.7 + 0.2 * c) + i * 1.7 + c) for c in range(3)]
            free = [lerp(tip[c], w[c], loose) for c in range(3)]
            pts.append([lerp(free[c], CUBE['verts'][i][c], gather) for c in range(3)] if i < 8 else [v * (1 + 0.5 * gather) for v in free])
        if t < START + 0.5:
            spark(ctx, C['x'], C['y'], HANDOFF['r'], rot=HANDOFF['rot'], alpha=1 - prog(t, START, START + 0.35))
        if t >= hit_dim:
            draw_segs(ctx, CUBE['segs'], cam, r=s, color='text', width=3 + 2 * pulse(t - hit_dim, 6),
                      grow=lambda i: ease_out(prog(t, group_t(AXIS[i]), group_t(AXIS[i]) + 0.16)))
            for d in (1, 2):
                ctx.flash(0.1 * pulse(t - group_t(d), 10), 'text')
        hot = f['onsetPulse'] > 0.45
        for i, p in enumerate(pts):
            q = project(rot(p, s[0], s[1]), cam)
            a = 1 if i < 8 else 1 - gather
            if a <= 0:
                continue
            with ctx.glow('me', 14, 0.6 * a):
                ctx.circle(q[0], q[1], (10 if hot else 8) * clamp(q[2], 0.7, 1.3), fill=True, color='meHot' if hot else 'me', alpha=a)
            if i < 8:
                ctx.text(f'p{i}', q[0] + 13, q[1] - 10, size=15, font='mono', color='mute', alpha=prog(t, START + 0.4, START + 0.9) * (1 - prog(t, hit_dim, hit_dim + 0.4)))
        say(ctx, t, 12, 13)
        ca = prog(t, START + P, START + 1.6 * P) * (1 - prog(t, cut_circle - 0.3, cut_circle))
        ctx.rrect(110, 200, 330, 250, 14, fill='raised', stroke='line', alpha=ca, shadow=0.4)
        ctx.text('points', 128, 228, size=14, font='mono', color='mute', alpha=ca)
        for i, p in enumerate(pts[:8]):
            if t > START + P + i * 0.06:
                ctx.text(f'p{i} ({fmt(p[0])},{fmt(-p[1])},{fmt(p[2])})', 128, 258 + 24 * i, size=16, font='mono', color='sub', alpha=ca)
        if t >= hit_dim:
            dims = min(3, 1 + int((t - hit_dim) / (P / 2)))
            word = text(14)
            size = ctx.fit(word, 520, font='serif', weight=900, max_size=120)
            punch = 1 + 0.07 * pulse(t - group_t(dims - 1), 8)
            with ctx.at(1500, 420, sx=punch, sy=0.05 if dims == 1 else punch):
                if dims >= 3:
                    for l in range(8, 0, -1):
                        big(ctx, word, l * 3.5, -l * 3.5, size=size, weight=900, color='sub', alpha=0.2, stroke=1.5)
                big(ctx, word, 0, 0, size=size, weight=900, color='text')
            pill(ctx, 1500, 300, f'{dims}D', align='center', font='mono', size=17, color='text')
        ctx.flash(0.28 * pulse(t - hit_dim, 9), 'text')
        draw_cursor(ctx, [{'t': START, 'x': 1600, 'y': 160}, {'t': hit_dim - 0.3, 'x': C['x'] + 260, 'y': C['y'] + 20},
                          {'t': cut_circle, 'x': C['x'] + 240, 'y': C['y'] - 110}], t)

    # ------------------------------------------------------------------ circle -> CIRCUMFERENCE
    def circle_shot(ctx, t, f, u):
        stage(ctx, t)
        relax = ease_in_out(prog(t, cut_circle, cut_circle + 1.6 * P))
        measured = prog(t, hit_circ, hit_circ + SWEEP)
        spark(ctx, C['x'], C['y'], R_CIRCLE * 0.86, color='meDim', alpha=0.28 * relax, core=0, rot=0.05 * (t - cut_circle))
        with ctx.glow('me', 16, 0.4):
            ctx.poly(morph(cube_hull, circle, relax), close=True, color='me', width=5)
        ctx.line(C['x'] - 9, C['y'], C['x'] + 9, C['y'], color='sub')
        ctx.line(C['x'], C['y'] - 9, C['x'], C['y'] + 9, color='sub')
        rr = R_CIRCLE + 30
        fade = 1 - prog(t, hit_circ - 0.1, hit_circ + 0.12)
        on_path(ctx, text(15), lambda d: (C['x'] + math.cos(-2.42 + d / rr) * rr, C['y'] + math.sin(-2.42 + d / rr) * rr, -2.42 + d / rr + math.pi / 2),
                size=40, weight=600, spacing_em=0.12, reveal=env.lyrics.typed(15, t), alpha=fade)
        if t >= t_hand:
            r2 = R_CIRCLE + 56
            on_path(ctx, text(16), lambda d: (C['x'] + math.cos(2.5 - d / r2) * r2, C['y'] + math.sin(2.5 - d / r2) * r2, 2.5 - d / r2 - math.pi / 2),
                    size=30, weight=400, spacing_em=0.1, reveal=env.lyrics.typed(16, t), alpha=fade)
            th = hand_angle(t)
            ln = R_CIRCLE * ease_out(prog(t, t_hand, t_hand + 0.3))
            ctx.line(C['x'], C['y'], C['x'] + math.cos(th) * ln, C['y'] + math.sin(th) * ln, color='me', width=3)
            ctx.text('r', C['x'] + math.cos(th) * ln * 0.5 + 12, C['y'] + math.sin(th) * ln * 0.5 - 10, size=26, font='serif', italic=True, color='me')
        a0 = hand_angle(hit_circ)
        if measured > 0:
            swept = TAU * ease_in_out(measured)
            word = text(17)
            step = TAU / max(1, len(word))
            ctx.circle(C['x'], C['y'], R_CIRCLE, a0=a0, a1=a0 + swept, width=8, color='text')
            for i, ch in enumerate(word):
                off = (i + 0.5) * step
                if off > swept:
                    break
                a = a0 + off
                k = pulse(swept - off, 2.2)
                with ctx.at(C['x'] + math.cos(a) * (R_CIRCLE + 48), C['y'] + math.sin(a) * (R_CIRCLE + 48), rot=a + math.pi / 2, scale=1 + 0.45 * k):
                    ctx.text(ch, 0, 0, size=60, weight=900, font='serif', align='center', color='text')
            ctx.text(f'C = 2 * PI * r = {TAU * ease_in_out(measured):.4f}', C['x'], C['y'] + 54, size=21, font='mono', align='center', color='text')
        ctx.flash(0.25 * pulse(t - hit_circ, 9), 'text')
        if t < hit_circ:
            draw_cursor(ctx, [{'t': cut_circle, 'x': C['x'] + 240, 'y': C['y'] - 110}, {'t': t_hand, 'x': C['x'] + 330, 'y': C['y'] + 40},
                              {'t': hit_circ - 0.02, 'x': C['x'] + math.cos(a0) * R_CIRCLE, 'y': C['y'] + math.sin(a0) * R_CIRCLE, 'click': True}], t)
        else:
            a = hand_angle(t)
            pointer(ctx, C['x'] + math.cos(a) * R_CIRCLE, C['y'] + math.sin(a) * R_CIRCLE, scale=1.5, down=1)

    # ------------------------------------------------------------------ sine -> TANGENTS
    def sine(ctx, t, f, u):
        stage(ctx, t)
        g = sine_geo(t)
        Rc, ccx, ccy, th, X0, X1, y_at, slope = g['Rc'], g['ccx'], g['ccy'], g['th'], g['X0'], g['X1'], g['yAt'], g['slope']
        with ctx.glow('me', 12, 0.35):
            ctx.circle(ccx, ccy, Rc, color='me', width=5)
        hx, hy = ccx + math.cos(th) * Rc, ccy + math.sin(th) * Rc
        ctx.line(ccx, ccy, hx, hy, color='me', width=3)
        ctx.circle(hx, hy, 6, fill=True, color='me')
        ctx.line(ccx - Rc - 16, ccy, X1, ccy, color='sub', alpha=0.6 * g['k'], width=1.5)
        ctx.dashed(hx, hy, X0, hy, dash=6, gap=8, color='sub', alpha=g['k'], width=1.5)
        x_end = lerp(X0, X1, ease_out(prog(t, cut_sine + 0.3, cut_sine + 1.0)))
        x = X0
        while x <= x_end:
            ctx.line(x, ccy, x, y_at(x), color='meDim', alpha=0.5, width=2)
            x += 12
        curve = []
        x = X0
        while x <= x_end:
            curve.append((x, y_at(x)))
            x += 6
        if len(curve) > 1:
            with ctx.glow('me', 12, 0.4):
                ctx.poly(curve, color='me', width=5)
        say(ctx, t, 18, None, x=110, y=96)
        if t >= t_sit:
            on_path(ctx, text(19), lambda d: (X0 + 60 + d, y_at(X0 + 60 + d) - 26, math.atan(slope(X0 + 60 + d))),
                    size=32, weight=600, spacing_em=0.2, reveal=env.lyrics.typed(19, t))
            xr = lerp(X0, X1, 0.74)
            yr, m = y_at(xr), slope(xr)
            l = math.hypot(1, m)
            half = 140 * ease_out(prog(t, t_sit, t_sit + 0.3))
            ctx.line(xr - half / l, yr - half * m / l, xr + half / l, yr + half * m / l, color='text', width=4)
            ctx.circle(xr, yr, 6, fill=True, color='text')
            pointer(ctx, xr - 4, yr - 2 - 160 * (1 - ease_out(prog(t, t_sit, t_sit + 0.35))), kind='hand', scale=1.4, alpha=prog(t, t_sit, t_sit + 0.12))
        if t >= hit_tan:
            for i, uu in enumerate((0.16, 0.36, 0.56)):
                x = lerp(X0, X1, uu)
                y, m = y_at(x), slope(x)
                l = math.hypot(1, m)
                half = 120 * ease_out(prog(t, hit_tan + i * 0.03, hit_tan + i * 0.03 + 0.16))
                ctx.line(x - half / l, y - half * m / l, x + half / l, y + half * m / l, color='text', width=4)
                ctx.circle(x, y, 6, fill=True, color='text')
            gift(ctx, 20, t, hit_tan, 1100, 520, 760, 100)
        ctx.flash(0.28 * pulse(t - hit_tan, 8), 'text')

    # ------------------------------------------------------------------ infinity -> LIMITATIONS
    def limit(ctx, t, f, u):
        stopped = t >= hit_lim
        box = stage(ctx, t, busy=not stopped)
        g = sine_geo(t)
        k = ease_in_out(prog(t, cut_limit, cut_limit + 2 * P))
        X0, X1, yL = lerp(g['X0'], 160, k), 1800, 230
        base = lerp(C['y'], 420, k)
        locked = prog(t, hit_lim, hit_lim + 0.25)
        run = min(t, hit_lim) - cut_limit

        def y_at(x):
            uu = (x - X0) / (X1 - X0)
            return (base - (base - yL - 12) * (1 - math.exp(-uu * 4.2)) * k
                    + g['Rc'] * lerp(1, math.exp(-uu * 5), k) * (1 - 0.9 * locked) * math.sin(g['th'] - g['kx'] * (x - X0)))
        ctx.circle(g['ccx'], g['ccy'], g['Rc'], color='me', width=5, alpha=1 - prog(t, cut_limit, cut_limit + 0.35))
        ctx.line(X0, base + 50, X1, base + 50, color='sub', width=1.5)
        ctx.line(X0, base + 50, X0, yL - 40, color='sub', width=1.5)
        for i in range(9):
            x = lerp(X0, X1, (i + 1) / 9.5)
            ctx.line(x, base + 50, x, base + 58, color='sub', width=1.5)
            ctx.text(f'1e{int(run * 6) + i * 3}', x, base + 76, size=15, font='mono', color='mute', align='center', alpha=k)
        la = prog(t, cut_limit + P, cut_limit + 2 * P)
        if locked > 0:
            with ctx.glow('text', 14, 0.5 * locked):
                ctx.line(X0, yL, X1, yL, color='text', width=3 + 3 * locked, alpha=la)
        else:
            ctx.dashed(X0, yL, X1, yL, dash=14, gap=12, color='text', width=3, alpha=la)
        curve = [(x, y_at(x)) for x in range(int(X0), int(X1), 6)]
        for x in range(int(X0), int(X1), 13):
            ctx.line(x, base + 50, x, y_at(x), color='meDim', alpha=0.3 * k, width=2)
        with ctx.glow('me', 12, 0.4):
            ctx.poly(curve, color='me', width=5)
        xr = lerp(X0, X1, clamp(0.25 + run * 0.2))
        with ctx.glow('me', 14, 0.7):
            ctx.circle(xr, y_at(xr), 9, fill=True, color='meHot')
        say(ctx, t, 21, 22, 110, 110, 30)
        if stopped:
            word = text(23)
            step = (X1 - X0 - 60) / max(1, len(word))
            for i, ch in enumerate(word):
                ki = ease_out(prog(t, hit_lim + i * 0.02, hit_lim + i * 0.02 + 0.14))
                if ki > 0:
                    ctx.text(ch, X0 + 30 + (i + 0.5) * step, yL - 14 - (1 - ki) * 70, size=72, weight=900, font='serif', align='center', color='text', alpha=ki)
            pill(ctx, box['send'][0] - 40, box['send'][1] - 46, 'Stopped', align='right', size=15, color='text', alpha=prog(t, hit_lim, hit_lim + 0.2))
        ctx.flash(0.3 * pulse(t - hit_lim, 8), 'text')
        sx, sy = box['send']
        draw_cursor(ctx, [{'t': cut_limit, 'x': 1500, 'y': 360}, {'t': hit_lim - 1.2 * P, 'x': 1380, 'y': 470},
                          {'t': hit_lim, 'x': sx + 3, 'y': sy + 4, 'click': True}, {'t': END, 'x': sx + 70, 'y': sy - 70}], t)

    return {
        'v1-points': {'render': points, 'palette': 'on'},
        'v1-circle': {'render': circle_shot, 'palette': 'on'},
        'v1-sine': {'render': sine, 'palette': 'on'},
        'v1-limit': {'render': limit, 'palette': 'on'},
    }
