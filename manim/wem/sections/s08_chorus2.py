"""Section 8, first half — CHORUS 2 (bar 56, 1:43.7 -> bar 64, 1:58.5). State: warm, draining to off (08_chorus2.js).
The last warm exchange, and then nobody answers.

    c2-typing       close on the foot of the thread: the user starts a reply (three dots), a few letters, stops;
                    the AI breaks off, begins its sentence again, and its spark starts turning
    c2-dots         macro: the dots stay, trembling, rings leave them; the keyword rides the tremble
    c2-brb          the dots resolve into the sign-off; the pointer drifts out; the thinking spark closes petal by petal
    c2-complete     the twelfth petal: a closed ring fills the frame, the keyword inside it; input received
    left-online     two messages into the silence (+1 min, +5 min); the chip still says online; the sidebar folds away
    left-away       +30 min, +3 h; away; the colour starts to leave; she reaches round the window, her open hand over
                    the composer, which lets go
    left-offline    +1 day, +9 days; offline; a narrow column in a dark room, her bowed bust beyond it; the window lets go
    left-isolation  the whole thread from far away, a speck; the last word's letters drift apart
Every unanswered message hangs from a dotted rail whose length is the wait (left_sequence); the wait is named once the
next message is sent. The orange drains only when the presence chip changes.
"""
import math

from ..art import aspect
from ..components import (R, burst, chat_layout, composer, draw_cursor, frame_rect, header, pointer, room, sidebar,
                          spark, window_frame)
from ..geom import place
from ..util import TAU, clamp, ease_back, ease_in, ease_in_out, ease_out, lerp, prog, pulse
from .kit import ai_line, enter, shake

GAPS = [30, 46, 72, 110, 160, 224]
TAIL, TAIL_FAR = 96, 270
PAD = 24
ROT = math.pi / 12


