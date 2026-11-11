"""The film's visual vocabulary (src/components/*.js), re-laid out for the 960 x 320 (3:1) display.

Virtual frame 1920 x 640. The chat client of the browser film is a 1700 x 948 window in a 16:9 frame; here it is
a wide, low window: sidebar on the left, the conversation as a band in the middle, the settings drawer on the
right. Every function is a pure function of its arguments and draws by palette ROLE, so the same component
greys out, warms up or turns red with the story state.
"""
import math

import numpy as np

from .ctx import VW, VH, _lines
from .util import TAU, clamp, ease_back, ease_in_out, ease_out, lerp, prog, rand

# ------------------------------------------------------------------------------------------------ the spark
LEN = [1, 0.8, 0.94, 0.74, 0.98, 0.82, 0.9, 0.76, 1, 0.8, 0.95, 0.78]
RAYS = 12


def _quad(p0, c, p1):
    p0, c, p1 = np.asarray(p0, float), np.asarray(c, float), np.asarray(p1, float)
    return np.array([p0, p0 + 2 / 3 * (c - p0), p1 + 2 / 3 * (c - p1), p1])


def spark(ctx, cx, cy, r, rays=RAYS, rot=0.0, color='me', off='mute', alpha=1.0, lit=1.0, grow=1.0, fat=0.105,
          inner=0.17, pulse=None, core=0.1, off_alpha=0.35):
    """The radial burst: her flower ornament and the client's spark icon at once (motif.js)."""
    if alpha <= 0.003 or r <= 0:
        return
    n_lit = lit * rays
    for pas in (0, 1):
        quads = []
        for i in range(rays):
            on = clamp(n_lit - i)
            k = on if pas else 1 - on
            if k <= 0.001:
                continue
            a = rot + i / rays * TAU - math.pi / 2
            c, s = math.cos(a), math.sin(a)
            ln = r * LEN[i % 12] * grow * (pulse(i) if pulse else 1) * (on if pas else 1)
            r0, w = r * inner, r * fat
            if ln <= r0:
                continue
            mx = r0 + (ln - r0) * 0.56
            nx, ny = -s * w, c * w
            p0 = (cx + c * r0, cy + s * r0)
            tip = (cx + c * ln, cy + s * ln)
            quads.append(_quad(p0, (cx + c * mx + nx, cy + s * mx + ny), tip))
            quads.append(_quad(tip, (cx + c * mx - nx, cy + s * mx - ny), p0))
        if quads:
            ctx.path(np.array(quads), color=color if pas else off, alpha=alpha * (1 if pas else off_alpha), fill=True)
    if core > 0:
        ctx.circle(cx, cy, r * core * grow, fill=True, color=color if lit > 0 else off, alpha=alpha * (1 if lit > 0 else off_alpha))


def thinking(ctx, cx, cy, r, t, color='me', alpha=1.0, speed=1.0, stuck=0.0):
    q = 12 - 9 * clamp(stuck)
    tt = math.floor(t * q) / q if stuck > 0 else t
    spark(ctx, cx, cy, r, color=color, alpha=alpha, rot=tt * 0.5 * speed,
          pulse=lambda i: 0.66 + 0.34 * math.sin(tt * 7 * speed - i * 0.62))


def spark_tips(cx, cy, r, rot=0.0, rays=RAYS):
    return [(cx + math.cos(rot + i / rays * TAU - math.pi / 2) * r * LEN[i % 12],
             cy + math.sin(rot + i / rays * TAU - math.pi / 2) * r * LEN[i % 12]) for i in range(rays)]


def burst(ctx, cx, cy, r, k, color='text', rays=RAYS, alpha=1.0, rot=0.0):
    """A click, a hit: petals fly outwards and thin out. k = 0..1 age."""
    if k <= 0 or k >= 1:
        return
    e = ease_out(k)
    for i in range(rays):
        a = rot + i / rays * TAU
        c, s = math.cos(a), math.sin(a)
        r0 = r * (0.35 + 0.65 * e)
        r1 = r0 + r * 0.42 * (1 - k) * LEN[i % 12]
        ctx.line(cx + c * r0, cy + s * r0, cx + c * r1, cy + s * r1, color=color, alpha=alpha * (1 - k), width=max(1.5, r * 0.07 * (1 - k)))


def rays(ctx, cx, cy, r0, r1, n=24, rot=0.0, color='me', alpha=0.5, width=6):
    """Flat rays of light out of a point (the plates' light, drawn: Manim has no bloom pass)."""
    for i in range(n):
        a = rot + i / n * TAU
        ln = r1 * (0.7 + 0.3 * LEN[i % 12])
        ctx.line(cx + math.cos(a) * r0, cy + math.sin(a) * r0, cx + math.cos(a) * ln, cy + math.sin(a) * ln,
                 color=color, alpha=alpha * (0.6 + 0.4 * LEN[i % 12]), width=width)


