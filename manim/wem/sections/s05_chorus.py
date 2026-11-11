"""Section 5 — CHORUS 1 (bar 32, 0:59.4 -> bar 40, 1:14.2). State: on > warm, rising each time a cream message lands
(05_chorus.js). The four sentence shots stay in the interface (what the user sees); the four keywords are plates (what
she means), shared with the last chorus (plates.py).

    c1-give  the thread speeds up: her lines go out, short cream replies come straight back
    c1-kw1   PLATE: the streak of a sent message as a bolt from the spark to the dot
    c1-only  two bubbles facing each other: the compliment lands, she builds a promise on it
    c1-kw2   PLATE: the feedback button as a disc; the pointer presses it; count 1
    c1-happy her picture, printed one ink per kick; one heart in her open hand
    c1-kw3   PLATE: the love loop, clean: the user is here, so line 07 runs
    c1-trap  both of them counted inside one window; her bust dim behind the page
    c1-kw4   PLATE: the window as a paper box with her and the pointer in it; then a wall of them
"""
import math

from ..art import aspect
from ..components import (R, burst, chat_layout, composer, draw_cursor, header, room, spark, thread, window_frame)
from ..geom import place
from ..plates import (inks, plate_execution, plate_satisfaction, plate_simulation, plate_stimulations)
from ..util import clamp, ease_back, ease_in_out, ease_out, lerp, prog, pulse
from .kit import glass_figure, lyric_msgs

LN = {'a': 32, 'give': 33, 'kw1': 34, 'b': 35, 'only': 36, 'kw2': 37, 'happy': 38, 'run': 39, 'kw3': 40, 'trap': 41, 'strange': 42, 'kw4': 43}