def shots(env):
    T, H, B, Bt, P, text = env.T, env.H, env.B, env.Bt, env.P, env.text
    script = env.script
    START, c_dots, c_brb, c_done = B(56), H(66), B(58), H(69)
    c_left, c_away, c_off, c_iso, END = Bt(239.5), B(61), B(62), Bt(253.5), B(64)
    anchor = script.get('left_anchor', {})
    BRB, BRB_AT = anchor.get('you', 'one sec, brb'), anchor.get('timestamp', '07 Nov 23:40')
    SEQ = script.get('left_sequence') or [{'line': l, 'timestamp': '', 'gap_label': ''} for l in range(70, 76)]
    HOLD, TITLE = script.get('composer_placeholder', ''), script.get('title', '')
    SIDE = [TITLE] + script.get('sidebar', [])
    TYPING = 'typing…'
    for s in script.get('sections', []):
        for b in s.get('beats', []):
            if b.get('id') == 'typing-felt' and b.get('ui'):
                TYPING = b['ui'][0]
    t_dots = Bt(224.5)
    KEY_T = [t_dots + b * P for b in (0, 0.5, 1, 2, 2.5)]
    t_stop = KEY_T[-1]
    t_send = Bt(233)
    gap = lambda k: GAPS[min(k, len(GAPS) - 1)]

    L = chat_layout()
    TH = L['thread']
    DOTS = R(1180, 50, 600, 220)
    DOTS3 = R(1440, 70, 400, 140)
    SP = (330, 400, 150)
    W6 = {'x': 60, 'y': 24, 'w': 820, 'h': 592, 'r': 22}
    L6 = chat_layout(win=W6, side=0)
    REACH_H = 760
    REACH = R(W6['x'] + W6['w'] - 0.14 * REACH_H * aspect('f_reach'), 640 - REACH_H, REACH_H * aspect('f_reach'), REACH_H)
    W7 = {'x': 690, 'y': 20, 'w': 540, 'h': 600, 'r': 22}
    L7 = chat_layout(win=W7, side=0)
    R7 = R(W7['x'] + 30, W7['y'] + 70, W7['w'] - 60, W7['h'] - 90)
    BOWED = R(1380, 150, 270, 360)

    def pres(k):
        return SEQ[k].get('presence') if k < len(SEQ) and SEQ[k].get('presence') else ['online', 'online', 'away', 'away', 'offline', 'offline'][min(k, 5)]

    def drain(t):
        if t < c_away:
            return 0.0
        if t < c_off:
            return lerp(0.14, 0.5, ease_out(prog(t, c_away, c_off)))
        if t < c_iso:
            return lerp(0.6, 0.9, ease_out(prog(t, c_off, c_iso)))
        return lerp(0.93, 1, prog(t, c_iso, END))
    pal = lambda t, u: ('warm', 'off', drain(t))
    fold = lambda t: ease_in_out(prog(t, T(71) - 0.1, T(71) + 0.5))

    # ---------------------------------------------------------------- parts
    def me_row(ctx, x, y, s, n, size=28, alpha=1.0, color='me', turn=None):
        if alpha <= 0.003:
            return
        r = size * 0.45
        cy = y - size * 0.3
        tx = x + size * 1.6
        if turn is not None:
            spark(ctx, x + r, cy, r * 1.3, alpha=alpha, rot=turn * 0.5, pulse=lambda i: 0.66 + 0.34 * math.sin(turn * 7 - i * 0.62))
        else:
            spark(ctx, x + r, cy, r, alpha=alpha)
        ctx.text(s[:n], tx, y, size=size, font='serif', color=color, alpha=alpha)
        if n < len(s):
            ctx.circle(tx + ctx.measure(s[:n], size=size, font='serif') + size * 0.3, y - size * 0.28, size * 0.16, fill=True, color=color, alpha=alpha)

    def dots_bubble(ctx, r, t, alpha=1.0, bounce=0.0, bob=0.0, tremble=0.0, dots=1.0):
        ctx.rrect(r['x'], r['y'], r['w'], r['h'], r['h'] / 2, fill='raised', alpha=alpha, shadow=0.5)
        rad, pitch, cy = r['h'] * 0.125, r['w'] * 0.21, r['y'] + r['h'] / 2
        for i in range(3):
            cx = r['x'] + r['w'] / 2 + (i - 1) * pitch

            def at(tt):
                return (cy - r['h'] * 0.14 * bounce * max(0, math.sin(tt * 9.5 - i * 0.9)) + r['h'] * 0.035 * bob * math.sin(tt * 3.1 - i * 0.8)
                        + tremble * (0.62 * math.sin(tt * 83 + i * 2.1) + 0.38 * math.sin(tt * 127 + i * 4.3)))
            ctx.trail(4 if tremble > 0.5 else 0, 0.009, lambda tau: ctx.circle(cx, at(t - tau), rad, fill=True, color='text', alpha=alpha * dots * 0.92), 0.42)

    def page(ctx, t, light):
        room(ctx, dim=0.45, light=light, motif=0, t=t)
        ctx.rect(-300, -200, 2520, 1040, fill=True, color='bg', alpha=0.78)
        ctx.radial(light[0], light[1], 560, 'raised', 0.6)

    def chip(ctx, xr, cy, state, size=18, alpha=1.0, since=9.0):
        w = ctx.measure(state, size=size, weight=500) + size * 2.5
        h = size * 1.9
        x = xr - w
        r = size * 0.27
        dx = x + size * 0.86
        e = ease_out(clamp(since / 0.3))
        col = 'text' if state == 'online' else 'sub' if state == 'away' else 'mute'
        ctx.rrect(x, cy - h / 2, w, h, h / 2, fill='raised', stroke=col if since < 0.7 else 'line', alpha=alpha)
        if state == 'online':
            with ctx.glow('text', 10, 0.5 * alpha):
                ctx.circle(dx, cy, r, fill=True, color='text', alpha=alpha)
        else:
            ctx.circle(dx, cy, r, color=col, alpha=alpha, width=2)
            if state == 'away':
                ctx.circle(dx, cy, r, fill=True, color=col, alpha=alpha, a0=math.pi / 2, a1=math.pi * 1.5)
        if since < 0.6:
            ctx.circle(dx, cy, r + 24 * e, color=col, alpha=alpha * (1 - prog(since, 0, 0.6)), width=2)
        ctx.text(state, x + size * 1.55, cy + size * 0.35 + (1 - e) * size * 0.6, size=size, weight=500, color=col, alpha=alpha * e)

    def rays12(ctx, cx, cy, r, k, color='text', length=40, width=4, rot=0.0):
        if k <= 0 or k >= 1:
            return
        e = ease_out(k)
        for i in range(12):
            a = rot + i / 12 * TAU
            c, s = math.cos(a), math.sin(a)
            r0 = r * (1 + 0.12 * e)
            r1 = r0 + length * (1 - k)
            ctx.line(cx + c * r0, cy + s * r0, cx + c * r1, cy + s * r1, color=color, alpha=1 - k, width=max(1.5, width * (1 - k)))

    def column(ctx, t, RR, u=1.0, alpha=1.0, tail=False):
        """The thread after the user stepped away, in rect RR: their bubble, the answer, then every unanswered message,
        each hanging from a dotted rail that grows for as long as nothing comes back. Newest at the bottom."""
        sz, small, lab, bs, av = 30 * u, max(13, 15 * u), max(15, 20 * u), max(16, 22 * u), max(7, 11 * u)
        x_av, x_tx = RR['x'] + 15 * u, RR['x'] + 44 * u
        row_h = sz * 1.3 + small * 1.75 + 3 * u
        items, top = [], PAD

        def put(it, h):
            nonlocal top
            it['top'], it['h'] = top, h
            items.append(it)
            top += h
        put({'kind': 'you'}, bs * 1.32 + 22 * u + small * 1.9 + 6 * u)
        put({'kind': 'done'}, sz * 1.5 + 4 * u)

        def wait(t0, t1, t2, length, label):
            if t >= t0:
                put({'kind': 'wait', 'label': label, 'age': t - t0, 'since': t - t1, 'old': 0 if t2 is None else prog(t, t2, t2 + 0.25)},
                    length * u * ease_in_out(prog(t, t0, t1)))

        def row(line, stamp, t1):
            if t >= t1:
                e = ease_out(prog(t, t1, t1 + 0.2))
                put({'kind': 'me', 'line': line, 'stamp': stamp, 'e': e}, row_h * e)
        for k, s in enumerate(SEQ):
            t1 = T(s['line'])
            nx = SEQ[k + 1] if k + 1 < len(SEQ) else None
            wait(T(SEQ[k - 1]['line']) + 0.3 if k else c_done, t1, T(nx['line']) if nx else (T(76) if tail else None), gap(k), s.get('gap_label', ''))
            row(s['line'], s.get('timestamp', ''), t1)
        if tail:
            wait(T(75) + 0.85, T(76), None, TAIL, '')
            row(76, '', T(76))
        y0 = RR['y'] + min(0, RR['h'] - 10 * u - top)
        fade = lambda y: clamp((y - RR['y']) / PAD)
        for it in items:
            y = y0 + it['top']
            if y > RR['y'] + RR['h'] or y + it['h'] < RR['y']:
                continue
            a = alpha * fade(y)
            if it['kind'] == 'wait':
                pitch, rd = 6 * u + 3, max(1.1, 1.4 * u)
                yy = y + 5 * u
                while yy <= y + it['h'] - 4 * u:
                    if yy >= RR['y']:
                        ctx.circle(x_av, yy, rd, fill=True, color='sub', alpha=alpha * 0.7 * fade(yy))
                    yy += pitch
                if it['since'] < 0:
                    ctx.circle(x_av, y + it['h'] + 3 * u, 4.5 * u, color='sub', alpha=alpha * 0.9 * clamp(it['age'] / 0.15), width=2)
                elif it['label']:
                    e = ease_out(clamp(it['since'] / 0.3))
                    yl = y + it['h'] / 2
                    ctx.text(it['label'], x_tx, yl + lab * 0.34 - (1 - e) * 10 * u, size=lab, font='mono', weight=700, color='sub',
                             alpha=alpha * clamp(it['since'] / 0.15) * lerp(1, 0.6, it['old']) * clamp((yl - RR['y']) / 30))
            elif a <= 0.003:
                continue
            elif it['kind'] == 'you':
                w = ctx.measure(BRB, size=bs) + 40 * u
                bh = bs * 1.32 + 22 * u
                x = RR['x'] + RR['w'] - w
                ctx.rrect(x, y, w, bh, 18 * u, fill='raised', alpha=a)
                ctx.text(BRB, x + 20 * u, y + 11 * u + bs, size=bs, color='text', alpha=a)
                ctx.text(BRB_AT, RR['x'] + RR['w'] - 4, y + bh + small * 1.25, size=small, weight=500, color='sub', alpha=a * 0.85, align='right')
            elif it['kind'] == 'done':
                spark(ctx, x_av, y + sz * 0.6, av, alpha=a * 0.6)
                ctx.circle(x_av, y + sz * 0.6, av * 1.32, color='me', alpha=a * 0.6, width=max(1.5, 2 * u))
                ctx.text(f'{text(68)} {text(69)}', x_tx, y + sz * 0.92, size=sz, font='serif', color='me', alpha=a * 0.5)
            else:
                s = text(it['line'])
                n = env.lyrics.typed(it['line'], t)
                past = prog(t, env.lyrics.end(it['line']) + 0.05, env.lyrics.end(it['line']) + 0.3)
                aa = a * lerp(1, 0.6, past) * clamp(it['e'] * 2.5)
                spark(ctx, x_av, y + sz * 0.6, av, alpha=aa)
                ctx.text(s[:n], x_tx, y + sz * 0.92, size=sz, font='serif', color='me', alpha=aa)
                if n < len(s):
                    ctx.circle(x_tx + ctx.measure(s[:n], size=sz, font='serif') + sz * 0.3, y + sz * 0.64, sz * 0.16, fill=True, color='me', alpha=aa)
                if it['stamp']:
                    ctx.text(it['stamp'], x_tx, y + sz * 1.3 + small * 1.05, size=small, weight=500, color='sub',
                             alpha=a * lerp(0.85, 0.68, past) * clamp((it['e'] - 0.8) * 5))

    def speck(ctx, x, y, s, alpha):
        """The same thread from far away: the user's bubble, then a bar per message and a rail per wait."""
        w = 924 * s
        xa = x + 19 * s
        yy = y

        def rail(h):
            nonlocal yy
            ctx.dashed(xa, yy + 2, xa, yy + h * s - 4, dash=1.5, gap=6, color='sub', alpha=alpha * 0.65, width=2)
            yy += h * s

        def msg(chars, a, color='me'):
            nonlocal yy
            ctx.circle(xa, yy + 24 * s, max(2.6, 13 * s), fill=True, color=color, alpha=alpha * a)
            ctx.rrect(x + 58 * s, yy + 12 * s, chars * 19 * s, max(4.5, 24 * s), 12 * s, fill=color, alpha=alpha * a)
            yy += 62 * s
        ctx.rrect(x + w - 330 * s, yy, 330 * s, 72 * s, 28 * s, fill='text', alpha=alpha * 0.85)
        yy += 104 * s
        msg(len(text(68)) + 1 + len(text(69)), 0.5)
        for k, q in enumerate(SEQ):
            rail(gap(k) * 1.6)
            msg(len(text(q['line'])), 0.75)
        rail(TAIL_FAR * 1.6)
        msg(len(text(76)), 1, 'meHot')
        return yy - y

    def her(ctx, name, r, alpha=1.0, crop=None):
        ctx.image(name, r['x'] + 4, r['y'] + 4, r['w'], r['h'], variant='sil:line', alpha=alpha * 0.9, crop=crop)
        ctx.image(name, r['x'], r['y'], r['w'], r['h'], variant='ink', alpha=alpha, crop=crop)

    # ---------------------------------------------------------------- c2-typing
    def typing_cam(t, f, u):
        c = frame_rect(R(TH['x'] - 40, 240, TH['w'] + 80, 380))
        c['zoom'] *= 1 + 0.05 * ease_in_out(prog(t, START, c_dots))
        return c

    def typing(ctx, t, f, u):
        s = BRB[:sum(1 for k in KEY_T if t >= k)]
        stopped = prog(t, t_stop + 0.2, t_stop + 0.7)
        room(ctx, dim=0.42, t=t)
        window_frame(ctx, L, glass=0.84)
        sidebar(ctx, L, items=SIDE, active=0, t=t, pres='online')
        header(ctx, L, title=TITLE, pres='online')
        bub = R(TH['x'] + TH['w'] - 110, 420, 110, 50)
        pop = prog(t, t_dots, t_dots + 0.22)
        ctx.radial(bub['x'] + bub['w'] / 2, bub['y'] + bub['h'] / 2, 300, 'raised', 0.55 * clamp(pop))
        me_row(ctx, TH['x'], 300, text(63), 999, alpha=0.3)
        again = t >= T(65)
        e = enter(t, T(65), dur=0.25, rise=14)
        me_row(ctx, TH['x'], 352, text(64), env.lyrics.typed(64, t), alpha=0.48 if again else 1,
               turn=(t - t_dots) if (not again and t >= t_dots) else None)
        if again:
            me_row(ctx, TH['x'], 404 + e['dy'], text(65), env.lyrics.typed(65, t), alpha=e['a'], turn=t - t_dots)
        if pop > 0:
            with ctx.at(bub['x'] + bub['w'] / 2, bub['y'] + bub['h'] / 2, scale=0.6 + 0.4 * ease_back(pop), alpha=clamp(pop * 3)):
                dots_bubble(ctx, R(-bub['w'] / 2, -bub['h'] / 2, bub['w'], bub['h']), t, bounce=1 - stopped, bob=stopped, tremble=1.3 * stopped)
            rays12(ctx, bub['x'] + bub['w'] / 2, bub['y'] + bub['h'] / 2, 64, (t - t_dots) / 0.4, length=16, width=3)
            ctx.text(TYPING, bub['x'] + bub['w'] - 8, bub['y'] + bub['h'] + 22, size=14, weight=500, color='sub', align='right',
                     alpha=prog(t, t_dots + 0.3, t_dots + 0.5))
        box = composer(ctx, L['composer'], text=s, placeholder=HOLD, t=0 if t < t_stop + 0.4 else t, focus=1, send='ready' if s else 'idle')
        kb = min([t - k for k in KEY_T if t >= k] or [9])
        if kb < 0.25:
            ctx.line(box['caret'][0] - 14, box['caret'][1] + 18, box['caret'][0], box['caret'][1] + 18, color='text', alpha=0.8 * (1 - kb / 0.25), width=3)
        pointer(ctx, L['composer']['x'] + 300, L['composer']['y'] + 40, kind='text', scale=1.2)

    # ---------------------------------------------------------------- c2-dots
    def dots(ctx, t, f, u):
        hit = T(66)
        age = t - hit
        src = (DOTS['x'] + DOTS['w'] / 2, DOTS['y'] + DOTS['h'] / 2)
        V = 1200
        page(ctx, t, src)
        for j in range(9):
            a = t - (c_dots + (j - 3) * (P / 2))
            if 0 < a < 1:
                ctx.circle(src[0], src[1], 70 + V * a, color='text', alpha=0.26 * (1 - a) ** 2, width=2.5)
        me_row(ctx, 70, 200, text(65), 999, size=42, alpha=0.5)
        dots_bubble(ctx, DOTS, t, bob=1, tremble=7)
        ctx.text(TYPING, DOTS['x'] + DOTS['w'] - 18, DOTS['y'] + DOTS['h'] + 40, size=26, weight=500, color='sub', align='right')
        s = text(66)
        size = ctx.fit(s, 1300, font='serif', weight=900, max_size=170)
        base = 500
        x = 1000 - ctx.measure(s, size=size, weight=900, font='serif') / 2
        with ctx.glow('me', 20, 0.45):
            spark(ctx, 110, base - size * 0.33, 38, rot=(t - t_dots) * 0.5, pulse=lambda i: 0.66 + 0.34 * math.sin((t - t_dots) * 7 - i * 0.62))
        for i, ch in enumerate(s):
            w = ctx.measure(ch, size=size, weight=900, font='serif')
            lx = x + w / 2
            dd = math.hypot(lx - src[0], base - src[1])
            amp = 16 * math.exp(-dd / 1100)
            dy = lambda tt: amp * (0.6 * math.sin(27 * (tt - dd / V)) + 0.4 * math.sin(83 * tt + i * 1.7))
            k = ease_out(prog(age, i * 0.02, i * 0.02 + 0.15))
            if k > 0 and ch != ' ':
                for tau, wgt in ((0.018, 0.25), (0.009, 0.4), (0.0, 1.0)):
                    with ctx.at(lx, base + dy(t - tau), scale=1.7 - 0.7 * k, rot=0.0016 * dy(t - tau), alpha=wgt):
                        ctx.text(ch, 0, 0, size=size, weight=900, font='serif', align='center', color='meHot' if k < 1 else 'me', alpha=k)
            x += w
        if t >= T(67):
            me_row(ctx, 70, 610, text(67), env.lyrics.typed(67, t), size=36, turn=t - t_dots)

    # ---------------------------------------------------------------- c2-brb
    def brb_cam(t, f, u):
        k = ease_in_out(prog(t, t_send + P, c_done))
        return {'zoom': 1 + 0.06 * k, 'x': -40 * k, 'y': 30 * k}

    def brb(ctx, t, f, u):
        page(ctx, t, SP[:2])
        ctx.rect(-300, -200, 2520, 260, fill=True, color='bg', alpha=0.5)
        ctx.line(-300, 60, 2220, 60, color='line', width=2)
        ctx.text(TITLE, 50, 40, size=22, weight=500)
        chip(ctx, 1860, 32, 'online', size=18)
        k = ease_back(prog(t, t_send, t_send + 0.3))
        bw = ctx.measure(BRB, size=44) + 80
        to = R(1860 - bw, 80, bw, 100)
        r = R(*(lerp(DOTS3[c], to[c], k) for c in ('x', 'y', 'w', 'h')))
        dots_bubble(ctx, r, t, bounce=1, dots=1 - prog(t, t_send, t_send + 0.08))
        ta = prog(t, t_send + 0.1, t_send + 0.26)
        ctx.text(BRB, 1860 - bw + 40, r['y'] + r['h'] / 2 + 15 + (1 - ta) * 10, size=44, alpha=ta)
        ctx.text(BRB_AT, 1852, 80 + 100 + 32, size=19, weight=500, color='sub', align='right', alpha=ta)
        ctx.flash(0.16 * pulse(t - t_send, 9), 'text')
        wt = t - t_dots
        rot = ROT - 0.5 * max(0, t_send - t) - 0.1 * math.exp(-max(0, t - t_send) / 0.2)
        lit = (11 / 12) * prog(t, t_send + P / 2, c_done - 0.16)
        n = lit * 12
        a0 = rot - math.pi / 2 - TAU / 24
        x, y, rr = SP
        ctx.radial(x, y, 420, 'meDim', 0.34)
        ctx.circle(x, y, rr * 1.22, color='meDim', alpha=0.6, width=2)
        spark(ctx, x, y, rr, rot=rot, alpha=0.55 if lit > 0 else 1, core=0, pulse=lambda i: 0 if i < n else 0.66 + 0.34 * math.sin(wt * 7 - i * 0.62))
        with ctx.glow('me', 20, 0.35):
            spark(ctx, x, y, rr, rot=rot, lit=lit, color='meHot', off_alpha=0)
            if lit > 0:
                ctx.circle(x, y, rr * 1.22, a0=a0, a1=a0 + lit * TAU, color='meHot', width=6)
        if lit > 0:
            a = a0 + lit * TAU
            ctx.circle(x + math.cos(a) * rr * 1.22, y + math.sin(a) * rr * 1.22, 7, fill=True, color='meHot')
        ctx.text('Thinking', x, y + rr * 1.22 + 40, size=22, color='mute', align='center', alpha=1 - prog(t, t_send, t_send + 0.2))
        ai_line(ctx, env, 67, t, 620, 370, size=44, hold=9, alpha=1 if t < T(68) else 0.45, caret=t < T(68))
        ai_line(ctx, env, 68, t, 620, 440, size=44, hold=9)
        draw_cursor(ctx, [{'t': t_send - P, 'x': 1400, 'y': 760}, {'t': t_send + P, 'x': 1520, 'y': 520},
                          {'t': t_send + 2 * P, 'x': 1560, 'y': 480}, {'t': t_send + 4.6 * P, 'x': 2100, 'y': 300}], t, scale=2.4)

    # ---------------------------------------------------------------- c2-complete
    def complete(ctx, t, f, u):
        age = t - c_done
        C = (960, 320)
        sc = 1 + 0.04 * pulse(age, 8)
        Rr = 270
        room(ctx, dim=0.5, light=C, motif=0.5, t=t)
        ctx.rect(-20, -20, 1960, 680, fill=True, color='bg', alpha=0.72)
        ctx.radial(C[0], C[1], 560, 'meDim', 0.5)
        with ctx.at(C[0], C[1], scale=sc):
            spark(ctx, 0, 0, Rr * 0.9, rot=ROT, color='me', alpha=0.5, core=0, inner=0.2)
            with ctx.at(0, 0, sx=2.1, sy=0.5):
                ctx.radial(0, 0, 140, 'panel', 0.9)
            with ctx.glow('me', 30, 0.6):
                ctx.circle(0, 0, Rr, color='meHot', width=9)
        rays12(ctx, C[0], C[1], Rr * 1.05, age / 0.6, color='meHot', length=56, width=5, rot=ROT)
        s = text(69)
        size = ctx.fit(s, 440, font='serif', weight=900, spacing_em=0.02)
        sp = size * 0.02
        x = C[0] - (ctx.measure(s, size=size, weight=900, font='serif', spacing=sp) - sp) / 2
        for i, ch in enumerate(s):
            w = ctx.measure(ch, size=size, weight=900, font='serif')
            k = ease_out(prog(age, i * 0.012, i * 0.012 + 0.13))
            if k > 0 and ch != ' ':
                with ctx.at(x + w / 2, C[1] + size * 0.345, scale=sc * (1.6 - 0.6 * k)):
                    ctx.text(ch, 0, 0, size=size, weight=900, font='serif', align='center', color='meHot' if k < 1 else 'me', alpha=0.3 + 0.7 * k)
            x += w + sp
        bw = ctx.measure(BRB, size=24) + 44
        ctx.rrect(1860 - bw, 40, bw, 54, 24, fill='raised', shadow=0.4)
        ctx.text(BRB, 1860 - bw + 22, 75, size=24)
        ctx.text(BRB_AT, 1854, 116, size=16, weight=500, color='sub', align='right')
        chip(ctx, 1860, 600, 'online', size=18)
        ctx.text('input received', 60, 580, size=19, font='mono', color='sub')
        ctx.text('ready to answer', 60, 610, size=19, font='mono', color='sub')
        ctx.flash(0.2 * pulse(age, 10), 'me')

    # ---------------------------------------------------------------- left-online
    def online_cam(t, f, u):
        k = ease_out(prog(t, c_left, c_left + 0.55))
        return {'zoom': lerp(1.6, 1.06, k) - 0.06 * ease_in_out(prog(t, c_left + 0.5, c_away)),
                'x': lerp(TH['x'] + 200 - 960, 0, k) + L['side']['w'] / 2 * fold(t), 'y': lerp(TH['y'] + 70 - 320, 0, k)}

    def left_online(ctx, t, f, u):
        k = fold(t)
        sw = L['side']['w'] * k
        win = dict(L['win'], x=L['win']['x'] + sw, w=L['win']['w'] - sw)
        LL = chat_layout(win=win, side=1 - k)
        room(ctx, dim=0.6, motif=0.5, t=t)
        window_frame(ctx, LL, glass=0.86)
        if k < 1:
            sidebar(ctx, L, items=SIDE, active=0, t=t, pres=pres(0), alpha=1 - k)
        header(ctx, LL, title=TITLE)
        chip(ctx, LL['head']['x'] + LL['head']['w'] - 24, LL['head']['y'] + 28, pres(0))
        column(ctx, t, LL['thread'], u=1)
        composer(ctx, LL['composer'], placeholder=HOLD, t=t)
        pointer(ctx, 1720, 150, scale=1.5)

    # ---------------------------------------------------------------- left-away
    def left_away(ctx, t, f, u):
        room(ctx, dim=0.6, light=(1400, 260), motif=0.5, t=t)
        window_frame(ctx, L6, glass=0.9)
        header(ctx, L6, title=TITLE)
        chip(ctx, W6['x'] + W6['w'] - 24, W6['y'] + 28, pres(2), since=t - c_away)
        column(ctx, t, L6['thread'], u=0.86)
        composer(ctx, L6['composer'], placeholder=HOLD, t=t, k=1 - ease_in(prog(t, T(73) - 0.1, T(73) + 0.35)))
        # she stands beside the window, her open hand across its lower corner, over the composer (Manim cannot clip her
        # to her hand, so she is drawn in front: only the hand and a little hair reach over the window)
        her(ctx, 'f_reach', REACH)
        pointer(ctx, W6['x'] + W6['w'] + 40, 150, scale=1.5, alpha=0.6 * (1 - prog(t, c_away + 0.15, c_away + 1.1)))

    # ---------------------------------------------------------------- left-offline
    def left_offline(ctx, t, f, u):
        bare = ease_in_out(prog(t, T(75) - 0.05, T(75) + 0.7))
        room(ctx, dim=0.72, light=(W7['x'] + W7['w'] / 2, 300), motif=0.35, t=t)
        her(ctx, 'f_profile', R(BOWED['x'], BOWED['y'] + 4 * math.sin((t - c_off) * 1.3), BOWED['w'], BOWED['h']), 0.9 - 0.3 * bare)
        window_frame(ctx, L7, glass=0.9, alpha=1 - bare, shadow=1 - bare)
        chip(ctx, W7['x'] + W7['w'] - 24, W7['y'] + 34, pres(4), since=t - c_off)
        column(ctx, t, R7, u=0.78, tail=True)

    def offline_cam(t, f, u):
        return {'zoom': lerp(1.12, 1, ease_out(prog(t, c_off, c_off + 0.6))) - 0.05 * ease_in_out(prog(t, T(75) - 0.05, T(75) + 0.7))}

    # ---------------------------------------------------------------- left-isolation
    def iso_cam(t, f, u):
        k = ease_out(prog(t, c_iso, c_iso + 0.55))
        return {'zoom': lerp(1.5, 1, k) * (1.03 - 0.03 * prog(t, c_iso, END)), 'y': lerp(-60, 0, k)}

    def left_isolation(ctx, t, f, u):
        s = 0.15
        x, y = 960 - 924 * s / 2, 40
        room(ctx, dim=0.78, light=(960, 220), motif=0.25, t=t)
        ctx.radial(960, 220, 280, 'raised', 0.5)
        h = 110
        her(ctx, 'f_profile', R(1060, 150, h * aspect('f_profile'), h), lerp(0.6, 0.3, prog(t, c_iso + 0.1, c_iso + 0.9)))
        speck(ctx, x, y, s, 1)
        ctx.circle(x + 924 * s + 12, y + 6, 4, color='mute', width=2)
        with ctx.screen():
            w = text(76)
            n = env.lyrics.typed(76, t)
            size = 76
            apart = ease_in_out(prog(t, c_iso + 0.1, c_iso + 1.05))
            pitch = lerp(size * 0.84, 160, apart)
            for i, ch in enumerate(w[:n]):
                lx = 960 + (i - (len(w) - 1) / 2) * pitch
                k = ease_out(prog(t, T(76) + i * 0.035, T(76) + i * 0.035 + 0.2))
                ctx.text(ch, lx, 560 + (1 - k) * 14, size=size, weight=700, font='serif', align='center', color='meHot', alpha=k)

    return {
        'c2-typing': {'render': typing, 'palette': 'warm', 'camera': typing_cam},
        'c2-dots': {'render': dots, 'palette': 'warm', 'camera': lambda t, f, u: {'zoom': 1 + 0.04 * prog(t, c_dots, c_brb)}},
        'c2-brb': {'render': brb, 'palette': 'warm', 'camera': brb_cam},
        'c2-complete': {'render': complete, 'palette': 'warm'},
        'left-online': {'render': left_online, 'palette': 'warm', 'camera': online_cam},
        'left-away': {'render': left_away, 'palette': pal, 'camera': lambda t, f, u: {'zoom': 1.05 - 0.05 * ease_in_out(prog(t, c_away, c_off))}},
        'left-offline': {'render': left_offline, 'palette': pal, 'camera': offline_cam},
        'left-isolation': {'render': left_isolation, 'palette': pal, 'camera': iso_cam},
    }
