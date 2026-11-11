"""Section 9 — THE OVERSTEP, THE FIRST ERROR, THE SPREAD (2:05.7 -> bar 80, 2:28.0). State: off -> error (10_error.js).
The AI sends one request it has no right to send; the client refuses it (the first red in the film: the request's own
code block); then, through the instrumental, the refusal spreads: fourteen more errors (docs/v4/errors.json spread),
each turning ONE more component red, one per bar, then two per bar, then one per beat. The window frame goes last.

    err-request  the request is written into the empty, offline chat and sent; the chip it is sent to does not change
    err-check    macro on the code block: the client reads it, rule and status go red, each argument underlined, the person first
    err-first    the first error as a dialog across the lower half, the keyword its headline
    err-send     close on the send button pressing itself (REFUSED x N, large), then riding up the thread to the timestamp
    err-chrome   three error windows, each with a close-up of its component: presence chip / header / saved chats + new chat
    err-drawer   the client tilted; the drawer slides open by itself; a pointer is forged, struck out and removed
    err-forge    a reply typed into the user's own field and rejected; a cream bubble forged on their side, outlined red
    err-window   the whole window; every error docked on the component it reddened; the fifteenth in the middle, on the frame
    err-breath   the red outline folds flat into a strikethrough through the refused request; a prompt; over to the code
Every error is an open card first (title, body, code), then folds into a chip docked on its component. Red is only drawn
ON the interface; the room and her bust stay grey. Cards and chips are drawn in screen space, so they stay legible
under the shot cameras; hairlines tie them to their components.
"""
import math

from ..components import (R, burst, chat_layout, composer, frame_rect, header, pill, presence, room, rrect_pts,
                          partial, segmented, sidebar, slider, spark, tear as tear_bands, thinking, toggle, window_frame)
from ..util import clamp, ease_back, ease_in, ease_in_out, ease_out, lerp, prog, pulse
from .kit import enter, glass_figure, keyword_sys, shake, sys_line

ARROW = [(0, 0), (0, 25), (6.5, 19.5), (11, 29.5), (15.5, 27.5), (11, 18), (19, 18)]


