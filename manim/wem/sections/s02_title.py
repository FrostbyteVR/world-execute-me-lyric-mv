"""Section 2 — TITLE and the first question (bar 8, 0:15.1 -> beat 63, 0:29.4). State: off -> on (02_title.js).
The spark lights up: the first orange in the film. Then, over the instrumental, the user arrives.

    title       the spark ignites petal by petal; the launch command is typed and entered
    chat-open   the whole client: a blank conversation; a cream cursor crosses the window, presence turns online
    chat-type   close on the composer: the user starts one question, deletes it, types the real one
    chat-think  the question is sent; the AI starts thinking; we fall into the spark
"""
import math
import re

from ..components import (R, burst, chat_layout, composer, draw_cursor, frame_rect, header, room, sidebar, spark,
                          thread, window_frame)
from ..util import clamp, ease_in, ease_in_out, ease_out, lerp, prog, pulse
from .kit import enter, glass_figure

# where the thinking spark ends up, full frame: verse 1 starts from exactly this burst
HANDOFF = {'cx': 960, 'cy': 330, 'r': 200, 'rot': 0.26}


def shots(env):
    T, B, Bt, P, text = env.T, env.B, env.Bt, env.P, env.text
    L = chat_layout()
    DROP, t_type, t_enter, END = B(8), env.features.snap_to_beat(T(11)), B(9), Bt(63)
    QUESTION = env.script.get('question', 'how would you love me')
    false = 'why did'
    for sec in env.script.get('sections', []):
        for b in sec.get('beats', []):
            for s in b.get('you', []):
                if re.match(r'^type, then delete:', s):
                    false = s.split(': ', 1)[1]
    t_send = B(14)
    side_items = env.script.get('sidebar', [])
    comp_y = L['composer']['y']

    def typing(t):
        b = (t - B(12)) / P
        if b < 1.6:
            return false[:int(clamp(b / 1.5) * len(false) + 1e-6)]
        if b < 2.7:
            return false
        if b < 3.4:
            return false[:math.ceil((1 - (b - 2.7) / 0.7) * len(false))]
        if b < 4:
            return ''
        return QUESTION[:int(clamp((b - 4) / 2.8) * len(QUESTION) + 1e-6)]

    def base(ctx, t, pres='online', title='New conversation', glass=0.82, alpha=1.0):
        room(ctx, dim=0.42, t=t)
        glass_figure(ctx, 0.75 * alpha, color='meDim')
        window_frame(ctx, L, glass=glass, alpha=0.35 + 0.65 * alpha)
        sidebar(ctx, L, t=t, items=side_items, pres=pres, alpha=alpha)
        header(ctx, L, title=title, pres=pres, alpha=alpha)

    # ------------------------------------------------------------------ the spark lights up
    def title(ctx, t, f, u):
        lit = ease_out(prog(t, DROP, DROP + 2 * P))
        cx, cy = 960, 235
        room(ctx, light=(960, 240), dim=0.62, t=t, motif=0.6)
        glass_figure(ctx, 0.5 * lit, color='meDim')
        ctx.radial(cx, cy, 520, 'meDim', 0.5 * lit)
        with ctx.glow('me', 50, 0.6 * lit):
            spark(ctx, cx, cy, 150 * (1 + 0.03 * f['beatPulse']), lit=lit, grow=0.25 + 0.75 * lit, rot=0.04 * (t - DROP))
        cmd = text(11)
        n = int(prog(t, t_type, t_type + 0.72) * len(cmd) + 1e-6)
        size = 58
        cw = ctx.cw(size)
        s = '> ' + cmd[:n]
        x = 960 - (len(cmd) + 2) * cw / 2
        y = 520
        a = prog(t, DROP + 0.3, DROP + 0.55)
        bw = (len(cmd) + 2) * cw + 80
        if t_enter <= t < t_enter + 0.1:
            ctx.rrect(x - 40, y - 70, bw, 104, 20, fill='text')
            ctx.text(s, x, y, size=size, weight=700, font='mono', color='bg')
        else:
            ctx.rrect(x - 40, y - 70, bw, 104, 20, fill='bg', stroke='line', alpha=a, shadow=0.8)
            ctx.text(s, x, y, size=size, weight=700, font='mono', color='text', alpha=a)
        if t < t_enter and ((n < len(cmd) and t >= t_type) or int(t * 5) % 2 == 0):
            ctx.rect(x + len(s) * cw + 6, y - size * 0.8, cw * 0.82, size * 0.98, fill=True, color='me', alpha=a)
        ctx.flash(0.5 * pulse(t - t_enter, 7), 'me')

    # ------------------------------------------------------------------ a blank conversation; the user arrives
    def open_cam(t, f, u):
        return {'zoom': 1 + 0.04 * ease_in_out(prog(t, t_enter, B(12))), 'y': 8 * prog(t, t_enter, B(12))}

    def chat_open(ctx, t, f, u):
        t_in = B(10)
        here = prog(t, t_in, t_in + 0.25)
        t_focus = B(11) + 2 * P
        base(ctx, t, pres='online' if here > 0 else 'offline')
        if 0 < here < 1:
            burst(ctx, L['head']['x'] + L['head']['w'] - 110, L['head']['y'] + 28, 34, here, color='text')
        cx = L['main']['x'] + L['main']['w'] / 2
        ctx.radial(cx, 250, 240, 'meDim', 0.4)
        with ctx.glow('me', 26, 0.5):
            spark(ctx, cx, 250, 70 * (1 + 0.04 * f['beatPulse']), rot=0.08 * (t - B(6)))
        box = composer(ctx, L['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, focus=1 if t >= t_focus else 0)
        cx_, cy_ = box['caret']
        draw_cursor(ctx, [{'t': t_in - 0.15, 'x': 2010, 'y': 150}, {'t': t_in + 1.5 * P, 'x': 1480, 'y': 230},
                          {'t': B(11), 'x': 1240, 'y': 380}, {'t': t_focus, 'x': cx_ + 40, 'y': cy_ + 6, 'click': True},
                          {'t': B(12), 'x': cx_ + 300, 'y': cy_ + 60}], t,
                    kind='text' if t_focus - 0.3 < t < t_focus + 0.5 else 'arrow')

    # ------------------------------------------------------------------ the question
    def type_cam(t, f, u):
        c = frame_rect(R(L['composer']['x'] - 60, comp_y - 150, L['composer']['w'] + 120, L['composer']['h'] + 200))
        c['zoom'] *= 1 + 0.04 * prog(t, B(12), t_send)
        return c

    def chat_type(ctx, t, f, u):
        s = typing(t)
        b = (t - B(12)) / P
        dele = 2.7 < b < 3.4
        base(ctx, t)
        cx = L['main']['x'] + L['main']['w'] / 2
        with ctx.glow('me', 26, 0.5):
            spark(ctx, cx, 250, 70, rot=0.08 * (t - B(6)))
        ready = s == QUESTION
        box = composer(ctx, L['composer'], text=s, placeholder=env.script.get('composer_placeholder', ''), t=0 if dele else t,
                       focus=1, send='ready' if ready else 'idle', size=26)
        kb = ((t - B(12)) * 14) % 1
        cx_, cy_ = box['caret']
        if s and not ready and not dele:
            ctx.line(cx_ - 2, cy_ + 18, cx_ + 12, cy_ + 18, color='text', alpha=0.7 * (1 - kb), width=3)
        t_go = t_send - 1.1 * P
        draw_cursor(ctx, [{'t': B(12), 'x': cx_ + 300, 'y': cy_ + 60}, {'t': t_go, 'x': L['composer']['x'] + 520, 'y': comp_y + 120},
                          {'t': t_send - 0.04, 'x': box['send'][0] + 3, 'y': box['send'][1] + 4, 'click': True}], t, scale=1.2)

    # ------------------------------------------------------------------ sent; thinking
    def think_cam(t, f, u):
        k = ease_in(prog(t, B(15), END))
        return {'zoom': 1 + 2.4 * k, 'x': lerp(0, -470, k), 'y': lerp(0, -60, k)}

    def chat_think(ctx, t, f, u):
        k = ease_in(prog(t, B(15), END))
        a = 1 - prog(t, B(15) + P, END - 0.25)
        base(ctx, t, alpha=a)
        items = thread(ctx, L['thread'], [{'who': 'you', 'text': QUESTION, 'at': t_send, 'status': 'sent'}], t, alpha=a)
        composer(ctx, L['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, send='busy', alpha=max(a, 0.3))
        y_last = (items[0]['y'] + items[0]['h']) if items else L['thread']['y']
        fx_, fy_ = L['thread']['x'] + 18, y_last + 34
        t_on = t_send + P
        with ctx.screen():
            if t >= t_on:
                e = enter(t, t_on, dur=0.3)
                # the spark's place in the thread, in screen space (the camera is zooming into it)
                sx, sy = ctx_to_screen(think_cam(t, f, u), fx_, fy_)
                x, y = lerp(sx, HANDOFF['cx'], k), lerp(sy, HANDOFF['cy'], k)
                r = lerp(18 * think_cam(t, f, u)['zoom'], HANDOFF['r'], k)
                settle = ease_in_out(prog(t, END - 1.5 * P, END - 0.08))
                ctx.radial(x, y, r * 2.6, 'meDim', 0.5 * k)
                with ctx.glow('me', 20 + 40 * k, 0.5):
                    spark(ctx, x, y, r * (0.7 + 0.3 * e['k']), alpha=e['a'], rot=HANDOFF['rot'] + 0.5 * (t - END) * (1 - settle),
                          pulse=lambda i: lerp(0.66 + 0.34 * math.sin(t * 7 - i * 0.62), 1, settle))
                ctx.text('Thinking', x + 30, y + 7, size=19, color='mute', alpha=e['a'] * (1 - prog(t, B(15), B(15) + P)))

    def ctx_to_screen(cam, x, y):
        z = cam['zoom']
        return (960 + (x - 960 - cam['x']) * z, 320 + (y - 320 - cam['y']) * z)

    return {
        'title': {'render': title, 'palette': lambda t, u: ('off', 'on', ease_out(prog(t, DROP, DROP + 0.5)))},
        'chat-open': {'render': chat_open, 'palette': 'on', 'camera': open_cam},
        'chat-type': {'render': chat_type, 'palette': 'on', 'camera': type_cam},
        'chat-think': {'render': chat_think, 'palette': 'on', 'camera': think_cam},
    }