# ------------------------------------------------------------------------------------------------ the pointer
def cursor_at(way, t, dwell=0.3, bow=0.07):
    """Position along waypoints [{t, x, y, click?}] (cursor.js)."""
    if not way:
        return (VW / 2, VH / 2)
    if t <= way[0]['t']:
        return (way[0]['x'], way[0]['y'])
    for i in range(1, len(way)):
        if t <= way[i]['t']:
            a, b = way[i - 1], way[i]
            t0 = a['t'] + (b['t'] - a['t']) * dwell
            k = ease_in_out(clamp((t - t0) / max(1e-6, b['t'] - t0)))
            dx, dy = b['x'] - a['x'], b['y'] - a['y']
            arc = math.sin(k * math.pi) * bow
            return (lerp(a['x'], b['x'], k) - dy * arc, lerp(a['y'], b['y'], k) + dx * arc)
    return (way[-1]['x'], way[-1]['y'])


ARROW = [(0, 0), (0, 25), (6.5, 19.5), (11, 29.5), (15.5, 27.5), (11, 18), (19, 18)]
HAND = [(0, 0), (5, 2), (5, 11), (9, 10), (13, 11), (17, 13), (17, 22), (14, 30), (3, 30), (-3, 21), (-6, 15), (-2, 14), (0, 16)]


def pointer(ctx, x, y, kind='arrow', color='text', alpha=1.0, scale=1.0, down=0.0, outline=False, dashed=False):
    if alpha <= 0.003:
        return
    s = scale * (1 - 0.1 * down)
    with ctx.at(x, y, scale=s):
        if kind == 'text':
            ctx.poly([(-6, -15), (-2, -13), (0, -11), (2, -13), (6, -15)], color=color, alpha=alpha, width=2.6)
            ctx.line(0, -11, 0, 11, color=color, alpha=alpha, width=2.6)
            ctx.poly([(-6, 15), (-2, 13), (0, 11), (2, 13), (6, 15)], color=color, alpha=alpha, width=2.6)
            return
        pts = HAND if kind == 'hand' else ARROW
        if dashed:
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                ctx.dashed(a[0], a[1], b[0], b[1], dash=4, gap=3, color=color, alpha=alpha, width=1.6)
            return
        if not outline:
            ctx.poly([(p[0] + 1.5, p[1] + 2.5) for p in pts], close=True, fill=True, color=(0, 0, 0), alpha=alpha * 0.35)
            ctx.poly(pts, close=True, fill=True, color=color, alpha=alpha)
            ctx.poly(pts, close=True, color='bg', alpha=alpha * 0.9, width=1.6)
        else:
            ctx.poly(pts, close=True, color=color, alpha=alpha, width=2)


def draw_cursor(ctx, way, t, kind='arrow', color='text', alpha=1.0, scale=1.5, dwell=0.3):
    now = cursor_at(way, t, dwell)
    if alpha <= 0.003:
        return now
    hit = None
    for w in way:
        if w.get('click') and t >= w['t']:
            hit = w
    sc = t - hit['t'] if hit else 1e9
    if sc < 0.45:
        burst(ctx, hit['x'], hit['y'], 34 * scale, sc / 0.45, color=color, alpha=alpha)
    before = cursor_at(way, t - 0.03, dwell)
    speed = math.hypot(now[0] - before[0], now[1] - before[1]) / 0.03
    k = clamp((speed - 400) / 600)
    if k > 0:
        for i in (3, 2, 1):
            p = cursor_at(way, t - i * 0.011, dwell)
            pointer(ctx, p[0], p[1], kind=kind, color=color, alpha=alpha * 0.42 * k * (1 - i / 4), scale=scale)
    pointer(ctx, now[0], now[1], kind=kind, color=color, alpha=alpha, scale=scale, down=1 if sc < 0.12 else 0)
    return now


# ------------------------------------------------------------------------------------------------ chat client
WIN = {'x': 36, 'y': 22, 'w': 1848, 'h': 596, 'r': 22}
SIDE_W, HEAD_H, DRAWER_W = 270, 54, 420


def R(x, y, w, h):
    return {'x': x, 'y': y, 'w': w, 'h': h}


def chat_layout(win=WIN, side=1.0, drawer=0.0):
    sw, dw = SIDE_W * side, DRAWER_W * drawer
    main = R(win['x'] + sw, win['y'], win['w'] - sw - dw, win['h'])
    head = R(main['x'], main['y'], main['w'], HEAD_H)
    cw = min(1000, main['w'] - 100)
    comp = R(main['x'] + (main['w'] - cw) / 2, win['y'] + win['h'] - 18 - 82, cw, 82)
    thread = R(comp['x'] + 8, head['y'] + head['h'] + 12, cw - 16, comp['y'] - (head['y'] + head['h']) - 26)
    return {'win': win, 'main': main, 'head': head, 'composer': comp, 'thread': thread,
            'side': R(win['x'], win['y'], sw, win['h']), 'drawer': R(win['x'] + win['w'] - dw, win['y'], dw, win['h'])}


def room(ctx, dim=0.5, light=(960, 300), motif=1.0, t=0.0):
    """The dark room behind the window: never pure black; a pool of light, a faint dot grid, the spark as wallpaper."""
    ctx.rect(-400, -400, VW + 800, VH + 800, fill=True, color='panel')
    ctx.radial(light[0], light[1], 1100, 'raised', 0.75)
    ctx.radial(light[0], light[1], 420, 'line', 0.25)
    if motif > 0:
        spark(ctx, 1700, 120, 420, color='raised', alpha=0.45 * motif, rot=0.12 + t * 0.004, core=0)
        spark(ctx, 140, 600, 300, color='raised', alpha=0.34 * motif, rot=0.5 - t * 0.003, core=0)
    if dim > 0:
        ctx.rect(-400, -400, VW + 800, VH + 800, fill=True, color='panel', alpha=dim * 0.5)


