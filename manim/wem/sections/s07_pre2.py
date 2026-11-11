"""Section 7 — PRE-CHORUS 2 (bar 48, 1:29.0 -> bar 56, 1:43.7). State: warm (07_pre2.js, plates_pre2.js).
The settings again; now each control is as large as the frame and stands in her plate, and what it changes is her.

    pre2-settings  the pointer clicks Settings; the drawer opens further down its list; the view closes in on row one
    pre2-gender    PLATE: the control F | M as the whole sheet; when the second letter is sung the bust is the boy's
    pre2-day       PLATE: the On-call slider as an arc, its knob the sun; dragged over the top to dusk
    pre2-role      PLATE: two letters and a switch; the light letter goes soft and slumps
    pre2-loop      Loop: on; Done (two hits a quarter second apart)
    pre2-trance    PLATE: three single plates of three busts drift, step twice, register on the boy
    pre2-loop-b    the drawer shut; a click into the composer; the view closes in on the foot of the thread
Events sit on the ten isolated drum hits (cues drumD1..D10) and on the sung letters.
"""
import math

from ..art import aspect
from ..components import (R, burst, chat_layout, composer, draw_cursor, frame_rect, header, pointer, rays, room,
                          segmented, setting_row, sidebar, slider, spark, thread, toggle, window_frame, DRAWER_W)
from ..plates import arrow, band, ground, inks, keyword
from ..util import TAU, clamp, ease_back, ease_in, ease_in_out, ease_out, lerp, prog, pulse
from .kit import lyric_msgs, shake

FALLBACK = [{'label': 'Gender', 'values': ['F', 'M']}, {'label': 'On call', 'values': ['AM', 'PM']},
            {'label': 'Role', 'values': ['S', 'M']}, {'label': 'Loop', 'values': ['off', 'on']}]