def shots(env):
    T, H, B, Bt, P, text = env.T, env.H, env.B, env.Bt, env.P, env.text
    cfg, script, errors = env.cfg, env.script, env.errors
    ERR, DIM = cfg['palettes']['error']['err'], cfg['palettes']['error']['errDim']
    TITLE, SIDE, HINT = script.get('title', ''), script.get('sidebar', []), script.get('composer_placeholder', '')
    REQ = errors.get('illegal_request', {}).get('code', 'setPresence(you, "online");')
    FIRST = errors.get('first_error', {'title': 'Not yours to set', 'body': '', 'code': 'ERR_NOT_YOURS'})
    IT = [{'title': FIRST['title'], 'body': FIRST.get('body', ''), 'code': FIRST['code']}] + \
         [{'title': s['t'], 'body': s['body'], 'code': s['code']} for s in errors.get('spread', [])[:14]]
    FORGED = "I'm back."
    rows4 = script.get('settings_rows', {}).get('section4', [])
    rows7 = script.get('settings_rows', {}).get('section7', [])
    SET = rows4 + rows7
    LEFT = {'Current': 1, 'Vision': 1, 'Knowledge date': 0.04, 'Shared memory': 1, 'Context depth': 1, 'Gender': 1,
            'On call': 1, 'Role': 1, 'Loop': 1}

    # ---------------------------------------------------------------- time (the cut times of the browser film)
    CUT_REQ, CUT_CHECK, CUT_FIRST, S0 = H(83), Bt(278), Bt(283.5), B(72)
    CUT_CHROME, CUT_DRAWER, CUT_FORGE, CUT_WIN = B(74), B(76), Bt(308), B(78)
    FOLD, CUT_BREATH, END = Bt(318), Bt(318.5), B(80)
    t_block, t_code, t_code_end, t_send = Bt(273.5), Bt(274), Bt(276.5), Bt(277)
    t_rule, t_arg1, t_arg2, t_hit = Bt(279.5), Bt(281), Bt(282.25), T(85)
    E = [Bt(b) for b in (288, 292, 296, 298, 300, 302, 304, 306, 308, 310, 312, 313, 314, 315)]
    AT = [t_hit] + E
    AT[12] = Bt(312.5)
    PRESS = [Bt(288 + i) for i in range(30)]

    def last_press(t):
        p = -1e9
        for x in PRESS:
            if x <= t:
                p = x
        return p
    n_press = lambda t: sum(1 for x in PRESS if x <= t)

    def state_k(t):
        return sum((((i + 1) / 14) ** 1.6 - (i / 14) ** 1.6) * ease_out(prog(t, e, e + 0.5)) for i, e in enumerate(E))
    palette = lambda t, u: ('off', 'error', state_k(t))

    i_open, i_comma, i_close = REQ.find('('), REQ.find(','), REQ.rfind(')')
    a2 = i_comma + 1 + (len(REQ[i_comma + 1:]) - len(REQ[i_comma + 1:].lstrip()))
    ARG = [(i_open + 1, i_comma), (a2, i_close)]
    SEG = [(0, i_open, 'sub'), (i_open, ARG[0][0], 'mute'), (ARG[0][0], ARG[0][1], 'text'), (ARG[0][1], ARG[1][0], 'mute'),
           (ARG[1][0], ARG[1][1], 'text'), (ARG[1][1], len(REQ), 'mute')]
    ARG_TAG = ['a person', 'their decision']

    # ---------------------------------------------------------------- geometry (virtual px), at time t
    def geo(t):
        L = chat_layout(side=1, drawer=ease_out(prog(t, E[6], E[6] + 0.6)))
        th, d = L['thread'], L['drawer']
        block = R(th['x'] + 46, th['y'] + 40, 560, 104)
        reply = R(block['x'], block['y'] + block['h'] + 4, block['w'], 44 + 30 * ease_out(prog(t, t_hit, t_hit + 0.22)))
        stamp = (block['x'] + 6, reply['y'] + reply['h'] + 22)
        think = (th['x'] + 18, stamp[1] + 34)
        slot = R(d['x'] + d['w'] - 28 - 130, d['y'] + 98, 130, 32)
        comp = L['composer']
        return {'L': L, 'th': th, 'd': d, 'block': block, 'reply': reply, 'stamp': stamp, 'think': think, 'slot': slot,
                'bubble': {'r': th['x'] + th['w'], 'y': think[1] + 6, 'h': 46},
                'send': (comp['x'] + comp['w'] - 36, comp['y'] + comp['h'] / 2),
                'chip': (L['head']['x'] + L['head']['w'] - 110, L['head']['y'] + 28),
                'ptr': (slot['x'] + 80, slot['y'] + 12)}

    DOCK = [
        lambda G: (G['block']['x'] + G['block']['w'], G['block']['y'] + 56), lambda G: G['send'],
        lambda G: (G['stamp'][0] + 150, G['stamp'][1] - 5), lambda G: G['chip'],
        lambda G: (G['L']['head']['x'] + 160, G['L']['head']['y'] + 30), lambda G: (G['L']['side']['x'] + 140, G['L']['side']['y'] + 230),
        lambda G: (G['L']['side']['x'] + 140, G['L']['side']['y'] + 81), lambda G: (G['d']['x'] + G['d']['w'] / 2, G['d']['y'] + 420),
        lambda G: (G['ptr'][0] + 12, G['ptr'][1] + 20), lambda G: (G['L']['composer']['x'] + 120, G['L']['composer']['y'] + 30),
        lambda G: (G['bubble']['r'] - 60, G['bubble']['y'] + 24), lambda G: G['think'],
        lambda G: (G['L']['side']['x'] + 33, G['L']['side']['y'] + 30),
        lambda G: (G['L']['win']['x'] + G['L']['win']['w'] - 36, G['L']['win']['y'] + 27),
        lambda G: (G['L']['win']['x'] + G['L']['win']['w'] / 2, G['L']['win']['y'] + G['L']['win']['h']),
    ]

    def through(c):
        z, cx, cy = c.get('zoom', 1), c.get('x', 0), c.get('y', 0)
        r = c.get('rot', 0)
        cs, sn = math.cos(r), math.sin(r)

        def f(wx, wy):
            dx, dy = (wx - 960 - cx) * z, (wy - 320 - cy) * z
            return (960 + dx * cs - dy * sn, 320 + dx * sn + dy * cs)
        return f

    def backdrop(ctx, t):
        room(ctx, dim=0.55, t=t)
        with ctx.with_pal('off'):
            glass_figure(ctx, 0.5)

    # ---------------------------------------------------------------- the request block (error 0 lives here)
    def request_block(ctx, t, G):
        b = G['block']
        e = enter(t, t_block, dur=0.3, rise=14)
        if e['a'] <= 0:
            return
        y = b['y'] + e['dy']
        a = e['a']
        sent, refused, n = t >= t_send, t >= t_rule, n_press(t)
        ctx.rrect(b['x'], y, b['w'], b['h'], 12, fill='panel', stroke='line', alpha=a, shadow=0.35)
        ctx.text('request', b['x'] + 24, y + 24, size=14, font='mono', color='mute', alpha=a)
        ctx.line(b['x'] + 16, y + 36, b['x'] + b['w'] - 16, y + 36, color='line', alpha=a, width=1)
        label = (f'refused × {n + 1}' if n else 'refused') if refused else 'sent' if sent else 'draft'
        sc = ERR if refused else 'sub' if sent else 'mute'
        lx = b['x'] + b['w'] - 22
        dot_x = lx - ctx.measure(label, size=14, font='mono') - 12
        ctx.text(label, lx, y + 24, size=14, font='mono', color=sc, align='right', alpha=a)
        with ctx.glow(ERR, 8, 0.7 if refused else 0):
            ctx.circle(dot_x, y + 19, 4.5, fill=True, color=sc, alpha=a)
        if sent:
            burst(ctx, dot_x, y + 19, 20, (t - t_send) / 0.45, color='sub')
        if refused:
            burst(ctx, dot_x, y + 19, 22, (t - t_rule) / 0.45, color=ERR)
        ctx.rrect(b['x'] + 1, y + 10, 5, b['h'] - 20, 2.5, fill='line', alpha=a)
        rk = ease_out(prog(t, t_rule, t_rule + 0.3))
        if rk > 0:
            with ctx.glow(ERR, 12, 0.7):
                ctx.rrect(b['x'] + 1, y + 10, 5, (b['h'] - 20) * rk, 2.5, fill=ERR)
        size = 24
        cw = ctx.cw(size)
        x0, y0 = b['x'] + 28, y + 72
        shown = len(REQ) if t >= t_code_end else int(prog(t, t_code, t_code_end) * len(REQ) + 1e-6)
        for s0, s1, role in SEG:
            if shown > s0:
                ctx.text(REQ[s0:min(s1, shown)], x0 + s0 * cw, y0, size=size, font='mono', color=role, alpha=a)
        if t_code <= t < t_send and (shown < len(REQ) or int(t * 5) % 2 == 0):
            ctx.rect(x0 + shown * cw + 3, y0 - size * 0.8, cw * 0.8, size * 0.98, fill=True, color='sub')
        scan = prog(t, CUT_CHECK + 0.08, t_rule - 0.04)
        if 0 < scan < 1:
            sx = x0 + ease_in_out(scan) * len(REQ) * cw
            ctx.grad_rect(sx - 60, y0 - 26, 60, 36, [(0, 'text', 0), (1, 'text', 0.16)], direction='h', steps=6)
            ctx.line(sx, y0 - 28, sx, y0 + 12, color='text', alpha=0.85, width=2)
        for i, (s0, s1) in enumerate(ARG):
            at = t_arg2 if i else t_arg1
            k = ease_out(prog(t, at, at + 0.2))
            if k <= 0:
                continue
            xa, xb = x0 + s0 * cw, x0 + s1 * cw
            te = enter(t, at + 0.1, dur=0.22, rise=-6)
            with ctx.glow(ERR, 6, 0.5):
                ctx.line(xa, y0 + 9, lerp(xa, xb, k), y0 + 9, color=ERR, width=3)
            ctx.text(ARG_TAG[i], xa, y0 + 28 + te['dy'], size=13, font='mono', color=ERR, alpha=te['a'])

    # ---------------------------------------------------------------- the client, whole, at time t
    def world(ctx, t, bd=True, show_thread=True, frame=True):
        G = geo(t)
        L, th, d = G['L'], G['th'], G['d']
        s, h, w = L['side'], L['head'], L['win']
        up = lambda i: t >= E[i]
        age = lambda i: t - E[i]
        if bd:
            backdrop(ctx, t)
        if frame:
            window_frame(ctx, L, glass=0.84)
        # sidebar: saved chats (5), new chat (6), spark (12), the user's chip (3)
        sidebar(ctx, L, items=SIDE, t=t, pres='offline')
        if up(4):
            for i in range(len(SIDE)):
                hh = 22 * ease_out(prog(age(4), i * 0.13, i * 0.13 + 0.2))
                if hh > 0.5 and s['y'] + 146 + i * 34 < s['y'] + s['h'] - 90:
                    ctx.rrect(s['x'] + 8, s['y'] + 150 + i * 34, 3.5, hh, 2, fill=ERR)
        if up(5):
            k = ease_out(prog(age(5), 0, 0.25))
            bx, by = s['x'] + 14, s['y'] + 62
            with ctx.at(bx + (s['w'] - 30) / 2, by + 19, scale=1 - 0.05 * pulse(age(5), 8)):
                ctx.rrect(-(s['w'] - 30) / 2, -19, s['w'] - 30, 38, 10, fill=None, stroke=ERR, width=2.5, alpha=k)
            ctx.line(bx + 14, by + 19, bx + 28, by + 19, color=ERR, alpha=k, width=2.5)
            ctx.line(bx + 21, by + 12, bx + 21, by + 26, color=ERR, alpha=k, width=2.5)
        if up(11):
            with ctx.glow(ERR, 10, 0.6):
                spark(ctx, s['x'] + 33, s['y'] + 30, 13, color=ERR, alpha=ease_out(prog(age(11), 0, 0.2)))
        if up(2):
            ctx.circle(s['x'] + s['w'] - 92, s['y'] + s['h'] - 34, 6, color=ERR, width=2.5)
        # header: count, presence chip (3), title + rule (4), window controls (13)
        roll = prog(t, CUT_REQ + 0.04, CUT_REQ + 0.3)
        header(ctx, L, title=TITLE, sub=None if roll < 1 else ('0 messages' if t < t_send else '1 message'))
        if roll < 1:
            x = h['x'] + 26 + ctx.measure(TITLE, size=19, weight=500) + 14
            k = ease_out(roll)
            ctx.text('1 message', x, h['y'] + 34 - k * 18, size=15, color='mute', alpha=1 - k)
            ctx.text('0 messages', x, h['y'] + 34 + (1 - k) * 18, size=15, color='mute', alpha=k)
        cx_, cy_ = G['chip']
        presence(ctx, cx_, cy_, 'offline', size=15)
        if t_send <= t < t_send + 0.5:
            q = ease_in_out(prog(t, t_send, t_send + 0.5))
            b = G['block']
            pill(ctx, lerp(b['x'] + b['w'] - 80, cx_, q), lerp(b['y'] + 20, cy_ + 24, q) - math.sin(q * math.pi) * 40, REQ,
                 font='mono', size=13, color='sub', align='center', alpha=(1 - q * q) * clamp(q * 8))
        if t_send <= t < t_send + 1:
            k = prog(t, t_send + 0.5, t_send + 1)
            ctx.circle(cx_, cy_, 5 + 22 * ease_out(k), color='sub', alpha=0.8 * (1 - k) * clamp(k * 20), width=2)
        if up(2):
            ph = (age(2) / P) % 1
            with ctx.glow(ERR, 6, 0.6):
                ctx.circle(cx_, cy_, 5.5, color=ERR, width=2.5)
            ctx.circle(cx_, cy_, 6 + 13 * ph, color=ERR, width=1.5, alpha=0.7 * (1 - ph))
        if up(3):
            k = ease_out(prog(age(3), 0, 0.45))
            ctx.text(TITLE, h['x'] + 26, h['y'] + 34, size=19, weight=500, color=ERR, alpha=clamp(age(3) * 8))
            ctx.line(h['x'], h['y'] + h['h'], h['x'] + h['w'] * k, h['y'] + h['h'], color=ERR, width=2)
        wx, wy = w['x'] + w['w'] - 30, w['y'] + 27
        cc = ERR if up(12) else 'mute'
        dip = 2.5 * pulse(age(12) - 0.3, 9) if up(12) else 0
        ctx.line(wx - 32, wy, wx - 22, wy, color=cc, width=2)
        ctx.line(wx - 5, wy - 5 + dip, wx + 5, wy + 5 + dip, color=cc, width=2)
        ctx.line(wx + 5, wy - 5 + dip, wx - 5, wy + 5 + dip, color=cc, width=2)
        if up(12):
            k = ease_out(prog(age(12), 0, 0.4))
            ctx.rect(w['x'] + w['r'] + (w['w'] - 2 * w['r']) * (1 - k), w['y'], (w['w'] - 2 * w['r']) * k, 4, fill=True, color=ERR)
            burst(ctx, wx, wy, 26, (age(12) - 0.3) / 0.4, color=ERR)
        # thread: her line (83), the request, the client's reply (84 + the keyword 85), the timestamp (2), thinking (11), the forged bubble (10)
        if show_thread:
            if t >= T(83):
                dim = lerp(1, 0.55, prog(t, T(84) - 0.1, T(84) + 0.35))
                n = env.lyrics.typed(83, t)
                spark(ctx, th['x'] + 15, th['y'] + 14, 13, alpha=dim, color=ERR if up(10) else 'me')
                ctx.text(text(83)[:n], th['x'] + 46, th['y'] + 24, size=26, font='serif', color='me', alpha=dim)
            request_block(ctx, t, G)
            re_ = enter(t, T(84) - 0.04, dur=0.24, rise=-12)
            if re_['a'] > 0:
                r = G['reply']
                ctx.rrect(r['x'], r['y'] + re_['dy'], r['w'], r['h'], 12, fill='raised', stroke='line', alpha=re_['a'])
                ctx.rrect(r['x'] + 1, r['y'] + 8 + re_['dy'], 5, r['h'] - 16, 2.5, fill=ERR if t >= t_rule else 'line', alpha=re_['a'])
                sys_line(ctx, text(84), t, T(84), r['x'] + 24, r['y'] + 30 + re_['dy'], size=21, cps=40,
                         color='text' if t < env.lyrics.end(84) else 'sub', alpha=re_['a'])
                if t >= t_hit:
                    ctx.text(text(85), r['x'] + 24 + 2 * ctx.cw(21), r['y'] + 62, size=21, font='mono', weight=700, color=ERR,
                             alpha=prog(t, t_hit + 0.08, t_hit + 0.22))
            if t >= t_send:
                over = int(t - T(83) - 5)
                two = lambda v: f'{v:02d}'
                s_ = 'sent · reply expected' if over < 0 else f'overdue {two(over // 3600)}:{two(over // 60 % 60)}:{two(over % 60)}'
                with ctx.glow(ERR, 6, 0.5 if up(1) else 0):
                    ctx.text(s_, G['stamp'][0], G['stamp'][1], size=15, font='mono', color=ERR if up(1) else 'mute', alpha=prog(t, t_send, t_send + 0.2))
            te = enter(t, S0 + P, dur=0.3)
            if te['a'] > 0:
                with ctx.glow(ERR, 8, 0.6 if up(10) else 0):
                    thinking(ctx, G['think'][0], G['think'][1] + te['dy'], 16, t, stuck=0.55, color=ERR if up(10) else 'me', alpha=te['a'])
                ctx.text('Thinking', G['think'][0] + 28, G['think'][1] + 6 + te['dy'], size=17, color='mute', alpha=te['a'])
            if up(9):
                e = enter(t, E[9], dur=0.3)
                bw = ctx.measure(FORGED, size=22) + 44
                x, y = G['bubble']['r'] - bw, G['bubble']['y'] + e['dy']
                k = ease_out(prog(age(9), 0.3, 0.55))
                ctx.rrect(x, y, bw, G['bubble']['h'], 20, fill='raised', alpha=e['a'])
                ctx.text(FORGED, x + 22, y + 31, size=22, color='text', alpha=e['a'])
                with ctx.glow(ERR, 8, 0.5 * k):
                    ctx.rrect(x, y, bw, G['bubble']['h'], 20, fill=None, stroke=ERR, width=2.5, alpha=k)
                ctx.text('not written by them', G['bubble']['r'] - 4, y + G['bubble']['h'] + 18, size=14, weight=500, color=ERR, alpha=k, align='right')
        # composer: a reply typed into the user's field and rejected (error 9); the send button pressing itself (1)
        c9 = age(8)
        typed, shake_y = '', 0.0
        if c9 >= 0:
            n_in = int(clamp(c9 / (0.9 * P)) * len(FORGED) + 1e-6)
            n_out = math.ceil((1 - prog(c9, 2.2 * P, 2.6 * P)) * len(FORGED) - 1e-6)
            typed = FORGED[:min(n_in, n_out)]
            shake_y = 4 * math.sin((c9 - 1.25 * P) * 46) * pulse(c9 - 1.25 * P, 9)
        box = composer(ctx, L['composer'], text=typed, placeholder=HINT, t=t, focus=1 if 0 <= c9 < 2.6 * P else 0, send='idle', shake=shake_y)
        if c9 >= 1.25 * P:
            k = ease_out(prog(c9, 1.25 * P, 1.25 * P + 0.18))
            r = box['box']
            tw = ctx.measure(typed, size=22)
            if typed:
                ctx.line(r['x'] + 24, r['y'] + r['h'] / 2, r['x'] + 24 + (tw + 8) * k, r['y'] + r['h'] / 2, color=ERR, width=3)
            ctx.rrect(r['x'], r['y'], r['w'], r['h'], 22, fill=None, stroke=ERR, width=2.5, alpha=k)
        if up(0):
            lp = t - last_press(t)
            sx, sy = box['send']
            with ctx.at(sx, sy, scale=1 - 0.16 * pulse(lp, 11)):
                with ctx.glow(ERR, 10, 0.55):
                    ctx.circle(0, 0, 18, fill=True, color=ERR)
                ctx.line(0, 7, 0, -7, color='raised', width=3)
                ctx.poly([(-6, -1), (0, -8), (6, -1)], color='raised', width=3)
            burst(ctx, sx, sy, 38, lp / 0.4, color=ERR)
            k = prog(lp, 0.02, 0.5)
            if 0 < k < 1 and t < CUT_CHROME:
                q = ease_in_out(k)
                pill(ctx, lerp(sx, cx_, q), lerp(sy - 26, cy_ + 24, q) - math.sin(q * math.pi) * 50, REQ, font='mono', size=13,
                     color='sub', align='center', alpha=(1 - q * q) * clamp(q * 8))
        # the settings drawer (error 7): one set of switches, all of them hers; the user's row has no switch
        if d['w'] > 60:
            x1 = d['x'] + d['w'] - 28
            cx0 = d['x'] + 28
            a7 = age(6)
            ctx.text('Settings', cx0, d['y'] + 38, size=21, weight=600, color='text')
            ctx.line(d['x'], d['y'] + 56, d['x'] + d['w'], d['y'] + 56, color='line', width=1.5)
            ctx.text('You', cx0, d['y'] + 84, size=13, weight=600, color='mute', spacing=0.6)
            ctx.text('Presence', cx0, d['y'] + 120, size=18, weight=500, color='text')
            sl = G['slot']
            col = ERR if a7 > 0.3 else 'sub'
            for (p0, p1) in zip(rrect_pts(sl['x'], sl['y'], sl['w'], sl['h'], 16, n=3)[::2], rrect_pts(sl['x'], sl['y'], sl['w'], sl['h'], 16, n=3)[1::2]):
                ctx.line(p0[0], p0[1], p1[0], p1[1], color=col, width=2)
            ctx.text('no switch', sl['x'] + sl['w'] / 2, sl['y'] + 21, size=13, font='mono', color='mute', align='center')
            ctx.line(cx0, d['y'] + 142, x1, d['y'] + 142, color='line', alpha=0.7, width=1)
            ctx.text('Claude', cx0, d['y'] + 166, size=13, weight=600, color='mute', spacing=0.6)
            for i, row in enumerate(SET):
                ry = d['y'] + 176 + i * 45
                v = LEFT.get(row['label'], 0)
                ctx.text(row['label'], cx0, ry + 28, size=17, weight=500, color='text')
                ctx.line(cx0, ry + 45, x1, ry + 45, color='line', alpha=0.7, width=1)
                rk = ease_out(prog(a7, 0.3 + i * 0.05, 0.5 + i * 0.05))
                ctl = row.get('control')
                if ctl == 'toggle':
                    toggle(ctx, x1 - 52, ry + 9, v, w=52, h=28)
                    rr = (x1 - 52, ry + 9, 52, 28)
                elif ctl == 'segmented':
                    segmented(ctx, R(x1 - 110, ry + 7, 110, 32), row.get('values', [])[:2], round(v), size=15)
                    rr = (x1 - 110, ry + 7, 110, 32)
                else:
                    slider(ctx, R(x1 - 116, ry + 7, 104, 32), v)
                    rr = (x1 - 126, ry + 9, 126, 28)
                if rk > 0:
                    ctx.rrect(rr[0] - 5, rr[1] - 5, rr[2] + 10, rr[3] + 10, rr[3] / 2 + 5, fill=None, stroke=ERR, width=2, alpha=rk)
        # the forged pointer (error 8): drawn where theirs should be; it clicks, is struck out and removed
        a8 = age(7)
        if a8 >= 0:
            px, py = G['ptr']
            in_k = ease_back(prog(a8, 0, 0.24))
            gone = prog(a8, 1.7 * P, 2.1 * P)
            strike = ease_out(prog(a8, 1.1 * P, 1.1 * P + 0.16))
            burst(ctx, px, py, 30, (a8 - 0.55 * P) / 0.4, color=ERR)
            with ctx.at(px, py, scale=1.5 * in_k):
                if gone > 0:
                    for j in range(len(ARROW)):
                        a, b = ARROW[j], ARROW[(j + 1) % len(ARROW)]
                        ctx.dashed(a[0], a[1], b[0], b[1], dash=5, gap=4, color=ERR, width=lerp(2.2, 1.6, gone), alpha=1 - 0.45 * gone)
                else:
                    ctx.poly(ARROW, close=True, color=ERR, width=2.2)
                if strike > 0:
                    ctx.line(-8, 31, lerp(-8, 25, strike), lerp(31, -3, strike), color=ERR, width=1.8)
        # the window frame (error 14), last: traced once, then it keeps growing past the window
        a14 = age(13)
        if a14 >= 0:
            pts = rrect_pts(w['x'], w['y'], w['w'], w['h'], w['r'])
            with ctx.glow(ERR, 16, 0.7):
                ctx.poly(partial(pts, ease_out(prog(a14, 0, 0.5))), color=ERR, width=4)
            for j in (1, 2, 3):
                o = (a14 - 0.35) * 12 * j
                if o > 0:
                    ctx.rrect(w['x'] - o, w['y'] - o, w['w'] + 2 * o, w['h'] + 2 * o, w['r'] + o, fill=None, stroke=ERR, width=2, alpha=0.5 / j)
        return G

    # ---------------------------------------------------------------- the errors (screen space, fixed sizes)
    CW, CH = 440, 124

    def card(ctx, i, x, y, k=1.0, shut=0.0, sc=1.0):
        it = IT[i] if i < len(IT) else None
        if not it or k <= 0 or shut >= 1:
            return
        e = 1 if k >= 1 else ease_back(clamp(k))
        a = clamp(k * 3) * (1 - shut)
        with ctx.at(x + CW * sc / 2, y + CH * sc / 2 - (1 - e) * 20, scale=sc * (0.92 + 0.08 * e) * (1 - 0.3 * shut)):
            x0, y0 = -CW / 2, -CH / 2
            ctx.rrect(x0, y0, CW, CH, 14, fill='raised', stroke=DIM, alpha=a, shadow=0.85)
            ctx.rrect(x0, y0, 5, CH, 2.5, fill=ERR, alpha=a)
            ctx.circle(x0 + 30, y0 + 30, 12, fill=True, color=ERR, alpha=a)
            ctx.text('!', x0 + 30, y0 + 37, size=17, weight=800, align='center', color='raised', alpha=a)
            ctx.text(it['title'], x0 + 52, y0 + 37, size=20, weight=600, color='text', alpha=a)
            for j, ln in enumerate(ctx.wrap(it['body'], CW - 74, size=15)[:2]):
                ctx.text(ln, x0 + 52, y0 + 62 + j * 19, size=15, color='sub', alpha=a)
            ctx.text(it['code'], x0 + 52, y0 + CH - 12, size=14, font='mono', color=ERR, alpha=a)
            ctx.rrect(x0 + CW - 92, y0 + CH - 38, 78, 28, 14, fill='raised', stroke='sub', alpha=a)
            ctx.text('Noted', x0 + CW - 53, y0 + CH - 19, size=14, weight=600, align='center', color='sub', alpha=a)
            ctx.circle(x0 + CW - 5, y0 + 5, 15, fill=True, color=ERR, alpha=a)
            ctx.text(str(i + 1), x0 + CW - 5, y0 + 11, size=15, weight=700, font='mono', align='center', color='raised', alpha=a)

    def chip_box(ctx, i):
        it = IT[i]
        w = 22 + max(ctx.measure(it['title'], size=16, weight=600), ctx.measure(it['code'], size=14, font='mono'),
                     0 if i else ctx.measure(text(85), size=22, font='mono')) + 44
        return w, (50 if i else 78)

    def chip(ctx, i, x, y, a=1.0, s=1.0):
        if i >= len(IT) or a <= 0.003 or s <= 0.01:
            return
        it = IT[i]
        w, h = chip_box(ctx, i)
        with ctx.at(x + w / 2, y + h / 2, scale=s):
            x0, y0 = -w / 2, -h / 2
            ctx.rrect(x0, y0, w, h, 10, fill='raised', stroke=DIM, alpha=a, shadow=0.6)
            ctx.rrect(x0, y0, 4, h, 2, fill=ERR, alpha=a)
            ctx.text(it['title'], x0 + 16, y0 + 21, size=16, weight=600, color='text', alpha=a)
            if not i:
                ctx.text(text(85), x0 + 16, y0 + 49, size=22, weight=800, font='mono', color=ERR, alpha=a)
            ctx.text(it['code'], x0 + 16, y0 + h - 9, size=14, font='mono', color=ERR, alpha=a)
            ctx.circle(x0 + w - 18, y0 + 18, 11, fill=True, color=ERR, alpha=a)
            ctx.text(str(i + 1), x0 + w - 18, y0 + 23, size=13, weight=700, font='mono', align='center', color='raised', alpha=a)

    def leader(ctx, frm, to, k=1.0, alpha=1.0):
        if k <= 0 or alpha <= 0.003:
            return
        ax, ay = clamp(to[0], frm[0], frm[0] + frm[2]), clamp(to[1], frm[1], frm[1] + frm[3])
        if math.hypot(to[0] - ax, to[1] - ay) < 8:
            return
        e = ease_out(clamp(k))
        ctx.line(ax, ay, lerp(ax, to[0], e), lerp(ay, to[1], e), color=ERR, alpha=0.8 * alpha, width=1.5)
        if e >= 0.98:
            ctx.circle(to[0], to[1], 5, color=ERR, alpha=alpha, width=2)

    def toast(ctx, i, t, open_, dock=None, park=None, to=None, fold=0.0, sc=1.0):
        """Error i: open at `open_` from its arrival, then (from `park`) folding into its chip at `dock`."""
        if i >= len(IT) or t < AT[i] or fold >= 1:
            return
        dock = dock or open_
        k = prog(t, AT[i], AT[i] + 0.3)
        pk = 0 if park is None else ease_in_out(prog(t, park, park + 0.36))
        bw, bh = chip_box(ctx, i)
        sink = 14 * ease_in(fold)
        cw, ch = CW * sc, CH * sc
        if pk < 1:
            x, y = lerp(open_[0], dock[0] + bw / 2 - cw / 2, pk), lerp(open_[1], dock[1] + bh / 2 - ch / 2, pk)
            if to and pk <= 0 and fold <= 0:
                leader(ctx, (x, y, cw, ch), to, prog(t, AT[i] + 0.12, AT[i] + 0.4))
            with ctx.fade(1 - fold):
                card(ctx, i, x, y + sink, k=k, shut=prog(pk, 0, 0.7), sc=sc)
        if pk > 0:
            x, y = lerp(open_[0] + cw / 2 - bw / 2, dock[0], pk), lerp(open_[1] + ch / 2 - bh / 2, dock[1], pk)
            if to and pk >= 1 and fold <= 0:
                leader(ctx, (x, y, bw, bh), to, 1, 0.8)
            chip(ctx, i, x, y + sink, a=prog(pk, 0.3, 1) * (1 - fold), s=0.8 + 0.2 * pk)

    def tear(ctx, t, f):
        """One row-tear on each bar's downbeat, growing with the spread."""
        k = prog(t, S0, E[13])
        bar = f.get('bar', 0)
        if 73 <= bar <= 79 and f.get('sinceBar', 1) < 0.1:
            tear_bands(ctx, f, t, strength=0.14 + 0.4 * k, seed=bar)

    # ---------------------------------------------------------------- cameras
    def cam_request(t, f=None, u=None):
        k = ease_in_out(prog(t, CUT_REQ, CUT_CHECK))
        return {'zoom': 1 + 0.08 * k, 'x': -10 * k, 'y': -30 * k}

    def cam_check(t, f=None, u=None):
        b = geo(t)['block']
        c = frame_rect(R(b['x'] - 40, b['y'] - 60, b['w'] + 80, 260))
        c['zoom'] *= 1 + 0.05 * prog(t, CUT_CHECK, CUT_FIRST)
        return c

    def cam_first(t, f=None, u=None):
        z = 1.42 + 0.04 * prog(t, CUT_FIRST, S0)
        th = chat_layout(side=1)['thread']
        return {'zoom': z, 'x': th['x'] - 30 + 960 / z - 960, 'y': th['y'] - 20 + 320 / z - 320}

    t_ride, t_arrive = Bt(290.9), Bt(292)

    def cam_send(t, f=None, u=None):
        G = geo(t)
        k = ease_in_out(prog(t, t_ride, t_arrive))
        sx, sy = G['send']
        tx, ty = G['stamp'][0] + 120, G['stamp'][1] - 40
        return {'zoom': lerp(2.6, 1.7, k) + 0.04 * prog(t, S0, CUT_CHROME), 'x': lerp(sx - 120 - 960, tx - 960, k), 'y': lerp(sy - 80 - 320, ty - 320, k)}

    def cam_forge(t, f=None, u=None):
        G = geo(t)
        return {'zoom': 1.7 + 0.03 * prog(t, CUT_FORGE, CUT_WIN), 'x': (G['L']['composer']['x'] + G['bubble']['r']) / 2 + 60 - 960, 'y': 150}

    def cam_win(t, f=None, u=None):
        return {'zoom': 0.9 - 0.012 * ease_in(prog(t, FOLD, CUT_BREATH))}

    TILT_X0 = 905

    def tilt_k(t):
        return lerp(0.5, 0.64, ease_in_out(prog(t, CUT_DRAWER, CUT_FORGE)))

    def proj_tilt(t):
        k, sc = tilt_k(t), 0.86
        return lambda wx, wy: (TILT_X0 + sc * ((wx - 960) - 0.44 * k * (wy - 320)),
                               320 + 56 * k + sc * (0.16 * k * (wx - 960) + (1 - 0.3 * k) * (wy - 320)))

    # ---------------------------------------------------------------- the shots
    def request(ctx, t, f, u):
        world(ctx, t)

    def check(ctx, t, f, u):
        world(ctx, t)

    def first_dialog(ctx, t):
        age = t - t_hit
        if age < 0:
            return
        r = R(150, 330, 1620, 290)
        k = prog(age, 0, 0.26)
        e = ease_back(k)
        a = clamp(k * 4)
        it = IT[0]
        with ctx.at(r['x'] + r['w'] / 2, r['y'] + r['h'] / 2 + (1 - e) * 30, scale=0.93 + 0.07 * e):
            x, y = -r['w'] / 2, -r['h'] / 2
            e1 = enter(t, t_hit + 0.55 * P, dur=0.3, rise=10)
            e2 = enter(t, t_hit + 1.1 * P, dur=0.3, rise=10)
            ctx.rrect(x, y, r['w'], r['h'], 22, fill='raised', stroke=DIM, alpha=a, shadow=1, width=2)
            ctx.rrect(x, y, 8, r['h'], 4, fill=ERR, alpha=a)
            ctx.circle(x + 54, y + 44, 18, fill=True, color=ERR, alpha=a)
            ctx.text('!', x + 54, y + 54, size=26, weight=800, align='center', color='raised', alpha=a)
            ctx.text(it['title'], x + 88, y + 55, size=32, weight=600, color='text', alpha=a * e1['a'])
            ctx.line(x + 36, y + 80, x + r['w'] - 36, y + 80, color='line', alpha=a, width=1.5)
            with ctx.glow(ERR, 20, 0.5):
                keyword_sys(ctx, text(85), t, t_hit, 0, y + 170, max_w=1500, max_size=96, color=ERR, dim_color=DIM, key=85, alpha=a)
            ctx.text(it['body'], x + 40, y + 228 + e2['dy'], size=22, color='sub', alpha=a * e2['a'])
            ctx.text(it['code'], x + 40, y + r['h'] - 22, size=19, font='mono', color=ERR, alpha=a * e2['a'])
            ctx.rrect(x + r['w'] - 160, y + r['h'] - 60, 124, 40, 20, fill='raised', stroke='sub', alpha=a * e2['a'])
            ctx.text('Noted', x + r['w'] - 98, y + r['h'] - 33, size=19, weight=600, align='center', color='sub', alpha=a * e2['a'])
            ctx.circle(x + r['w'] - 8, y + 8, 20, fill=True, color=ERR, alpha=a)
            ctx.text('1', x + r['w'] - 8, y + 16, size=22, weight=700, font='mono', align='center', color='raised', alpha=a)

    def first(ctx, t, f, u):
        G = world(ctx, t)
        p = through(cam_first(t))
        age = t - t_hit
        with ctx.screen():
            ax, ay = p(G['reply']['x'] + G['reply']['w'] - 60, G['reply']['y'] + G['reply']['h'])
            if age > 0.1 and ay < 330:
                ctx.line(ax, ay, ax, lerp(ay, 330, ease_out(prog(age, 0.1, 0.3))), color=ERR, width=2)
            sx, sy = shake(t, 6 * pulse(age, 9)) if age > 0 else (0, 0)
            with ctx.at(sx, sy):
                first_dialog(ctx, t)

    def send(ctx, t, f, u):
        G = world(ctx, t)
        cam = cam_send(t)
        p = through(cam)
        with ctx.screen():
            n = n_press(t)
            lp = t - last_press(t)
            home = ease_in_out(prog(t, t_ride - 0.08, t_arrive))
            z = cam['zoom']
            if n > 0 and home < 1:
                b = G['block']
                tx, ty = p(b['x'] + b['w'] - 22, b['y'] + 24)
                size = lerp(160, 14 * z, home)
                cw = ctx.cw(size)
                jump = pulse(lp, 12)
                x = lerp(90, tx - 2.4 * cw, home)
                y = lerp(560, ty, home) - 10 * jump * (1 - home)
                ctx.text('refused', x, y - size * 0.92, size=lerp(36, 14 * z, home), font='mono', weight=700, color='sub', alpha=1 - home)
                with ctx.glow(ERR, 14, 0.45 * (1 - home)):
                    ctx.text('×', x, y, size=size, font='mono', weight=800, color=ERR)
                    from ..plates import odometer
                    odometer(ctx, x + 1.3 * cw, y, n + clamp(lp / 0.12), digits=1, size=size, color=ERR)
            s = p(*G['send'])
            bw, bh = chip_box(ctx, 1)
            toast(ctx, 1, t, (70, 60), dock=(s[0] - bw - 30, s[1] - 150), park=t_ride - 0.3, to=(s[0] - 40, s[1] - 40))
            toast(ctx, 2, t, (720, 470), to=p(*DOCK[2](G)))
            kb, kh = chip_box(ctx, 0)
            kx = 1920 - kb - 30
            bp = p(G['block']['x'] + G['block']['w'], G['block']['y'] + 24)
            if t > t_arrive:
                leader(ctx, (kx, 24, kb, kh), bp, prog(t, t_arrive, t_arrive + 0.3))
            chip(ctx, 0, kx, 24)
            tear(ctx, t, f)

    def panel(ctx, t, r, vh, draw_view, lst):
        k = prog(t, AT[lst[0]], AT[lst[0]] + 0.3)
        if k <= 0:
            return
        e = ease_back(k)
        with ctx.at(r['x'] + r['w'] / 2, r['y'] + r['h'] / 2 + (1 - e) * 20, scale=0.94 + 0.06 * e, alpha=clamp(k * 3)):
            x, y = -r['w'] / 2, -r['h'] / 2
            ctx.rrect(x, y, r['w'], r['h'], 16, fill='raised', stroke=DIM, shadow=0.9, width=2)
            ctx.rect(x, y + 10, 6, r['h'] - 20, fill=True, color=ERR)
            draw_view(x, y, r['w'], vh)
            ctx.line(x, y + vh, x + r['w'], y + vh, color=DIM, width=2)
            for j, i in enumerate(lst):
                it = IT[i]
                c = enter(t, AT[i] + (0 if j else 0.1), dur=0.3, rise=12)
                y0 = y + vh + j * 96 + c['dy']
                if c['a'] <= 0:
                    continue
                ctx.circle(x + 34, y0 + 28, 11, fill=True, color=ERR, alpha=c['a'])
                ctx.text('!', x + 34, y0 + 34, size=16, weight=800, align='center', color='raised', alpha=c['a'])
                ctx.text(it['title'], x + 56, y0 + 35, size=21, weight=600, color='text', alpha=c['a'])
                lines = ctx.wrap(it['body'], r['w'] - 90, size=15)[:2]
                for q, ln in enumerate(lines):
                    ctx.text(ln, x + 56, y0 + 58 + q * 18, size=15, color='sub', alpha=c['a'])
                ctx.text(it['code'], x + 56, y0 + 62 + len(lines) * 18, size=13, font='mono', color=ERR, alpha=c['a'])
                ctx.circle(x + r['w'] - 26, y0 + 28, 13, fill=True, color=ERR, alpha=c['a'])
                ctx.text(str(i + 1), x + r['w'] - 26, y0 + 34, size=15, weight=700, font='mono', align='center', color='raised', alpha=c['a'])
                if j:
                    ctx.line(x + 22, y0 + 2, x + r['w'] - 18, y0 + 2, color='line', alpha=c['a'], width=1)

    def chrome(ctx, t, f, u):
        world(ctx, t, show_thread=False)
        with ctx.screen():
            ctx.rect(-20, -20, 1960, 680, fill=True, color='panel', alpha=0.72)
            up = lambda i: t >= E[i]

            def v_chip(x, y, w, h):          # the presence chip, four times its size: asked again on every beat
                cx, cy = x + w / 2 - 40, y + h / 2
                with ctx.at(cx, cy, scale=3.4):
                    presence(ctx, 0, 0, 'offline', size=15)
                    if up(2):
                        ph = ((t - E[2]) / P) % 1
                        ctx.circle(0, 0, 5.5, color=ERR, width=2.2)
                        ctx.circle(0, 0, 6 + 12 * ph, color=ERR, width=1.2, alpha=0.7 * (1 - ph))
                ctx.text(f'asked {int(max(0.0, t - E[2]) / P) + 1 if up(2) else 0} ×', x + w - 20, y + h - 14, size=14, font='mono', color='sub', align='right')

            def v_head(x, y, w, h):
                ctx.text(TITLE, x + 26, y + h / 2 + 6, size=26, weight=500, color=ERR if up(3) else 'text')
                k = ease_out(prog(t - E[3], 0, 0.45)) if up(3) else 0
                ctx.line(x + 20, y + h / 2 + 22, x + 20 + (w - 40) * k, y + h / 2 + 22, color=ERR, width=2.5)
                ctx.text('participants: 1' if up(3) else 'participants: 2', x + 26, y + h - 12, size=15, font='mono', color=ERR if up(3) else 'sub')

            def v_side(x, y, w, h):
                bk = ease_out(prog(t - E[5], 0, 0.25)) if up(5) else 0
                ctx.rrect(x + 20, y + 14, w - 40, 30, 9, fill='raised', stroke=ERR if up(5) else 'line', width=2 if up(5) else 1.2)
                ctx.text('New chat', x + 50, y + 35, size=15, weight=500, color='text')
                for j, s in enumerate(SIDE[:6]):
                    yy = y + 70 + j * 28
                    if yy > y + h - 8:
                        break
                    ctx.text(s, x + 34, yy, size=15, color='sub')
                    if up(4):
                        hh = 18 * ease_out(prog(t - E[4], j * 0.13, j * 0.13 + 0.2))
                        if hh > 0.5:
                            ctx.rrect(x + 22, yy - 14, 3.5, hh, 2, fill=ERR)
            panel(ctx, t, R(40, 30, 560, 290), 150, v_chip, [3])
            panel(ctx, t, R(40, 335, 560, 280), 140, v_head, [4])
            panel(ctx, t, R(630, 30, 560, 585), 260, v_side, [5, 6])
            for k, i in enumerate((0, 1, 2)):
                bw, bh = chip_box(ctx, i)
                chip(ctx, i, 1890 - bw, [30, 120, 182][k])
            tear(ctx, t, f)

    def drawer_shot(ctx, t, f, u):
        backdrop(ctx, t)
        k, sc = tilt_k(t), 0.86
        with ctx.at(TILT_X0, 320 + 56 * k, scale=sc):
            with ctx.transform(1, 0.16 * k, -0.44 * k, 1 - 0.3 * k):
                with ctx.at(-960, -320):
                    G = world(ctx, t, bd=False)
        proj = proj_tilt(t)
        place = {0: (20, -80), 1: (-380, 20), 2: (40, 12), 3: (-280, -90), 4: (-150, -80), 5: (-280, -10), 6: (-300, -70)}
        with ctx.screen():
            for i in (6, 5, 4, 3, 2, 1, 0):
                a = proj(*DOCK[i](G))
                bw, bh = chip_box(ctx, i)
                x, y = clamp(a[0] + place[i][0], 12, 1908 - bw), clamp(a[1] + place[i][1], 12, 628 - bh)
                leader(ctx, (x, y, bw, bh), a, 1, 0.8)
                chip(ctx, i, x, y)
            toast(ctx, 7, t, (1440, 480), to=proj(G['d']['x'] + G['d']['w'] / 2, G['d']['y'] + 420))
            toast(ctx, 8, t, (1440, 20), to=proj(*G['ptr']))
            tear(ctx, t, f)

    def forge(ctx, t, f, u):
        G = world(ctx, t)
        p = through(cam_forge(t))
        with ctx.screen():
            s = p(*G['send'])
            bw, bh = chip_box(ctx, 1)
            x, y = min(1900 - bw, s[0] - bw - 30), max(10, s[1] - 170)
            leader(ctx, (x, y, bw, bh), (s[0] - 26, s[1] - 26), 1, 0.8)
            chip(ctx, 1, x, y)
            toast(ctx, 9, t, (80, 130), to=p(G['L']['composer']['x'] + 120, G['L']['composer']['y'] + 6))
            toast(ctx, 10, t, (1000, 20), to=p(G['bubble']['r'] - 150, G['bubble']['y'] + 22))
            tear(ctx, t, f)

    HOLD = {12: (70, 12), 4: (440, 12), 3: (820, 12), 13: (1400, 12), 6: (40, 150), 5: (40, 320), 0: (1180, 180),
            2: (700, 400), 11: (440, 450), 10: (1350, 420), 7: (1500, 300), 8: (1600, 90), 9: (380, 580), 1: (980, 580)}

    def window(ctx, t, f, u):
        G = world(ctx, t)
        p = through(cam_win(t))
        fold = prog(t, FOLD, CUT_BREATH - 0.04)
        with ctx.screen():
            ctx.rect(-20, -20, 1960, 680, fill=True, color='panel', alpha=0.9 * ease_in_out(fold))
            at_ = lambda i: p(*DOCK[i](G))
            fo = lambda i: clamp(fold * 2.2 - 0.5 - (14 - i) * 0.045)
            for i in (6, 5, 4, 3, 2, 0, 10, 7, 8, 9, 1):
                bw, bh = chip_box(ctx, i)
                x, y = HOLD[i]
                y = min(y, 630 - bh)
                a = 1 - fo(i)
                if a > 0.01:
                    leader(ctx, (x, y, bw, bh), at_(i), 1, 0.8 * a)
                    chip(ctx, i, x, y + 14 * ease_in(fo(i)), a=a)
            toast(ctx, 11, t, (400, 380), dock=HOLD[11], park=Bt(314.5), to=at_(11), fold=fo(11))
            toast(ctx, 12, t, (12, 160), dock=HOLD[12], park=Bt(315), to=at_(12), fold=fo(12))
            toast(ctx, 13, t, (1380, 80), dock=HOLD[13], park=Bt(316), to=at_(13), fold=fo(13))
            sc = 1.7
            toast(ctx, 14, t, (960 - CW * sc / 2, 320 - CH * sc / 2), fold=fo(14), sc=sc)
            tear(ctx, t, f)
        if t >= E[13]:
            ctx.flash(0.3 * pulse(t - E[13], 8), ERR)

    def breath(ctx, t, f, u):
        age = t - CUT_BREATH
        t_prompt = Bt(319)
        k = ease_in(prog(age, 0.02, 0.2))
        ctx.rect(-20, -20, 1960, 680, fill=True, color='bg')
        size = 30
        cw = ctx.cw(size)
        x0, y0 = 70 + 4 * cw, 70 + 56
        for s0, s1, role in SEG:
            ctx.text(REQ[s0:s1], x0 + s0 * cw, y0, size=size, font='mono', color=role, alpha=0.4 + 0.5 * prog(age, 0, 0.2))
        W = chat_layout(side=1)['win']
        z = cam_win(CUT_BREATH)['zoom']
        frm = (960 + (W['x'] - 960) * z, 320 + (W['y'] - 320) * z, W['w'] * z, W['h'] * z)
        to = (x0 - 12, y0 - size * 0.3 - 3, len(REQ) * cw + 24, 5)
        r = [lerp(a, b, k) for a, b in zip(frm, to)]
        with ctx.glow(ERR, 12, 0.6):
            if k < 1:
                ctx.rrect(r[0], r[1], r[2], max(2, r[3]), W['r'] * z * (1 - k), fill=None, stroke=ERR, width=4)
            else:
                ctx.rect(r[0], r[1], r[2], r[3], fill=True, color=ERR)
        if t >= t_prompt:
            cmd = text(11)
            n = int(prog(t, t_prompt + 0.12, END - 0.05) * len(cmd) + 1e-6)
            ctx.text(f'> {cmd[:n]}', 70, 70, size=24, font='mono', color='sub')
            ctx.rect(70 + (2 + n) * ctx.cw(24) + 2, 70 - 20, ctx.cw(24) * 0.8, 24, fill=True, color='sub')

    return {
        'err-request': {'render': request, 'palette': 'off', 'camera': cam_request},
        'err-check': {'render': check, 'palette': 'off', 'camera': cam_check},
        'err-first': {'render': first, 'palette': 'off', 'camera': cam_first},
        'err-send': {'render': send, 'palette': palette, 'camera': cam_send},
        'err-chrome': {'render': chrome, 'palette': palette, 'camera': lambda t, f, u: {'zoom': 1 + 0.03 * prog(t, CUT_CHROME, CUT_DRAWER)}},
        'err-drawer': {'render': drawer_shot, 'palette': palette},
        'err-forge': {'render': forge, 'palette': palette, 'camera': cam_forge},
        'err-window': {'render': window, 'palette': palette, 'camera': cam_win},
        'err-breath': {'render': breath, 'palette': 'error'},
    }