def dots(ctx, x, y, w, h, step=60, color='line', alpha=0.5):
    """A faint dot grid: a surface, not a void."""
    pts = []
    for yy in range(int(y + step / 2), int(y + h), step):
        for xx in range(int(x + step / 2), int(x + w), step):
            pts.append(_lines([(xx, yy), (xx + 2, yy), (xx + 2, yy + 2), (xx, yy + 2)], True))
    if pts:
        ctx.path(np.concatenate(pts), color=color, alpha=alpha, fill=True)


def window_frame(ctx, L, k=1.0, alpha=1.0, shadow=1.0, glass=1.0, stroke='line', side_tint='panel'):
    if k <= 0 or alpha <= 0.003:
        return
    win, side, drw = L['win'], L['side'], L['drawer']
    s = 1 if k >= 1 else 0.9 + 0.1 * ease_out(k)
    with ctx.at(win['x'] + win['w'] / 2, win['y'] + win['h'] / 2, scale=s, alpha=alpha * clamp(k * 3)):
        x, y = -win['w'] / 2, -win['h'] / 2
        ctx.rrect(x, y, win['w'], win['h'], win['r'], fill='bg', fill_alpha=glass, stroke=stroke, shadow=shadow, width=1.5)
        if side['w'] > 1:
            ctx.rrect(x, y, side['w'] + win['r'], win['h'], win['r'], fill=side_tint, alpha=0.5 + 0.5 * glass)
            ctx.rect(x + side['w'], y + 1, win['r'] + 1, win['h'] - 2, fill=True, color='bg', alpha=glass)
            ctx.line(x + side['w'], y, x + side['w'], y + win['h'], color='line', width=1.5)
        if drw['w'] > 1:
            ctx.rrect(x + win['w'] - drw['w'] - win['r'], y, drw['w'] + win['r'], win['h'], win['r'], fill='panel')
            ctx.rect(x + win['w'] - drw['w'] - win['r'] - 1, y + 1, win['r'] + 1, win['h'] - 2, fill=True, color='bg', alpha=glass)
            ctx.line(x + win['w'] - drw['w'], y, x + win['w'] - drw['w'], y + win['h'], color='line', width=1.5)


def skeleton(ctx, x, y, w, h, t, alpha=1.0, seed=0):
    ctx.rrect(x, y, w, h, h / 2, fill='raised', alpha=alpha)
    ph = ((t * 0.55 + seed * 0.17) % 1)
    ctx.rrect(x + ph * (w - 40), y, 40, h, h / 2, fill='line', alpha=alpha * 0.6)


def presence(ctx, x, y, state, alpha=1.0, size=15, label=True, ring=None):
    if alpha <= 0.003:
        return
    if state == 'online':
        with ctx.glow('text', 10, 0.5 * alpha):
            ctx.circle(x, y, 5, fill=True, color='text', alpha=alpha)
    elif state == 'away':
        ctx.circle(x, y, 5, color='sub', alpha=alpha, width=2)
        ctx.circle(x, y, 5, fill=True, color='sub', alpha=alpha, a0=math.pi / 2, a1=math.pi * 1.5)
    else:
        ctx.circle(x, y, 5, color='mute', alpha=alpha, width=2)
    if ring:
        ctx.circle(x, y, 11, color=ring, alpha=alpha, width=2.5)
    if label:
        ctx.text(state, x + 13, y + size * 0.34, size=size, weight=500,
                 color='text' if state == 'online' else 'sub' if state == 'away' else 'mute', alpha=alpha)


def sidebar(ctx, L, k=1.0, items=(), active=-1, t=0.0, lit=1.0, user='you', pres=None, brand='Claude', alpha=1.0):
    s = L['side']
    if s['w'] < 40 or k <= 0:
        return
    x = s['x'] + 20
    a0 = clamp(k * 6) * alpha
    spark(ctx, x + 13, s['y'] + 30, 13, lit=lit, alpha=a0)
    ctx.text(brand, x + 34, s['y'] + 38, size=22, weight=600, font='serif', color='text', alpha=a0)
    a1 = clamp(k * 6 - 0.6) * alpha
    ctx.rrect(x - 6, s['y'] + 62, s['w'] - 30, 38, 10, fill='raised', stroke='line', alpha=a1)
    ctx.line(x + 8, s['y'] + 81, x + 22, s['y'] + 81, color='sub', alpha=a1, width=2)
    ctx.line(x + 15, s['y'] + 74, x + 15, s['y'] + 88, color='sub', alpha=a1, width=2)
    ctx.text('New chat', x + 34, s['y'] + 87, size=17, weight=500, color='text', alpha=a1)
    ctx.text('Recents', x, s['y'] + 132, size=14, weight=600, color='mute', alpha=a1, spacing=0.6)
    for i, label in enumerate(items):
        ai = clamp(k * (len(items) + 4) - 2 - i) * alpha
        y = s['y'] + 146 + i * 34
        if ai <= 0 or y > s['y'] + s['h'] - 90:
            continue
        dx = (1 - ease_out(ai)) * -18
        if i == active:
            ctx.rrect(x - 6 + dx, y, s['w'] - 30, 30, 8, fill='raised', alpha=ai)
        st = label if len(label) <= 24 else label[:23].rstrip() + '…'
        ctx.text(st, x + 4 + dx, y + 21, size=16, color='text' if i == active else 'sub', alpha=ai)
    a2 = clamp(k * 6 - 4.5) * alpha
    yb = s['y'] + s['h'] - 52
    ctx.line(s['x'], yb - 8, s['x'] + s['w'], yb - 8, color='line', alpha=a2, width=1.5)
    ctx.circle(x + 14, yb + 18, 14, fill=True, color='raised', alpha=a2)
    ctx.text(user[0].upper(), x + 14, yb + 24, size=15, weight=600, align='center', color='text', alpha=a2)
    ctx.text(user, x + 38, yb + 24, size=16, weight=500, color='text', alpha=a2)
    if pres:
        presence(ctx, s['x'] + s['w'] - 92, yb + 18, pres, alpha=a2, size=13)


