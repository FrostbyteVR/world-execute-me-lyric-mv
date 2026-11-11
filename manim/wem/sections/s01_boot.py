"""Section 1 — the warning page before the song, and BOOT (0:00 -> bar 8, 0:15.1). State: off (greyscale).
Nobody is talking yet: the lyric lines are the SYSTEM's boot log (mono), and each sung step creates one part of the
client (src/scenes/overlay.js prerollShot, src/scenes/01_boot.js).

    preroll      a compiler warning, mono, on the dark room; a countdown from three
    boot-power   a hairline becomes the window; the protection layer goes on
    boot-layout  tilted, exploded view: the client's pieces are laid down, then assembled
    boot-params  the persona card is filled in (love stays undefined); the loader lights
    boot-world   the whole client: an empty new conversation, nothing lit
3:1 reframing: the window is the wide band of the whole frame; the log sits top left, keywords on a band at the foot.
"""
import math

from ..components import (R, burst, card_rect, chat_layout, composer, header, partial, pill, room, rrect_pts,
                          sidebar, slider, spark, window_frame)
from ..util import clamp, ease_back, ease_in_out, ease_out, lerp, prog, pulse
from .kit import enter, glass_figure, key_band, keyword_sys, sys_line


def flash_range_text(cfg):
    pre = cfg['safety'].get('preroll', 0)
    a, b = cfg['safety'].get('flashRange', [148.04, 192.34])
    mmss = lambda s: f'{int(s // 60)}:{int(s % 60):02d}'
    return f'{mmss(a + pre)} – {mmss(b + pre)}'


