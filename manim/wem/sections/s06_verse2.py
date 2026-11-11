"""Section 6 — VERSE 2 (bar 40, 1:14.2 -> bar 48, 1:29.0). State: warm (06_verse2.js, plates_verse2.js).
Four role-play requests, and the user never waits for an answer to finish. On every noun the film leaves the
interface for a plate; the user's next click on Send ends it.

    v2-ask1..3   the user clicks Send: the request flies up out of the composer, her answer begins under it
    v2-eggplant  she IS the eggplant (code characters, its own purple); cut open; its colour leaves, molecules drawn out
    v2-tomato    the same grammar: lycopene, vitamin C, vitamin E
    v2-cat       herself in characters; the cat ears; printed solid with her purr as tabby stripes
    v2-ask4      be god: on the kick the lights go down round the user's bubble
    v2-proof     a proof without its cream plate; a sun behind her; the cream plate registers on the keyword
"""
import math

from ..art import aspect
from ..components import R, burst, chat_layout, composer, cursor_at, draw_cursor, header, pointer, rays, room, spark, window_frame
from ..geom import SHAPE, in_poly, place
from ..plates import arrow, band, ground, inks, keyword
from ..util import TAU, clamp, ease_back, ease_in_out, ease_out, lerp, prog, pulse, rand

REQ = [('nounEggplant', 44, 43), ('nounTomato', 47, 46), ('nounTabby', 50, 49), (None, 53, 52)]
DATA_CHARS = '01{}[]<>=+*;:#&%$@'