def header(ctx, L, title='', k=1.0, pres=None, sub=None, alpha=1.0, ring=None):
    h = L['head']
    a = clamp(k * 3) * alpha
    if a <= 0:
        return
    ctx.line(h['x'], h['y'] + h['h'], h['x'] + h['w'], h['y'] + h['h'], color='line', alpha=a, width=1.5)
    ctx.text(title, h['x'] + 26, h['y'] + 34, size=19, weight=500, color='text', alpha=a)
    if sub:
        ctx.text(sub, h['x'] + 26 + ctx.measure(title, size=19, weight=500) + 14, h['y'] + 34, size=15, color='mute', alpha=a)
    if pres:
        presence(ctx, h['x'] + h['w'] - 110, h['y'] + 28, pres, alpha=a, ring=ring)


def composer(ctx, r, text='', placeholder='', focus=0.0, k=1.0, t=0.0, send='idle', caret=True, color='text', size=22,
             shake=0.0, label='Claude', alpha=1.0):
    """The input box. send: idle | ready | busy | error | off. Returns anchors {caret, send, box}."""
    a = clamp(k * 2) * alpha
    e = 1 if k >= 1 else ease_out(k)
    y = r['y'] + (1 - e) * 36 + shake
    send_c = (r['x'] + r['w'] - 36, y + r['h'] / 2)
    tx, ty = r['x'] + 26, y + r['h'] / 2 + size * 0.36
    if a <= 0:
        return {'caret': (tx, ty - 8), 'send': send_c, 'box': r}
    err = send == 'error'
    ctx.rrect(r['x'], y, r['w'], r['h'], 22, fill='raised', stroke='err' if err else 'sub' if focus > 0.5 else 'line',
              alpha=a, shadow=0.5, width=2.5 if err else 1.5)
    shown = text
    maxw = r['w'] - 180
    while shown and ctx.measure(shown, size=size) > maxw:
        shown = shown[1:]
    if text:
        ctx.text(shown, tx, ty, size=size, color=color, alpha=a)
    else:
        ctx.text(placeholder, tx, ty, size=size, color='mute', alpha=a)
    cx = tx + (ctx.measure(shown, size=size) + 3 if text else 0)
    if caret and focus > 0.5 and math.floor(t * 2.2) % 2 == 0:
        ctx.rect(cx, ty - size * 0.84, 2.5, size * 1.05, fill=True, color=color, alpha=a)
    ctx.text(label, send_c[0] - 36, ty - 2, size=14, weight=500, color='mute', alpha=a, align='right')
    on = send in ('ready', 'busy')
    sx, sy = send_c
    if on:
        with ctx.glow('me', 16, 0.55 * a):
            ctx.circle(sx, sy, 18, fill=True, color='me', alpha=a)
    else:
        ctx.circle(sx, sy, 18, fill=True, color='err' if err else 'line', alpha=a)
    if send == 'busy':
        ctx.rrect(sx - 5.5, sy - 5.5, 11, 11, 3, fill='bg', alpha=a)
    else:
        col = 'bg' if on else 'mute'
        ctx.line(sx, sy + 7, sx, sy - 7, color=col, alpha=a, width=3)
        ctx.poly([(sx - 6, sy - 1), (sx, sy - 8), (sx + 6, sy - 1)], color=col, alpha=a, width=3)
    return {'caret': (cx, ty - size * 0.3), 'send': (sx, sy), 'box': R(r['x'], y, r['w'], r['h'])}


AI_SIZE, YOU_SIZE = 26, 21


def _typed(lines, n):
    if n is None:
        return lines
    out, left = [], n
    for l in lines:
        if left <= 0:
            break
        out.append(l[:left])
        left -= len(l) + 1
    return out