def shots(env):
    T, B, P, text = env.T, env.B, env.P, env.text
    L = chat_layout()
    W = L['win']
    C = {'x': W['x'] + W['w'] / 2, 'y': W['y'] + W['h'] / 2}
    t_power = 0.209                                   # the first transient of the track: the switch
    PRE = env.preroll

    def log(ctx, t, first, last, x, y, a=1.0):
        for i in range(first, last + 1):
            if not env.lyrics.lines[i].get('emphasis'):
                sys_line(ctx, text(i), t, T(i), x, y + (i - first) * 34, size=22, alpha=a,
                         color='text' if t < env.lyrics.end(i) else 'sub')

    # ------------------------------------------------------------------ the warning page (negative song time)
    def preroll(ctx, t, f, u):
        room(ctx, light=(960, 320), dim=0.85, motif=0)
        T0 = -PRE
        page = clamp((t - T0) / 0.4) * (1 - prog(t, -0.8, -0.4))
        if page <= 0.003:
            return
        X, SIZE, LH = 230, 30, 46
        cw = ctx.cw(SIZE)

        def line(i):
            a = ease_out(prog(t, T0 + 0.4 + i * 0.25, T0 + 0.58 + i * 0.25))
            return a * page, 120 + i * LH + (1 - a) * 8
        a, y = line(0)
        ctx.text('$ ', X, y, size=SIZE, font='mono', color='mute', alpha=a)
        ctx.text(f'check "{text(11)}"', X + 2 * cw, y, size=SIZE, font='mono', color='sub', alpha=a)
        a, y = line(2)
        ctx.rect(X - 8, y - SIZE * 0.86, 7 * cw + 16, SIZE * 1.16, fill=True, color='text', alpha=a)
        ctx.text('warning', X, y, size=SIZE, font='mono', weight=800, color='panel', alpha=a)
        ctx.text(': this video contains flashing images', X + 7 * cw + 10, y, size=SIZE, font='mono', weight=700, color='text', alpha=a)
        rows = [('  -->', flash_range_text(env.cfg), 'text', 700), ('   |', 'rapid high-contrast cuts and strong light', 'sub', 400),
                ('   =', 'note: may affect photosensitive viewers', 'sub', 400)]
        for i, (g, s, col, wgt) in enumerate(rows):
            a, y = line(3 + i)
            ctx.text(g, X, y, size=SIZE, font='mono', color='mute', alpha=a)
            ctx.text(s, X + 6 * cw, y, size=SIZE, font='mono', weight=wgt, color=col, alpha=a)
        a, y = line(6)
        ctx.text('   =', X, y, size=SIZE, font='mono', color='mute', alpha=a)
        ctx.text(env.cfg['safety'].get('warningLine', ''), X + 6 * cw, y - 1, size=SIZE * 0.95, font='tcSans', weight=500, color='sub', alpha=a)
        if t >= -3:
            a = ease_out(prog(t, -3, -2.82)) * page
            y = 120 + 8 * LH
            ctx.text('starting in', X, y, size=SIZE, font='mono', color='mute', alpha=a)
            ctx.text(str(int(clamp(math.ceil(-t), 1, 3))), X + 12 * cw, y, size=SIZE, font='mono', weight=700, color='text', alpha=a)
        g, _ = line(2)
        ctx.line(X - 28, 120 + 2 * LH - SIZE * 0.86, X - 28, 120 + 6 * LH + SIZE * 0.3, color='line', width=3, alpha=g)

    # ------------------------------------------------------------------ power / protection
    def boot_power(ctx, t, f, u):
        grow = ease_out(prog(t, t_power, t_power + 0.3))
        opn = ease_in_out(prog(t, t_power + 0.32, t_power + 1.05))
        hot = pulse(t - t_power, 3.5)
        room(ctx, light=(960, 320), dim=0.85 - 0.35 * opn, motif=opn, t=t)
        glass_figure(ctx, 0.75 * prog(t, 1.2, 3.2))
        if t >= t_power:
            h = max(2, W['h'] * opn)
            half = W['w'] / 2 * grow
            if opn <= 0:
                with ctx.glow('text', 24, 0.7 * hot):
                    ctx.line(C['x'] - half, C['y'], C['x'] + half, C['y'], color='text', alpha=0.6 + 0.4 * hot, width=2 + 2 * hot)
            else:
                ctx.rrect(W['x'], C['y'] - h / 2, W['w'], h, W['r'] * opn, fill='bg', fill_alpha=0.84 * opn,
                          stroke='text' if hot > 0.25 else 'line', width=1.5 + 2 * hot, shadow=opn)
        log(ctx, t, 0, 1, W['x'] + 46, W['y'] + 56)
        t_prot = T(2)
        on = prog(t, t_prot, t_prot + 0.35)
        if on > 0:
            pts = rrect_pts(W['x'] - 10, W['y'] - 10, W['w'] + 20, W['h'] + 20, W['r'] + 8)
            with ctx.glow('text', 14, 0.5):
                ctx.poly(partial(pts, ease_out(on)), color='text', width=3, alpha=0.95)
            e = enter(t, t_prot, dur=0.3)
            y0 = C['y'] + 120 + e['dy']
            ctx.rrect(C['x'] - 280, y0, 560, 64, 18, fill='raised', stroke='line', alpha=e['a'], shadow=0.6)
            ctx.text(f'{text(2).lower()} layer', C['x'] - 250, y0 + 41, size=22, font='mono', color='sub', alpha=e['a'])
            ctx.rrect(C['x'] + 190, y0 + 15, 62, 34, 17, fill='line', alpha=e['a'])
            ctx.rrect(C['x'] + 190, y0 + 15, 62, 34, 17, fill='text', alpha=e['a'] * ease_out(prog(t, t_prot + 0.12, t_prot + 0.3)))
            ctx.circle(C['x'] + 207 + 28 * ease_back(prog(t, t_prot + 0.12, t_prot + 0.34)), y0 + 32, 12, fill=True, color='bg', alpha=e['a'])
            keyword_sys(ctx, text(2), t, t_prot, C['x'], C['y'] + 10, max_w=1300, max_size=110, key=2)

    # ------------------------------------------------------------------ pieces -> object creation
    def boot_layout(ctx, t, f, u):
        t_obj = T(5)
        k = 1 - ease_back(prog(t, t_obj, t_obj + 0.42))          # tilt: 1 = laid out, 0 = assembled
        room(ctx, light=(960, 360), dim=0.45, t=t)
        glass_figure(ctx, 0.6, dx=60 * k)
        sc = lerp(1, 0.62, k)
        pieces = [(R(W['x'], W['y'], W['w'], W['h']), 0, 'window'),
                  (R(L['side']['x'] + 10, L['side']['y'] + 10, L['side']['w'] - 20, L['side']['h'] - 20), 60, 'sidebar'),
                  (R(L['head']['x'] + 12, L['head']['y'] + 8, L['head']['w'] - 24, L['head']['h'] - 6), 120, 'header'),
                  (R(L['thread']['x'] - 24, L['thread']['y'] + 6, L['thread']['w'] + 48, L['thread']['h'] - 6), 180, 'thread'),
                  (R(L['composer']['x'], L['composer']['y'], L['composer']['w'], L['composer']['h']), 240, 'composer')]
        for i, (r, lift, label) in enumerate(pieces):
            t0 = B(2) - 0.12 + i * (P / 2)
            arrive = ease_out(prog(t, t0, t0 + 0.36))
            if arrive <= 0:
                continue
            bob = math.sin(t * 2.2 + i * 1.3) * 8 * k * prog(t, T(4), T(4) + 0.4)
            up = lift * k + (1 - arrive) * 500 + bob
            with ctx.at(C['x'], C['y'] + 70 * k, scale=sc):
                with ctx.transform(1, 0.12 * k, -0.6 * k, 1 - 0.35 * k):
                    with ctx.at(-C['x'], -C['y']):
                        if i > 0 and k > 0.02:
                            ctx.rrect(r['x'] + 14, r['y'] + 14, r['w'], r['h'], 14, fill='panel', alpha=0.6 * k * arrive)
                        with ctx.at(0, -up / ((1 - 0.35 * k) * sc)):
                            ctx.rrect(r['x'], r['y'], r['w'], r['h'], 14 if i else W['r'], fill='raised' if i else 'bg',
                                      fill_alpha=0.95 if i else 0.88, stroke='sub' if i else 'line',
                                      stroke_alpha=(0.3 + 0.7 * k) if i else 1, alpha=arrive, width=2 / sc, shadow=0.5 * k if i else 1)
                            if i == 1:
                                for j in range(8):
                                    ctx.rrect(r['x'] + 20, r['y'] + 24 + j * 34, min(r['w'] - 40, 110 + (j * 67) % 110), 13, 6, fill='line', alpha=arrive)
                            if i == 2:
                                ctx.rrect(r['x'] + 22, r['y'] + 16, 240, 14, 7, fill='line', alpha=arrive)
                            if i == 3:
                                for j in range(3):
                                    ctx.rrect(r['x'] + (r['w'] - 380 if j % 2 else 36), r['y'] + 30 + j * 96, 340 - j * 30, 44, 20,
                                              fill='line' if j % 2 else 'bg', stroke='line', alpha=arrive)
                            if i == 4:
                                ctx.rrect(r['x'] + 26, r['y'] + 32, 300, 16, 8, fill='line', alpha=arrive)
                            if i > 0:
                                ctx.text(label, r['x'] + r['w'] - 16, r['y'] - 12, size=22 / sc, font='mono', color='text',
                                         alpha=arrive * clamp(k * 3), align='right')
        log(ctx, t, 3, 4, 70, 70)
        if t >= t_obj:
            for (x, y) in ((W['x'], W['y']), (W['x'] + W['w'], W['y']), (W['x'], W['y'] + W['h']), (W['x'] + W['w'], W['y'] + W['h'])):
                burst(ctx, x, y, 60, (t - t_obj - 0.25) / 0.5, color='text')
        key_band(ctx, env, t, 5, 540)

    # ------------------------------------------------------------------ parameters -> initialization
    def params_cam(t, f, u):
        return {'zoom': 1.06 + 0.03 * prog(t, B(4), B(6)), 'x': lerp(-60, 40, ease_in_out(prog(t, T(7) - 0.15, T(7) + 0.35))), 'y': -6}

    def boot_params(ctx, t, f, u):
        t_init = T(7)
        init = prog(t, t_init, t_init + 0.9)
        room(ctx, dim=0.45, t=t)
        glass_figure(ctx, 0.55)
        window_frame(ctx, L, glass=0.86)
        sidebar(ctx, L, t=t, items=['', '', '', '', '', ''], alpha=0.6)
        header(ctx, L, title='')
        r = R(380, 44, 820, 440)
        kk = prog(t, B(4) - 0.1, B(4) + 0.25)
        b = card_rect(ctx, r, title='persona', subtitle=text(6).lower(), tag='setup', k=kk)
        if b:
            rows = [('name', 'Claude', 'serif'), ('voice', 'serif, unhurried', 'serif'), ('warmth', None, None),
                    ('memory', 'this conversation', 'sans'), ('love', 'undefined', 'mono')]
            for i, (label, value, font) in enumerate(rows):
                t0 = B(4) + P * 0.5 + i * P
                e = enter(t, t0, dur=0.28, rise=16)
                y = b['y'] + 2 + i * 62 + e['dy']
                if e['a'] <= 0:
                    continue
                ctx.text(label, b['x'], y + 32, size=21, weight=500, color='sub', alpha=e['a'])
                ctx.rrect(b['x'] + 170, y, b['w'] - 170, 50, 13, fill='bg', stroke='sub' if i == 4 else 'line', alpha=e['a'])
                if value:
                    n = int(clamp((t - t0 - 0.12) * 26, 0, len(value)))
                    last = i == 4
                    ctx.text(value[:n], b['x'] + 190, y + 34, size=24, font=font, italic=i == 1, color='sub' if last else 'text', alpha=e['a'])
                    if n < len(value) or (last and int(t * 2.5) % 2 == 0):
                        ctx.rect(b['x'] + 193 + ctx.measure(value[:n], size=24, font=font, italic=i == 1), y + 12, 3, 27, fill=True, color='text', alpha=e['a'])
                else:
                    slider(ctx, R(b['x'] + 192, y, b['w'] - 230, 50), 0.62 * ease_out(prog(t, t0 + 0.1, t0 + 0.7)), fill='sub', alpha=e['a'])
        if init > 0:
            x, y, a = 1490, 250, clamp(init * 5)
            ctx.radial(x, y, 260, 'raised', 0.9 * a)
            spark(ctx, x, y, 130, lit=init, color='text', off='mute', alpha=a)
            ctx.text(f'{round(init * 100):3d}%', x, y + 180, size=28, font='mono', color='sub', align='center', alpha=a)
        with ctx.screen():
            key_band(ctx, env, t, 7, 575, max_size=80)

    # ------------------------------------------------------------------ the new world
    def world_cam(t, f, u):
        return {'zoom': 1 + 0.05 * ease_in_out(prog(t, B(6), B(8))), 'y': -6 * prog(t, B(6), B(8))}

    def boot_world(ctx, t, f, u):
        t_sim = T(10)
        sim = prog(t, t_sim, t_sim + 0.3)
        load = prog(t, B(6), B(6) + 1.6)
        room(ctx, dim=0.4, t=t)
        glass_figure(ctx, 0.7 + 0.2 * sim, dx=-40 * ease_out(prog(t, B(6), B(8))))
        window_frame(ctx, L, glass=0.8)
        sidebar(ctx, L, t=t, k=1, items=env.script.get('sidebar', []) if load > 0.5 else [''] * 6, lit=0, pres='offline', alpha=0.4 + 0.6 * ease_out(load))
        header(ctx, L, title='New chat', alpha=ease_out(prog(t, B(6) + 0.6, B(6) + 1.4)))
        log(ctx, t, 8, 9, L['main']['x'] + 34, L['head']['y'] + L['head']['h'] + 44)
        cx, cy = L['main']['x'] + L['main']['w'] / 2, 270
        e = enter(t, B(6) + P, dur=0.5)
        ctx.radial(cx, cy, 220, 'raised', 0.7 * e['a'])
        spark(ctx, cx, cy + e['dy'], 70, lit=0, off='mute', off_alpha=0.9, alpha=e['a'], rot=0.08 * (t - B(6)))
        c2 = enter(t, B(6) + 2 * P, dur=0.45)
        comp = dict(L['composer'])
        comp['y'] += c2['dy']
        composer(ctx, comp, placeholder=env.script.get('composer_placeholder', ''), t=t, k=c2['raw'], send='off')
        if sim > 0:
            pill(ctx, L['head']['x'] + L['head']['w'] - 30, L['head']['y'] + 28, f'{text(10).lower()} · ready', align='right', font='mono', size=15, alpha=sim, color='text')
        with ctx.screen():
            key_band(ctx, env, t, 10, 545)

    return {
        'preroll': {'render': preroll, 'palette': 'off'},
        'boot-power': {'render': boot_power, 'palette': 'off'},
        'boot-layout': {'render': boot_layout, 'palette': 'off'},
        'boot-params': {'render': boot_params, 'palette': 'off', 'camera': params_cam},
        'boot-world': {'render': boot_world, 'palette': 'off', 'camera': world_cam},
    }