def shots(env):
    T, B, Bt, P, text = env.T, env.B, env.Bt, env.P, env.text
    cards = env.script.get('cards_section6', [])
    req = lambda i: cards[i]['request'] if i < len(cards) else ''
    SEND = [B(40), Bt(167.5), Bt(175.5), Bt(183.5)]
    NOUN = [env.features.snap_half(env.cue(REQ[k][0], SEND[k] + 0.5)) for k in range(3)]
    DARK, END = Bt(184.5), B(48)
    W0 = chat_layout(side=0)
    TH = W0['thread']
    BTN = (W0['composer']['x'] + W0['composer']['w'] - 36, W0['composer']['y'] + W0['composer']['h'] / 2)

    # ------------------------------------------------------------------ the glimpses of the interface
    def glimpse_cam(k):
        def cam(t, f, u):
            p = prog(t, u['at'], u['until'])
            return {'zoom': 1.25 + 0.04 * p + 0.05 * k, 'x': 80 - 40 * k, 'y': 110 - 6 * p, 'rot': (0, -0.02, 0.016, 0)[k]}
        return cam

    def glimpse(k):
        def render(ctx, t, f, u):
            cut, (cue, line, kw) = SEND[k], REQ[k]
            dark = clamp((t - Bt(184)) * 30) if k == 3 else 0
            room(ctx, dim=0.5, t=t)
            window_frame(ctx, W0, glass=0.95)
            ctx.radial(960, 450, 560, 'meDim', 0.34)
            header(ctx, W0, title=env.script.get('title', ''), pres='online')
            y_prev, y_you, y_me = 210, 290, 400
            ctx.text(text(kw), TH['x'] + 46, y_prev, size=30, weight=700, font='serif', color='meHot', alpha=0.6)
            spark(ctx, TH['x'] + 15, y_prev - 12, 13, alpha=0.6)
            if t >= T(line):
                s = text(line)
                n = env.lyrics.typed(line, t)
                spark(ctx, TH['x'] + 15, y_me - 14, 13)
                ctx.text(s[:n], TH['x'] + 46, y_me, size=40, font='serif', color='me', alpha=1)
            composer(ctx, W0['composer'], placeholder=env.script.get('composer_placeholder', ''), t=t, send='busy')
            burst(ctx, BTN[0], BTN[1], 40, (t - cut) / 0.45, color='text')
            if dark > 0:
                with ctx.screen():
                    ctx.rect(0, 0, 1920, 640, fill=True, color='panel', alpha=0.9 * dark)
            # the request, thrown up out of the composer
            kk = prog(t, cut - 0.06, cut + 0.22)
            s = req(k)
            sz = 30
            bw = ctx.measure(s, size=sz) + 50
            xr = TH['x'] + TH['w']
            yb = y_you + (1 - ease_back(kk)) * 220
            if kk > 0:
                fill = 'text' if dark > 0.5 else 'raised'
                ctx.rrect(xr - bw, yb - 46, bw, 64, 30, fill=fill, stroke='text', width=2, alpha=clamp(kk * 4))
                ctx.text(s, xr - bw + 25, yb - 2, size=sz, color='bg' if dark > 0.5 else 'text', weight=500 if dark > 0.5 else 400, alpha=clamp(kk * 4))
            if dark > 0 and t >= T(line):
                ctx.text(text(line)[:env.lyrics.typed(line, t)], TH['x'] + 46, y_me, size=40, font='serif', color='me', alpha=dark)
            way = ([{'t': cut, 'x': BTN[0] + 3, 'y': BTN[1] + 4}, {'t': DARK, 'x': 1500, 'y': 420}] if k == 3 else
                   [{'t': cut, 'x': BTN[0] + 3, 'y': BTN[1] + 4}, {'t': cut + 0.6, 'x': BTN[0] + 40, 'y': BTN[1] + 30}])
            draw_cursor(ctx, way, t)
        return render

    # ------------------------------------------------------------------ the shared foot of the verse plates
    def foot(ctx, t, word, hit, lines, nxt):
        for i in lines:
            if T(i) <= t < (T(lines[lines.index(i) + 1]) if lines.index(i) + 1 < len(lines) else 1e9):
                band(ctx, text(i), env.lyrics.typed(i, t), x=70, y=82, size=40)
        keyword(ctx, word, t, x=640, y=604, max_w=1100, max_size=110, at=hit, step=0.02, color='me')
        if nxt:
            s, a, z = nxt
            n = int(clamp((t - Bt(a)) / max(1e-6, Bt(z) - Bt(a))) * len(s))
            if n > 0:
                ctx.text(s[:n], 1840, 600, size=28, color='text', align='right')
                if int(t * 4) % 2 == 0:
                    ctx.rect(1844, 574, 3, 32, fill=True, color='text')

    def glyph_fill(ctx, outline, t, color, cell=20, seed=1, alpha=1.0, shift=(0, 0)):
        xs, ys = [p[0] for p in outline], [p[1] for p in outline]
        y = min(ys) + cell / 2
        j = 0
        while y < max(ys):
            x = min(xs) + cell / 2
            i = 0
            while x < max(xs):
                if in_poly(outline, x, y):
                    ch = DATA_CHARS[int(rand(seed, i, j, int(t * 6)) * len(DATA_CHARS))]
                    ctx.text(ch, x + shift[0], y + shift[1] + 6, size=cell * 0.9, font='mono', weight=700, color=color, alpha=alpha, align='center')
                x += cell
                i += 1
            y += cell
            j += 1

    def molecule(ctx, x, y, r, label, formula, value, a):
        pts = [(x + math.cos(i / 6 * TAU) * r, y + math.sin(i / 6 * TAU) * r) for i in range(6)]
        ctx.poly(pts, close=True, color='text', width=3, alpha=a)
        for p in pts[::2]:
            ctx.line(p[0], p[1], p[0] + (p[0] - x) * 0.6, p[1] + (p[1] - y) * 0.6, color='text', width=3, alpha=a)
        ctx.text(label, x + r * 1.9, y - 6, size=26, weight=600, color='text', alpha=a)
        ctx.text(f'{formula}   {value}', x + r * 1.9, y + 24, size=18, font='mono', color='sub', alpha=a)

    def plate_fruit(kind, k, settle_cue, open_beat, hit_line, lines, nxt):
        spot = 'eggplant' if kind == 'eggplant' else 'tomato'
        rows = cards[k]['rows'] if k < len(cards) else []
        mols = [r for r in rows if r['label'] not in ('Water', 'Carbohydrate')][:3] if kind == 'eggplant' else \
            [r for r in rows if r['label'] in ('Lycopene', 'Vitamin C', 'Vitamin E')]

        def render(ctx, t, f, u):
            at, opn, hit = NOUN[k], Bt(open_beat), T(hit_line)
            ground(ctx, light=(600, 300, 380, 'raised', 1))
            C = (560, 320)
            rr = 230 if kind == 'eggplant' else 200
            outline = place(kind, cx=C[0], cy=C[1], r=rr, rot_=0.5 if kind == 'eggplant' else 0, sx=0.8 if kind == 'eggplant' else 1.15, sy=1)
            gone = ease_in_out(prog(t, hit, hit + 0.6))
            split = ease_out(prog(t, opn, opn + 0.2)) * 60
            settle = ease_out(prog(t, at, env.cue(settle_cue, at + 0.4)))
            halves = ((-split, -split * 0.3), (split, split * 0.3)) if kind == 'eggplant' else ((0, -split * 1.2), (0, 0))
            for hi, (dx, dy) in enumerate(halves):
                with ctx.at(dx, dy):
                    pts = [p for p in outline if (p[0] - C[0]) * (1 if kind == 'eggplant' else 0) + (p[1] - C[1]) * (0 if kind == 'eggplant' else 1) * (1 if hi == 0 else -1) <= (0 if hi == 0 else 1e9)] if split > 1 else outline
                    if split > 1:
                        if kind == 'eggplant':
                            pts = [p for p in outline if (p[0] - C[0] < 0) == (hi == 0)]
                        else:
                            pts = [p for p in outline if (p[1] - C[1] < -rr * 0.35) == (hi == 0)]
                    if len(pts) < 3:
                        continue
                    with ctx.at(8, 8):
                        ctx.poly(pts, close=True, fill=True, color='bg', alpha=1 - gone)
                    ctx.poly(pts, close=True, fill=True, color=f'{spot}.dark', alpha=(1 - gone) * settle)
                    glyph_fill(ctx, pts, t, f'{spot}.light', cell=22, seed=k * 2 + hi, alpha=(1 - gone) * (0.4 + 0.6 * settle))
                    ctx.poly(pts, close=True, color='text' if gone > 0 else f'{spot}.base', width=3 + 2 * gone)
            # her spark is the calyx
            cal = outline[0]
            spark(ctx, cal[0] + halves[0][0], cal[1] + halves[0][1] - 14, 54, rot=0.2)
            # on the keyword, what it holds is drawn out of it in cream, towards the user (the right)
            for i, r in enumerate(mols):
                e = ease_out(prog(t, hit + i * 0.12, hit + i * 0.12 + 0.5))
                if e <= 0:
                    continue
                x = lerp(C[0], 1080, e)
                y = 160 + i * 130
                molecule(ctx, x, y, 34, r['label'], r.get('formula', ''), r.get('value', ''), e)
            foot(ctx, t, text(hit_line), hit, lines, nxt)
        return render

    def plate_cat(ctx, t, f, u):
        at, ears, develop, hit = NOUN[2], env.cue('nounCat', NOUN[2] + 0.4), Bt(180), T(52)
        ground(ctx, light=(520, 300, 380, 'raised', 1))
        dev = ease_out(prog(t, develop, develop + 0.15))
        h = 560
        x0 = 520 - h * aspect('f_bust') / 2
        if dev < 1:
            name = 'cat_bust' if t >= ears else 'f_bust'
            pop = ease_back(prog(t, ears, ears + 0.2)) if t >= ears else 0
            ctx.image(name, x0, 80 - 10 * pop, h * aspect(name), h, variant='dots:me', alpha=1 - dev)
        if dev > 0:
            inks(ctx, 'cat_paws', x0, 80, h, offsets={'black': (8, 8)}, alpha=dev)
            # her purr: tabby stripes from her to the right edge
            given = ease_in_out(prog(t, hit, hit + 0.7))
            for i in range(14):
                x = 860 + i * 70 + given * 300
                if x > 1900:
                    continue
                w = 26 + 10 * math.sin(i * 1.3 + t * 8)
                ctx.rect(x, 140 + 40 * math.sin(i * 0.7), w, 300 - 60 * math.sin(i * 0.9), fill=True,
                         color='text' if given > 0.5 else ('me' if i % 2 else 'meDim'), alpha=dev * (1 - 0.6 * given * (i / 14)))
            rows = cards[2]['rows'] if len(cards) > 2 else []
            for i, r in enumerate(rows):
                ctx.text(f"{r['label']}: {r['value']}", 900, 500 + i * 26, size=18, font='mono', color='sub', alpha=dev)
        foot(ctx, t, text(52), hit, [50, 51], (req(3), 181, 183.1))

    def plate_proof(ctx, t, f, u):
        at, sun, slide, hit = DARK, env.cue('nounGod', DARK + 0.7), Bt(188), T(55)
        ground(ctx, light=None)
        h = 600
        w = h * aspect('f_bust')
        x0, y0 = 520 - w / 2, 40
        ctx.image('f_bust', x0 + 8, y0 + 8, w, h, variant='sil:bg', alpha=0.9)
        s = ease_out(prog(t, sun, sun + 0.2))
        if s > 0:
            face = (x0 + w * 0.48, y0 + h * 0.3)
            rays(ctx, face[0], face[1], 60, 520 * s, n=28, rot=t * 0.05, color='me', alpha=0.6 * s, width=10)
            ctx.circle(face[0], face[1], 110 * s, fill=True, color='meHot', alpha=s)
        ctx.image('f_bust', x0, y0, w, h, variant='ob')
        # the missing plate slides over from the user's message and registers on the keyword
        k = ease_in_out(prog(t, slide, hit))
        bub = (1560, 120)
        if t >= slide - 0.3:
            ctx.image('f_bust', lerp(bub[0], x0, k), lerp(bub[1], y0, k), w, h, variant='ink', alpha=0.25 + 0.75 * k)
        s4 = req(3)
        bw = ctx.measure(s4, size=34, weight=500) + 60
        ctx.rrect(1860 - bw, 60, bw, 70, 34, fill='text')
        ctx.text(s4, 1860 - bw + 30, 107, size=34, weight=500, color='bg')
        for i in (53, 54):
            nxt_t = T(i + 1)
            if T(i) <= t < nxt_t:
                band(ctx, text(i), env.lyrics.typed(i, t), x=1020, y=280, size=38)
        keyword(ctx, text(55), t, x=1300, y=604, max_w=1000, max_size=110, at=hit, step=0.02, color='me')
        if t >= T(56):
            band(ctx, text(56), env.lyrics.typed(56, t), x=1020, y=380, size=34)
        leave = Bt(191)
        p = ease_in_out(prog(t, leave, END))
        pointer(ctx, lerp(1500, 1700, p), lerp(420, 40, p), scale=1.5)

    return {
        'v2-ask1': {'render': glimpse(0), 'camera': glimpse_cam(0), 'palette': 'warm'},
        'v2-eggplant': {'render': plate_fruit('eggplant', 0, 'nounEggplantEnd', 164, 46, [44, 45], (req(1), 164.75, 166.75)), 'palette': 'warm'},
        'v2-ask2': {'render': glimpse(1), 'camera': glimpse_cam(1), 'palette': 'warm'},
        'v2-tomato': {'render': plate_fruit('tomato', 1, 'nounTomatoEnd', 172, 49, [47, 48], (req(2), 172.75, 174.9)), 'palette': 'warm'},
        'v2-ask3': {'render': glimpse(2), 'camera': glimpse_cam(2), 'palette': 'warm'},
        'v2-cat': {'render': plate_cat, 'palette': 'warm'},
        'v2-ask4': {'render': glimpse(3), 'camera': glimpse_cam(3), 'palette': 'warm'},
        'v2-proof': {'render': plate_proof, 'palette': 'warm'},
    }