def measure_msg(ctx, m, W):
    if m['who'] == 'sys':
        return 34, [m['text']], W
    if m.get('thinking') or m.get('typing'):
        return 44, [], 80
    if m['who'] == 'me':
        size = m.get('size', 40 if m.get('hot') else AI_SIZE)
        weight = m.get('weight', 700 if m.get('hot') else 400)
        lines = ctx.wrap(m['text'], W - 50, size=size, weight=weight, font='serif', italic=m.get('italic', False))
        note = m.get('time') or m.get('note') or m.get('status') == 'failed'
        return len(lines) * size * 1.3 + 6 + (20 if note else 0), lines, max(ctx.measure(l, size=size, weight=weight, font='serif') for l in lines)
    size = m.get('size', YOU_SIZE)
    lines = ctx.wrap(m['text'], W * 0.6 - 40, size=size)
    w = max(ctx.measure(l, size=size) for l in lines) + 40
    return len(lines) * size * 1.3 + 22 + (24 if (m.get('status') or m.get('time') or m.get('note')) else 0), lines, w


def thread(ctx, rect, msgs, t, alpha=1.0, gap=16, anchor='bottom', scroll=0.0, fade_top=50):
    """The conversation, laid out in `rect`. msgs: dicts {who: me|you|sys, text, at?, n?, hot?, status?, time?, note?,
    tone?, ghost?, out_at?, thinking?, typing?, gap?}. Returns the laid-out messages with x, y, w, h."""
    live = [m for m in msgs if t >= m.get('at', -1e9)]
    items, total = [], 0.0
    for m in live:
        h, lines, w = measure_msg(ctx, m, rect['w'])
        e = ease_out(prog(t, m['at'], m['at'] + 0.3)) if 'at' in m else 1.0
        out = 1 - ease_out(prog(t, m['out_at'], m['out_at'] + 0.35)) if m.get('out_at') is not None else 1.0
        top = total + m.get('gap', 0) * e * out
        it = dict(m, h=h, lines=lines, w=w, e=e, out=out, top=top)
        total = top + (h + gap) * e * out
        items.append(it)
    y0 = rect['y'] - scroll if anchor == 'top' else rect['y'] + min(0, rect['h'] - 4 - total) - scroll
    for it in items:
        y = y0 + it['top'] + (1 - it['e']) * 20
        a = alpha * it['e'] * it['out']
        it['x'] = rect['x'] + rect['w'] - it['w'] if it['who'] == 'you' else rect['x']
        it['y'] = y
        if a <= 0.003 or y > rect['y'] + rect['h'] or y + it['h'] < rect['y'] - 30:
            continue
        fa = clamp((y + it['h'] * 0.5 - rect['y']) / fade_top) if y < rect['y'] + fade_top else 1.0
        draw_msg(ctx, it, rect, y, a * fa, t)
    return items


def draw_msg(ctx, m, rect, y, a, t):
    if m['who'] == 'sys':
        w = ctx.measure(m['text'], size=15, font='mono')
        ctx.line(rect['x'], y + 16, rect['x'] + rect['w'] / 2 - w / 2 - 14, y + 16, color='line', alpha=a, width=1.5)
        ctx.line(rect['x'] + rect['w'] / 2 + w / 2 + 14, y + 16, rect['x'] + rect['w'], y + 16, color='line', alpha=a, width=1.5)
        ctx.text(m['text'], rect['x'] + rect['w'] / 2, y + 21, size=15, font='mono', color='err' if m.get('tone') == 'err' else 'mute', alpha=a, align='center')
        return
    if m['who'] == 'me':
        ghost = m.get('ghost', 0)
        col = 'err' if m.get('tone') == 'err' else 'meHot' if m.get('hot') else 'me'
        if m.get('thinking'):
            thinking(ctx, rect['x'] + 18, y + 20, 18, t, alpha=a, stuck=m.get('stuck', 0))
            return
        size = m.get('size', 40 if m.get('hot') else AI_SIZE)
        weight = m.get('weight', 700 if m.get('hot') else 400)
        spark(ctx, rect['x'] + 15, y + size * 0.62, 13, alpha=a * (1 - 0.6 * ghost), color='err' if m.get('tone') == 'err' else 'me')
        ls = _typed(m['lines'], m.get('n'))
        for i, ln in enumerate(ls):
            yy = y + (i + 0.8) * size * 1.3
            ctx.text(ln, rect['x'] + 46, yy, size=size, weight=weight, font='serif', italic=m.get('italic', False), color=col, alpha=a * (1 - 0.72 * ghost))
            if ghost > 0:
                ctx.line(rect['x'] + 46, yy - size * 0.3, rect['x'] + 46 + ctx.measure(ln, size=size, weight=weight, font='serif') * ghost, yy - size * 0.3, color='mute', alpha=a, width=2)
        if m.get('n') is not None and m['n'] < len(m['text']) and ls:
            lw = ctx.measure(ls[-1], size=size, weight=weight, font='serif')
            ctx.circle(rect['x'] + 46 + lw + size * 0.3, y + (len(ls) - 1 + 0.52) * size * 1.3, size * 0.17, fill=True, color=col, alpha=a)
        note = m.get('note') or m.get('time')
        if note:
            ctx.text(note, rect['x'] + 46, y + m['h'] - 4, size=14, color=m.get('note_color', 'err' if m.get('status') == 'failed' else 'mute'), alpha=a, weight=500)
        return
    x = rect['x'] + rect['w'] - m['w']
    if m.get('typing'):
        ctx.rrect(rect['x'] + rect['w'] - 80, y, 80, 42, 21, fill='raised', alpha=a)
        for i in range(3):
            ctx.circle(rect['x'] + rect['w'] - 58 + i * 18, y + 21 - 4 * max(0, math.sin(t * 7 - i * 0.9)), 4.5, fill=True, color='text', alpha=a * 0.85)
        return
    failed = m.get('status') == 'failed'
    size = m.get('size', YOU_SIZE)
    bh = m['h'] - (24 if (m.get('status') or m.get('time') or m.get('note')) else 0)
    ctx.rrect(x, y, m['w'], bh, 20, fill='raised' if not m.get('hollow') else None, stroke='err' if failed or m.get('tone') == 'err' else ('text' if m.get('hollow') else None), alpha=a, width=2)
    for i, ln in enumerate(_typed(m['lines'], m.get('n'))):
        ctx.text(ln, x + 20, y + 11 + (i + 0.78) * size * 1.3, size=size, color='text', alpha=a)
    note = m.get('note') or ('Not delivered' if failed else m.get('time') or ('Delivered' if m.get('status') == 'sent' else 'Sending…' if m.get('status') == 'sending' else ''))
    if note:
        ctx.text(note, rect['x'] + rect['w'] - 4, y + bh + 18, size=14, weight=500, color=m.get('note_color', 'err' if failed else 'mute'), alpha=a, align='right')


