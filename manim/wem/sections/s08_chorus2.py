"""Section 8, first half — CHORUS 2 (bar 56, 1:43.7 -> bar 64, 1:58.5). State: warm, draining to off (08_chorus2.js).
The last warm exchange, and then nobody answers.

    c2-typing       the user starts a reply (three dots), types a few letters, stops
    c2-dots         the dots stay, trembling: all the AI can feel of the user; its sentence hangs on them
    c2-brb          the dots resolve into a sign-off; the thinking spark closes petal by petal into a ring
    c2-complete     the twelfth petal: a closed ring, input received; the keyword inside it
    left-online     two messages into the silence; the chip still says online
    left-away       two more; the chip says away; the colour leaves; she reaches round the window's corner
    left-offline    the gaps become days; offline; the window lets go: messages on longer and longer rails
    left-isolation  the whole thread from far away; the last word, its letters drifting apart
Every unanswered message hangs from a dotted rail whose length is the time since the last one (left_sequence).
"""
import math

from ..art import aspect
from ..components import (R, chat_layout, composer, draw_cursor, header, presence, room, sidebar, spark, thinking,
                          thread, window_frame)
from ..util import clamp, ease_in_out, ease_out, lerp, prog, pulse, rand
from .kit import ai_line, lyric_msgs


