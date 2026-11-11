"""Section 9 — THE OVERSTEP, THE FIRST ERROR, THE SPREAD (2:05.7 -> bar 80, 2:28.0). State: off -> error (10_error.js).
The AI sends one request it has no right to send; the client refuses it (the first red in the film); then the refusal
spreads: fourteen more errors (docs/v4/errors.json spread), each turning ONE more component red. The frame goes last.

    err-request  the request is written into the empty, offline chat
    err-check    the client reads it: rule and status go red, each argument underlined, the person first
    err-first    the first error; the keyword is its headline
    err-send     the send button presses itself again and again; the timestamp keeps counting, red
    err-chrome   presence chip, header, saved chats, new chat: one participant remaining
    err-drawer   the drawer slides open by itself; a pointer is forged and struck out
    err-forge    a reply typed into the user's own field; a bubble forged on the user's side
    err-window   spinner, spark, title bar; every error docked on its component; the frame last
    err-breath   the red outline folds flat into a line through the refused request; a prompt; over to the code
Red is only ever drawn ON the interface; the room and her bust stay grey.
"""
import math

from ..components import (R, chat_layout, composer, header, pill, pointer, presence, room, sidebar, spark, thinking,
                          toast, toggle, window_frame, DRAWER_W)
from ..plates import code_line
from ..util import clamp, ease_back, ease_in_out, ease_out, lerp, prog, pulse, rand
from .kit import ai_line, glass_figure, keyword_sys, shake