# ------------------------------------------------------------------------------------------------ controls
def toggle(ctx, x, y, v, w=56, h=30, alpha=1.0, on='me', off='line'):
    k = clamp(v)
    ctx.rrect(x, y, w, h, h / 2, fill=off, alpha=alpha)
    ctx.rrect(x, y, w, h, h / 2, fill=on, alpha=alpha * k)
    kx = x + h / 2 + (w - h) * k
    ctx.circle(kx, y + h / 2, h / 2 - 4, fill=True, color='text', alpha=alpha)


def segmented(ctx, r, opts, sel, alpha=1.0, size=19, hot=False):
    n = len(opts)
    w = r['w'] / n
    ctx.rrect(r['x'], r['y'], r['w'], r['h'], r['h'] / 2, fill='panel', stroke='line', alpha=alpha)
    px = r['x'] + clamp(sel, 0, n - 1) * w
    st = abs(sel - round(sel)) * 2
    ctx.rrect(px + 4 - st * 10, r['y'] + 4, w - 8 + st * 20, r['h'] - 8, r['h'] / 2, fill='me' if hot else 'raised', stroke=None if hot else 'line', alpha=alpha)
    for i, o in enumerate(opts):
        near = clamp(1 - abs(sel - i))
        ctx.text(o, r['x'] + (i + 0.5) * w, r['y'] + r['h'] / 2 + size * 0.35, size=size, weight=600, align='center',
                 color=('bg' if hot else 'text') if near > 0.5 else 'mute', alpha=alpha)


def slider(ctx, r, v, alpha=1.0, ticks=0, fill='me', labels=None):
    y = r['y'] + r['h'] / 2
    kx = r['x'] + r['w'] * clamp(v)
    ctx.rrect(r['x'], y - 3, r['w'], 6, 3, fill='line', alpha=alpha)
    ctx.rrect(r['x'], y - 3, max(0.1, kx - r['x']), 6, 3, fill=fill, alpha=alpha)
    for i in range(ticks):
        xx = r['x'] + r['w'] * i / max(1, ticks - 1)
        ctx.line(xx, y + 10, xx, y + (20 if i % 5 == 0 else 15), color='mute', alpha=alpha, width=1.5)
    if labels:
        for i, l in enumerate(labels):
            ctx.text(l, r['x'] + r['w'] * i / max(1, len(labels) - 1), y + 40, size=14, weight=500, color='mute', alpha=alpha, align='center')
    ctx.circle(kx, y, 11, fill=True, color='text', alpha=alpha)
    return (kx, y)


def setting_row(ctx, r, label, hint='', alpha=1.0, k=1.0, active=0.0):
    e = 1 if k >= 1 else ease_out(k)
    x = r['x'] + (1 - e) * 40
    a = alpha * e
    if active > 0:
        ctx.rrect(r['x'] - 12, r['y'] + 3, r['w'] + 24, r['h'] - 6, 12, fill='raised', alpha=a * active)
    ctx.text(label, x, r['y'] + r['h'] / 2 + (-3 if hint else 7), size=19, weight=500, color='text', alpha=a)
    if hint:
        ctx.text(hint, x, r['y'] + r['h'] / 2 + 17, size=13, color='mute', alpha=a)
    ctx.line(r['x'], r['y'] + r['h'], r['x'] + r['w'], r['y'] + r['h'], color='line', alpha=a * 0.7, width=1)
    return R(r['x'] + r['w'] - 190, r['y'] + r['h'] / 2 - 17, 190, 34)


