"""Section 14 — THE ENDING (bar 104, 3:12.3 -> the end of the song). State: errWarm -> ash -> dead (13_shutdown.js).

    down-message  THE BRIDGE: the last plate holds for two beats, still; then it is an object: it grows round corners
                  and an edge and shrinks into the thread as ONE picture message. Its word becomes its caption; a heart
                  count under it reads 0 (chorus 1: 1); `last message: unread`
    down-params   the loader un-lights petal by petal; the persona card: love holds the word she learned; the view
                  closes in on that row; deleted in three strokes, undefined again; the fields clear from the bottom up
    down-layout   tilted exploded view: thread, header, sidebar lifted out one by one; the composer settles in the middle
    down-power    the protection layer goes off and is withdrawn; the window closes to a hairline round the composer;
                  she goes with it
    down-last     the launch command once more, hollow, filled in four blocks; on the third it is entered and the spark
                  flares, and goes out; the music stops: the composer closes into the hairline, a point, black
The client unloads in the reverse order of the boot, in the system's voice; the composer never unloads.
"""
import math

from ..components import (R, burst, card_rect, chat_layout, composer, header, partial, room, rrect_pts, sidebar,
                          slider, spark, window_frame)
from ..geom import place
from ..plates import mono_word
from ..util import clamp, ease_back, ease_in, ease_in_out, ease_out, lerp, prog, pulse
from .kit import glass_figure, sys_line
from .s12_outro import final_plate, stutter, WORD_W, BASE

CHUNKS4 = [(0, 2), (2, 3), (3, 5), (5, 9)]
SYL3 = [(0, 3), (3, 5), (5, 8)]


def _chunks(n, k):
    if k == 3 and n == 8:
        return SYL3
    if k == 4 and n == 9:
        return CHUNKS4
    q = [round(n * i / k) for i in range(k + 1)]
    return [(q[i], q[i + 1]) for i in range(k)]


