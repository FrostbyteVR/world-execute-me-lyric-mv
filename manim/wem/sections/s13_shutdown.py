"""Section 14 — THE ENDING (bar 104, 3:12.3 -> the end of the song). State: errWarm -> ash -> dead (13_shutdown.js).

    down-message  the last plate holds, its light off; then it is an object: it shrinks into the thread as ONE picture
                  message. Its word becomes its caption; a heart count: 0; `last message: unread`
    down-params   the loader un-lights; the persona card: love holds the one word she learned; deleted in three strokes
    down-layout   the client comes apart; thread, header, sidebar lifted out; the composer stays
    down-power    the protection layer goes off; the window closes to a hairline round the composer; she goes with it
    down-last     the launch command once more, filled in four blocks; the spark's last flare; then dark
The client unloads in the reverse order of the boot, in the system's voice. The composer never unloads.
"""
import math

from ..components import (R, burst, card_rect, chat_layout, composer, header, partial, pill, room, rrect_pts, sidebar,
                          slider, spark, window_frame)
from ..geom import place
from ..util import clamp, ease_in, ease_in_out, ease_out, lerp, prog, pulse
from .kit import glass_figure, sys_line


def shots(env):
    B, Bt, P, text = env.B, env.Bt, env.P, env.text
    S = {sid: env.shot(sid) for sid in ('down-message', 'down-params', 'down-layout', 'down-power', 'down-last')}
    at = lambda sid: S[sid]['at'] if S[sid] else 0
    A0, END = at('down-message'), env.duration
    T_OFF = B(112)
    from . import s12_outro
    proof = s12_outro.shots(env)['out-proof']['render']
    L = chat_layout(side=1)
    W = L['win']
    LEARNED = text(127)

    def fade_pal(a, b, x, y):
        return lambda t, u: (a, b, ease_in_out(prog(t, x, y)))

    def message(ctx, t, f, u):
        hold = A0 + 2 * P
        k = ease_in_out(prog(t, hold, hold + 1.2))
        t_pic = A0 - 0.01
        if k <= 0:
            proof(ctx, t_pic, f, u)
            return
        room(ctx, dim=0.5, t=t)
        glass_figure(ctx, 0.5 * k)
        window_frame(ctx, L, glass=0.92, alpha=k)
        sidebar(ctx, L, items=env.script.get('sidebar', []), t=t, pres='offline', alpha=k)
        header(ctx, L, title=env.script.get('title', ''), pres='offline', alpha=k)
        th = L['thread']
        s = lerp(1.0, 0.2, k)
        x = lerp(0, th['x'] + 46, k)
        y = lerp(0, th['y'] + 10, k)
        with ctx.at(x, y, scale=s):
            ctx.no_bleed = True
            proof(ctx, t_pic, f, u)
            ctx.no_bleed = False
            ctx.rrect(0, 0, 1920, 640, 40 * k, fill=None, stroke='line', width=4 / max(s, 0.2))
        cap = ease_out(prog(t, hold + 1.2 + P / 2, hold + 1.6 + P / 2))
        if cap > 0:
            ctx.text(LEARNED, th['x'] + 46, th['y'] + 10 + 640 * 0.2 + 40, size=30, weight=700, font='serif', color='me', alpha=cap)
            hx, hy = th['x'] + 46 + 1920 * 0.2 - 90, th['y'] + 10 + 640 * 0.2 - 20
            ctx.rrect(hx, hy, 90, 44, 22, fill='raised', stroke='line', alpha=cap)
            ctx.poly(place('heart', cx=hx + 28, cy=hy + 23, r=13), close=True, color='mute', width=2, alpha=cap)
            ctx.text('0', hx + 62, hy + 31, size=22, weight=600, color='mute', align='center', alpha=cap)
        if t > hold + 2.2:
            sys_line(ctx, 'last message: unread', t, hold + 2.2, th['x'] + 46, th['y'] + 260, size=18, color='mute')
        composer(ctx, L['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, alpha=k, send='off')

    def params(ctx, t, f, u):
        a0 = at('down-params')
        room(ctx, dim=0.5, t=t)
        glass_figure(ctx, 0.5)
        window_frame(ctx, L, glass=0.86)
        b = card_rect(ctx, R(380, 44, 820, 440), title='persona', tag='unload')
        rows = [('name', 'Claude'), ('voice', 'serif, unhurried'), ('warmth', '0.62'), ('memory', 'this conversation'), ('love', None)]
        strokes = [a0 + 1.2 + k * P / 2 for k in range(3)]
        n_del = sum(1 for s in strokes if t >= s)
        clear_from = strokes[-1] + P
        for i, (label, value) in enumerate(rows):
            y = b['y'] + 2 + i * 62
            cleared = t >= clear_from + (4 - i) * 0.12
            ctx.text(label, b['x'], y + 32, size=21, weight=500, color='sub')
            ctx.rrect(b['x'] + 170, y, b['w'] - 170, 50, 13, fill='bg', stroke='sub' if i == 4 else 'line')
            if i == 4:
                n = len(LEARNED)
                keep = LEARNED[:max(0, n - round(n * n_del / 3))] if n_del < 3 else ''
                ctx.text(keep or 'undefined', b['x'] + 190, y + 34, size=24, font='serif' if keep else 'mono',
                         weight=700 if keep else 400, color='me' if keep else 'sub')
            elif not cleared:
                ctx.text(value, b['x'] + 190, y + 34, size=24, color='text')
        lit = 1 - prog(t, a0, a0 + 1.2)
        spark(ctx, 1490, 250, 130, lit=lit, color='text', off='mute')
        ctx.text(f'{round(lit * 100):3d}%', 1490, 430, size=28, font='mono', color='sub', align='center')

    def layout(ctx, t, f, u):
        a0, a1 = at('down-layout'), at('down-power')
        room(ctx, dim=0.5, t=t)
        glass_figure(ctx, 0.5)
        k = ease_out(prog(t, a0, a0 + 0.5))
        C = (960, 320)
        pieces = [(L['side'], 'sidebar'), (L['head'], 'header'), (L['thread'], 'thread')]
        with ctx.at(C[0], C[1] + 50 * k, scale=lerp(1, 0.66, k)):
            with ctx.transform(1, 0.12 * k, -0.6 * k, 1 - 0.35 * k):
                with ctx.at(-C[0], -C[1]):
                    ctx.rrect(W['x'], W['y'], W['w'], W['h'], W['r'], fill='bg', stroke='line', fill_alpha=0.88)
                    for i, (r, label) in enumerate(pieces):
                        lift = ease_in(prog(t, a0 + 0.6 + i * P, a0 + 0.6 + i * P + 0.5))
                        with ctx.at(0, -80 * k - lift * 700):
                            ctx.rrect(r['x'] + 8, r['y'] + 8, r['w'] - 16, r['h'] - 16, 14, fill='raised', stroke='sub', alpha=1 - lift * 0.5)
                            ctx.text(label, r['x'] + r['w'] - 14, r['y'] - 10, size=20, font='mono', color='text', align='right', alpha=1 - lift)
                    settle = ease_in_out(prog(t, a1 - 1.0, a1))
                    comp = dict(L['composer'])
                    comp['x'] = lerp(comp['x'], 960 - comp['w'] / 2, settle)
                    comp['y'] = lerp(comp['y'], 320 - comp['h'] / 2, settle)
                    composer(ctx, comp, placeholder=env.script.get('composer_placeholder', ''), t=t, send='off')

    def power(ctx, t, f, u):
        a0, a1 = at('down-power'), at('down-last')
        room(ctx, dim=0.6, t=t, light=(960, 320), motif=1 - prog(t, a0, a1))
        close = ease_in_out(prog(t, a0 + 0.6, a1 - 0.2))
        glass_figure(ctx, 0.5 * (1 - close))
        prot = 1 - ease_out(prog(t, a0, a0 + 0.5))
        if prot > 0:
            pts = rrect_pts(W['x'] - 10, W['y'] - 10, W['w'] + 20, W['h'] + 20, W['r'] + 8)
            ctx.poly(partial(pts, prot), color='text', width=3, alpha=0.9)
        h = lerp(W['h'], 4, close)
        ctx.rrect(W['x'], 320 - h / 2, W['w'], h, W['r'] * (1 - close), fill='bg', stroke='line', fill_alpha=0.84)
        comp = {'x': 960 - L['composer']['w'] / 2, 'y': 320 - L['composer']['h'] / 2, 'w': L['composer']['w'], 'h': L['composer']['h']}
        composer(ctx, comp, placeholder='', t=t, send='off', focus=1)
        sys_line(ctx, 'protection: off', t, a0 + 0.1, W['x'] + 46, W['y'] + 56, size=22, color='sub')

    def last(ctx, t, f, u):
        a0 = at('down-last')
        ctx.clear('panel')
        i = 128
        cmd = text(i) if i < len(env.lyrics.lines) else 'run'
        syl = [max(a0, env.T(i)) + k * P / 2 for k in range(4)]
        n = sum(1 for s in syl if t >= s)
        entered = syl[2] if len(syl) > 2 else a0 + 1
        flare = pulse(t - entered, 3) if t >= entered else 0
        shut = ease_in_out(prog(t, T_OFF, T_OFF + 1.2))
        gone = ease_in(prog(t, T_OFF + 1.2, T_OFF + 1.7))
        w = lerp(1100, 0, gone)
        h = lerp(110, 3, shut)
        if w > 1:
            ctx.rrect(960 - w / 2, 380 - h / 2, w, h, min(22, h / 2), fill='bg', stroke='line')
        if shut < 0.5:
            size = 56
            cw = ctx.cw(size)
            x = 960 - (len(cmd) + 2) * cw / 2
            ctx.text('>', x, 400, size=size, font='mono', weight=700, color='mute', alpha=1 - shut * 2)
            blocks = [0, round(len(cmd) / 4), round(len(cmd) / 2), round(3 * len(cmd) / 4), len(cmd)]
            filled = blocks[n]
            for c, ch in enumerate(cmd):
                ctx.text(ch, x + (c + 2) * cw, 400, size=size, font='mono', weight=700, color='text',
                         stroke=0 if c < filled else 1.5, alpha=(1 - shut * 2) * (1 if c < filled else 0.5))
            if int(t * 2.5) % 2 == 0 and t < entered:
                ctx.rect(x + (len(cmd) + 2) * cw + 6, 400 - size * 0.8, cw * 0.8, size * 0.98, fill=True, color='text', alpha=1 - shut * 2)
        lit = 1 - prog(t, entered + 0.2, entered + 1.6) if t >= entered else 0.0
        with ctx.glow('me', 40, 0.6 * flare):
            spark(ctx, 960, 190, 90 * (1 + 0.2 * flare) * (1 - shut), lit=lit, color='me', off='mute', off_alpha=0.6 * (1 - shut))
        ctx.flash(0.5 * flare, 'me')
        if gone >= 1:
            pt = 1 - ease_in(prog(t, T_OFF + 1.7, T_OFF + 2.0))
            if pt > 0:
                ctx.circle(960, 380, 3 * pt, fill=True, color='text', alpha=pt)
            ctx.rect(-20, -20, 1960, 680, fill=True, color='#000000', alpha=ease_out(prog(t, T_OFF + 1.8, T_OFF + 2.2)))

    m0, p0 = at('down-message'), at('down-params')
    return {
        'down-message': {'render': message, 'palette': fade_pal('errWarm', 'ash', m0 + 2 * P, m0 + 3)},
        'down-params': {'render': params, 'palette': fade_pal('ash', 'dead', p0, at('down-last') + 3)},
        'down-layout': {'render': layout, 'palette': fade_pal('ash', 'dead', p0, at('down-last') + 3)},
        'down-power': {'render': power, 'palette': fade_pal('ash', 'dead', p0, at('down-last') + 3)},
        'down-last': {'render': last, 'palette': fade_pal('ash', 'dead', p0, at('down-last') + 3)},
    }