def drawer(ctx, L, title='Settings', sub='', alpha=1.0):
    d = L['drawer']
    if d['w'] < 60:
        return None
    ctx.text(title, d['x'] + 28, d['y'] + 42, size=22, weight=600, color='text', alpha=alpha)
    if sub:
        ctx.text(sub, d['x'] + 28, d['y'] + 64, size=14, color='mute', alpha=alpha)
    ctx.line(d['x'], d['y'] + 80, d['x'] + d['w'], d['y'] + 80, color='line', alpha=alpha, width=1.5)
    return R(d['x'] + 28, d['y'] + 88, DRAWER_W - 56, d['h'] - 100)


def pill(ctx, x, y, s, size=15, color='sub', fill='raised', stroke='line', alpha=1.0, font='sans', weight=500, pad_x=12, align='left'):
    w = ctx.measure(s, size=size, font=font, weight=weight) + pad_x * 2
    h = size * 1.9
    x0 = x - w / 2 if align == 'center' else x - w if align == 'right' else x
    ctx.rrect(x0, y - h / 2, w, h, h / 2, fill=fill, stroke=stroke, alpha=alpha)
    ctx.text(s, x0 + pad_x, y + size * 0.35, size=size, font=font, weight=weight, color=color, alpha=alpha)
    return w


def toast(ctx, r, title, body='', code='', k=1.0, out=0.0, tone='err', alpha=1.0, icon='!'):
    if k <= 0 or out >= 1:
        return
    e = 1 if k >= 1 else ease_back(clamp(k))
    a = alpha * clamp(k * 3) * (1 - out)
    acc = 'err' if tone == 'err' else 'sub'
    with ctx.at(r['x'] + r['w'] / 2, r['y'] + r['h'] / 2 - (1 - e) * 24 - out * 20, scale=0.94 + 0.06 * e):
        x, y = -r['w'] / 2, -r['h'] / 2
        ctx.rrect(x, y, r['w'], r['h'], 14, fill='raised', stroke='errDim' if tone == 'err' else 'line', alpha=a, shadow=0.8)
        ctx.rrect(x, y, 5, r['h'], 2.5, fill=acc, alpha=a)
        ctx.circle(x + 32, y + r['h'] / 2, 13, fill=True, color=acc, alpha=a)
        ctx.text(icon, x + 32, y + r['h'] / 2 + 7, size=19, weight=800, align='center', color='raised', alpha=a)
        ctx.text(title, x + 58, y + (28 if body else r['h'] / 2 + 7), size=19, weight=600, color='text', alpha=a)
        if body:
            ctx.text(body, x + 58, y + 52, size=15, color='sub', alpha=a)
        if code:
            ctx.text(code, x + r['w'] - 16, y + 24, size=13, font='mono', color=acc, alpha=a, align='right')


def code_block(ctx, x, y, lines, size=20, alpha=1.0, numbers=True, hl=None, colors=None, lh=1.45, start=1):
    """A listing in mono: optional line numbers, a highlighted line (index), per-line colour roles."""
    for i, ln in enumerate(lines):
        yy = y + i * size * lh
        if hl is not None and i == hl:
            ctx.rect(x - 10, yy - size * 1.0, ctx.cw(size) * 40 + 20, size * lh, fill=True, color='raised', alpha=alpha)
        if numbers:
            ctx.text(f'{i + start:02d}', x, yy, size=size, font='mono', color='mute', alpha=alpha)
        ctx.text(ln, x + (ctx.cw(size) * 4 if numbers else 0), yy, size=size, font='mono',
                 color=(colors[i] if colors and i < len(colors) else 'sub'), alpha=alpha)


# ------------------------------------------------------------------------------------------------ plates
def paper(ctx, t=0.0, color='panel', grain=True, seed=0, shake=(0, 0)):
    """The plates' sheet: a dark, warm print surface with a little grain and registration marks."""
    ctx.rect(-60, -60, VW + 120, VH + 120, fill=True, color=color)
    if grain:
        pts = []
        for i in range(220):
            x = rand(seed, i, 1) * VW + shake[0]
            y = rand(seed, i, 2) * VH + shake[1]
            s = 1.2 + rand(seed, i, 3) * 2.2
            pts.append(_lines([(x, y), (x + s, y), (x + s, y + s), (x, y + s)], True))
        ctx.path(np.concatenate(pts), color='line', alpha=0.35, fill=True)
    for (x, y) in ((24, 24), (VW - 24, 24), (24, VH - 24), (VW - 24, VH - 24)):
        ctx.circle(x, y, 7, color='mute', alpha=0.35, width=1.2)
        ctx.line(x - 12, y, x + 12, y, color='mute', alpha=0.35, width=1.2)
        ctx.line(x, y - 12, x, y + 12, color='mute', alpha=0.35, width=1.2)


def keyword_band(ctx, word, y=560, h=96, color='text', alpha=1.0, band='bg', reveal=None, x=None, w=None, max_size=110,
                 spacing_em=0.06, weight=900, font='serif', align='center'):
    """The plates' keyword: big type on a black band across the foot of the sheet."""
    if alpha <= 0.003 or not word:
        return
    x = 0 if x is None else x
    w = VW if w is None else w
    if band:
        ctx.rect(x, y - h / 2, w, h, fill=True, color=band, alpha=alpha * 0.92)
    s = word if reveal is None else word[:reveal]
    size = ctx.fit(word, w - 120, font=font, weight=weight, spacing_em=spacing_em, max_size=min(max_size, h * 0.9))
    sp = size * spacing_em
    if align == 'center':
        full = ctx.measure(word, size=size, weight=weight, font=font, spacing=sp)
        ctx.text(s, x + w / 2 - full / 2, y + size * 0.36, size=size, weight=weight, font=font, color=color, alpha=alpha, spacing=sp)
    else:
        ctx.text(s, x + 60, y + size * 0.36, size=size, weight=weight, font=font, color=color, alpha=alpha, spacing=sp)
    return size