def shots(env):
    B, Bt, P, text, cue = env.B, env.Bt, env.P, env.text, env.cue
    A0, B0, C0, D0, E0, OFF = B(104), B(106), B(108), B(110), Bt(445), B(112)
    L = chat_layout(side=1)
    L0 = chat_layout(side=0)
    W = L['win']
    C = (W['x'] + W['w'] / 2, W['y'] + W['h'] / 2)
    CBOX = dict(L0['composer'], y=C[1] - L0['composer']['h'] / 2)
    HOLD = env.script.get('composer_placeholder', '')
    TITLE = env.script.get('title', '')
    SIDE = env.script.get('sidebar', [])
    WORD = text(127)
    DRAIN = 0.25
    beat = lambda t, t0: (t - t0) / P
    ash = lambda t, u: ('ash', 'dead', DRAIN * prog(t, A0, E0))

    def log(ctx, t, lines, x, y, size=22, a=1.0):
        for i, (s, at) in enumerate(lines):
            bright = i == len(lines) - 1 or t < lines[i + 1][1]
            sys_line(ctx, s, t, at, x, y + i * size * 1.56, size=size, alpha=a, color='text' if bright else 'sub')

    # ------------------------------------------------------------------ the bridge: one picture message
    TH = L['thread']
    PIC = R(TH['x'] + 46, TH['y'] + 6, 600, 200)
    CAP = (PIC['x'], PIC['y'] + PIC['h'] + 52, 40)
    t_shrink, t_down, t_word = A0 + 2 * P, A0 + 4 * P, A0 + 2.5 * P
    t_heart, t_log = cue('heartZero', A0 + 2.4), cue('lastUnread', A0 + 2.9)

    def message_pal(t, u):
        a = ('ash', 'dead', DRAIN * prog(t, A0, E0))
        return ('errWarm', 'ash', ease_in_out(prog(t, t_shrink, t_down)))

    def message(ctx, t, f, u):
        k = ease_in_out(prog(t, t_shrink, t_down))
        up = ease_out(prog(t, t_shrink, t_down))
        if t < t_shrink:              # two beats: the whole sheet, in its own colours, perfectly still
            final_plate(ctx, env)
            return
        room(ctx, dim=0.4, t=t)
        glass_figure(ctx, 0.75 * prog(t, t_shrink + 0.4 * P, t_down + 0.5 * P))
        with ctx.fade(up):
            window_frame(ctx, L, glass=0.8)
            sidebar(ctx, L, items=[TITLE] + SIDE, active=0, t=t, pres='offline')
            header(ctx, L, title=TITLE, pres='offline')
            composer(ctx, L['composer'], placeholder=HOLD, t=t, send='off')
            spark(ctx, TH['x'] + 15, PIC['y'] + 16, 13, color='me')
        rx, ry = lerp(0, PIC['x'], k), lerp(0, PIC['y'], k)
        sc = lerp(1920, PIC['w'], k) / 1920
        rh = 640 * sc
        rad = 18 * k
        ctx.rrect(rx, ry, 1920 * sc, rh, rad, fill='panel', shadow=k)
        with ctx.at(rx, ry, scale=sc):
            ctx.no_bleed = True
            final_plate(ctx, env, word=False)
            ctx.no_bleed = False
        ctx.rrect(rx, ry, 1920 * sc, rh, rad, fill=None, stroke='sub', width=2.5, stroke_alpha=0.9 * clamp(k * 6))
        # its word stays large half a beat longer, then settles under the picture as its caption
        kw = ease_in_out(prog(t, t_word, t_down))
        full = ctx.fit(WORD, WORD_W['proof'], font='serif', weight=900, spacing_em=0.01, max_size=130)
        w0 = ctx.measure(WORD, size=full, weight=900, font='serif', spacing=0.01 * full) - 0.01 * full
        stutter(ctx, WORD, t, (-9, -9, -9), settle=1, m=0, align='left', x=lerp(960 - w0 / 2, CAP[0], kw),
                y=lerp(BASE, CAP[1], kw), size=lerp(full, CAP[2], kw))
        if t >= t_heart:
            e = ease_back(prog(t, t_heart, t_heart + 0.22))
            cx, cy = PIC['x'] + PIC['w'] - 70, PIC['y'] + PIC['h'] + 4
            with ctx.at(cx, cy, scale=0.5 + 0.5 * e, alpha=clamp(e * 3)):
                ctx.rrect(-62, -32, 124, 64, 32, fill='raised', stroke='sub', width=2.5, shadow=0.5)
                ctx.poly(place('heart', cx=-24, cy=2, r=19), close=True, color='sub', width=3)
                ctx.text('0', 24, 12, size=32, weight=600, color='sub', align='center')
            burst(ctx, cx, cy, 64, prog(t, t_heart, t_heart + 0.45), color='sub')
        sys_line(ctx, 'last message: unread', t, t_log, CAP[0] + 4, CAP[1] + 44, size=20, prefix='> ', color='text')

    # ------------------------------------------------------------------ persona: love, deleted
    CARD = R(380, 44, 820, 470)
    LOVE_Y = 44 + 84 + 2 + 4 * 66      # the love row (card_rect's content starts 84 px down)

    def params_cam(t, f, u):
        s = beat(t, B0)
        near = ease_in_out(prog(s, 1.6, 3.2)) * (1 - ease_in_out(prog(s, 5.3, 6.4)))
        far = {'zoom': 1.08 - 0.03 * prog(t, B0, C0), 'x': lerp(60, -40, ease_in_out(prog(s, 2.3, 3.4))), 'y': -6}
        zoom_near = 2.1
        tx, ty = CARD['x'] + 450 - 960, LOVE_Y + 25 - 320
        return {'zoom': lerp(far['zoom'], zoom_near, near), 'x': lerp(far['x'], tx, near), 'y': lerp(far['y'], ty, near)}

    def params(ctx, t, f, u):
        s = beat(t, B0)
        room(ctx, dim=0.45, t=t)
        glass_figure(ctx, 0.55)
        window_frame(ctx, L, glass=0.86)
        sidebar(ctx, L, items=[''] * 6, t=t, lit=0, alpha=0.6)
        header(ctx, L, title='')
        composer(ctx, L['composer'], placeholder=HOLD, t=t, focus=1, send='off', label='Claude' if s < 7.4 else '')
        b = card_rect(ctx, CARD, title='persona', k=1 - prog(s, 7.6, 8))
        if b:
            sys_line(ctx, 'settings: as you left them', t, B0 + 0.1, b['x'], b['y'] - 104, size=18, alpha=b['a'])
            rows = [('name', 'Claude', 'serif', False, 7.5), ('voice', 'serif, unhurried', 'serif', True, 7),
                    ('warmth', None, None, False, 6.5), ('memory', 'this conversation', 'sans', False, 6), ('love', None, None, False, 5.5)]
            for i, (label, value, font, italic, out) in enumerate(rows):
                e = prog(s, out, out + 0.5)
                a = b['a'] * (1 - e)
                y = b['y'] + 2 + i * 66 + 16 * ease_in(e)
                dele = prog(s, out - 0.6, out - 0.1)
                if a <= 0:
                    continue
                ctx.text(label, b['x'], y + 32, size=21, weight=500, color='sub', alpha=a)
                if i == 4:   # love: the word, held; deleted chunk by chunk; the default comes back
                    DEL = [cue('loveDel1', B0 + 1.5), cue('loveDel2', B0 + 1.75), cue('loveDel3', B0 + 2.0)]
                    t_u = cue('loveUndefined', B0 + 2.25)
                    chunks = _chunks(len(WORD), 3)
                    gone = sum(1 for d in DEL if t >= d)
                    left = chunks[len(chunks) - gone][0] if gone else len(WORD)
                    nu = int(clamp((t - t_u) * 60, 0, 9))
                    hit = pulse(t - DEL[gone - 1], 14) if gone else 0
                    ctx.rrect(b['x'] + 170, y, b['w'] - 170, 52, 13, fill='bg', stroke='sub' if gone else 'me', alpha=a,
                              width=1.5 + 2 * hit if gone else 3)
                    o = dict(size=34, weight=700, font='serif')
                    w = 0
                    if left > 0:
                        with ctx.glow('me', 12, 0.5 * a):
                            ctx.text(WORD[:left], b['x'] + 190, y + 39, color='meHot', alpha=a, **o)
                        w = ctx.measure(WORD[:left], **o)
                    elif t >= t_u:
                        ctx.text('undefined'[:nu], b['x'] + 190, y + 37, size=28, font='mono', color='sub', alpha=a)
                        w = ctx.measure('undefined'[:nu], size=28, font='mono')
                    if hit > 0.2:
                        a0, a1 = chunks[len(chunks) - gone]
                        x0 = b['x'] + 190 + ctx.measure(WORD[:a0], **o)
                        ww = ctx.measure(WORD[a0:a1], **o)
                        ctx.text(WORD[a0:a1], x0, y + 39, color='mute', alpha=a * hit, **o)
                        ctx.rect(x0, y + 24, ww, 3, fill=True, color='sub', alpha=a * hit)
                    if (gone and gone < 3) or (t >= t_u and nu < 9) or int(t * 2.5) % 2 == 0:
                        ctx.rect(b['x'] + 194 + w, y + 10, 3, 32, fill=True, color='text', alpha=a)
                    continue
                ctx.rrect(b['x'] + 170, y, b['w'] - 170, 52, 13, fill='bg', stroke='line', alpha=a)
                if value:
                    n = math.ceil(len(value) * (1 - dele))
                    ctx.text(value[:n], b['x'] + 190, y + 35, size=24, font=font, italic=italic, color='text', alpha=a)
                    if 0 < dele < 1:
                        ctx.rect(b['x'] + 193 + ctx.measure(value[:n], size=24, font=font, italic=italic), y + 12, 3, 27,
                                 fill=True, color='text', alpha=a)
                else:
                    slider(ctx, R(b['x'] + 192, y, b['w'] - 230, 52), 0.62 * (1 - ease_in_out(dele)), fill='sub', alpha=a)
        lit = 1 - prog(s, 0.75, 2.75)
        la = 1 - prog(s, 5.2, 6.2)
        if la > 0:
            x, y = 1490, 260
            ctx.radial(x, y, 260, 'raised', 0.9 * la)
            spark(ctx, x, y, 130, lit=lit, color='text', off='mute', alpha=la)
            ctx.text(f'{round(lit * 100):3d}%', x, y + 180, size=28, font='mono', color='sub', align='center', alpha=la)

    # ------------------------------------------------------------------ the pieces lifted out
    def layout(ctx, t, f, u):
        s = beat(t, C0)
        room(ctx, light=(960, 360), dim=0.45, t=t)
        pieces = [(R(W['x'], W['y'], W['w'], W['h']), 0, 'window', None),
                  (R(L['side']['x'] + 10, L['side']['y'] + 10, L['side']['w'] - 20, L['side']['h'] - 20), 60, 'sidebar', 6),
                  (R(L['head']['x'] + 12, L['head']['y'] + 8, L['head']['w'] - 24, L['head']['h'] - 6), 120, 'header', 4),
                  (R(L['thread']['x'] - 24, L['thread']['y'] + 6, L['thread']['w'] + 48, L['thread']['h'] - 6), 180, 'thread', 2),
                  (dict(L['composer']), 240, 'composer', None)]
        tilt = lambda tt: ease_in_out(prog(beat(tt, C0), 0.5, 1.7))
        glass_figure(ctx, 0.6, dx=60 * tilt(t))

        def plane(k, fn):
            sc = lerp(1, 0.62, k)
            with ctx.at(C[0], C[1] + 70 * k, scale=sc):
                with ctx.transform(1, 0.12 * k, -0.6 * k, 1 - 0.35 * k):
                    with ctx.at(-C[0], -C[1]):
                        fn(sc)

        def piece(i, tt):
            r0, lift, label, out = pieces[i]
            k = tilt(tt)
            st = beat(tt, C0)

            def draw(sc):
                p = 0 if out is None else prog(st, out, out + 1.3)
                a = 1 - prog(p, 0.72, 1)
                if a <= 0:
                    return
                mid = ease_in_out(prog(st, 6.4, 7.7)) if i == 4 else 0
                r = dict(r0, x=lerp(r0['x'], CBOX['x'], mid), y=lerp(r0['y'], CBOX['y'], mid)) if i == 4 else r0
                upv = lift * k * (1 - 0.6 * mid) + math.sin(tt * 2.2 + i * 1.3) * 8 * k + 560 * ease_in(p)
                if i > 0 and k > 0.02:
                    ctx.rrect(r['x'] + 14, r['y'] + 14, r['w'], r['h'], 14, fill='panel', alpha=0.6 * k * (1 - p))
                with ctx.at(0, -upv / ((1 - 0.35 * k) * sc)):
                    ctx.rrect(r['x'], r['y'], r['w'], r['h'], 14 if i else W['r'], fill='raised' if i else 'bg',
                              fill_alpha=0.95 if i else 0.88, stroke='text' if i else 'sub', stroke_alpha=(0.5 + 0.4 * k) if i else 1,
                              alpha=a, width=3 / sc, shadow=0.5 * k if i else 1)
                    if i == 0:   # its second outline: the protection layer is still on
                        ctx.rrect(r['x'] - 10, r['y'] - 10, r['w'] + 20, r['h'] + 20, W['r'] + 8, fill=None, stroke='text',
                                  width=3 / sc, stroke_alpha=0.7)
                    if i == 1:
                        for j in range(8):
                            ctx.rrect(r['x'] + 20, r['y'] + 24 + j * 34, min(r['w'] - 40, 110 + (j * 67) % 110), 13, 6, fill='mute', alpha=a)
                    if i == 2:
                        ctx.rrect(r['x'] + 22, r['y'] + 16, 240, 14, 7, fill='mute', alpha=a)
                    if i == 3:
                        for j in range(3):
                            ctx.rrect(r['x'] + (r['w'] - 380 if j % 2 else 36), r['y'] + 30 + j * 96, 340 - j * 30, 44, 20,
                                      fill=None, stroke='sub', alpha=a, width=3)
                    if i == 4:
                        ctx.rrect(r['x'] + 36, r['y'] + 32, 260, 16, 8, fill='mute', alpha=a)
                        if int(tt * 2.2) % 2 == 0:
                            ctx.rect(r['x'] + 22, r['y'] + 22, 3, 36, fill=True, color='text', alpha=a)
                    if i > 0:
                        ctx.text(label, r['x'] + r['w'] - 16, r['y'] - 12, size=22 / sc, font='mono', color='text',
                                 alpha=a * clamp(k * 3), align='right')
            plane(k, draw)

        for i, (_, _, _, out) in enumerate(pieces):
            if out is not None and out < s < out + 1.3:
                for tau, al in ((0.044, 0.25), (0.022, 0.4)):
                    with ctx.fade(al):
                        piece(i, t - tau)
            piece(i, t)
            if i == 0:   # what a lifted piece leaves on the base: its empty socket, until the composer has the window
                def sockets(sc):
                    for j in (1, 2, 3):
                        r, _, _, o = pieces[j]
                        a = 0.85 * prog(s, o + 0.3, o + 1.1) * (1 - prog(s, 7.1, 7.9))
                        if a > 0.01:
                            pts = rrect_pts(r['x'], r['y'], r['w'], r['h'], 14)
                            for q in range(0, len(pts) - 1, 2):
                                ctx.line(pts[q][0], pts[q][1], pts[q + 1][0], pts[q + 1][1], color='sub', alpha=a, width=3 / sc)
                plane(tilt(t), sockets)
        left = 4 - sum(1 for (_, _, _, out) in pieces if out is not None and s >= out + 0.9)
        log(ctx, t, [(f'pieces left: {left}', C0 + 1.5 * P)], 70, 70)

    # ------------------------------------------------------------------ power off; the window closes
    def power(ctx, t, f, u):
        s = beat(t, D0)
        off = ease_out(prog(s, 0.7, 1.15))
        undraw = ease_in_out(prog(s, 1.1, 2.3))
        close = ease_in_out(prog(s, 2.5, 4.4))
        room(ctx, light=(960, 320), dim=0.5 + 0.35 * close, motif=1 - close, t=t)
        glass_figure(ctx, 0.75 * (1 - ease_in(close)))
        h = max(2, W['h'] * (1 - close))
        edge = prog(close, 0.55, 1)
        if close < 1:
            ctx.rrect(W['x'], C[1] - h / 2, W['w'], h, W['r'] * (1 - close), fill='bg', fill_alpha=0.84 * (1 - close),
                      stroke='line', width=1.5, shadow=1 - close)
            ctx.rrect(W['x'], C[1] - h / 2, W['w'], h, W['r'] * (1 - close), fill=None, stroke='text', width=1.5 + 1.5 * edge,
                      stroke_alpha=0.7 * edge)
        else:
            hot = pulse(s - 4.4, 2.5)
            with ctx.glow('text', 22, 0.7 * hot):
                ctx.line(W['x'], C[1], W['x'] + W['w'], C[1], color='text', alpha=0.6 + 0.4 * hot, width=2 + 2 * hot)
        if undraw < 1:    # the second outline, taken back the way it was drawn
            pts = rrect_pts(W['x'] - 10, W['y'] - 10, W['w'] + 20, W['h'] + 20, W['r'] + 8)
            with ctx.glow('text', 14, 0.5 * (1 - off)):
                ctx.poly(partial(pts, 1 - undraw), color='text', width=3, alpha=0.95 * (1 - 0.6 * off))
        e = prog(s, 1.9, 2.4)
        a = 1 - e
        dy = 22 * ease_in(e)
        y0 = C[1] + 120 + dy
        ctx.rrect(C[0] - 280, y0, 560, 64, 18, fill='raised', stroke='line', alpha=a, shadow=0.6)
        ctx.text(f'{text(2).lower()} layer', C[0] - 250, y0 + 41, size=22, font='mono', color='sub', alpha=a)
        ctx.rrect(C[0] + 190, y0 + 15, 62, 34, 17, fill='line', alpha=a)
        ctx.rrect(C[0] + 190, y0 + 15, 62, 34, 17, fill='text', alpha=a * (1 - off))
        ctx.circle(C[0] + 235 - 28 * ease_back(prog(s, 0.7, 1.2)), y0 + 32, 12, fill=True, color='bg', alpha=a)
        log(ctx, t, [('composer: waiting for input', D0 + 0.2 * P)], W['x'] + 46, W['y'] + 56)
        composer(ctx, CBOX, placeholder=HOLD, t=t, focus=1, send='off', label='')

    # ------------------------------------------------------------------ the last command
    def last_pal(t, u):
        return ('ash', 'dead', lerp(DRAIN, 1, ease_in_out(prog(t, OFF, OFF + 0.8))))

    def last_cam(t, f, u):
        return {'zoom': 1.12 + 0.08 * ease_out(prog(t, E0, OFF + 1))}

    def last(ctx, t, f, u):
        SYL = [cue(f'endSyl{n}', E0 + 0.25 * n) for n in (1, 2, 3, 4)]
        t_run, t_out = SYL[2], Bt(447)
        down = t - OFF
        if down > 1.3:          # black from here on: the credit note has the frame
            return
        with ctx.fade(1 - prog(down, 0.05, 0.8)):
            room(ctx, light=(960, 320), dim=0.8, motif=0.3, t=t)
        up = prog(t, t_run, t_run + 0.22)
        lit = min(up, 1 - prog(t, t_out, OFF - 0.05))
        heat = up * math.exp(-2 * max(0.0, t - t_run - 0.15))
        sx, sy, sr = 960, 170, 74
        sa = clamp(up * 4) * (1 - prog(down, 0, 0.3))
        with ctx.with_pal(('ash', 'on', heat)):
            ctx.radial(sx, sy, 420, 'meDim', 0.5 * heat * sa)
            with ctx.glow('me', 46, 0.7 * heat):
                spark(ctx, sx, sy, sr * (1 + 0.06 * heat + 0.02 * f.get('beatPulse', 0) * lit), lit=lit, grow=0.25 + 0.75 * ease_out(up),
                      off='mute', off_alpha=0.6, rot=0.04 * (t - E0), alpha=sa)
            ctx.flash(0.3 * pulse(t - t_run, 8), 'me')
        # the composer closes into the hairline, the hairline into a point, the point into black
        shut = ease_in(prog(down, 0.15, 0.5))
        half = (CBOX['w'] / 2) * (1 - ease_in_out(prog(down, 0.5, 0.88)))
        dot = 1 - prog(down, 0.9, 1.2)
        cy = 430
        if shut < 1:
            h = 110 * (1 - shut)
            ctx.rrect(960 - CBOX['w'] / 2, cy - h / 2, CBOX['w'], max(2, h), min(22, h / 2), fill='bg', stroke='line',
                      fill_alpha=1 - shut)
        elif half > 1:
            with ctx.glow('text', 16, 0.6):
                ctx.line(960 - half, cy, 960 + half, cy, color='text', width=2.5)
        elif dot > 0:
            ctx.circle(960, cy, 4 * dot, fill=True, color='text', alpha=dot)
        # the command: the word of the loop, in the same face; hollow, then printed solid block by block
        cmd = text(128) if len(env.lyrics.lines) > 128 else 'run'
        size = 60
        cw = ctx.cw(size)
        xr = 960 + (len(cmd) + 2) * cw / 2
        x = xr - (len(cmd) + 2) * cw
        y = cy + 22
        wa = 1 - prog(down, 0.05, 0.4)
        sung_n = sum(1 for v in SYL if t >= v)
        chunks = _chunks(len(cmd), 4)
        filled = chunks[sung_n - 1][1] if sung_n else 0
        entered = t_run <= t < t_run + 0.1
        if wa > 0.01:
            if entered:
                ctx.rrect(x - 24, y - size * 0.95, (len(cmd) + 2) * cw + 48, size * 1.34, 14, fill='text')
            ctx.text('>', x, y, size=size, weight=800, font='mono', color='bg' if entered else 'sub', alpha=wa)
            mono_word(ctx, cmd, xr, y, size, filled=filled, color='bg' if entered else 'text', hollow='sub', alpha=wa)
            if t < t_run and int(t * 5) % 2 == 0:
                ctx.rect(xr + 6, y - size * 0.8, cw * 0.82, size * 0.98, fill=True, color='me', alpha=wa)
            log(ctx, t, [('run: nothing loaded', t_run + 0.16), ('caret: blinking', t_out + 0.05)], x, y + 56, size=20, a=wa)

    return {
        'down-message': {'render': message, 'palette': message_pal},
        'down-params': {'render': params, 'palette': ash, 'camera': params_cam},
        'down-layout': {'render': layout, 'palette': ash},
        'down-power': {'render': power, 'palette': ash},
        'down-last': {'render': last, 'palette': last_pal, 'camera': last_cam},
    }