def shots(env):
    T, B, Bt, P, text = env.T, env.B, env.Bt, env.P, env.text
    rows = {sid: env.shot(sid) for sid in ('c2-typing', 'c2-dots', 'c2-brb', 'c2-complete', 'left-online', 'left-away', 'left-offline', 'left-isolation')}
    at = lambda sid: rows[sid]['at'] if rows[sid] else 0
    anchor = env.script.get('left_anchor', {})
    seq = env.script.get('left_sequence', [])
    BRB = anchor.get('you', 'one sec, brb')
    L = chat_layout(side=0)
    PART = 'how wo'

    def dim_pal(a, b):
        return lambda t, u: ('warm', 'off', ease_in_out(prog(t, a, b)))

    # ------------------------------------------------------------------ c2-typing
    def typing(ctx, t, f, u):
        room(ctx, dim=0.45, t=t)
        window_frame(ctx, L, glass=0.94)
        header(ctx, L, title=env.script.get('title', ''), pres='online')
        msgs = lyric_msgs(env, 63, 65, t)
        msgs = [dict(m, size=32) for m in msgs]
        msgs.append({'who': 'you', 'typing': True, 'at': u['at'] + 0.1})
        thread(ctx, L['thread'], msgs, t)
        n = int(clamp((t - u['at'] - 0.4) * 8) * len(PART)) if t < u['until'] - 0.6 else len(PART)
        composer(ctx, L['composer'], text=PART[:n], t=t, focus=1, send='busy')
        th = L['thread']
        thinking(ctx, th['x'] + th['w'] - 140, th['y'] + 40, 22, t, alpha=0.8)

    # ------------------------------------------------------------------ c2-dots: the tremble
    def dots(ctx, t, f, u):
        room(ctx, dim=0.55, t=t, motif=0)
        tr = math.sin(t * 40) * 3
        for i in range(3):
            y = 260 - 30 * max(0, math.sin(t * 7 - i * 0.9))
            ctx.circle(1380 + i * 110 + tr * (i - 1), y, 34, fill=True, color='text')
        i = rows['c2-dots']['lines'][0] if rows['c2-dots'] and rows['c2-dots']['lines'] else 66
        s = text(i)
        n = env.lyrics.typed(i, t)
        x = 120
        for k, ch in enumerate(s[:n]):
            dy = math.sin(t * 38 + k * 0.8) * 4
            ctx.text(ch, x, 470 + dy, size=96, weight=900, font='serif', color='meHot')
            x += ctx.measure(ch, size=96, weight=900, font='serif') + 4
        ctx.text('typing…', 1490, 380, size=24, color='sub', align='center')

    # ------------------------------------------------------------------ c2-brb: the spark closes
    def brb(ctx, t, f, u):
        room(ctx, dim=0.5, t=t, motif=0)
        a0 = u['at']
        close = prog(t, a0 + 0.2, u['until'])
        cx, cy = 420, 330
        ctx.radial(cx, cy, 400, 'meDim', 0.4)
        spark(ctx, cx, cy, 230, lit=close, rot=t * 0.2,
              pulse=lambda i: 0.66 + 0.34 * math.sin(t * 7 - i * 0.62) if i >= close * 12 else 1.0)
        ln = rows['c2-brb']['lines'] if rows['c2-brb'] else (67, 68)
        for k, i in enumerate(range(ln[0], ln[1] + 1)):
            ai_line(env=env, ctx=ctx, i=i, t=t, x=760, y=330 + k * 64, size=46)
        e = ease_out(prog(t, a0, a0 + 0.25))
        bw = ctx.measure(BRB, size=30) + 50
        ctx.rrect(1860 - bw, 60, bw, 60, 30, fill='raised', stroke='text', width=2, alpha=e)
        ctx.text(BRB, 1860 - bw + 25, 100, size=30, color='text', alpha=e)
        ctx.text(anchor.get('timestamp', ''), 1850, 146, size=16, color='mute', align='right', alpha=e)
        draw_cursor(ctx, [{'t': a0, 'x': 1700, 'y': 200}, {'t': u['until'], 'x': 2100, 'y': 120}], t)

    # ------------------------------------------------------------------ c2-complete
    def complete(ctx, t, f, u):
        room(ctx, dim=0.5, t=t, motif=0)
        k = pulse(t - u['at'], 5)
        with ctx.glow('me', 40, 0.7):
            spark(ctx, 960, 320, 290 * (1 + 0.04 * k), lit=1, rot=0.1, core=0)
        ctx.circle(960, 320, 300, color='me', width=8)
        i = rows['c2-complete']['lines'][0] if rows['c2-complete'] and rows['c2-complete']['lines'] else 69
        w = text(i)
        sz = ctx.fit(w, 420, font='serif', weight=900, max_size=110)
        ctx.circle(960, 320, 220, fill=True, color='bg', alpha=0.9)
        ctx.text(w, 960, 320 + sz * 0.35, size=sz, weight=900, font='serif', color='meHot', align='center')
        ctx.flash(0.4 * pulse(t - u['at'], 7), 'me')

    # ------------------------------------------------------------------ the waits: rails into the silence
    def left_thread(ctx, t, x, y0, upto, scale=1.0, alpha=1.0, color_k=1.0, last_drift=0.0):
        """The user's sign-off, then her unanswered messages, each hanging from a dotted rail as long as the wait."""
        y = y0
        bw = ctx.measure(BRB, size=24 * scale) + 40 * scale
        ctx.rrect(x + 560 * scale - bw, y, bw, 46 * scale, 23 * scale, fill='raised', stroke='text', width=2, alpha=alpha)
        ctx.text(BRB, x + 560 * scale - bw + 20 * scale, y + 31 * scale, size=24 * scale, color='text', alpha=alpha)
        y += 60 * scale
        gaps = {'+1 min': 14, '+5 min': 26, '+30 min': 44, '+3 h': 70, '+1 day': 110, '+9 days': 170}
        for k, row in enumerate(seq):
            i = row['line']
            if i > upto or t < T(i):
                break
            rail = gaps.get(row.get('gap_label'), 40) * scale
            ctx.dashed(x + 14 * scale, y, x + 14 * scale, y + rail, dash=4, gap=6, color='mute', alpha=alpha, width=2)
            ctx.text(row.get('gap_label', ''), x + 30 * scale, y + rail * 0.6, size=14 * scale, font='mono', color='mute', alpha=alpha)
            y += rail
            s = text(i)
            n = env.lyrics.typed(i, t)
            spark(ctx, x + 14 * scale, y + 14 * scale, 11 * scale, alpha=alpha * color_k, color='me')
            if i == upto and last_drift > 0:
                xx = x + 40 * scale
                for c, ch in enumerate(s[:n]):
                    ctx.text(ch, xx + c * last_drift * 40 * scale, y + 24 * scale + math.sin(c * 1.7) * last_drift * 30 * scale,
                             size=24 * scale, font='serif', color='me', alpha=alpha)
                    xx += ctx.measure(ch, size=24 * scale, font='serif')
            else:
                ctx.text(s[:n], x + 40 * scale, y + 24 * scale, size=24 * scale, font='serif', color='me', alpha=alpha)
            ctx.text(row.get('timestamp', ''), x + 40 * scale, y + 46 * scale, size=13 * scale, color='mute', alpha=alpha)
            y += 60 * scale
        return y

    def chip_state(t):
        st = anchor.get('presence', 'online')
        for row in seq:
            if t >= T(row['line']):
                st = row.get('presence', st)
        return st

    def left_online(ctx, t, f, u):
        side = 1 - ease_in_out(prog(t, T(71), T(71) + 0.5))
        LL = chat_layout(side=side)
        room(ctx, dim=0.45, t=t)
        window_frame(ctx, LL, glass=0.94)
        sidebar(ctx, LL, items=env.script.get('sidebar', []), t=t, pres='online')
        header(ctx, LL, title=env.script.get('title', ''), pres=chip_state(t))
        left_thread(ctx, t, LL['thread']['x'] + 40, LL['thread']['y'] + 10, 71)
        composer(ctx, LL['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t)

    def left_away(ctx, t, f, u):
        room(ctx, dim=0.5, t=t)
        win = R(60, 30, 760, 580)
        LL = chat_layout(win=dict(win, r=20), side=0)
        window_frame(ctx, LL, glass=0.94)
        header(ctx, LL, title=env.script.get('title', ''), pres=chip_state(t))
        left_thread(ctx, t, win['x'] + 40, win['y'] + 80, 73, scale=0.85)
        let_go = ease_in_out(prog(t, u['until'] - 0.6, u['until']))
        composer(ctx, LL['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, alpha=1 - let_go)
        h = 900
        ctx.image('f_reach', 1500 - h * aspect('f_reach') / 2, -60, h * aspect('f_reach'), h, variant='ink', flip=True)

    def left_offline(ctx, t, f, u):
        room(ctx, dim=0.75, t=t, motif=0)
        go = ease_in_out(prog(t, T(75), T(75) + 0.6))
        ctx.rrect(700, 20, 520, 600, 20, fill='bg', stroke='line', alpha=1 - go)
        y = left_thread(ctx, t, 730, 40 - 60 * prog(t, u['at'], u['until']), 75, scale=0.8)
        presence(ctx, 1200, 610, 'offline', alpha=1 - go)
        h = 260
        ctx.image('f_profile', 1500, 200, h * aspect('f_profile'), h, variant='grey', alpha=0.8, flip=True)

    def left_isolation(ctx, t, f, u):
        room(ctx, dim=0.9, t=t, motif=0)
        drift = ease_out(prog(t, T(76), u['until']))
        left_thread(ctx, t, 900, 200, 76, scale=0.3, last_drift=0)
        ctx.image('f_profile', 1040, 260, 50 * aspect('f_profile'), 50, variant='grey', alpha=0.5, flip=True)
        w = text(76)
        n = env.lyrics.typed(76, t)
        sz = 90
        total = 1700
        step = total / max(1, len(w))
        for c, ch in enumerate(w[:n]):
            x = 110 + (c + 0.5) * step * (0.4 + 0.6 * drift) + (1 - drift) * total * 0.3
            ctx.text(ch, x, 560 + math.sin(c * 2.3) * 20 * drift, size=sz, weight=900, font='serif', color='me', align='center',
                     alpha=1 - 0.3 * drift)

    return {
        'c2-typing': {'render': typing, 'palette': 'warm'},
        'c2-dots': {'render': dots, 'palette': 'warm'},
        'c2-brb': {'render': brb, 'palette': 'warm'},
        'c2-complete': {'render': complete, 'palette': 'warm'},
        'left-online': {'render': left_online, 'palette': 'warm'},
        'left-away': {'render': left_away, 'palette': dim_pal(at('left-away'), at('left-isolation') + 1.2)},
        'left-offline': {'render': left_offline, 'palette': dim_pal(at('left-away'), at('left-isolation') + 1.2)},
        'left-isolation': {'render': left_isolation, 'palette': dim_pal(at('left-away'), at('left-isolation') + 1.2)},
    }