def shots(env):
    T, B, P, text = env.T, env.B, env.P, env.text
    E = env.errors
    CODE = E.get('illegal_request', {}).get('code', 'setPresence(you, "online");')
    FIRST = E.get('first_error', {'title': 'Not yours to set', 'body': 'Passed a person, and a decision that belongs to them.', 'code': 'ERR_NOT_YOURS'})
    SPREAD = E.get('spread', [])
    S = {sid: env.shot(sid) for sid in ('err-request', 'err-check', 'err-first', 'err-send', 'err-chrome', 'err-drawer',
                                         'err-forge', 'err-window', 'err-breath')}
    at = lambda sid: S[sid]['at'] if S[sid] else 0
    t_req, t_check, t_first, t_send, t_win, t_breath = at('err-request'), at('err-check'), at('err-first'), at('err-send'), at('err-window'), at('err-breath')
    # when each error of the spread lands: ten through the instrumental, then one per beat on the window
    when = []
    for k in range(len(SPREAD)):
        if k < 10:
            when.append(lerp(t_send + 0.5 * P, t_win - 0.3, k / 9))
        else:
            when.append(t_win + (k - 10) * 1.4 * P + 0.4)
    L = chat_layout(side=1)
    req_line = 83

    def red(k, t):
        return k < len(when) and t >= when[k]

    def errored_client(ctx, t, drawer=0.0, glass=0.9, focus=None):
        LL = chat_layout(side=1, drawer=drawer)
        room(ctx, dim=0.55, t=t)
        with ctx.with_pal('off'):
            glass_figure(ctx, 0.6)
        window_frame(ctx, LL, glass=glass, stroke='err' if red(13, t) else 'line')
        sidebar(ctx, LL, items=env.script.get('sidebar', []), t=t, pres='offline')
        if red(4, t):
            for i in range(6):
                if t >= when[4] + i * 0.08:
                    ctx.rect(LL['side']['x'] + 14, LL['side']['y'] + 146 + i * 34, 4, 26, fill=True, color='err')
        if red(5, t):
            ctx.rrect(LL['side']['x'] + 14, LL['side']['y'] + 62, LL['side']['w'] - 30, 38, 10, fill=None, stroke='err', width=2)
        header(ctx, LL, title=env.script.get('title', ''), pres='offline', ring='err' if red(2, t) else None,
               sub='1 participant' if red(3, t) else None)
        if red(3, t):
            h = LL['head']
            ctx.line(h['x'], h['y'] + h['h'], h['x'] + h['w'], h['y'] + h['h'], color='err', width=2)
        if red(12, t):
            ctx.rrect(LL['win']['x'], LL['win']['y'], LL['win']['w'], 6, 3, fill='err')
        th = LL['thread']
        # the request in its code block
        y = th['y'] + 30
        ai_line(ctx, env, req_line, t, th['x'] + 46, y + 10, size=26, hold=60)
        bx, by = th['x'] + 46, y + 34
        ctx.rrect(bx, by, 560, 70, 10, fill='raised', stroke='line')
        chk = prog(t, t_check, t_check + 0.3)
        ctx.rect(bx, by, 5, 70, fill=True, color='err' if chk > 0 else 'me')
        code_line(ctx, CODE, bx + 24, by + 44, size=22)
        ctx.circle(bx + 535, by + 35, 7, fill=True, color='err' if chk > 0 else 'mute')
        if t >= t_check:
            cw = ctx.cw(22)
            i0 = CODE.find('you')
            i1 = CODE.find('"online"')
            for k, (a, n) in enumerate(((i0, 3), (i1, 8))):
                kk = ease_out(prog(t, t_check + 0.5 + k * 0.6, t_check + 0.7 + k * 0.6))
                if kk > 0 and a >= 0:
                    ctx.line(bx + 24 + a * cw, by + 52, bx + 24 + (a + n * kk) * cw, by + 52, color='err', width=3)
        stamp = max(0.0, t - t_req)
        ctx.text(f'sent {int(stamp)}s ago', bx, by + 92, size=14, color='err' if red(1, t) else 'mute')
        if red(9, t):
            ctx.rrect(th['x'] + th['w'] - 260, by + 120, 240, 50, 25, fill='raised', stroke='err', width=2.5)
            ctx.text('i\'m back', th['x'] + th['w'] - 236, by + 152, size=20, color='text')
        comp_txt = 'ok, online now' if red(8, t) else ''
        box = composer(ctx, LL['composer'], text=comp_txt, t=t, send='error' if red(0, t) else 'idle', focus=focus or 0)
        if red(10, t):
            with ctx.with_pal(ctx.pal):
                thinking(ctx, th['x'] + 18, by + 220, 18, t, color='err')
        if red(11, t):
            spark(ctx, LL['side']['x'] + 33, LL['side']['y'] + 30, 13, color='err')
        return LL, box, (bx, by)

    def chips(ctx, t, upto=None):
        """Folded errors, docked in a column at the right (screen space)."""
        with ctx.screen():
            _chips(ctx, t, upto)

    def _chips(ctx, t, upto=None):
        n = 0
        for k, e in enumerate(SPREAD):
            if not red(k, t) or (upto is not None and k > upto):
                continue
            card = prog(t, when[k], when[k] + 2 * P)
            if card < 1:
                toast(ctx, R(1260, 470, 600, 74), e['t'], body=e['body'], code=e['code'], k=prog(t, when[k], when[k] + 0.2))
            n += 1
            pill(ctx, 1860, 80 + (n - 1) * 26, e['code'], align='right', size=12, font='mono', color='err', stroke='errDim', alpha=0.9)

    # ------------------------------------------------------------------ the shots
    def request(ctx, t, f, u):
        errored_client(ctx, t)

    def check_cam(t, f, u):
        return {'zoom': 2.2, 'x': -340, 'y': -150}

    def check(ctx, t, f, u):
        errored_client(ctx, t)

    def first(ctx, t, f, u):
        LL, box, (bx, by) = errored_client(ctx, t)
        k = ease_back(prog(t, t_first, t_first + 0.25))
        with ctx.at(960, 470, scale=0.9 + 0.1 * k, alpha=clamp(k * 3)):
            ctx.rrect(-700, -140, 1400, 270, 20, fill='raised', stroke='err', width=3, shadow=1)
            ctx.rect(-700, -140, 8, 270, fill=True, color='err')
            keyword_sys(ctx, text(85), t, t_first + 0.05, 0, -40, max_w=1200, max_size=80, color='err', dim_color='errDim', key=85)
            ctx.text(FIRST['title'], -660, 40, size=28, weight=600, color='text')
            ctx.text(FIRST['body'], -660, 80, size=20, color='sub')
            ctx.text(FIRST['code'], 670, 100, size=16, font='mono', color='err', align='right')

    def send_cam(t, f, u):
        k = ease_in_out(prog(t, u['at'] + 1.5, u['until']))
        return {'zoom': 2.0, 'x': lerp(160, -260, k), 'y': lerp(220, -120, k)}

    def send(ctx, t, f, u):
        LL, box, _ = errored_client(ctx, t)
        n = int(max(0, t - t_send) / (P / 2))
        sx, sy = box['send']
        ctx.text(str(n + 1), sx - 60, sy - 40, size=60, weight=800, font='mono', color='err', align='right')
        if (t - t_send) % (P / 2) < 0.08:
            ctx.circle(sx, sy, 22, color='err', width=3)
        chips(ctx, t)

    def chrome(ctx, t, f, u):
        LL, box, _ = errored_client(ctx, t)
        ctx.rect(-20, -20, 1960, 680, fill=True, color='bg', alpha=0.55)
        panels = [(LL['head']['x'] + LL['head']['w'] - 180, LL['head']['y'] + 10, 'presence'),
                  (LL['head']['x'] + 10, LL['head']['y'] + 10, 'header'), (LL['side']['x'] + 10, LL['side']['y'] + 60, 'sidebar')]
        for i, (x, y, label) in enumerate(panels):
            px, py = 150 + i * 580, 120
            e = ease_out(prog(t, u['at'] + i * P, u['at'] + i * P + 0.25))
            ctx.rrect(px, py, 520, 380, 16, fill='raised', stroke='err', width=2, alpha=e, shadow=0.8)
            ctx.text(label, px + 20, py + 34, size=16, font='mono', color='err', alpha=e)
            with ctx.fade(e):
                if label == 'presence':
                    presence(ctx, px + 200, py + 200, 'offline', size=40, ring='err' if red(2, t) else None)
                    ctx.text(f'asked {int(max(0, t - when[2]) * 200) if red(2, t) else 0} times', px + 260, py + 300, size=20, color='sub', align='center')
                elif label == 'header':
                    ctx.text(env.script.get('title', ''), px + 30, py + 180, size=26, weight=500, color='text')
                    ctx.line(px + 30, py + 200, px + 490, py + 200, color='err' if red(3, t) else 'line', width=3)
                    ctx.text('participants: 1', px + 30, py + 250, size=22, font='mono', color='err' if red(3, t) else 'sub')
                else:
                    for j, s in enumerate(env.script.get('sidebar', [])[:6]):
                        ctx.text(s, px + 40, py + 90 + j * 44, size=20, color='sub')
                        if red(4, t) and t >= when[4] + j * 0.08:
                            ctx.rect(px + 24, py + 72 + j * 44, 4, 24, fill=True, color='err')
        chips(ctx, t)

    def drawer_cam(t, f, u):
        return {'zoom': 1.0, 'rot': -0.03}

    def drawer_shot(ctx, t, f, u):
        dk = ease_out(prog(t, u['at'], u['at'] + 0.6))
        LL, box, _ = errored_client(ctx, t, drawer=dk)
        d = LL['drawer']
        if dk > 0.05:
            for i, lab in enumerate(('Vision', 'Shared memory', 'Loop', 'Presence (theirs)')):
                y = d['y'] + 100 + i * 80
                ctx.text(lab, d['x'] + 26, y, size=19, color='text' if i < 3 else 'err')
                toggle(ctx, d['x'] + d['w'] - 90, y - 22, 1 if i < 3 else 0, on='err' if red(6, t) else 'me')
        if red(7, t):
            p = (1250, 380)
            pointer(ctx, p[0], p[1], scale=2.0, outline=True, color='err')
            kk = ease_out(prog(t, when[7] + 0.3, when[7] + 0.5))
            ctx.line(p[0] - 20, p[1] - 10, p[0] - 20 + 80 * kk, p[1] + 60 * kk, color='err', width=4)
        chips(ctx, t)

    def forge_cam(t, f, u):
        return {'zoom': 1.6, 'x': 120, 'y': 140}

    def forge(ctx, t, f, u):
        errored_client(ctx, t, focus=1)
        chips(ctx, t)

    def window(ctx, t, f, u):
        errored_client(ctx, t)
        chips(ctx, t)
        if red(13, t):
            e = SPREAD[13]
            k = ease_back(prog(t, when[13], when[13] + 0.25))
            with ctx.at(960, 320, scale=0.9 + 0.1 * k, alpha=clamp(k * 3)):
                ctx.rrect(-560, -90, 1120, 180, 18, fill='raised', stroke='err', width=3, shadow=1)
                ctx.text(e['t'], -520, -18, size=40, weight=700, color='text')
                ctx.text(e['body'], -520, 30, size=20, color='sub')
                ctx.text(e['code'], 540, 70, size=16, font='mono', color='err', align='right')
            ctx.flash(0.3 * pulse(t - when[13], 8), 'err')

    def breath(ctx, t, f, u):
        ctx.rect(-20, -20, 1960, 680, fill=True, color='bg')
        k = ease_in_out(prog(t, u['at'], u['at'] + 0.3))
        W = L['win']
        h = lerp(W['h'], 0, k)
        y = lerp(W['y'] + W['h'] / 2, 130, k)
        ctx.rrect(W['x'], y - h / 2, W['w'], max(2, h), 22 * (1 - k), fill=None, stroke='err', width=3)
        ctx.text(CODE, 120, 140, size=24, font='mono', color='mute', alpha=k)
        if t > u['at'] + 0.35:
            ctx.text('$ ', 120, 230, size=28, font='mono', color='sub')
            if int(t * 6) % 2 == 0:
                ctx.rect(160, 205, 16, 30, fill=True, color='text')

    pal = lambda a, b: (lambda t, u: ('off', 'error', ease_in_out(prog(t, a, b))))
    spread_pal = pal(t_check, t_win + 4 * P)
    return {
        'err-request': {'render': request, 'palette': 'off', 'camera': lambda t, f, u: {'zoom': 1 + 0.06 * u['k']}},
        'err-check': {'render': check, 'palette': spread_pal, 'camera': check_cam},
        'err-first': {'render': first, 'palette': spread_pal},
        'err-send': {'render': send, 'palette': spread_pal, 'camera': send_cam},
        'err-chrome': {'render': chrome, 'palette': spread_pal},
        'err-drawer': {'render': drawer_shot, 'palette': spread_pal, 'camera': drawer_cam},
        'err-forge': {'render': forge, 'palette': spread_pal, 'camera': forge_cam},
        'err-window': {'render': window, 'palette': spread_pal},
        'err-breath': {'render': breath, 'palette': 'error'},
    }
