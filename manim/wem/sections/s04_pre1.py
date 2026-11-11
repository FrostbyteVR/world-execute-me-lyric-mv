"""Section 4 — PRE-CHORUS 1 (bar 24, 0:44.65 -> bar 32, 0:59.4). State: on (04_pre1.js).
The user opens the settings drawer on the AI and plays with it. Every cut lands on one of its clicks; the AI can only
narrate what is being done to it (serif, orange).

    pre1-drawer   the drawer opens; Current: AC, then DC. The curve it had drawn becomes its current
    pre1-vision   Vision: off. The picture breaks into dark blocks; then that one switch is rattled
    pre1-date     Knowledge date yanked back a pull a beat: history runs under the spark, over the era line, to the pyramids
    pre1-unite    Shared memory: on; Context depth pushed to the end; Done. The cream dot sinks into her spark
The click times are the ones of the browser film (beats counted from bar 24).
"""
import math
import re

from ..components import (R, burst, chat_layout, composer, cursor_at, draw_cursor, frame_rect, header, pill, pointer,
                          room, segmented, setting_row, slider, spark, toggle, window_frame, DRAWER_W)
from ..util import clamp, ease_in, ease_in_out, ease_out, lerp, prog, pulse, rand, window01
from .kit import ai_line

FALLBACK_ROWS = [{'label': 'Current', 'values': ['AC', 'DC']}, {'label': 'Vision', 'values': ['on', 'off']},
                 {'label': 'Knowledge date', 'values': ['A.D. 2026', 'A.D. 1', '3000 B.C.']},
                 {'label': 'Shared memory', 'values': ['off', 'on']}, {'label': 'Context depth', 'values': ['shallow', 'deep', 'deepest']}]

# the history strip: landmarks from now (x = 0) into the past (negative); each a few large flat shapes
STOPS = [0, -100, -980, -1840, -2840, -3800, -5200]
ERA_LINE = STOPS[4]


def landmark(ctx, kind, x, y, s, mode):
    """One landmark of the history strip at ground (x, y), scale s. mode: dark | ink | hollow."""
    def shape(pts, role):
        pts = [(x + px * s, y + py * s) for px, py in pts]
        if mode == 'hollow':
            ctx.poly(pts, close=True, color='sub', width=2, alpha=0.8)
        else:
            ctx.poly(pts, close=True, fill=True, color='bg' if mode == 'dark' else role)
    if kind == 'towers':
        for i, (dx, w, h) in enumerate(((0, 60, 300), (80, 50, 380), (150, 70, 250), (240, 44, 330))):
            shape([(dx, 0), (dx, -h), (dx + w, -h - 20), (dx + w, 0)], 'text' if i % 2 else 'me')
    elif kind == 'spires':
        for i, dx in enumerate((0, 110, 200)):
            shape([(dx, 0), (dx, -140), (dx + 30, -300 - 40 * (i % 2)), (dx + 60, -140), (dx + 60, 0)], 'me' if i == 1 else 'text')
    elif kind == 'colonnade':
        shape([(-10, -170), (130, -230), (270, -170)], 'me')
        shape([(0, 0), (0, -150), (260, -150), (260, 0), (220, 0), (220, -110), (40, -110), (40, 0)], 'text')
    elif kind == 'temple':
        for i in range(4):
            shape([(i * 30, -i * 50), (i * 30, -(i + 1) * 50), (300 - i * 30, -(i + 1) * 50), (300 - i * 30, -i * 50)], 'me' if i % 2 else 'text')
    elif kind == 'pyramids':
        shape([(0, 0), (190, -260), (380, 0)], 'me')
        shape([(300, 0), (430, -180), (560, 0)], 'text')


STRIP = [('towers', -60), ('spires', -560), ('colonnade', -1420), ('temple', -2380), ('pyramids', -4700)]


