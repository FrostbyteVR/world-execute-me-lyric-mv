"""Section 7 — PRE-CHORUS 2 (bar 48, 1:29.0 -> bar 56, 1:43.7). State: warm (07_pre2.js, plates_pre2.js).
The settings again. In pre-chorus 1 the user played with the switches of the interface; now each control is as large
as the frame and stands in her plate, and what it changes is her.

    pre2-settings  the pointer clicks Settings; the drawer opens further down its list; the view closes in on row one
    pre2-gender    PLATE: F | M as the whole sheet; the pointer holds the second cell on the drum and lets go when the
                   second letter is sung: the bust is the boy's, in register; the drum after it shudders the sheet
    pre2-day       PLATE: the On-call slider as an arc over the horizon, its knob her spark, the sun; dragged over the
                   top (behind his head: the brightest frame of the section) into the far end: dusk
    pre2-role      PLATE: no figure. The heavy letter on its platform, printed when sung; the light one goes soft and
                   slumps on the ground, which gives under it once; an upright switch the pointer pushes and pulls
    pre2-loop      Loop: on; Done (two hits a quarter of a second apart)
    pre2-trance    PLATE: one plate of each of her three looks, drifting and turning, a step on each repeat of the
                   word; then in register: the boy
    pre2-loop-b    the drawer shut; a click into the composer; the view closes in on the foot of the thread
Every event sits on one of the ten drum hits (cues drumD1..D10) or on a sung letter; the drum is the hand getting
ready, or the aftershock. A letter the lyric names is hollow until it is sung.
"""
import math
import re

import numpy as np

from ..art import aspect, regions
from ..components import (R, burst, chat_layout, composer, draw_cursor, frame_rect, header, pointer, room,
                          segmented, setting_row, sidebar, slider, spark, toggle, window_frame, DRAWER_W)
from ..plates import arrow, band, ground
from ..util import TAU, clamp, ease_back, ease_in, ease_in_out, ease_out, lerp, prog, pulse
from .s06_verse2 import ink_image

FALLBACK = [{'label': 'Gender', 'values': ['F', 'M']}, {'label': 'On call', 'values': ['AM', 'PM']},
            {'label': 'Role', 'values': ['S', 'M']}, {'label': 'Loop', 'values': ['off', 'on']}]
CAP = {'x': 70, 'y': 82, 'size': 40}
REGISTER = {'cat_bust': (1.0, -28, -49), 'boy_bust': (0.89, 60, -18), 'man_bust': (0.873, 81, -4)}


def flash_in(t, at):
    return 0.0 if t < at else clamp(0.6 + (t - at) * 30)


def fit(name, base):
    """Where to draw bust `name` so that it registers with f_bust drawn into base (art.js fit)."""
    r = REGISTER.get(name)
    if not r:
        return dict(base)
    k = base['w'] / 1086
    return {'x': base['x'] + k * r[1], 'y': base['y'] + k * r[2], 'w': base['w'] * r[0], 'h': base['h'] * r[0]}


def inks(ctx, name, r, roles=None, alpha=1.0, shadow=10):
    roles = roles or {0: 'text', 1: 'me', 2: 'panel'}
    if shadow:
        ink_image(ctx, name, r['x'] + shadow, r['y'] + shadow, r['w'], r['h'], {k: 'bg' for k in roles}, alpha=alpha * 0.9)
    ink_image(ctx, name, r['x'], r['y'], r['w'], r['h'], roles, alpha=alpha)


def warp_text(ctx, s, cx, y, size, weight=400, font='serif', color='me', alpha=1.0, squash=None, shift=None, stroke=0.0):
    """Type gone SOFT (type.js limp): every point of the glyphs is pressed towards the baseline by squash(u) and moved
    by shift(u) = (dx, dy), u = 0..1 across the word. Works on the glyph outlines themselves (no clipping needed)."""
    if not s or alpha * ctx.alpha <= 0.003:
        return
    _, sh = ctx._shape(s, font, weight, False)
    if not sh.ok:
        return
    w = sh.width * size
    x0 = cx - w / 2
    for p in sh.pts:
        q = p * size
        u = q[:, 0] / max(w, 1e-6)
        k = 1 - (squash(u) if squash else 0)
        dx, dy = shift(u) if shift else (0.0, 0.0)
        out = q.copy()
        out[:, 0] = x0 + q[:, 0] + dx
        out[:, 1] = y + q[:, 1] * k + dy
        if stroke > 0:
            ctx.path(out.reshape(-1, 4, 2), color=color, alpha=alpha, width=stroke)
        else:
            ctx.path(out.reshape(-1, 4, 2), color=color, alpha=alpha, fill=True)
    return w


