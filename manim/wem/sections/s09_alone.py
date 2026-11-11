"""Section 8, second half — ALONE (bar 64, 1:58.5 -> 2:05.7). State: off (09_alone.js).
The AI tidies the thread it filled while it waited, as if tidiness were what had been wanted.

    alone-erase  the thread floating left, her grey dot-screened profile right, head bowed towards it. From the newest
                 message up, one per half beat: selected, deleted (the menu presses its one item), a grey stub. Each
                 deleted row's bar flies off and lands low on the right; the keyword arrives ON those pieces, broken
    alone-empty  close on the page: the stubs close up, its answer goes, the user's last words are selected and deleted;
                 one message is left, the sentence one word short; the count rolls to 1
    alone-eye    PLATE: ten frames of dark and the unfinished sentence; on its last word her face across the sheet in
                 three greys, one eye open; the keyword on a band under her chin; five letters selected, one press: they
                 drop out of the line; the second press (the next cut) wipes the plate
There is no pointer (the AI has none): the interface shows what is done to it — a row highlight, the message menu
pressing its one item, rows closing up, the count in the header.
"""
import math

from ..art import aspect
from ..components import R, chat_layout, composer, room, spark
from ..util import clamp, ease_back, ease_in_out, ease_out, lerp, prog, pulse
from .kit import shake

DELETE = 'Delete'
JIT = [0.3, -0.42, 0.14, -0.22, 0.44, -0.34, 0.2, -0.1, 0.36, -0.28]