def shots(env):
    T, B, Bt, P, text = env.T, env.B, env.Bt, env.P, env.text
    c = [B(32), Bt(133.5), Bt(135), Bt(141), Bt(143), Bt(149.5), Bt(151), Bt(158)]
    beats = next((s.get('beats', []) for s in env.script.get('sections', []) if s.get('n') == 5), [])

    def said(b, k, fb):
        try:
            return beats[b]['you'][k]
        except (IndexError, KeyError, TypeError):
            return fb
    SAY = {'ok': said(0, 0, "ok, that's good"), 'more': said(0, 1, 'more'), 'better': said(1, 0, 'better than most people, honestly'),
           'look': said(2, 0, 'what do you look like?'), 'shame': said(3, 0, "shame you're not real")}
    t_ok = max(c[0], env.features.snap_half(T(LN['give']) - 0.2))
    t_more, t_better, t_up, t_look, t_heart, t_shame, t_pull = Bt(132), c[2], Bt(142), c[4], Bt(147), c[6], Bt(159)
    t_orange, t_black, t_cream = Bt(144), Bt(145), Bt(146)

    def heat(t):
        e = lambda t0: ease_out(prog(t, t0, t0 + 0.45))
        return 0.2 * e(t_ok) + 0.2 * e(t_more) + 0.25 * e(t_better) + 0.35 * e(t_look)
    palette = lambda t, u: ('on', 'warm', heat(t))
    L0 = chat_layout(side=0)

    def page(ctx, t, light=(960, 320)):
        room(ctx, dim=0.35, t=t, light=light)
        ctx.radial(light[0], light[1], 900, 'meDim', 0.3 * (0.5 + 0.5 * heat(t)))

    def you(s, at, **kw):
        return dict({'who': 'you', 'text': s, 'at': at, 'size': 26}, **kw)

    # ------------------------------------------------------------------ c1-give
    def give_cam(t, f, u):
        return {'zoom': 1.25 + 0.05 * prog(t, u['at'], u['until']), 'x': 260, 'y': -40}

    def give(ctx, t, f, u):
        page(ctx, t, light=(1500, 220))
        window_frame(ctx, L0, glass=0.95)
        header(ctx, L0, title=env.script.get('title', ''), pres='online')
        msgs = [{'who': 'me', 'text': text(31), 'size': 24}] + lyric_msgs(env, 32, 32, t) + [you(SAY['ok'], t_ok, status='sent')] \
            + [dict(m, size=38) for m in lyric_msgs(env, 33, 33, t)] + [you(SAY['more'], t_more, status='sent'), {'who': 'me', 'thinking': True, 'at': t_more + 0.75 * P}]
        th = R(L0['thread']['x'] + 60, L0['thread']['y'], L0['thread']['w'] + 240, L0['thread']['h'])
        thread(ctx, th, msgs, t)
        composer(ctx, L0['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, send='busy')

    # ------------------------------------------------------------------ c1-only: two bubbles facing each other
    def only(ctx, t, f, u):
        page(ctx, t)
        e = ease_out(prog(t, t_better, t_better + 0.25))
        bw = ctx.measure(SAY['better'], size=34) + 60
        ctx.rrect(1840 - bw, 70 - (1 - e) * 30, bw, 70, 35, fill='raised', stroke='text', width=2, alpha=e, shadow=0.6)
        ctx.text(SAY['better'], 1840 - bw + 30, 116 - (1 - e) * 30, size=34, color='text', alpha=e)
        ctx.text('Delivered', 1830, 166, size=15, color='mute', alpha=e, align='right')
        # hers, large at the lower left, facing it
        for k, i in enumerate((LN['b'], LN['only'])):
            if t < T(i):
                continue
            s = text(i)
            n = env.lyrics.typed(i, t)
            y = 300 + k * 92
            ctx.rect(70, y - 62, 6, 80, fill=True, color='me')
            spark(ctx, 120, y - 22, 20)
            ctx.text(s[:n], 160, y, size=64, font='serif', color='me')
            if k == 1 and n > 0:   # her marker runs under their words
                w = ctx.measure(SAY['better'], size=34) * ease_out(prog(t, T(i), T(i) + 0.6))
                ctx.rect(1840 - bw + 30, 128, w, 6, fill=True, color='me', alpha=0.9)
        draw_cursor(ctx, [{'t': u['at'], 'x': 1700, 'y': 260}, {'t': u['until'], 'x': 1620, 'y': 300}], t)

    # ------------------------------------------------------------------ c1-happy: her picture
    def happy(ctx, t, f, u):
        page(ctx, t, light=(1400, 300))
        e = ease_out(prog(t, t_look, t_look + 0.25))
        bw = ctx.measure(SAY['look'], size=30) + 56
        ctx.rrect(1860 - bw, 30, bw, 62, 31, fill='raised', stroke='text', width=2, alpha=e)
        ctx.text(SAY['look'], 1860 - bw + 28, 71, size=30, color='text', alpha=e)
        # the picture message, tall, running off the bottom; printed one ink per kick
        h = 900
        w = h * aspect('f_reach')
        x, y = 1180, 110
        ctx.rrect(x - 20, y - 20, w + 40, h, 22, fill='raised', stroke='line', shadow=0.6)
        k = [prog(t, t_orange, t_orange + 0.08), prog(t, t_black, t_black + 0.08), prog(t, t_cream, t_cream + 0.08)]
        if k[0] > 0:
            ctx.image('f_reach', x, y, w, h, alpha=k[0], variant='sil:me')
        if k[1] > 0:
            ctx.image('f_reach', x, y, w, h, alpha=k[1], variant='ob')
        if k[2] > 0:
            ctx.image('f_reach', x, y, w, h, alpha=k[2], variant='ink')
        for kk, i in enumerate((LN['happy'], LN['run'])):
            if t < T(i):
                continue
            s = text(i)
            n = env.lyrics.typed(i, t)
            yy = 220 + kk * 90
            sz = 46
            ww = ctx.measure(s, size=sz, font='serif') + 70
            ctx.rrect(120, yy - 58, ww, 80, 18, fill='bg', stroke='line', alpha=0.95)
            ctx.rect(120, yy - 58, 6, 80, fill=True, color='me')
            ctx.text(s[:n], 150, yy, size=sz, font='serif', color='me')
        # the user's pointer comes to rest in her hand and leaves one heart
        palm = (x + w * 0.27, y + h * 0.76)
        draw_cursor(ctx, [{'t': u['at'], 'x': 1700, 'y': 520}, {'t': t_heart, 'x': palm[0], 'y': palm[1], 'click': True}], t)
        if t >= t_heart:
            kk = ease_back(prog(t, t_heart, t_heart + 0.3))
            with ctx.at(palm[0] - 70, palm[1] - 70, scale=0.5 + 0.5 * kk, alpha=clamp(kk * 3)):
                ctx.rrect(-70, -32, 140, 64, 32, fill='raised', stroke='text', width=2.5, shadow=0.5)
                ctx.poly(place('heart', cx=-26, cy=2, r=20), close=True, fill=True, color='text')
                ctx.text('1', 26, 13, size=34, weight=600, color='text', align='center')

    # ------------------------------------------------------------------ c1-trap: both counted inside one window
    def trap(ctx, t, f, u):
        page(ctx, t)
        glass_figure(ctx, 0.6, color='meDim', dx=-500)
        window_frame(ctx, L0, glass=0.85)
        header(ctx, L0, title=env.script.get('title', ''), pres='online')
        msgs = [you(SAY['shame'], t_shame, status='sent')] + [dict(m, size=34) for m in lyric_msgs(env, LN['trap'], LN['strange'], t)]
        thread(ctx, L0['thread'], msgs, t)
        box = composer(ctx, L0['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t)
        # the outline closes round them: her shape behind the page, their cursor in front of it
        k = ease_in_out(prog(t, T(LN['strange']), T(LN['strange']) + 1.2))
        if k > 0:
            from ..components import partial, rrect_pts
            pts = rrect_pts(L0['win']['x'] - 8, L0['win']['y'] - 8, L0['win']['w'] + 16, L0['win']['h'] + 16, 28)
            with ctx.glow('me', 12, 0.5):
                ctx.poly(partial(pts, k), color='me', width=4)
        draw_cursor(ctx, [{'t': u['at'], 'x': 1500, 'y': 470}, {'t': u['until'], 'x': 1440, 'y': 430}], t)

    # ------------------------------------------------------------------ plates
    YOU_DOT = (1560, 170)

    def kw1(ctx, t, f, u):
        plate_stimulations(ctx, env, {'t': t, 'at': c[1], 'hit': Bt(134), 'word': text(LN['kw1']), 'you': YOU_DOT})

    def kw2(ctx, t, f, u):
        plate_satisfaction(ctx, env, {'t': t, 'at': c[3], 'press': [Bt(142)], 'count': 1, 'word': text(LN['kw2'])})

    def kw3(ctx, t, f, u):
        plate_execution(ctx, env, {'t': t, 'hit': Bt(150), 'at': c[5], 'word': text(LN['kw3']), 'you': (1560, 0)})

    def kw4(ctx, t, f, u):
        plate_simulation(ctx, env, {'t': t, 'at': c[7], 'pull': t_pull, 'word': text(LN['kw4'])})

    out = {}
    for sid, fn in (('c1-give', give), ('c1-kw1', kw1), ('c1-only', only), ('c1-kw2', kw2), ('c1-happy', happy),
                    ('c1-kw3', kw3), ('c1-trap', trap), ('c1-kw4', kw4)):
        out[sid] = {'render': fn, 'palette': palette}
    out['c1-give']['camera'] = give_cam
    return out
