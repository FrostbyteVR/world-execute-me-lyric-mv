"""Helpers every section file shares (src/scenes/kit.js)."""
import math

from ..components import (chat_layout, composer, header, room, sidebar, thread, window_frame)
from ..util import clamp, ease_out, prog


def ai_line(ctx, env, i, t, x, y, size=40, weight=400, color='me', alpha=1.0, align='left', italic=False, caret=True, hold=1e9):
    """A lyric line in the AI's voice (serif), typed, at a free position. Returns its full width."""
    if i is None or i < 0 or i >= len(env.lyrics.lines) or t < env.T(i):
        return 0
    full = env.text(i)
    n = env.lyrics.typed(i, t)
    o = dict(size=size, weight=weight, font='serif', italic=italic)
    w = ctx.measure(full, **o)
    x0 = x - w / 2 if align == 'center' else x - w if align == 'right' else x
    a = alpha * (1 - prog(t, env.lyrics.end(i) + hold, env.lyrics.end(i) + hold + 0.3))
    ctx.text(full[:n], x0, y, color=color, alpha=a, **o)
    if caret and n < len(full):
        ctx.circle(x0 + ctx.measure(full[:n], **o) + size * 0.3, y - size * 0.28, size * 0.16, fill=True, color=color, alpha=a)
    return w


def lyric_msgs(env, a, b, t=None, hot=True):
    """Lyric lines a..b as the AI's messages, typed as they are sung (keyword lines larger)."""
    out = []
    for i in range(a, b + 1):
        ln = env.lyrics.lines[i]
        m = {'who': 'me', 'text': ln['text'], 'at': env.T(i)}
        if t is not None:
            m['n'] = env.lyrics.typed(i, t)
        if hot and ln.get('emphasis'):
            m['hot'] = True
        out.append(m)
    return out


def client(ctx, env, t, side=1.0, drawer=0.0, title=None, pres='online', active=0, glass=1.0, dim=0.45, lit=1.0,
           side_items=None, alpha=1.0, ring=None):
    """Room + window + sidebar + header: the whole chat client. Returns the layout."""
    L = chat_layout(side=side, drawer=drawer)
    room(ctx, dim=dim, t=t)
    window_frame(ctx, L, glass=glass, alpha=alpha)
    sidebar(ctx, L, items=side_items if side_items is not None else env.script.get('sidebar', []), active=active, t=t,
            pres=pres, lit=lit, alpha=alpha)
    header(ctx, L, title=env.script.get('title', '') if title is None else title, pres=pres, alpha=alpha, ring=ring)
    return L


def section_fallback(env, row):
    pres = 'offline' if row['state'].startswith(('off', 'error', 'errWarm', 'ash', 'dead')) else 'online'
    lines = row['lines']

    def render(ctx, t, f, u):
        L = client(ctx, env, t, pres=pres)
        if lines:
            thread(ctx, L['thread'], lyric_msgs(env, lines[0], lines[1], t), t)
        composer(ctx, L['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t)
    return {'render': render}


# ---- more of kit.js / shot.js ------------------------------------------------------------------------------
from ..components import bust, spark  # noqa: E402
from ..util import rand, pulse  # noqa: E402

GLYPHS = 'ABCDEFGHIKLMNOPRSTUVXYZ0123456789#/<>[]'


def enter(t, t0, i=0, step=0.05, dur=0.32, rise=22):
    """Staggered, eased entrance of item i: {k, a, dy, s, raw} (shot.js enter)."""
    raw = clamp((t - t0 - i * step) / dur)
    k = 1 - (1 - raw) ** 3
    return {'raw': raw, 'k': k, 'a': clamp(raw * 2.2), 'dy': (1 - k) * rise, 's': 0.94 + 0.06 * k}


def shake(t, amp, seed=0):
    if amp <= 0:
        return (0.0, 0.0)
    s = lambda k: math.sin(t * (41 + k * 13 + seed) + k * 2.1) * 0.6 + math.sin(t * (97 + k * 29 + seed * 3) + k) * 0.4
    return (s(1) * amp, s(2) * amp)


def sys_line(ctx, s, t, at, x, y, size=20, color='sub', alpha=1.0, cps=60, prefix='› ', weight=400):
    """One line in the SYSTEM's voice: mono, typed."""
    if t < at:
        return 0
    n = min(len(s), int((t - at) * cps))
    ctx.text(prefix + s[:n], x, y, size=size, font='mono', color=color, alpha=alpha, weight=weight)
    return n


def keyword_sys(ctx, s, t, at, cx, cy, max_w=1200, max_size=96, color='text', dim_color='mute', alpha=1.0, key=0, weight=800, underline=True):
    """A keyword in the system's voice (mono caps): each character decodes from noise, the word lands with a punch."""
    age = t - at
    if age < 0 or alpha <= 0.003 or not s:
        return
    n = len(s)
    size = min(max_size, max_w / (n * 0.72)) * (1 + 0.06 * pulse(age, 9))
    cw, sp = ctx.cw(size), size * 0.12
    total = n * cw + (n - 1) * sp
    x = cx - total / 2
    for i in range(n):
        appear, settle = i * 0.018, i * 0.018 + 0.11
        if age >= appear and s[i] != ' ':
            ch = GLYPHS[int(rand(11, key, i, int(t * 40)) * len(GLYPHS))] if age < settle else s[i]
            ctx.text(ch, x, cy, size=size, weight=weight, font='mono', color=dim_color if age < settle else color, alpha=alpha)
        x += cw + sp
    if underline:
        w = total * ease_out(prog(age, 0, 0.3)) * 0.5
        ctx.line(cx - w, cy + size * 0.3, cx + w, cy + size * 0.3, color=dim_color, alpha=alpha * 0.9, width=2)


GLASS_FIG = {'cx': 1470, 'base': 1080, 'h': 1000}


def glass_figure(ctx, alpha, color='mute', dx=0.0, dy=0.0):
    """She is the first thing in the room at boot and the last to leave: the faceless bust as a flat two-step shape
    standing in the room behind the window's page (runs off the bottom of the frame)."""
    if alpha <= 0.003:
        return
    bust(ctx, 'f_bust', GLASS_FIG['cx'] + dx, GLASS_FIG['base'] + dy, GLASS_FIG['h'], variant=f'glass:{color}', alpha=alpha)


def drop_frames(t, fps, start=0.0):
    return start + math.floor((t - start) * fps + 1e-6) / fps


def replay(t, starts, length=1e9):
    last = None
    for s in starts:
        if t >= s and (last is None or s > last):
            last = s
    return -1 if last is None else min(length, t - last)


def pass_of(t, starts):
    return sum(1 for s in starts if t >= s)


def soft_beat(f):
    return clamp(f.get('beatPulse', 0) * 0.6 + f.get('barPulse', 0) * 0.4)


def key_band(ctx, env, t, i, y, max_size=110, max_w=1500):
    """Dark band + keyword in the system's voice, in screen space (boot)."""
    age = t - env.T(i)
    if age < 0:
        return
    ctx.grad_rect(0, y - 100, 1920, 160, [(0, 'panel', 0), (0.3, 'panel', 0.85 * clamp(age * 6)), (0.75, 'panel', 0.85 * clamp(age * 6)), (1, 'panel', 0)], steps=10)
    keyword_sys(ctx, env.text(i), t, env.T(i), 960, y + 20, max_w=max_w, max_size=max_size, key=i)