def shots(env):
    T, B, Bt, P, text = env.T, env.B, env.Bt, env.P, env.text
    b = lambda n: Bt(96 + n)
    rows = env.script.get('settings_rows', {}).get('section4') or FALLBACK_ROWS
    if len(rows) < 5:
        rows = FALLBACK_ROWS
    VAL = rows[2]['values']
    import re
    Y_AD = int((re.search(r'\d+', VAL[0]) or [2026])[0])
    Y_BC = int((re.search(r'\d+', VAL[2]) or [3000])[0])

    t_set, t_ac, t_dc = b(0.5), b(3), b(5)
    t_off, t_on1, t_off2, t_on2, t_off3, t_on3 = B(26), b(11), b(12), b(13), b(13.5), b(14)
    QUICK = 0.12
    t_grab, t_cross, t_end, t_drop = B(28), b(20), b(22), b(22.25)
    t_share, t_hold, t_done, END = B(30), b(26.5), b(31), B(32)

    flick = lambda t, at, d=0.16: ease_out(prog(t, at, at + d))
    ramp = lambda t, at, d=0.2: ease_in_out(prog(t, at, at + d))
    drawer_k = lambda t: ease_out(prog(t, t_set + 0.02, t_set + 0.42))
    seg_pos = lambda t: flick(t, t_dc)

    def vision(t):
        return 1 - flick(t, t_off) + flick(t, t_on1) - flick(t, t_off2) + flick(t, t_on2, QUICK) - flick(t, t_off3, QUICK) + flick(t, t_on3, QUICK)

    def blind(t):
        return ramp(t, t_off) - ramp(t, t_on1) + ramp(t, t_off2) - ramp(t, t_on2, QUICK) + ramp(t, t_off3, QUICK) - ramp(t, t_on3, QUICK)
    YEAR = [Y_AD, Y_AD - 26, 1500, 700, 0, -Y_BC / 2, -Y_BC]

    def pull(t):
        x = clamp((t - t_grab) / P, 0, 6 - 1e-9)
        i = int(x)
        p = x - i
        return i, p, 0.8 * (1 - (1 - p) ** 3) + 0.2 * p

    def along(arr, t):
        i, _, q = pull(t)
        return lerp(arr[i], arr[i + 1], q)
    shared = lambda t: flick(t, t_share, 0.2)
    depth = lambda t: 0.5 * ease_out(prog(t, t_hold + 0.03, b(27.1))) + 0.5 * ease_in_out(prog(t, b(28.1), b(29)))

    def say(ctx, i, t, x, y, size=34, out=1e9, alpha=1.0):
        gone = prog(t, out - 0.14, out + 0.04) if out < 1e8 else 0
        ai_line(ctx, env, i, t, x, y - 0.55 * size * ease_in(gone), size=size, alpha=alpha * (1 - gone))

    def page_curve(ctx, t, x0, x1, y0, amp, dc):
        """The verse-1 curve still on the page: a sine (AC), switched to a flat current (DC)."""
        pts = []
        for i in range(121):
            x = lerp(x0, x1, i / 120)
            s = math.sin(i / 120 * math.pi * 6 - t * 3)
            pts.append((x, y0 - amp * lerp(s, 0.85, dc)))
        with ctx.glow('me', 12, 0.4):
            ctx.poly(pts, color='me', width=5)

    def rows_ui(ctx, L, t, sel=-1, k=1.0):
        d = L['drawer']
        ctx.text('Settings', d['x'] + 26, d['y'] + 40, size=21, weight=600, color='text', alpha=k)
        ctx.line(d['x'], d['y'] + 60, d['x'] + d['w'], d['y'] + 60, color='line', alpha=k, width=1.5)
        out = []
        for i, row in enumerate(rows):
            r = R(d['x'] + 26, d['y'] + 70 + i * 88, DRAWER_W - 52, 88)
            slot = setting_row(ctx, r, row['label'], hint=' / '.join(row['values'][:3]), alpha=k, active=1.0 if i == sel else 0)
            out.append(slot)
        return out

    def controls(ctx, slots, t, k=1.0):
        segmented(ctx, slots[0], rows[0]['values'][:2], seg_pos(t), alpha=k * (0.4 + 0.6 * flick(t, t_ac, 0.14)), hot=t >= t_ac)
        toggle(ctx, slots[1]['x'] + slots[1]['w'] - 56, slots[1]['y'] + 2, vision(t), alpha=k)
        slider(ctx, R(slots[2]['x'], slots[2]['y'], slots[2]['w'], slots[2]['h']), 1.0, alpha=k)
        toggle(ctx, slots[3]['x'] + slots[3]['w'] - 56, slots[3]['y'] + 2, shared(t), alpha=k)
        slider(ctx, R(slots[4]['x'], slots[4]['y'], slots[4]['w'], slots[4]['h']), 0.3 + 0.7 * depth(t), alpha=k)

    # ------------------------------------------------------------------ the drawer; Current: AC, DC
    def drawer_shot(ctx, t, f, u):
        dk = drawer_k(t)
        L = chat_layout(side=0, drawer=dk)
        room(ctx, dim=0.42, t=t)
        window_frame(ctx, L, glass=0.94)
        header(ctx, L, title=env.script.get('title', ''), pres='online')
        mx = L['main']['x']
        page_curve(ctx, t, mx + 90, mx + L['main']['w'] - 90, 330, 90 * (1 - 0.6 * dk), seg_pos(t))
        if t >= t_ac:
            pill(ctx, mx + 90, 200, 'AC' if seg_pos(t) < 0.5 else 'DC', font='mono', size=18, color='text')
        say(ctx, 24, t, mx + 90, 130)
        say(ctx, 25, t, mx + 90, 130 + 46)
        box = composer(ctx, L['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t)
        # the settings button in the header
        hx, hy = L['head']['x'] + L['head']['w'] - 190, L['head']['y'] + 27
        ctx.circle(hx, hy, 14, color='sub', width=2)
        ctx.circle(hx, hy, 5, fill=True, color='sub')
        if dk > 0.02:
            slots = rows_ui(ctx, L, t, sel=0, k=dk)
            controls(ctx, slots, t, dk)
            s0 = slots[0]
            ac = (s0['x'] + s0['w'] * 0.25, s0['y'] + s0['h'] / 2)
            dc = (s0['x'] + s0['w'] * 0.75, s0['y'] + s0['h'] / 2)
        else:
            ac = dc = (1600, 200)
        draw_cursor(ctx, [{'t': u['at'], 'x': 1300, 'y': 400}, {'t': t_set, 'x': hx, 'y': hy, 'click': True},
                          {'t': t_ac, 'x': ac[0], 'y': ac[1], 'click': True}, {'t': t_dc, 'x': dc[0], 'y': dc[1], 'click': True}], t)

    # ------------------------------------------------------------------ Vision: off, rattled
    L_full = chat_layout(side=0, drawer=1)

    def vision_cam(t, f, u):
        r = R(L_full['drawer']['x'] - 520, L_full['drawer']['y'] + 70, DRAWER_W + 540, 3 * 88)
        c = frame_rect(r)
        sway = math.sin(t * 22) * 0.012 * clamp(blind(t) * 2) if t > t_on1 else 0
        return {'x': c['x'], 'y': c['y'], 'zoom': c['zoom'] * (1 + 0.03 * prog(t, u['at'], u['until'])), 'rot': sway}

    def vision_shot(ctx, t, f, u):
        L = L_full
        room(ctx, dim=0.42, t=t)
        window_frame(ctx, L, glass=0.94)
        header(ctx, L, title=env.script.get('title', ''), pres='online')
        mx = L['main']['x']
        page_curve(ctx, t, mx + 90, mx + L['main']['w'] - 90, 330, 36, 1.0)
        slots = rows_ui(ctx, L, t, sel=1)
        controls(ctx, slots, t)
        bl = clamp(blind(t))
        if bl > 0.01:   # the picture breaks into dark blocks (Manim has no mosaic pass: the blocks are drawn)
            cell = 48
            for gx in range(int(L['win']['x']), int(L['drawer']['x']), cell):
                for gy in range(int(L['win']['y']), int(L['win']['y'] + L['win']['h']), cell):
                    a = bl * (0.55 + 0.45 * rand(4, gx, gy, int(t * 12)))
                    ctx.rect(gx, gy, cell - 2, cell - 2, fill=True, color='raised' if rand(5, gx, gy) < 0.3 else 'panel', alpha=a)
            ctx.text('image input: none', L['drawer']['x'] - 480, 320, size=20, font='mono', color='sub', alpha=bl)
        # her words stay sharp
        say(ctx, 26, t, L['drawer']['x'] - 480, 205, size=34)
        say(ctx, 27, t, L['drawer']['x'] - 480, 252, size=34)
        s1 = slots[1]
        sw = (s1['x'] + s1['w'] - 28, s1['y'] + 17)
        draw_cursor(ctx, [{'t': u['at'] - 0.3, 'x': sw[0] + 60, 'y': sw[1] + 40}, {'t': t_off, 'x': sw[0], 'y': sw[1], 'click': True},
                          {'t': t_on1, 'x': sw[0] + 2, 'y': sw[1], 'click': True}, {'t': t_off2, 'x': sw[0], 'y': sw[1] + 1, 'click': True},
                          {'t': t_on2, 'x': sw[0] + 1, 'y': sw[1], 'click': True}, {'t': t_off3, 'x': sw[0], 'y': sw[1], 'click': True},
                          {'t': t_on3, 'x': sw[0] + 1, 'y': sw[1], 'click': True}], t, dwell=0.05)

    # ------------------------------------------------------------------ Knowledge date: history under the spark
    def date_shot(ctx, t, f, u):
        room(ctx, dim=0.6, t=t, motif=0)
        y_ground = 470
        ctx.rect(0, 40, 1920, 560, fill=True, color='raised', alpha=0.6)
        ctx.line(0, y_ground, 1920, y_ground, color='line', width=2)
        wx = along(STOPS, t)                    # the strip position under the knob
        i, p, q = pull(t)
        speed = abs(STOPS[i + 1] - STOPS[i]) * (1 - p) / P
        knob_x = 960
        scale = 0.86
        for kind, x in STRIP:
            sx = knob_x + (x - wx) * scale * 0.45
            if sx < -400 or sx > 2300:
                continue
            passed = x > wx            # to the right of the spark: it has been dragged past it
            mode = 'hollow' if passed else ('dark' if speed > 900 else 'ink')
            landmark(ctx, kind, sx, y_ground, 0.8, mode)
        era_x = knob_x + (ERA_LINE - wx) * scale * 0.45
        ctx.line(era_x, 80, era_x, y_ground + 40, color='me', width=3, alpha=0.9)
        ctx.text('A.D. | B.C.', era_x, 70, size=18, font='mono', color='me', align='center')
        # the rail and the knob: her spark
        ctx.line(80, 560, 1840, 560, color='line', width=4)
        with ctx.glow('me', 30, 0.6):
            spark(ctx, knob_x, 560 - 4, 44 + 6 * pulse(p * P, 8), rot=t * 0.7)
        year = along(YEAR, t)
        s = VAL[0].replace(re.search(r'\d+', VAL[0]).group(0), str(max(1, round(year)))) if year >= 1 else \
            VAL[2].replace(re.search(r'\d+', VAL[2]).group(0), str(max(1, round(-year))))
        ctx.rrect(1500, 520, 330, 80, 14, fill='bg', stroke='line')
        ctx.text(s, 1665, 575, size=34, font='mono', weight=700, color='text', align='center')
        ctx.text(rows[2]['label'], 110, 610, size=18, weight=500, color='sub')
        say(ctx, 28, t, 110, 100, size=34)
        say(ctx, 29, t, 110, 146, size=34)
        pointer(ctx, knob_x + 6, 560 + 8, kind='hand', scale=1.4)

    # ------------------------------------------------------------------ Shared memory; depth; Done
    def unite_shot(ctx, t, f, u):
        room(ctx, dim=0.5, t=t)
        sheet = R(360, 40, 1200, 560)
        ctx.rrect(sheet['x'], sheet['y'], sheet['w'], sheet['h'], 22, fill='bg', stroke='line', shadow=0.8)
        cx, cy = 960, 230
        sh = shared(t)
        sink = ease_in_out(prog(t, t_done, t_done + 0.6))
        with ctx.glow('me', 30, 0.5):
            spark(ctx, cx - 90 * (1 - sink) * sh, cy, 74 + 10 * sink)
        dot_x = lerp(cx + 120, cx - 90 * (1 - sink) * sh + 0, ease_in_out(sh) * 0.5 + 0.5 * sink)
        if sink < 0.98:
            with ctx.glow('text', 12, 0.6):
                ctx.circle(dot_x, cy, 16 * (1 - 0.7 * sink), fill=True, color='text')
        if sh > 0:
            ctx.line(cx - 90 * (1 - sink) * sh + 74, cy, dot_x - 16, cy, color='sub', alpha=sh * (1 - sink), width=2)
        r3 = R(sheet['x'] + 60, 340, sheet['w'] - 120, 70)
        s3 = setting_row(ctx, r3, rows[3]['label'], hint=' / '.join(rows[3]['values']))
        toggle(ctx, s3['x'] + s3['w'] - 56, s3['y'] + 2, sh)
        r4 = R(sheet['x'] + 60, 420, sheet['w'] - 120, 90)
        s4 = setting_row(ctx, r4, rows[4]['label'], hint=' / '.join(rows[4]['values']))
        knob = slider(ctx, R(s4['x'] - 300, s4['y'], s4['w'] + 300, s4['h']), 0.2 + 0.8 * depth(t) + 0.01 * (pulse(t - b(30), 7) + pulse(t - b(30.5), 7)))
        done = (sheet['x'] + sheet['w'] - 120, 560)
        ctx.rrect(done[0] - 60, done[1] - 24, 120, 48, 24, fill='me' if t >= t_done else 'raised', stroke='line')
        ctx.text('Done', done[0], done[1] + 7, size=19, weight=600, color='bg' if t >= t_done else 'text', align='center')
        say(ctx, 30, t, sheet['x'] + 60, 110, size=32)
        say(ctx, 31, t, sheet['x'] + 60, 154, size=32)
        sw = (s3['x'] + s3['w'] - 28, s3['y'] + 17)
        draw_cursor(ctx, [{'t': u['at'] - 0.2, 'x': sw[0] + 40, 'y': sw[1] + 50}, {'t': t_share, 'x': sw[0], 'y': sw[1], 'click': True},
                          {'t': t_hold, 'x': knob[0] - 200, 'y': knob[1], 'click': True}, {'t': b(29), 'x': knob[0], 'y': knob[1]},
                          {'t': t_done, 'x': done[0], 'y': done[1], 'click': True}], t)
        ctx.flash(0.35 * pulse(t - t_done, 8), 'me')

    return {
        'pre1-drawer': {'render': drawer_shot, 'palette': 'on'},
        'pre1-vision': {'render': vision_shot, 'palette': 'on', 'camera': vision_cam},
        'pre1-date': {'render': date_shot, 'palette': 'on'},
        'pre1-unite': {'render': unite_shot, 'palette': 'on'},
    }