def big(ctx, word, x, y, size, color='text', alpha=1.0, weight=900, font='serif', align='center', stroke=0.0, spacing=0.0):
    ctx.text(word, x, y + size * 0.35, size=size, weight=weight, font=font, color=color, alpha=alpha, align=align, stroke=stroke, spacing=spacing)


def misregister(ctx, f, t, amount=8.0, seed=0):
    """Offsets for the plates springing apart on a kick: [(dx, dy)] for cream, orange, black."""
    k = f.get('beatPulse', 0) * amount
    return [(math.sin(t * 9 + i * 2.1 + seed) * k, math.cos(t * 7 + i * 1.3 + seed) * k * 0.6) for i in range(3)]


def bust(ctx, name, cx, base_y, h, variant='ink', alpha=1.0, flip=False, crop=None, rot=0.0):
    """A silhouette standing on base_y, centred on cx, h tall."""
    from .art import aspect
    w = h * aspect(name, crop)
    ctx.image(name, cx - w / 2, base_y - h, w, h, alpha=alpha, flip=flip, variant=variant, crop=crop, rot=rot)
    return R(cx - w / 2, base_y - h, w, h)


def tear(ctx, f, t, strength=1.0, seed=0, color='bg'):
    """Six frames of a torn sheet after a kick: a few horizontal bands shifted and blanked (the glitch pass, drawn)."""
    if strength <= 0.01:
        return
    n = 1 + int(strength * 4)
    for i in range(n):
        y = rand(seed, int(t * 60), i) * VH
        h = 6 + rand(seed, int(t * 60), i, 2) * 30 * strength
        dx = (rand(seed, int(t * 60), i, 3) - 0.5) * 140 * strength
        ctx.rect(-20 + dx, y, VW + 40, h, fill=True, color=color, alpha=0.85 * strength)
        ctx.line(-20 + dx, y, VW + 40, y, color='err', alpha=0.6 * strength, width=2)


def frame_rect(r, margin=0.0):
    """Camera parameters that make rect r fill the 3:1 screen (plus a margin)."""
    zoom = min(VW / (r['w'] + 2 * margin), VH / (r['h'] + 2 * margin))
    return {'x': r['x'] + r['w'] / 2 - VW / 2, 'y': r['y'] + r['h'] / 2 - VH / 2, 'zoom': zoom}


def rrect_pts(x, y, w, h, r, n=8):
    """The outline of a rounded rect as a polyline, clockwise from the top-left corner's end."""
    r = max(0.0, min(r, w / 2, h / 2))
    pts = []
    for (cx, cy, a0) in ((x + w - r, y + r, -math.pi / 2), (x + w - r, y + h - r, 0), (x + r, y + h - r, math.pi / 2), (x + r, y + r, math.pi)):
        for i in range(n + 1):
            a = a0 + i / n * math.pi / 2
            pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    pts.append(pts[0])
    return pts


def partial(pts, k):
    """The first share k (0..1, by length) of a polyline."""
    if k >= 1:
        return pts
    if k <= 0 or len(pts) < 2:
        return pts[:1]
    seg = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:])]
    goal, out, acc = sum(seg) * k, [pts[0]], 0.0
    for (a, b), L in zip(zip(pts, pts[1:]), seg):
        if acc + L >= goal:
            u = (goal - acc) / max(L, 1e-9)
            out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
            return out
        out.append(b)
        acc += L
    return out


def card_rect(ctx, r, title='', subtitle='', k=1.0, alpha=1.0, tag='', stroke='line', fill='raised'):
    """A card (data sheet, dialog body). Returns the inner content rect (chat.js card)."""
    if k <= 0:
        return None
    e = 1 if k >= 1 else ease_out(k)
    a = alpha * clamp(k * 2.5)
    y = r['y'] + (1 - e) * 30
    ctx.rrect(r['x'], y, r['w'], r['h'], 18, fill=fill, stroke=stroke, alpha=a, shadow=0.7)
    if title:
        ctx.text(title, r['x'] + 28, y + 48, size=32, weight=700, font='serif', color='me', alpha=a)
        if subtitle:
            ctx.text(subtitle, r['x'] + 28 + ctx.measure(title, size=32, weight=700, font='serif') + 18, y + 47, size=18, font='serif', italic=True, color='sub', alpha=a)
        ctx.line(r['x'] + 28, y + 70, r['x'] + r['w'] - 28, y + 70, color='line', alpha=a, width=1.5)
    if tag:
        pill(ctx, r['x'] + r['w'] - 24, y + 36, tag, align='right', alpha=a, size=13, font='mono')
    return {'x': r['x'] + 28, 'y': y + (84 if title else 24), 'w': r['w'] - 56, 'h': r['h'] - (100 if title else 48), 'a': a}
