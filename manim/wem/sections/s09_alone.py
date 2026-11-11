"""Section 8, second half — ALONE (bar 64, 1:58.5 -> 2:05.7). State: off (09_alone.js).
The AI tidies the thread it filled while it waited, as if tidiness were what had been wanted.

    alone-erase  from the newest message up, one per half beat: selected, deleted, a grey stub; the pieces pile up
    alone-empty  the stubs go, the user's last words go; one message left: a sentence one word short
    alone-eye    PLATE: dark; then her face across the sheet, one eye open; the keyword under her chin; five letters
                 selected and deleted, the plate wiped
There is no pointer (the AI has none): the interface itself shows what is done to it.
"""
import math

from ..art import aspect
from ..components import R, chat_layout, composer, header, room, spark, window_frame
from ..plates import ground, keyword
from ..util import clamp, ease_in_out, ease_out, lerp, prog, pulse, rand
from .kit import ai_line


def shots(env):
    T, P, text = env.T, env.P, env.text
    seq = env.script.get('left_sequence', [])
    BRB = env.script.get('left_anchor', {}).get('you', 'one sec, brb')
    r_erase, r_empty, r_eye = env.shot('alone-erase'), env.shot('alone-empty'), env.shot('alone-eye')
    E0 = r_erase['at'] if r_erase else 118.5

    def figure(ctx, alpha=0.7):
        h = 620
        ctx.image('f_profile', 1300, 20, h * aspect('f_profile'), h, variant='dots:mute', alpha=alpha, flip=True)

    def erase(ctx, t, f, u):
        room(ctx, dim=0.7, t=t, motif=0)
        figure(ctx)
        msgs = [row['line'] for row in seq]
        x, y = 160, 60
        ctx.rrect(x + 380, y, 200, 40, 20, fill='raised', stroke='text', width=2)
        ctx.text(BRB, x + 400, y + 27, size=18, color='text')
        y += 60
        pieces = 0
        for k, i in enumerate(msgs):
            order = len(msgs) - 1 - k                    # newest first
            t_sel = E0 + 0.1 + order * P / 2
            sel = t >= t_sel
            gone = ease_out(prog(t, t_sel + 0.15, t_sel + 0.3))
            if sel and gone < 1:
                ctx.rect(x - 10, y - 4, 600, 40, fill=True, color='raised', alpha=0.9 * (1 - gone))
            if gone < 1:
                ctx.text(text(i), x + 30, y + 24, size=22, font='serif', color='me', alpha=1 - gone)
            else:
                ctx.text('deleted by me', x + 30, y + 22, size=16, font='mono', color='mute')
                pieces += 1
            spark(ctx, x + 10, y + 16, 9, color='mute' if gone >= 1 else 'me')
            y += 48
        # what came off the rows piles up beside the thread
        for p in range(pieces * 6):
            px = 1040 + rand(3, p, 1) * 220
            py = 560 - (p // 6) * 16 - rand(3, p, 2) * 14
            ctx.rect(px, py, 30 + rand(3, p, 3) * 40, 9, fill=True, color='meDim', alpha=0.9)
        lines = r_erase['lines'] if r_erase and r_erase['lines'] else (77, 79)
        for k, i in enumerate(range(lines[0], lines[1] + 1)):
            if env.lyrics.lines[i].get('emphasis'):
                if t >= T(i):
                    keyword(ctx, text(i), t, x=1150, y=600, max_w=700, max_size=90, at=T(i), step=0.02, color='me')
            else:
                ai_line(ctx, env, i, t, 760, 120 + k * 50, size=30, hold=0.3)

    def empty(ctx, t, f, u):
        L = chat_layout(side=0)
        room(ctx, dim=0.6, t=t)
        figure(ctx, 0.5)
        window_frame(ctx, L, glass=0.9)
        header(ctx, L, title=env.script.get('title', ''), pres='offline', sub='0 messages' if t > u['at'] + 0.5 else None)
        lines = r_empty['lines'] if r_empty and r_empty['lines'] else (80, 81)
        for k, i in enumerate(range(lines[0], lines[1] + 1)):
            ai_line(ctx, env, i, t, L['thread']['x'] + 46, L['thread']['y'] + 120 + k * 56, size=36, hold=9)
        spark(ctx, L['thread']['x'] + 15, L['thread']['y'] + 108, 13)
        composer(ctx, L['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, send='off')

    def eye(ctx, t, f, u):
        i = r_eye['lines'][0] if r_eye and r_eye['lines'] else 82
        look = T(i)
        if t < look:
            ctx.rect(-10, -10, 1940, 660, fill=True, color='bg')
            ai_line(ctx, env, i - 1, t, 200, 320, size=40, color='sub')
            return
        ground(ctx, light=None)
        h = 1920 * 1.0
        ctx.image('f_eye', 0, -560, 1920, 1920, variant='grey', flip=True)
        ctx.rect(0, 470, 1920, 140, fill=True, color='bg', alpha=0.95)
        w = text(i)
        sel_t = look + 0.35
        dele = prog(t, sel_t + 0.2, sel_t + 0.3)
        kept = w if dele <= 0 else w[:max(0, len(w) - 5)]
        res = keyword(ctx, kept, t, y=580, max_w=1760, max_size=120, at=look, color='text')
        if t >= sel_t and dele <= 0 and res:
            full = keyword(ctx, w, -1e9, y=580, max_w=1760, max_size=120, alpha=0.0)
            sw = ctx.measure(w[-5:], size=full['size'], weight=900, font='serif')
            ctx.rect(full['x'] + full['w'] - sw - 8, 580 - full['size'] * 0.8, sw + 16, full['size'] * 1.0, fill=True, color='sub', alpha=0.5)

    return {
        'alone-erase': {'render': erase, 'palette': 'off'},
        'alone-empty': {'render': empty, 'palette': 'off'},
        'alone-eye': {'render': eye, 'palette': 'off'},
    }