def shots(env):
    T, B, Bt, P, text, cue = env.T, env.B, env.Bt, env.P, env.text, env.cue
    rows = env.script.get('settings_rows', {}).get('section7') or FALLBACK
    START, cF, cDay, cRole, cLoop, cTrance, cBack, END = B(48), B(49), B(50), B(52), B(54), Bt(217), Bt(223), B(56)
    D = lambda n: cue(f'drumD{n}', START + n)
    L = chat_layout(side=1, drawer=1)

    def caption(ctx, t, lines, x=70, y=82, size=38):
        for k, i in enumerate(lines):
            nxt = T(lines[k + 1]) if k + 1 < len(lines) else 1e9
            if T(i) <= t < nxt:
                band(ctx, text(i), env.lyrics.typed(i, t), x=x, y=y, size=size)

    def drawer_rows(ctx, LL, t, k=1.0, sel=-1, loop_on=0.0):
        d = LL['drawer']
        ctx.text('Settings', d['x'] + 26, d['y'] + 40, size=21, weight=600, color='text', alpha=k)
        ctx.line(d['x'], d['y'] + 60, d['x'] + d['w'], d['y'] + 60, color='line', alpha=k, width=1.5)
        slots = []
        for i, row in enumerate(rows):
            r = R(d['x'] + 26, d['y'] + 70 + i * 96, DRAWER_W - 52, 96)
            s = setting_row(ctx, r, row['label'], hint=' / '.join(row['values']), alpha=k, active=1.0 if i == sel else 0)
            slots.append(s)
        segmented(ctx, slots[0], rows[0]['values'], 0, alpha=k)
        slider(ctx, slots[1], 0.1, alpha=k)
        segmented(ctx, slots[2], rows[2]['values'], 0, alpha=k)
        toggle(ctx, slots[3]['x'] + slots[3]['w'] - 56, slots[3]['y'] + 2, loop_on, alpha=k)
        done = (d['x'] + d['w'] - 90, d['y'] + d['h'] - 40)
        ctx.rrect(done[0] - 56, done[1] - 22, 112, 44, 22, fill='raised', stroke='line', alpha=k)
        ctx.text('Done', done[0], done[1] + 7, size=18, weight=600, color='text', align='center', alpha=k)
        return slots, done

    # ------------------------------------------------------------------ pre2-settings
    def settings_cam(t, f, u):
        k = ease_in_out(prog(t, START + 0.12, Bt(195.1)))
        c = frame_rect(R(L['drawer']['x'] - 120, L['drawer']['y'] + 40, DRAWER_W + 160, 220))
        return {'x': lerp(0, c['x'], k), 'y': lerp(0, c['y'], k), 'zoom': lerp(1, c['zoom'], k)}

    def settings_shot(ctx, t, f, u):
        dk = ease_out(prog(t, START + 0.05, START + 0.4))
        LL = chat_layout(side=1, drawer=dk)
        room(ctx, dim=0.45, t=t)
        window_frame(ctx, LL, glass=0.94)
        sidebar(ctx, LL, items=env.script.get('sidebar', []), t=t, pres='online')
        header(ctx, LL, title=env.script.get('title', ''), pres='online')
        thread(ctx, LL['thread'], [{'who': 'me', 'text': text(56), 'size': 30}], t)
        composer(ctx, LL['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t)
        slots, _ = drawer_rows(ctx, LL, t, k=dk, sel=0)
        caption(ctx, t, [57], x=LL['main']['x'] + 40, y=200, size=34)
        hx, hy = LL['head']['x'] + LL['head']['w'] - 190, LL['head']['y'] + 27
        f0 = (slots[0]['x'] + slots[0]['w'] * 0.25, slots[0]['y'] + 17)
        draw_cursor(ctx, [{'t': START, 'x': hx, 'y': hy, 'click': True}, {'t': Bt(193.6), 'x': f0[0] - 120, 'y': f0[1] + 50},
                          {'t': cF - 0.02, 'x': f0[0], 'y': f0[1] + 4, 'click': True}], t)

    # ------------------------------------------------------------------ pre2-gender
    def gender(ctx, t, f, u):
        ground(ctx, light=(960, 300, 380, 'raised', 1))
        vals = rows[0]['values']
        held = t >= D(1)
        let_go = t >= cue('letterM57', cF + 0.9)
        sel = ease_out(prog(t, cue('letterM57', cF + 0.9), cue('letterM57', cF + 0.9) + 0.15))
        thud = pulse(t - D(2), 10) if t >= D(2) else 0
        dx, dy = shake(t, 10 * thud)
        with ctx.at(dx, dy):
            r = R(60, 40, 1800, 470)
            ctx.rrect(r['x'] + 10, r['y'] + 10, r['w'], r['h'], 235, fill='bg')
            ctx.rrect(r['x'], r['y'], r['w'], r['h'], 235, fill='raised', stroke='line', width=3)
            cell = r['w'] / 2
            px = r['x'] + sel * cell
            ctx.rrect(px + 14, r['y'] + 14, cell - 28, r['h'] - 28, 220, fill='me', alpha=0.9)
            for i, v in enumerate(vals):
                on = (i == 0 and sel < 0.5) or (i == 1 and sel >= 0.5)
                land = cue('letterF', cF) if i == 0 else cue('letterM57', cF + 0.9)
                if t >= land:
                    ctx.text(v, r['x'] + cell * (i + 0.5) + (-330 if i == 0 else 330), 400, size=360, weight=900, font='serif',
                             color='bg' if on else 'sub', align='center')
            name = 'boy_bust' if let_go else 'f_bust'
            h = 500
            inks(ctx, name, 960 - h * aspect(name) / 2, 40, h, offsets={'black': (8, 8)})
            # the pointer touches the control, never her: it comes down on the other cell and holds it
            tip = (r['x'] + cell * 1.5 + 330, 360)
            dn = ease_out(prog(t, D(1) - 0.08, D(1)))
            arrow(ctx, tip[0] + 60 * (1 - dn) + 8, tip[1] - 60 * (1 - dn) + 8, 4.0, color='bg', edge=None)
            arrow(ctx, tip[0] + 60 * (1 - dn), tip[1] - 60 * (1 - dn), 4.0 * (0.95 if held and not let_go else 1))
        caption(ctx, t, [57, 58], x=70, y=600, size=36)

    # ------------------------------------------------------------------ pre2-day
    def day(ctx, t, f, u):
        drag = ease_in_out(prog(t, Bt(203), D(4)))
        top = 1 - abs(drag - 0.5) * 2
        dusk = ease_in_out(prog(t, D(3), D(4) + 0.3))
        ground(ctx, light=(960, 300, 420, 'raised', 1 - 0.7 * dusk))
        if dusk > 0:
            ctx.rect(0, 0, 1920, 640, fill=True, color='bg', alpha=0.55 * dusk)
        C, Rr = (960, 600), 520
        pts = [(C[0] + math.cos(math.pi + i / 60 * math.pi) * Rr * 1.55, C[1] + math.sin(math.pi + i / 60 * math.pi) * Rr) for i in range(61)]
        ctx.poly(pts, color='line', width=10)
        a = math.pi + drag * math.pi
        sx, sy = C[0] + math.cos(a) * Rr * 1.55, C[1] + math.sin(a) * Rr
        on = pts[:int(drag * 60) + 1]
        if len(on) > 1:
            ctx.poly(on, color='me', width=10)
        vals = rows[1]['values']
        ctx.text(vals[0], 160, 560, size=150, weight=900, font='serif', color='me' if drag < 0.5 else 'sub', align='center')
        ctx.text(vals[1], 1760, 560, size=150, weight=900, font='serif', color='me' if drag >= 0.5 else 'sub', align='center')
        h = 300
        bx = 960 - h * aspect('boy_bust') / 2
        inks(ctx, 'boy_bust', bx, 600 - h, h, variant='sil:bg' if dusk > 0.6 else 'ink', offsets={'black': (6, 6)} if dusk < 0.6 else None)
        rays(ctx, sx, sy, 50, 180 + 140 * top, n=20, rot=t * 0.2, color='meHot', alpha=0.4 + 0.5 * top, width=8)
        with ctx.glow('me', 30, 0.6):
            spark(ctx, sx, sy, 70 + 20 * top, rot=t * 0.5)
        pointer(ctx, sx + 20, sy + 30, kind='hand', scale=1.6, alpha=prog(t, cDay, cDay + 0.1))
        caption(ctx, t, [58, 59, 60], x=70, y=82, size=34)
        ctx.flash(0.3 * pulse(t - D(3), 8), 'meHot')

    # ------------------------------------------------------------------ pre2-role
    def role(ctx, t, f, u):
        s_at, m_at, land = cue('letterS', cRole + 1.8), cue('letterM61', cRole + 2.7), D(8)
        lighter = 0.3 * ease_out(prog(t, s_at, s_at + 0.1))
        ground(ctx, light=(700, 300, 420, 'raised', 1 + lighter))
        jolt = shake(t, 12 * pulse(t - s_at, 10)) if t >= s_at else (0, 0)
        with ctx.at(*jolt):
            vals = rows[2]['values']
            ctx.rect(150, 470, 420, 50, fill=True, color='bg')
            ctx.rect(150, 460, 420, 30, fill=True, color='me')
            if t >= s_at:
                k = ease_out(prog(t, s_at, s_at + 0.08))
                with ctx.at(360, 460, sy=0.6 + 0.4 * k):
                    ctx.text(vals[0], 8, 8, size=430, weight=900, font='serif', color='bg', align='center')
                    ctx.text(vals[0], 0, 0, size=430, weight=900, font='serif', color='me', align='center')
            if t >= m_at:
                soft = ease_in_out(prog(t, m_at, land))
                give = pulse(t - land, 6) * math.sin((t - land) * 25) if t >= land else 0
                with ctx.at(980, 560 + 10 * give, sy=1 - 0.8 * soft, sx=1 + 0.5 * soft, rot=0.0):
                    ctx.text(vals[1], 0, 0, size=330, weight=400, font='serif', color='text', align='center')
            ctx.line(700, 562 + (8 * pulse(t - land, 6) if t >= land else 0), 1300, 562, color='line', width=5)
            # the upright switch at the right
            sw = (1600, 120)
            ctx.rrect(sw[0] - 50, sw[1], 100, 380, 50, fill='bg', stroke='line', width=3)
            up = ease_out(prog(t, D(7), s_at)) * (1 - ease_in_out(prog(t, s_at + 0.2, m_at)))
            ky = lerp(sw[1] + 330, sw[1] + 50, up)
            ctx.circle(sw[0], ky, 42, fill=True, color='text')
            pointer(ctx, sw[0] + 10, ky + 10, kind='hand', scale=1.6, alpha=prog(t, D(6) - 0.1, D(6)))
        caption(ctx, t, [60, 61, 62], x=70, y=82, size=34)

    # ------------------------------------------------------------------ pre2-loop / loop-b
    def loop_cam(t, f, u):
        c = frame_rect(R(L['drawer']['x'] - 40, L['drawer']['y'] + 250, DRAWER_W + 60, 340))
        return c

    def loop_shot(ctx, t, f, u):
        room(ctx, dim=0.45, t=t)
        window_frame(ctx, L, glass=0.94)
        header(ctx, L, title=env.script.get('title', ''), pres='online')
        on = ease_out(prog(t, cLoop, cLoop + 0.12))
        slots, done = drawer_rows(ctx, L, t, sel=3, loop_on=on)
        sw = (slots[3]['x'] + slots[3]['w'] - 28, slots[3]['y'] + 17)
        draw_cursor(ctx, [{'t': cLoop - 0.3, 'x': sw[0] - 60, 'y': sw[1] + 40}, {'t': cLoop, 'x': sw[0], 'y': sw[1], 'click': True},
                          {'t': cLoop + 0.25, 'x': done[0], 'y': done[1], 'click': True}], t, dwell=0.05)

    def loop_b_cam(t, f, u):
        k = ease_in_out(prog(t, cBack + 0.1, END))
        LL = chat_layout(side=1)
        c = frame_rect(R(LL['thread']['x'] - 40, LL['thread']['y'] + 200, LL['thread']['w'] + 80, 260))
        return {'x': lerp(0, c['x'], k), 'y': lerp(0, c['y'], k), 'zoom': lerp(1, c['zoom'], k)}

    def loop_b(ctx, t, f, u):
        LL = chat_layout(side=1)
        room(ctx, dim=0.45, t=t)
        window_frame(ctx, LL, glass=0.94)
        sidebar(ctx, LL, items=env.script.get('sidebar', []), t=t, pres='online')
        header(ctx, LL, title=env.script.get('title', ''), pres='online')
        thread(ctx, LL['thread'], lyric_msgs(env, 63, 64, t), t)
        box = composer(ctx, LL['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, focus=1 if t > cBack + 0.1 else 0)
        draw_cursor(ctx, [{'t': cBack - 0.2, 'x': 1500, 'y': 520}, {'t': cBack + 0.08, 'x': box['caret'][0] + 60, 'y': box['caret'][1], 'click': True}], t)

    # ------------------------------------------------------------------ pre2-trance
    def trance(ctx, t, f, u):
        ground(ctx, light=(960, 300, 420, 'raised', 1))
        steps = [cue('tranceA', cTrance + 1.4), cue('tranceB', cTrance + 2.3)]
        n = sum(1 for s in steps if t >= s)
        reg = ease_in_out(prog(t, cBack - 0.3, cBack - 0.1))
        h = 540
        for i, (name, variant, alpha) in enumerate((('man_bust', 'sil:bg', 0.35), ('boy_bust', 'sil:me', 0.9), ('f_bust', 'sil:text', 0.75))):
            ang = (t - cTrance) * 0.35 + i * TAU / 3 + n * 0.6
            rad = 150 * (1 - reg)
            x = 960 + math.cos(ang) * rad - h * aspect(name) / 2
            y = 40 + math.sin(ang) * rad * 0.25
            if reg > 0.5 and name != 'boy_bust':
                alpha *= 1 - (reg - 0.5) * 2
            ctx.image(name, x, y, h * aspect(name), h, variant=variant, alpha=alpha, rot=math.sin(ang) * 0.05 * (1 - reg))
        if reg > 0.5:
            inks(ctx, 'boy_bust', 960 - h * aspect('boy_bust') / 2, 40, h, alpha=(reg - 0.5) * 2)
        caption(ctx, t, [62, 63], x=70, y=600, size=36)

    return {
        'pre2-settings': {'render': settings_shot, 'camera': settings_cam, 'palette': 'warm'},
        'pre2-gender': {'render': gender, 'palette': 'warm'},
        'pre2-day': {'render': day, 'palette': 'warm'},
        'pre2-role': {'render': role, 'palette': 'warm'},
        'pre2-loop': {'render': loop_shot, 'camera': loop_cam, 'palette': 'warm'},
        'pre2-trance': {'render': trance, 'palette': 'warm'},
        'pre2-loop-b': {'render': loop_b, 'camera': loop_b_cam, 'palette': 'warm'},
    }