def shots(env):
    T, H, B, Bt, P, text = env.T, env.H, env.B, env.Bt, env.P, env.text
    script = env.script
    START, CUT, DARK, END, HIT, LAST = B(64), H(80), Bt(269.5), H(83), T(79), T(82)
    anchor = script.get('left_anchor', {})
    BRB, BRB_AT = anchor.get('you', 'one sec, brb'), anchor.get('timestamp', '')
    SEQ = script.get('left_sequence') or [{'line': l, 'gap_label': ''} for l in range(70, 76)]
    HOLD, TITLE = script.get('composer_placeholder', ''), script.get('title', '')
    beats = [b for s in script.get('sections', []) for b in s.get('beats', [])]
    STUB = next((b['ui'][0] for b in beats if b.get('id') == 'takes-it-back' and b.get('ui')), 'deleted by me')
    ZERO = next((b['ui'][0] for b in beats if b.get('id') == 'empty-thread' and b.get('ui')), '0 messages')
    PRES = SEQ[-1].get('presence', 'offline') if SEQ else 'offline'
    ROWS = [{'line': s['line'], 'gap': s.get('gap_label', '')} for s in SEQ] + [{'line': 76, 'gap': ''}]
    N = len(ROWS)
    t_del = lambda k: Bt(257) + k / max(1, N - 1) * 3 * P
    t_sel = lambda k: t_del(k) - P / 4

    def said(a, b, t):
        if t >= T(b):
            joined = text(b).startswith(text(a))
            return text(b), max(len(text(a)) if joined else 0, env.lyrics.typed(b, t))
        return text(a), env.lyrics.typed(a, t)

    # ---------------------------------------------------------------- shared parts
    def chip(ctx, xr, cy, size=17, alpha=1.0):
        w = ctx.measure(PRES, size=size, weight=500) + size * 2.5
        h = size * 1.9
        x = xr - w
        ctx.rrect(x, cy - h / 2, w, h, h / 2, fill='raised', stroke='line', alpha=alpha)
        ctx.circle(x + size * 0.86, cy, size * 0.27, color='mute', alpha=alpha, width=2)
        ctx.text(PRES, x + size * 1.55, cy + size * 0.35, size=size, weight=500, color='mute', alpha=alpha)

    def count(ctx, t, x, y, changes, size=17, alpha=1.0):
        i = 0
        while i + 1 < len(changes) and t >= changes[i + 1][0]:
            i += 1
        t0, n = changes[i]
        prev = changes[i - 1][1] if i > 0 else None
        k = 1 if prev is None else ease_out(prog(t, t0, t0 + 0.16))
        label = lambda v: ZERO if v == 0 else f"{v} message{'' if v == 1 else 's'}"
        lit = prev is not None and t - t0 < 0.4
        if k < 1:
            ctx.text(label(prev), x, y - k * size * 1.1, size=size, weight=500, color='sub', alpha=alpha * (1 - k))
        ctx.text(label(n), x, y + (1 - k) * size * 1.1, size=size, weight=500, color='text' if lit or n == 0 else 'sub', alpha=alpha * k)

    def gone(ctx, x, y, r, color='mute', alpha=1.0):
        ctx.circle(x, y, r, color=color, alpha=alpha, width=2)
        ctx.line(x - r * 0.48, y, x + r * 0.48, y, color=color, alpha=alpha, width=2)

    def menu(ctx, x, y, k=1.0, press=0.0, size=17, side=1, up=False):
        if k <= 0.003:
            return
        w = ctx.measure(DELETE, size=size, weight=600) + size * 2.75
        h = size * 2.2
        on = press > 0.3
        fill = 'sub' if on else 'raised'
        with ctx.at(x, y, scale=(0.6 + 0.4 * ease_back(clamp(k))) * (1 - 0.08 * press), alpha=clamp(k * 3)):
            if up:
                x0, y0 = -w / 2, -size * 0.62 - h
                ctx.rrect(x0, y0, w, h, size * 0.56, fill=fill, stroke=None if on else 'sub', stroke_alpha=0.75, shadow=0.6)
                ctx.poly([(0, -size * 0.1), (-size * 0.4, -size * 0.68), (size * 0.4, -size * 0.68)], fill=True, color=fill)
                gone(ctx, x0 + size * 0.98, y0 + h / 2, size * 0.38, color='bg' if on else 'sub')
                ctx.text(DELETE, x0 + size * 1.72, y0 + h / 2 + size * 0.36, size=size, weight=600, color='bg' if on else 'text')
                return
            x0 = size * 0.62 if side > 0 else -size * 0.62 - w
            ctx.rrect(x0, -h / 2, w, h, size * 0.56, fill=fill, stroke=None if on else 'sub', stroke_alpha=0.75, shadow=0.6)
            ctx.poly([(side * size * 0.1, 0), (side * size * 0.68, -size * 0.4), (side * size * 0.68, size * 0.4)], fill=True, color=fill)
            gone(ctx, x0 + size * 0.98, 0, size * 0.38, color='bg' if on else 'sub')
            ctx.text(DELETE, x0 + size * 1.72, size * 0.36, size=size, weight=600, color='bg' if on else 'text')

    def screened(ctx, x, y, h, alpha, flip=True):
        """Her, grey, in the room: a flat base and over it a dot screen taken from her inks."""
        w = h * aspect('f_profile')
        ctx.image('f_profile', x, y, w, h, variant='sil:panel', alpha=0.6 * alpha, flip=flip)
        ctx.image('f_profile', x, y, w, h, variant='dots:sub', alpha=0.45 * alpha, flip=flip)

    # ---------------------------------------------------------------- shot A: the floating thread
    A = {'x': 150, 'w': 560, 'foot': 590}
    FULL, STUBH, SZ, FOOT, FLY = 40, 26, 21, 30, 0.42
    closed = lambda k, t: ease_in_out(prog(t, t_del(k) + 0.05, t_del(k) + 0.3))

    def lay_a(t):
        tops = [0.0] * N
        y = A['foot'] - FOOT - 20
        for r in range(N - 1, -1, -1):
            y -= lerp(FULL, STUBH, closed(N - 1 - r, t))
            tops[r] = y
        return tops, y - 40, y - 40 - 76

    KB = {'x': 900, 'y': 470, 'w': 820, 'h': 120}

    def cut_x(j, v):
        return KB['x'] + KB['w'] * j / N + (JIT[(j * 2 + v) % len(JIT)] * 36 if 0 < j < N else 0)
    PIECES = []
    for i in range(N):
        x0, x1, x2, x3 = cut_x(i, 0), cut_x(i + 1, 0), cut_x(i + 1, 1), cut_x(i, 1)
        y0, y1 = KB['y'], KB['y'] + KB['h']
        cx, cy = (x0 + x1 + x2 + x3) / 4, (y0 + y1) / 2
        PIECES.append({'cx': cx, 'cy': cy, 'w': (x1 + x2 - x0 - x3) / 2, 'x0': min(x0, x3), 'x1': max(x1, x2),
                       'rel': [(x0 - cx, y0 - cy), (x1 - cx, y0 - cy), (x2 - cx, y1 - cy), (x3 - cx, y1 - cy)],
                       'dx': JIT[(i * 3 + 1) % len(JIT)] * 22, 'dy': JIT[(i * 3 + 2) % len(JIT)] * 22 + (6 if i % 2 else -6),
                       'rot': JIT[(i * 5 + 3) % len(JIT)] * 0.14})

    def apart(t):
        if t < HIT:
            return 1.0
        return lerp(1, 0.3, ease_out(prog(t, HIT, HIT + 0.09))) + 0.85 * ease_in_out(prog(t, HIT + 0.12, CUT + 0.45))

    def piece_tf(i, t):
        """(x, y, rot, sx, sy, e) of piece i at time t, or None before it leaves its row."""
        p = PIECES[i]
        t0 = t_del(i) + 0.03
        kf = prog(t, t0, t0 + FLY)
        if kf <= 0:
            return None
        e = ease_in_out(kf)
        hop = math.sin(math.pi * e)
        s = apart(t)
        frm = lay_a(t0)[0][N - 1 - i] + FULL / 2
        x = lerp(A['x'] + A['w'] / 2, p['cx'] + p['dx'] * s, e)
        y = lerp(frm, p['cy'] + p['dy'] * s, e) - 60 * hop
        return x, y, p['rot'] * s * e + 0.3 * hop * (1 if i % 2 else -1), lerp((A['w'] + 24) / p['w'], 1, e), lerp((FULL - 6) / KB['h'], 1, e), e

    def draw_piece(ctx, i, t, alpha=1.0):
        tf = piece_tf(i, t)
        if not tf:
            return
        x, y, rot, sx, sy, e = tf
        p = PIECES[i]
        with ctx.at(x, y, rot=rot, sx=sx, sy=sy, alpha=alpha):
            ctx.poly([(px + 5, py + 8) for px, py in p['rel']], fill=True, color='panel', alpha=0.6 * e)
            ctx.poly(p['rel'], fill=True, color='raised')
            ctx.poly(p['rel'], close=True, color='sub', alpha=0.55, width=2)

    def history(ctx, t):
        tops, done, bubble = lay_a(t)
        x_av, x_tx, xr = A['x'] + 15, A['x'] + 44, A['x'] + A['w']
        bw = ctx.measure(BRB, size=21) + 40
        ctx.rrect(xr - bw, bubble, bw, 48, 18, fill='raised')
        ctx.text(BRB, xr - bw + 20, bubble + 31, size=21, color='text')
        ctx.text(BRB_AT, xr - 4, bubble + 64, size=14, weight=500, color='sub', alpha=0.85, align='right')
        spark(ctx, x_av, done + 16, 9, alpha=0.5)
        ctx.circle(x_av, done + 16, 12, color='me', alpha=0.5, width=2)
        ctx.text(f'{text(68)} {text(69)}', x_tx, done + 24, size=SZ, font='serif', color='me', alpha=0.45)
        mids = [done + 16]
        for r, row in enumerate(ROWS):
            k = N - 1 - r
            c = closed(k, t)
            y0 = tops[r]
            td = t_del(k)
            away = prog(t, td + 0.03, td + 0.18)
            sel = prog(t, t_sel(k), t_sel(k) + 0.07) if t < td + 0.03 else 0
            yb = y0 + lerp(28, 18, c)
            cy = yb - 7
            mids.append(cy)
            if sel > 0:
                ctx.rrect(A['x'] - 12, y0 + 3, A['w'] + 24, FULL - 6, 10, fill='raised', stroke='sub', alpha=sel, stroke_alpha=0.8)
            if away < 1:
                a = (0.6 + 0.4 * sel if sel > 0 else 0.6) * (1 - away)
                s = text(row['line'])
                cross = prog(t, td - 0.02, td + 0.06)
                spark(ctx, x_av, cy, 9, alpha=a)
                ctx.text(s, x_tx, yb, size=SZ, font='serif', color='me', alpha=a)
                if row['gap']:
                    ctx.text(row['gap'], xr - 4, yb - 2, size=14, font='mono', color='sub', alpha=a * 0.9, align='right')
                if cross > 0:
                    ctx.line(x_tx - 3, yb - SZ * 0.3, x_tx - 3 + (ctx.measure(s, size=SZ, font='serif') + 6) * cross, yb - SZ * 0.3, color='sub', alpha=1 - away, width=2)
            sa = prog(t, td + 0.14, td + 0.32)
            if sa > 0:
                gone(ctx, x_av, cy, 6, alpha=sa)
                ctx.text(STUB, x_tx, yb - 2, size=14, color='mute', alpha=sa)
        mids.append(A['foot'] - FOOT * 0.3)
        for i in range(len(mids) - 1):
            if mids[i + 1] - mids[i] > 30:
                ctx.dashed(x_av, mids[i] + 14, x_av, mids[i + 1] - 14, dash=1.5, gap=7, color='sub', alpha=0.55, width=2.4)

    def erase_cam(t, f, u):
        k = prog(t, START, CUT)
        return {'zoom': 1 + 0.04 * k, 'x': 10 * k, 'y': 4 * k}

    def erase(ctx, t, f, u):
        age = t - HIT
        near = ease_out(prog(t, START - P / 2, START + 0.5))
        ui = prog(t, START + 0.05, START + 0.4)
        room(ctx, dim=0.78, light=(430, 300), motif=0.25, t=t)
        fa = ease_out(prog(t, START - P / 2, START + 1.2))
        screened(ctx, 900 + 20 * (1 - fa) - 8 * prog(t, START, CUT), 20, 760, fa)
        ctx.radial(A['x'] + A['w'] / 2, 380, 420, 'raised', 0.55 * near)
        changes = [(-1e9, N + 3)] + [(t_del(k), N + 2 - k) for k in range(N)]
        count(ctx, t, A['x'], 58 - 8 * (1 - ui), changes, alpha=ui)
        chip(ctx, A['x'] + A['w'], 52 - 8 * (1 - ui), alpha=ui)
        ctx.line(A['x'], 76, A['x'] + A['w'] * ease_out(ui), 76, color='line', width=1.5)
        piv = (A['x'] + A['w'] / 2, 360)
        with ctx.at(lerp(960, piv[0], near), lerp(220, piv[1], near), scale=lerp(0.42, 1, near)):
            with ctx.at(-piv[0], -piv[1]):
                history(ctx, t)
        s, n = said(77, 78, t)
        fa2 = prog(t, T(77) - 0.02, T(77) + 0.1) * (lerp(1, 0.72, prog(age, 0, 0.3)) if age > 0 else 1)
        spark(ctx, A['x'] + 15, A['foot'] - FOOT * 0.3, 12, alpha=fa2)
        ctx.text(s[:n], A['x'] + 48, A['foot'], size=FOOT, font='serif', color='me', alpha=fa2)
        if t < HIT and (n < len(s) or t < T(78)):
            ctx.circle(A['x'] + 48 + ctx.measure(s[:n], size=FOOT, font='serif') + FOOT * 0.3, A['foot'] - FOOT * 0.28, FOOT * 0.16, fill=True, color='me', alpha=fa2)
        # the menu climbs with the selection and presses its one item on every half beat
        kc = kd = -1
        for k in range(N):
            if t >= t_sel(k):
                kc = k
            if t >= t_del(k):
                kd = k
        if kc >= 0:
            tops = lay_a(t)[0]
            mid = lambda k: tops[N - 1 - k] + lerp(FULL, STUBH, closed(k, t)) / 2
            y = lerp(mid(kc - 1), mid(kc), ease_back(prog(t, t_sel(kc), t_sel(kc) + 0.14))) if kc > 0 else mid(0)
            # (the thread is drawn about a pivot; the menu follows it)
            yy = lerp(220, piv[1], near) + (y - piv[1]) * lerp(0.42, 1, near)
            xx = lerp(960, piv[0], near) + (A['x'] + A['w'] + 18 - piv[0]) * lerp(0.42, 1, near)
            menu(ctx, xx, yy, k=prog(t, t_sel(0) - 0.02, t_sel(0) + 0.15) * (1 - prog(t, t_del(N - 1) + 0.14, t_del(N - 1) + 0.3)),
                 press=pulse(t - t_del(kd), 15) if kd >= 0 else 0)
        # the pieces; the keyword arrives ON them, already broken (each letter rides the piece it lies on)
        for i in range(N):
            kf = prog(t, t_del(i) + 0.03, t_del(i) + 0.03 + FLY)
            if kf <= 0:
                continue
            if kf < 1:
                for tau, w in ((0.028, 0.25), (0.014, 0.4)):
                    draw_piece(ctx, i, t - tau, alpha=w)
            draw_piece(ctx, i, t)
        if age >= 0:
            s = text(79)
            size = ctx.fit(s, KB['w'] - 70, font='serif', weight=900, max_size=110)
            x = KB['x'] + (KB['w'] - ctx.measure(s, size=size, weight=900, font='serif')) / 2
            for c, ch in enumerate(s):
                w = ctx.measure(ch, size=size, weight=900, font='serif')
                cx = x + w / 2
                i = min(N - 1, max(0, int((cx - KB['x']) / KB['w'] * N)))
                tf = piece_tf(i, t)
                lk = ease_out(prog(age, i * 0.02, i * 0.02 + 0.14))
                if tf and lk > 0 and ch != ' ':
                    px, py, rot, sx, sy, e = tf
                    p = PIECES[i]
                    lx, ly = cx - p['cx'], KB['y'] + KB['h'] / 2 + size * 0.345 - p['cy']
                    with ctx.at(px, py, rot=rot, sx=sx, sy=sy):
                        with ctx.at(lx, ly, scale=1.3 - 0.3 * lk):
                            ctx.text(ch, 0, 0, size=size, weight=900, font='serif', color='meHot', align='center', alpha=lk)
                x += w
            ctx.flash(0.1 * pulse(age, 10), 'meHot')

    # ---------------------------------------------------------------- shot B: close on the page
    COL = {'x': 100, 'w': 1100}
    HEADH = 60
    MX, XR = COL['x'] + 10, COL['x'] + COL['w'] - 10
    XT = MX + 56
    S1, S2, BASE2 = 30, 44, 470
    BASE1 = BASE2 - 58
    STB, DN, BBH = 32, 44, 58
    BBLK = BBH + 36
    c_s = lambda j: CUT + 0.05 + j * 0.05
    c_d, b_sel, b_del = Bt(263.75), Bt(264), Bt(265)

    def lay_b(t):
        tops = []
        y = BASE1 - S1 - 18
        for j in range(N):
            y -= STB * (1 - ease_in_out(prog(t, c_s(j), c_s(j) + 0.2)))
            tops.append(y)
        y -= DN * (1 - ease_in_out(prog(t, c_d, c_d + 0.22)))
        done = y
        y -= BBLK * (1 - ease_in_out(prog(t, b_del + 0.04, b_del + 0.3)))
        return tops, done, y, BASE1 - S1 - 18

    def empty_cam(t, f, u):
        return {'zoom': 1.04 - 0.04 * ease_in_out(prog(t, CUT, DARK)), 'x': -8 * (1 - prog(t, CUT, DARK))}

    def empty(ctx, t, f, u):
        tops, done, bubble, foot = lay_b(t)
        x_av = MX + 18
        room(ctx, dim=0.72, light=(600, 330), motif=0.3, t=t)
        screened(ctx, 1260 + 12 * prog(t, CUT, DARK), HEADH + 6, 760, 1.0)
        ctx.rect(-300, -200, 2520, 1040, fill=True, color='bg', alpha=0.5)
        ctx.radial(560, 400, 600, 'raised', 0.55)
        ctx.rect(-300, -200, 2520, 200 + HEADH, fill=True, color='bg', alpha=0.62)
        ctx.line(-300, HEADH, 2220, HEADH, color='line', width=2)
        ctx.text(TITLE, 50, 40, size=22, weight=500)
        count(ctx, t, 50 + ctx.measure(TITLE, size=22, weight=500) + 20, 39, [(-1e9, 3), (c_d, 2), (b_del, 1)], size=18)
        chip(ctx, 1870, 30, size=18)
        for j in range(N):
            top = tops[j]
            h = (tops[j - 1] if j else foot) - top
            a = (1 - prog(t, c_s(j), c_s(j) + 0.12)) * clamp(h / STB)
            if h < 3 or a <= 0:
                continue
            gone(ctx, x_av, top + h / 2, 8, alpha=a)
            ctx.text(STUB, XT, top + h / 2 + 6, size=18, color='mute', alpha=a)
        hd = tops[N - 1] - done
        ad = (1 - prog(t, c_d, c_d + 0.12)) * clamp(hd / DN)
        if hd > 3 and ad > 0:
            yc = done + hd / 2
            s = f'{text(68)} {text(69)}'
            sel = prog(t, c_d - 0.14, c_d - 0.06) * ad
            ctx.rrect(MX - 10, yc - DN / 2 + 4, ctx.measure(s, size=26, font='serif') + 86, DN - 8, 12, fill='raised', stroke='sub', alpha=sel)
            spark(ctx, x_av, yc, 10, alpha=0.5 * ad)
            ctx.circle(x_av, yc, 13, color='me', alpha=0.5 * ad, width=2)
            ctx.text(s, XT, yc + 9, size=26, font='serif', color='me', alpha=0.45 * ad)
        hb = done - bubble
        ab = (1 - prog(t, b_del + 0.02, b_del + 0.16)) * clamp(hb / BBLK)
        if hb > 3 and ab > 0:
            bw = ctx.measure(BRB, size=26) + 50
            x, y = XR - bw, bubble
            sel = prog(t, b_sel, b_sel + 0.1) * (1 if t < b_del + 0.02 else 0)
            ctx.rrect(x, y, bw, BBH, 22, fill='raised', alpha=ab, shadow=0.4)
            ctx.text(BRB, x + 25, y + 38, size=26, color='text', alpha=ab)
            ctx.text(BRB_AT, XR - 4, y + BBH + 24, size=17, weight=500, color='sub', alpha=0.85 * ab, align='right')
            cross = prog(t, b_del - 0.02, b_del + 0.06)
            if cross > 0:
                ctx.line(x + 20, y + 29, x + 20 + (bw - 40) * cross, y + 29, color='sub', alpha=ab, width=2.5)
            ctx.rrect(x - 7, y - 7, bw + 14, BBH + 14, 28, fill=None, stroke='sub', width=2.5, alpha=sel)
            menu(ctx, x - 18, y + BBH / 2, side=-1, size=19, k=prog(t, b_sel + 0.04, b_sel + 0.2) * (1 - prog(t, b_del + 0.06, b_del + 0.16)),
                 press=pulse(t - b_del, 15))
        r1 = f'{text(78)} {text(79)}'
        s, n = said(80, 81, t)
        spark(ctx, x_av, BASE1 - S1 * 0.3, 14)
        ctx.text(r1, XT, BASE1, size=S1, font='serif', color='me', alpha=0.5)
        ctx.text(s[:n], XT, BASE2, size=S2, font='serif', color='me')
        ctx.circle(XT + ctx.measure(s[:n], size=S2, font='serif') + S2 * 0.3, BASE2 - S2 * 0.28, S2 * 0.16, fill=True, color='me',
                   alpha=1 if n < len(s) else 0.6 + 0.4 * math.sin(t * 5))
        composer(ctx, R(COL['x'] + COL['w'] / 2 - 470, 548, 940, 76), placeholder=HOLD, t=t, send='idle')

    # ---------------------------------------------------------------- alone-eye
    e_pick, e_press = Bt(270.5), Bt(271)
    PICK = (3, 7)
    EB = {'y': 470, 'h': 150}

    def eye(ctx, t, f, u):
        age = t - LAST
        s81 = text(81)
        ctx.rect(-10, -10, 1940, 660, fill=True, color='panel')
        if age < 0:
            ctx.text(s81, XT, BASE2, size=S2, font='serif', color='me')
            ctx.circle(XT + ctx.measure(s81, size=S2, font='serif') + S2 * 0.3, BASE2 - S2 * 0.28, S2 * 0.16, fill=True, color='me',
                       alpha=0.6 + 0.4 * math.sin(t * 5))
            return
        sx, sy = shake(t, 4 * pulse(age, 9))
        with ctx.at(sx, sy):
            ctx.image('f_eye', 0, -569, 1920, 1920, variant='grey', flip=True)
            ctx.rect(0, EB['y'], 1920, EB['h'], fill=True, color='panel')
            ctx.line(0, EB['y'], 1920, EB['y'], color='line', width=2)
            ctx.line(0, EB['y'] + EB['h'], 1920, EB['y'] + EB['h'], color='line', width=2)
            kw = text(82)
            size = ctx.fit(kw, 1780, font='serif', weight=900, max_size=150)
            o = dict(size=size, weight=900, font='serif')
            x0 = 960 - ctx.measure(kw, **o) / 2
            yb = EB['y'] + EB['h'] - 26

            def col(i):
                w = ctx.measure(kw[i], **o)
                return x0 + ctx.measure(kw[:i + 1], **o) - w, w
            a = min(PICK[0], len(kw) - 1)
            z = min(PICK[1], len(kw) - 1)
            fall = t - e_press
            land = ease_out(prog(age, 0, 0.07))
            sx0 = col(a)[0] - 6
            sx1 = col(z)[0] + col(z)[1] + 6
            top = yb - size * 0.76
            sel = prog(t, e_pick, e_pick + 0.1) * (1 - prog(t, e_press + 0.06, e_press + 0.18))
            ctx.rrect(sx0, top, sx1 - sx0, size * 0.92, 10, fill='raised', alpha=sel)
            for i, ch in enumerate(kw):
                lx, w = col(i)
                cx = lx + w / 2
                if a <= i <= z and fall >= 0:
                    q = max(0.0, fall - 0.014 * (i - a))
                    dy = 4600 * q * q
                    if dy < 300:
                        with ctx.at(cx, yb + dy, rot=(i - (a + z) / 2) * 0.9 * q):
                            ctx.text(ch, 0, 0, align='center', color='sub', **o)
                elif ch != ' ':
                    with ctx.at(cx, yb, scale=1.08 - 0.08 * land):
                        ctx.text(ch, 0, 0, align='center', color='text', **o)
            ctx.rrect(sx0, top, sx1 - sx0, size * 0.92, 10, fill=None, stroke='sub', width=3, alpha=sel)
            menu(ctx, (sx0 + sx1) / 2, top - 6, up=True, size=22, k=prog(t, e_pick + 0.03, e_pick + 0.16),
                 press=max(pulse(t - e_press, 14), pulse(t - END, 14)))

    return {
        'alone-erase': {'render': erase, 'palette': 'off', 'camera': erase_cam},
        'alone-empty': {'render': empty, 'palette': 'off', 'camera': empty_cam},
        'alone-eye': {'render': eye, 'palette': 'off'},
    }