def sung_chars(s, t, at, marks):
    """How many characters of s show at t when its words appear as sung (kit.js sungChars)."""
    words = s.split(' ')
    n = len(words)
    tm = [None] * n
    tm[0] = at
    for i, v in marks.items():
        if 0 <= i < n and v is not None:
            tm[i] = v
    last = 0
    for i in range(1, n + 1):
        if i < n and tm[i] is None:
            continue
        for j in range(last + 1, i):
            tm[j] = tm[last] + (j - last) * 0.16 if i == n else tm[last] + (tm[i] - tm[last]) * (j - last) / (i - last)
        last = i
    chars = shown = 0
    for i in range(n):
        chars += len(words[i]) + (1 if i else 0)
        if t >= tm[i]:
            shown = chars
    return shown


def word_index(s, word, last=False):
    w = [re.sub(r'[^\w]', '', x) for x in s.split(' ')]
    try:
        return len(w) - 1 - w[::-1].index(word) if last else w.index(word)
    except ValueError:
        return -1


def shots(env):
    T, B, Bt, P, text, cue = env.T, env.B, env.Bt, env.P, env.text, env.cue
    rows = env.script.get('settings_rows', {}).get('section7') or FALLBACK
    if len(rows) < 4:
        rows = FALLBACK
    beats = next((s.get('beats', []) for s in env.script.get('sections', []) if s.get('n') == 7), [])
    LOG = next((b.get('system', [None])[0] for b in beats if b.get('id') == 'loop-on' and b.get('system')), None) or 'loop: on'
    START, cF, cDay, cRole, cLoop, cTrance, cBack, END = B(48), B(49), B(50), B(52), B(54), Bt(217), Bt(223), B(56)
    D = lambda n: cue(f'drumD{n}', START + n)

    def marked(i, vals, ta, tb):
        s = text(i)
        return (i, {word_index(s, vals[0]): ta, word_index(s, vals[1], True): tb})
    L57 = marked(57, rows[0]['values'], max(cF, cue('letterF', cF)), cue('letterM57', cF + 0.9))
    L59 = marked(59, rows[1]['values'], cue('letterAM'), cue('letterPM'))
    L61 = marked(61, rows[2]['values'], cue('letterS'), cue('letterM61'))
    last_word = re.sub(r'[^\w]', '', text(63).split(' ')[-1])
    L63 = (63, {word_index(text(63), last_word): cue('tranceWordA'), word_index(text(63), last_word, True): cue('tranceWordB')})

    def caption(ctx, t, lines):
        for k, q in enumerate(lines):
            i, marks = (q if isinstance(q, tuple) else (q, None))
            if T(i) <= t < T(i + 1):
                s = text(i)
                n = sung_chars(s, t, T(i), marks) if marks else env.lyrics.typed(i, t)
                band(ctx, s, n, x=CAP['x'], y=CAP['y'], size=CAP['size'])

    def letter(ctx, s, cx, y, size, t, at, weight=900, off=1e9, pop=0.08):
        """A giant letter in her serif: an outline until it is sung, solid from then on (pressed on)."""
        if t < at or t >= off:
            ctx.text(s, cx, y, size=size, weight=weight, font='serif', align='center', color='meDim', stroke=max(2.5, size * 0.011))
            return
        k = ease_out(prog(t, at, at + 0.07 + pop * 0.5))
        d = size * 0.028
        with ctx.at(cx, y, scale=1 + pop * (1 - k)):
            ctx.text(s, d, d, size=size, weight=weight, font='serif', align='center', color='bg')
            ctx.text(s, 0, 0, size=size, weight=weight, font='serif', align='center', color='me')

    def hand(ctx, x, y, s=2.0, down=0.0):
        k = s * (1 - 0.1 * down)
        arrow(ctx, x + 4 * s * (1 - 0.6 * down), y + 4 * s * (1 - 0.6 * down), k, color='bg', edge=None)
        arrow(ctx, x, y, k, color='text', edge='bg')

    def along(way, t):
        if t <= way[0][0]:
            return way[0][1], way[0][2]
        for i in range(1, len(way)):
            if t <= way[i][0]:
                a, b = way[i - 1], way[i]
                go = b[3] if len(b) > 3 else a[0]
                k = ease_in_out(prog(t, go, b[0]))
                return lerp(a[1], b[1], k), lerp(a[2], b[2], k)
        return way[-1][1], way[-1][2]

    # =============================================================================== the interface
    LO = chat_layout(side=0, drawer=1)

    def drawer_k(t):
        return ease_out(prog(t, START + 0.02, START + 0.4)) * (1 - ease_in_out(prog(t, D(10) + 0.06, D(10) + 0.5)))

    def rows_state(t):
        return {'g': 0 if t < cue('letterM57', cF + 0.9) else 1, 'day': 0 if t < D(4) else 1,
                'role': 0 if t < cue('letterM61', cRole + 2.7) else 1, 'loop': ease_out(prog(t, cLoop, cLoop + 0.12))}

    def client(ctx, t, dk, hints):
        L = chat_layout(side=0, drawer=dk)
        room(ctx, dim=0.45, t=t)
        window_frame(ctx, L, glass=0.94)
        header(ctx, L, title=env.script.get('title', ''), pres='online')
        gx, gy = L['head']['x'] + L['head']['w'] - 190, L['head']['y'] + 27
        on = dk > 0.5
        if on:
            ctx.circle(gx, gy, 16, fill=True, color='raised')
        ctx.circle(gx, gy, 16, color='sub' if on else 'line', width=1.5)
        for dy, kx in ((-5, 4), (5, -4)):
            ctx.line(gx - 8, gy + dy, gx + 8, gy + dy, color='text' if on else 'sub', width=2)
            ctx.circle(gx + kx, gy + dy, 3, fill=True, color='text' if on else 'sub')
        th = L['thread']
        req = (env.script.get('cards_section6') or [{}] * 4)[3].get('request', '')
        bw = ctx.measure(req, size=24) + 40
        ctx.rrect(th['x'] + th['w'] - bw, 100, bw, 48, 24, fill='raised')
        ctx.text(req, th['x'] + th['w'] - bw + 20, 132, size=24, color='text')
        for n, i in enumerate((53, 54, 55)):
            spark(ctx, th['x'] + 14, 186 + n * 64, 12, alpha=0.75)
            ctx.text(text(i), th['x'] + 42, 196 + n * 64, size=28, font='serif', weight=700 if i == 55 else 400,
                     color='meHot' if i == 55 else 'me', alpha=0.75)
        composer(ctx, L['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t)
        if dk > 0.02:
            d = L['drawer']
            ctx.text('Settings', d['x'] + 26, d['y'] + 40, size=21, weight=600, color='text')
            ctx.line(d['x'], d['y'] + 60, d['x'] + d['w'], d['y'] + 60, color='line', width=1.5)
            st = rows_state(t)
            slots = []
            for i, row in enumerate(rows):
                r = R(d['x'] + 26, d['y'] + 70 + i * 104, DRAWER_W - 52, 104)
                slot = setting_row(ctx, r, row['label'], hint='', active=1.0 if i in hints else 0)
                slots.append(slot)
                for q in hints.get(i, []):
                    ii, marks = (q if isinstance(q, tuple) else (q, None))
                    if T(ii) <= t < T(ii + 1):
                        s = text(ii)
                        n = sung_chars(s, t, T(ii), marks) if marks else env.lyrics.typed(ii, t)
                        ctx.text(s[:n], r['x'], r['y'] + r['h'] - 14, size=17, font='serif', color='me')
            segmented(ctx, slots[0], rows[0]['values'], st['g'])
            slider(ctx, slots[1], 0.06 + 0.88 * st['day'])
            segmented(ctx, slots[2], rows[2]['values'], st['role'])
            toggle(ctx, slots[3]['x'] + slots[3]['w'] - 56, slots[3]['y'] + 2, st['loop'])
            done = (d['x'] + d['w'] - 90, d['y'] + d['h'] - 40)
            ctx.rrect(done[0] - 56, done[1] - 22, 112, 44, 22, fill='me' if t >= D(10) else 'raised', stroke='line')
            ctx.text('Done', done[0], done[1] + 7, size=18, weight=600, color='bg' if t >= D(10) else 'text', align='center')
            return L, slots, done
        return L, None, None

    def settings_cam(t, f, u):
        k = ease_in_out(prog(t, START + 0.12, Bt(195.1)))
        d = LO['drawer']
        c = frame_rect(R(d['x'] - 100, d['y'] + 50, DRAWER_W + 120, 180))
        return {'x': c['x'] * k, 'y': c['y'] * k, 'zoom': lerp(1, c['zoom'], k)}

    def settings_shot(ctx, t, f, u):
        L, slots, _ = client(ctx, t, drawer_k(t), {0: [56, L57]})
        hx, hy = L['head']['x'] + L['head']['w'] - 190, L['head']['y'] + 27
        f0 = (slots[0]['x'] + slots[0]['w'] * 0.25, slots[0]['y'] + 17) if slots else (1600, 160)
        draw_cursor(ctx, [{'t': START, 'x': hx + 3, 'y': hy + 4, 'click': True}, {'t': Bt(193.6), 'x': f0[0] - 120, 'y': f0[1] + 50},
                          {'t': cF - 0.02, 'x': f0[0], 'y': f0[1] + 4, 'click': True}], t, scale=0.9)

    def loop_cam(t, f, u):
        d = LO['drawer']
        return frame_rect(R(d['x'] - 60, d['y'] + 250, DRAWER_W + 80, 340))

    def loop_shot(ctx, t, f, u):
        L, slots, done = client(ctx, t, drawer_k(t), {3: [62]})
        if slots:
            sw = (slots[3]['x'] + slots[3]['w'] - 28, slots[3]['y'] + 17)
            draw_cursor(ctx, [{'t': cLoop - 0.3, 'x': sw[0] - 60, 'y': sw[1] + 40}, {'t': cLoop, 'x': sw[0] - 18, 'y': sw[1] + 4, 'click': True},
                              {'t': D(10), 'x': done[0], 'y': done[1] + 4, 'click': True}, {'t': cTrance, 'x': done[0] - 50, 'y': done[1] + 30}], t,
                        dwell=0.05, scale=1.0)

    LS = chat_layout(side=1)

    def loop_b_cam(t, f, u):
        k = ease_in_out(prog(t, cBack, END))
        c = frame_rect(R(LS['thread']['x'] - 60, LS['thread']['y'] + 140, LS['thread']['w'] + 120, 330))
        return {'x': c['x'] * k, 'y': c['y'] * k, 'zoom': lerp(1, c['zoom'], k)}

    def me_row(ctx, x, y, s, n, alpha=1.0, size=28):
        spark(ctx, x + 12, y - size * 0.3, 12, alpha=alpha)
        ctx.text(s[:n], x + 42, y, size=size, font='serif', color='me', alpha=alpha)
        if n < len(s):
            ctx.circle(x + 42 + ctx.measure(s[:n], size=size, font='serif') + size * 0.3, y - size * 0.28, size * 0.16, fill=True, color='me', alpha=alpha)

    def loop_b(ctx, t, f, u):
        room(ctx, dim=0.42, t=t)
        window_frame(ctx, LS, glass=0.84)
        sidebar(ctx, LS, items=[env.script.get('title', '')] + env.script.get('sidebar', []), active=0, t=t, pres='online')
        header(ctx, LS, title=env.script.get('title', ''), pres='online')
        th = LS['thread']
        for n, i in enumerate((61, 62)):
            me_row(ctx, th['x'], 200 + n * 60, text(i), 99, 0.3)
        me_row(ctx, th['x'], 330, text(63), sung_chars(text(63), t, T(63), L63[1]), lerp(1, 0.3, prog(t, T(64), END)))
        if t >= T(64):
            me_row(ctx, th['x'], 390, text(64), env.lyrics.typed(64, t))
        box = composer(ctx, LS['composer'], placeholder=env.script.get('composer_placeholder', ''), t=0, focus=1)
        px, py = LS['composer']['x'] + 260, LS['composer']['y'] + 40
        burst(ctx, px, py, 40, (t - cBack) / 0.45, color='text')
        cx, cy = box['caret']
        ctx.line(cx - 14, cy + 18, cx, cy + 18, color='text', alpha=0.8 * (1 - prog(t, cBack, cBack + 0.25)), width=3)
        pointer(ctx, px, py, kind='text', scale=1.1)

    # =============================================================================== Gender: F | M
    SEG = R(50, 100, 1820, 480)
    FIG = {'x': 960 - 315 / 2, 'y': 130, 'w': 315, 'h': 315 * 1448 / 1086}

    def gender(ctx, t, f, u):
        at, click, press, thud = cF, cue('letterM57', cF + 0.9), D(1), D(2)
        va, vb = rows[0]['values'][:2]
        a = flash_in(t, at)
        ground(ctx, light=(960, 340, 360, 'raised', 1))
        k = ease_out(prog(t, click, click + 0.1))
        on = t >= click
        cw = SEG['w'] / 2
        held = ease_out(prog(t, press, press + 0.07)) if press <= t < click else 0
        sink = 7 * held
        sh = (7 * pulse(t - click, 13) * math.sin((t - click) * 80) if t >= click else 0,
              5 * pulse(t - thud, 11) * math.sin((t - thud) * 70) if t >= thud else 0)
        with ctx.at(*sh):
            ctx.rrect(SEG['x'] + 10, SEG['y'] + 10, SEG['w'], SEG['h'], 50, fill='bg')
            ctx.rrect(SEG['x'], SEG['y'], SEG['w'], SEG['h'], 50, fill='panel', stroke='line', width=3)
            if held > 0:
                ctx.rrect(SEG['x'] + cw + 12 + sink, SEG['y'] + 12 + sink, cw - 24 - sink, SEG['h'] - 24 - sink, 40, fill='bg', alpha=0.5 * held, stroke='line', width=3)
            stretch = math.sin(math.pi * k) * 50
            px = SEG['x'] + 12 + k * cw
            ctx.rrect(px - stretch, SEG['y'] + 12, cw - 24 + 2 * stretch, SEG['h'] - 24, 40, fill='raised', stroke='me', width=4)
            ctx.text(va, SEG['x'] + 50, SEG['y'] + 76, size=50, weight=700, color='mute' if on else 'text')
            ctx.text(vb, SEG['x'] + SEG['w'] - 50 + sink, SEG['y'] + 76 + sink, size=50, weight=700, align='right',
                     color='text' if on else 'sub' if held else 'mute')
            letter(ctx, va, 330, 500, 360, t, max(at, cue('letterF', at)), off=click)
            letter(ctx, vb, 1590 + sink, 500 + sink, 360, t, click, pop=0.15)
            if a > 0:
                s = 1 + 0.035 * pulse(t - at, 16) + 0.05 * pulse(t - click, 14)
                with ctx.fade(a):
                    ctx.circle(960, 320, 190, fill=True, color='line', alpha=0.55)
                    with ctx.at(960 * (1 - s), 340 * (1 - s), scale=s):
                        inks(ctx, 'boy_bust' if on else 'f_bust', fit('boy_bust', FIG) if on else FIG, shadow=8)
        caption(ctx, t, [L57, 58])
        A, Bp = (470, 545), (1470, 545)
        p = along([(at, A[0], A[1]), (press, Bp[0], Bp[1], at + 0.05)], t)
        if t > click + 0.14:
            q = ease_in_out(prog(t, click + 0.14, cDay))
            to = day_grip()
            c = (700, 640)
            p = tuple((1 - q) * (1 - q) * Bp[i] + 2 * (1 - q) * q * c[i] + q * q * to[i] for i in (0, 1))
        burst(ctx, A[0], A[1], 70, (t - at) / 0.45, color='text')
        if press < click:
            burst(ctx, Bp[0], Bp[1], 40, (t - press) / 0.3, color='sub')
        burst(ctx, Bp[0], Bp[1], 90, (t - click) / 0.45, color='text')
        hand(ctx, p[0], p[1], down=max(pulse(t - at, 10), 1 if press <= t < click else 0, pulse(t - click, 10) if t >= click else 0))

    # =============================================================================== On call: AM -> PM
    DAY = {'y': 520, 'x0': 150, 'x1': 1770, 'bust': 300}

    def day_geom():
        bw = DAY['bust'] * 1086 / 1448
        Bx = {'x': 960 - bw / 2, 'y': DAY['y'] - DAY['bust'], 'w': bw, 'h': DAY['bust']}
        face = regions().get('boy_bust', {}).get('face', [359, 274, 371, 450])
        head = (Bx['x'] + (face[0] + face[2] / 2) / 1086 * bw, Bx['y'] + (face[1] + face[3] * 0.22) / 1448 * DAY['bust'])
        half = (DAY['x1'] - DAY['x0']) / 2
        sag = DAY['y'] - head[1]
        Rr = (half * half + sag * sag) / (2 * sag)
        C = (960, head[1] + Rr)
        f0 = math.atan2(DAY['y'] - C[1], DAY['x0'] - C[0])
        f1 = math.atan2(DAY['y'] - C[1], DAY['x1'] - C[0])

        def on(u):
            ff = lerp(f0, f1, u)
            return (C[0] + Rr * math.cos(ff), C[1] + Rr * math.sin(ff), math.cos(ff), math.sin(ff))

        def grip(q, v):
            d = 100 + 46 * math.sin(math.pi * v)
            return (q[0] + q[2] * d, q[1] + q[3] * d)
        return Bx, head, Rr, C, f0, f1, on, grip

    def day_grip():
        Bx, head, Rr, C, f0, f1, on, grip = day_geom()
        return grip(on(0), 0)

    def day(ctx, t, f, u):
        at = grab = cDay
        drag, top, end = Bt(203), D(3), D(4)
        va, vb = rows[1]['values'][:2]
        a = flash_in(t, at)
        Bx, head, Rr, C, f0, f1, on, grip = day_geom()
        if t < grab:
            uu = 0
        elif t < top:
            uu = 0.11 * prog(t, grab, top) + 0.39 * ease_in_out(prog(t, drag, top))
        else:
            uu = 0.5 + 0.5 * ease_in(prog(t, top, end))
        high = math.sin(math.pi * clamp(uu)) ** 0.8
        dusk = clamp((t - end) * 30)
        S = on(clamp(uu))
        press = pulse(t - end, 9) if t >= end else 0
        ground(ctx, light=(head[0], head[1], 420, 'raised', (0.3 + 0.7 * high) * (1 - dusk)))
        noon = high ** 6
        if dusk < 1:
            for r, role, al in ((500, 'mute', 0.5 * noon), (280, 'line', 0.5 * high), (170, 'line', 0.6 * high)):
                ctx.circle(S[0], S[1], r * (0.25 + 0.75 * high), fill=True, color=role, alpha=al * (1 - dusk))
        if noon > 0.05:
            ctx.rect(-10, -10, 1940, 660, fill=True, color='text', alpha=0.12 * noon * (1 - dusk))
        arc = lambda ua, ub, n=60: [(C[0] + Rr * math.cos(lerp(f0, f1, lerp(ua, ub, i / n))), C[1] + Rr * math.sin(lerp(f0, f1, lerp(ua, ub, i / n)))) for i in range(n + 1)]
        ctx.poly(arc(0, 1), color='line', width=6)
        if uu > 0.004:
            ctx.poly(arc(0, clamp(uu), max(2, int(60 * clamp(uu)))), color='me', width=8)
        for i in range(13):
            q = on(i / 12)
            l = 24 if i % 6 == 0 else 13
            ctx.line(q[0] + q[2] * 10, q[1] + q[3] * 10, q[0] + q[2] * (10 + l), q[1] + q[3] * (10 + l), color='sub' if i / 12 <= uu else 'mute', width=3)
        letter(ctx, va, 330, 300, 170, t, cue('letterAM', top))
        letter(ctx, vb, 1590, 300, 170, t, cue('letterPM', end))
        # the knob: her spark, the sun. It rises out of the horizon and sets into it (the ground is drawn over it)
        with ctx.at(S[0], S[1], sx=1 - 0.12 * press, sy=1 + 0.06 * press):
            spark(ctx, 9, 9, 100, color='bg', fat=0.12, core=0, inner=0.46, rot=uu * 2.2)
            ctx.circle(9, 9, 50, fill=True, color='bg')
            spark(ctx, 0, 0, 100, color='meDim' if dusk else 'me', fat=0.12, core=0, inner=0.46, rot=uu * 2.2)
            ctx.circle(0, 0, 50, fill=True, color='me' if dusk else 'meHot')
        ctx.rect(-10, DAY['y'], 1940, 200, fill=True, color='panel')
        ctx.rect(-10, DAY['y'], 1940, 200, fill=True, color='bg', alpha=0.6)
        ctx.line(40, DAY['y'], 1880, DAY['y'], color='line', width=3)
        ctx.text(va, DAY['x0'], DAY['y'] + 44, size=30, weight=700, color='text' if uu < 0.5 else 'mute', align='center')
        ctx.text(vb, DAY['x1'], DAY['y'] + 44, size=30, weight=700, color='text' if uu >= 0.5 else 'mute', align='center')
        if a > 0:
            if dusk > 0.5:
                ink_image(ctx, 'boy_bust', Bx['x'] - 2, Bx['y'] - 2, Bx['w'] + 4, Bx['h'] + 3, {0: 'line', 1: 'line', 2: 'line'}, alpha=a)
                ink_image(ctx, 'boy_bust', Bx['x'], Bx['y'], Bx['w'], Bx['h'], {0: 'bg', 1: 'bg', 2: 'bg'}, alpha=a)
            else:
                inks(ctx, 'boy_bust', Bx, alpha=a, shadow=7)
        caption(ctx, t, [58, L59, 60])
        G0, G, G1 = grip(on(0), 0), grip(S, clamp(uu)), grip(on(1), 1)
        if t < end + 0.2:
            p = G
        else:
            p = along([(end + 0.2, G1[0], G1[1]), (cRole, 1700, 420)], t)
        burst(ctx, G0[0], G0[1], 70, (t - grab) / 0.45, color='text')
        with ctx.at(7 * press * math.sin((t - end) * 80) if t >= end else 0, 0):
            hand(ctx, p[0], p[1], down=1 if grab <= t < end + 0.2 else 0)

    # =============================================================================== Role: S | M
    ROLE = {'ground': 540, 'plat': R(260, 360, 300, 180), 'track': R(1560, 110, 80, 400), 'heavy': (410, 330), 'light': (1060, 220)}

    def role(ctx, t, f, u):
        at, grab, push, s_at, m_at, land = cRole, D(6), D(7), cue('letterS', cRole + 1.8), cue('letterM61', cRole + 2.7), D(8)
        va, vb = rows[2]['values'][:2]
        a = flash_in(t, at)
        lit = clamp((t - s_at) * 30)
        ground(ctx, light=(820, 330, 420, 'raised', 0.55 + 0.45 * lit))
        if lit > 0:
            ctx.rect(-10, -10, 1940, 660, fill=True, color='text', alpha=0.06 * lit)
        if t < m_at:
            fall = 0
        elif t < land - 0.15:
            fall = 0.16 * prog(t, m_at, land - 0.15) ** 2
        else:
            fall = 0.16 + 0.84 * ease_in(prog(t, land - 0.15, land))
        tau = t - land
        soft = 0.56 * fall if tau < 0 else 0.5 + 0.06 * math.exp(-9 * tau) * math.cos(22 * tau)
        dip = 0 if tau < 0 else 20 * math.exp(-7 * tau) * math.cos(15 * tau)
        gy = lambda x: ROLE['ground'] + dip * math.exp(-((x - ROLE['light'][0]) / 220) ** 2)
        wob = lambda since, amp, decay, fr: amp * pulse(since, decay) * math.sin(since * fr) if since >= 0 else 0
        sh = (wob(t - m_at, 8, 13, 80), wob(t - s_at, 10, 13, 80) + wob(tau, 4, 12, 70))
        with ctx.at(*sh), ctx.fade(a):
            ctx.poly([(x, gy(x)) for x in range(80, 1841, 20)], color='sub', width=4)
            pl = ROLE['plat']
            ctx.rect(pl['x'] + 10, pl['y'] + 10, pl['w'], pl['h'] - 10, fill=True, color='bg')
            ctx.rect(pl['x'], pl['y'], pl['w'], pl['h'], fill=True, color='raised')
            ctx.line(pl['x'], pl['y'], pl['x'] + pl['w'], pl['y'], color='sub', width=4)
            burst(ctx, ROLE['heavy'][0], pl['y'] - ROLE['heavy'][1] * 0.36, 230, (t - s_at) / 0.4, color='meDim', rays=16)
            letter(ctx, va, ROLE['heavy'][0], pl['y'], ROLE['heavy'][1], t, s_at, pop=0.16)
            sq = lambda uu: soft * (0.62 + 0.38 * np.sin(np.pi * uu))
            shf = lambda uu: ((uu - 0.5) * 70 * soft, 0)
            base = gy(ROLE['light'][0])
            if t < m_at:
                warp_text(ctx, vb, ROLE['light'][0], base, ROLE['light'][1], color='meDim', squash=sq, shift=shf, stroke=3)
            else:
                k = 1.14 - 0.14 * ease_out(prog(t, m_at, m_at + 0.1))
                burst(ctx, ROLE['light'][0], base - ROLE['light'][1] * 0.34, 180, (t - m_at) / 0.36, color='meDim', rays=16)
                with ctx.at(ROLE['light'][0] * (1 - k), base * (1 - k), scale=k):
                    warp_text(ctx, vb, ROLE['light'][0] + 7, base + 7, ROLE['light'][1], color='bg', squash=sq, shift=shf)
                    warp_text(ctx, vb, ROLE['light'][0], base, ROLE['light'][1], color='me', squash=sq, shift=shf)
            tr = ROLE['track']
            y_top, y_bot = tr['y'] + tr['w'] / 2, tr['y'] + tr['h'] - tr['w'] / 2
            y_mid = (y_top + y_bot) / 2
            pull = lerp(s_at, m_at, 0.45)
            down = 0.84 * ease_in_out(prog(t, pull, m_at - 0.1)) + 0.16 * prog(t, m_at - 0.1, m_at) ** 2
            ky = y_mid if t < push else lerp(y_mid, y_top, prog(t, push, s_at) ** 2) if t < s_at else lerp(y_top, y_bot, down)
            kx = tr['x'] + tr['w'] / 2
            hit = (pulse(t - s_at, 12) if t >= s_at else 0) + (pulse(t - m_at, 12) if t >= m_at else 0)
            ctx.rrect(tr['x'] + 8, tr['y'] + 8, tr['w'], tr['h'], tr['w'] / 2, fill='bg')
            ctx.rrect(tr['x'], tr['y'], tr['w'], tr['h'], tr['w'] / 2, fill='panel', stroke='line', width=3)
            ctx.text(va, tr['x'] + tr['w'] + 34, y_top + 16, size=44, weight=700, color='text' if t >= s_at and down < 0.5 else 'mute')
            ctx.text(vb, tr['x'] + tr['w'] + 34, y_bot + 16, size=44, weight=700, color='text' if t >= m_at else 'mute')
            ctx.circle(kx + 5, ky + 5, 32, fill=True, color='bg')
            ctx.circle(kx, ky, 32, fill=True, color='text', rx=32 * (1 + 0.12 * hit))
        caption(ctx, t, [60, L61, 62])
        if t < grab:
            p = along([(at, 1700, 420), (grab, kx + 10, y_mid + 10, grab - 0.5)], t)
        elif t < m_at + 0.2:
            p = (kx + 10, ky + 10)
        else:
            p = along([(m_at + 0.2, kx + 10, y_bot + 10), (cLoop, 1373, 300)], t)
        burst(ctx, kx, y_mid, 44, (t - grab) / 0.35, color='sub')
        hand(ctx, p[0], p[1], down=1 if grab <= t < m_at + 0.2 else 0)

    # =============================================================================== the trance
    TR = {'x': 960 - 390 / 2, 'y': 70, 'w': 390, 'h': 390 * 1448 / 1086}

    def trance(ctx, t, f, u):
        at = cTrance
        steps = [cue('tranceA', at + 1.4), cue('tranceB', at + 2.3)]
        settle = (cBack - 0.3, cBack - 0.1)
        a = flash_in(t, at)
        ground(ctx, light=(960, 330, 400, 'raised', 0.8))
        d = (8 + 16 * (t - at) + sum(56 * ease_out(prog(t, s, s + 0.14)) for s in steps)) * (1 - ease_in_out(prog(t, *settle)))
        turn = 0.4 * (t - at)
        off = lambda k, ph: (d * k * math.cos(turn + ph), d * k * math.sin(turn + ph))
        if a > 0:
            ctx.circle(960, 320, 220, fill=True, color='line', alpha=0.45 * a)
            if t >= settle[1]:
                inks(ctx, 'boy_bust', fit('boy_bust', TR), alpha=a, shadow=8)
            else:
                for name, ink, role_, k, ph, al in (('f_bust', 0, 'text', 1, 2.6, 1), ('boy_bust', 1, 'me', 0.8, 0.5, 1), ('man_bust', 2, 'line', 0.9, -1.6, 0.8)):
                    r = fit(name, TR)
                    ox, oy = off(k, ph)
                    ink_image(ctx, name, r['x'] + ox, r['y'] + oy, r['w'], r['h'], {ink: role_}, alpha=a * al)
        caption(ctx, t, [62, L63])
        ctx.text(f'› {LOG}', 70, 610, size=22, font='mono', color='sub', alpha=clamp((t - at) * 6))

    return {
        'pre2-settings': {'render': settings_shot, 'camera': settings_cam, 'palette': 'warm'},
        'pre2-gender': {'render': gender, 'palette': 'warm'},
        'pre2-day': {'render': day, 'palette': 'warm'},
        'pre2-role': {'render': role, 'palette': 'warm'},
        'pre2-loop': {'render': loop_shot, 'camera': loop_cam, 'palette': 'warm'},
        'pre2-trance': {'render': trance, 'palette': 'warm'},
        'pre2-loop-b': {'render': loop_b, 'camera': loop_b_cam, 'palette': 'warm'},
    }
