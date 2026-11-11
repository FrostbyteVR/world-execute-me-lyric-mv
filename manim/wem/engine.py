"""The film as a pure function of song time: frame(t) -> the mobjects of that frame (src/engine/engine.js).

    shots       ids, cut times, lines, colour states and transitions from STORYBOARD.md (data.load_shot_list);
                the drawing of each shot from wem/sections/*.py (a shot with no drawing yet falls back to its
                lyric lines as the AI's messages, as src/scenes/kit.js fallbackShot does)
    layers      at most two shots are live: A (outgoing) and B (incoming) while a transition runs
    overlay     the warning toast of the opening seconds and the credit note after the power-down
    finish      flash, vignette (the WebGL post of the browser film — bloom, grain, scanlines — is not ported:
                the Cairo renderer of Manim has no pixel shaders; glows and rays are drawn as shapes instead)
"""
import importlib
import math

import numpy as np
from manim import Group, ImageMobject

from .ctx import Ctx, VW, VH
from .data import Env
from .util import clamp, ease_in_out, ease_out, pulse, rand, prog

SECTIONS = ['s01_boot', 's02_title', 's03_verse1', 's04_pre1', 's05_chorus', 's06_verse2', 's07_pre2',
            's08_chorus2', 's09_alone', 's10_error', 's11_execution', 's11_count', 's12_chorusx', 's12_outro',
            's13_shutdown']


def _state_spec(state):
    """'off > on' -> ('off', 'on'); 'warm' -> 'warm'; 'errWarm > ash / ash > dead' -> first part."""
    s = state.split('/')[0].strip()
    parts = [p.strip() for p in s.split('>')]
    return parts if len(parts) > 1 else parts[0]


class Shot:
    def __init__(self, row, spec, P):
        self.id = row['id']
        self.at, self.until = row['at'], row['until']
        self.lines = row['lines']
        self.enter = dict(row['enter'])
        self.enter['dur'] = self.enter['beats'] * P
        self.state = row['state']
        self.spec = spec or {}
        self.start = self.end = None

    def palette(self, t, u):
        p = self.spec.get('palette')
        if callable(p):
            return p(t, u)
        if p is not None:
            return p
        st = _state_spec(self.state)
        if isinstance(st, list):
            return (st[0], st[1], ease_in_out(u['k']))
        return st


class Film:
    def __init__(self, env=None):
        self.env = env or Env()
        e = self.env
        specs = {}
        for name in SECTIONS:
            try:
                mod = importlib.import_module(f'wem.sections.{name}')
                specs.update(mod.shots(e))
            except ModuleNotFoundError as err:
                if err.name != f'wem.sections.{name}':
                    raise
        from .sections.fallback import fallback_spec
        self.shots = []
        for row in e.shots:
            spec = specs.get(row['id']) or fallback_spec(e, row)
            self.shots.append(Shot(row, spec, e.P))
        self.missing = [r['id'] for r in e.shots if r['id'] not in specs]
        self._sequence(e.duration + 1)
        self.ctx = Ctx(e)
        self.t_off = e.B(112)
        self._vignette = None

    def _sequence(self, end_time):
        """Overlaps around each cut from the transitions, clamped so at most two shots are ever live (shot.js)."""
        sh = self.shots

        def span(en):
            d, al = en.get('dur', 0), en.get('align', 'end')
            return (0, d) if al == 'start' else (d / 2, d / 2) if al == 'center' else (d, 0)
        over = []
        for i, s in enumerate(sh):
            want = span(s.enter) if i else (0, 0)
            room = s.at - sh[i - 1].at - over[i - 1][1] - 1e-6 if i else 0
            nxt = sh[i + 1].at if i + 1 < len(sh) else end_time
            over.append((max(0, min(want[0], room)), min(want[1], nxt - s.at)))
        for i, s in enumerate(sh):
            nxt = sh[i + 1] if i + 1 < len(sh) else None
            s.start = s.at - over[i][0]
            s.end = nxt.at + over[i + 1][1] if nxt else end_time

    # ---- one frame ----------------------------------------------------------------------------------------
    def _draw(self, shot, t, f, fx, M=None, alpha=1.0):
        ctx = self.ctx
        items = ctx.begin(t, f, fx)
        if M is not None:
            ctx.M = M
        ctx.base_M = ctx.M.copy()
        ctx.alpha = alpha
        u = {'at': shot.at, 'until': shot.until, 'dur': shot.until - shot.at, 'since': t - shot.at,
             'k': clamp((t - shot.at) / max(1e-6, shot.until - shot.at))}
        ctx.set_pal(shot.palette(t, u))
        state = ctx.pal
        ctx.clear()
        en = shot.enter
        if en.get('flash'):
            ctx.flash(en['flash'] * pulse(t - shot.at, 8))
        cam = shot.spec.get('camera')
        if cam:
            ctx.camera(**cam(t, f, u))
        try:
            shot.spec['render'](ctx, t, f, u)
        except Exception as err:  # one broken shot must not take the film down
            if not getattr(shot, '_reported', False):
                shot._reported = True
                print(f'[wem] shot {shot.id} failed at {t:.2f}: {err!r}')
                import traceback
                traceback.print_exc()
            del items[:]
            ctx.M = np.eye(3)
            ctx.clear()
            ctx.text(f'shot "{shot.id}" failed: {err}', 60, VH / 2, size=22, font='mono', color='err')
        return list(items), state

    @staticmethod
    def _affine(tx=0.0, ty=0.0, s=1.0, cx=VW / 2, cy=VH / 2):
        return np.array([[s, 0, cx - s * cx + tx], [0, s, cy - s * cy + ty], [0, 0, 1.0]])

    def frame(self, t):
        e, ctx = self.env, self.ctx
        ctx.reset_frame()
        tv = t - e.cfg['timing'].get('offset', 0)
        f = e.features.sample(tv)
        fx = {'flash': 0.0, 'flashColor': None}
        live = [s for s in self.shots if s.start <= tv < s.end]
        out = []
        if not live:
            ctx.begin(tv, f, fx)
            ctx.set_pal('dead')
            ctx.clear()
            return list(ctx.items)
        A = live[-2] if len(live) > 1 else live[0]
        B = live[-1] if len(live) > 1 else None
        if B is None:
            items, pal = self._draw(A, tv, f, fx)
            out += items
        else:
            k = clamp((tv - B.start) / max(1e-6, A.end - B.start))
            typ = B.enter.get('type', 'cut')
            ke = ease_in_out(k)
            if typ == 'push':
                MA, aA = self._affine(tx=-ke * VW), 1.0
                MB, aB = self._affine(tx=(1 - ke) * VW), 1.0
            elif typ == 'zoom':
                MA, aA = self._affine(s=1 + 0.5 * ke), 1 - ke
                MB, aB = self._affine(s=0.82 + 0.18 * ke), ke
            elif typ in ('glitch', 'slices'):
                j = (rand(91, int(tv * 60)) - 0.5) * 80 * math.sin(math.pi * k)
                MA, aA = self._affine(tx=j), 1.0
                MB, aB = self._affine(tx=-j), 1.0 if rand(92, int(tv * 30)) < k else k * 0.6
            else:  # fade, scan, cut with a lead-in
                MA, aA = None, 1.0
                MB, aB = None, ke
            ia, pal = self._draw(A, tv, f, fx, MA, aA)
            ib, palB = self._draw(B, tv, f, fx, MB, aB)
            out += ia + ib
            if typ == 'scan':
                ctx.begin(tv, f, fx)
                ctx.pal = palB
                y = ke * VH
                ctx.rect(-10, y - 3, VW + 20, 6, fill=True, color='text', alpha=0.7 * math.sin(math.pi * k))
                ctx.rect(-10, y - 30, VW + 20, 30, fill=True, color='text', alpha=0.08 * math.sin(math.pi * k))
                out += list(ctx.items)
            elif typ in ('glitch', 'slices'):
                from .components import tear
                ctx.begin(tv, f, fx)
                ctx.pal = palB
                tear(ctx, f, tv, strength=math.sin(math.pi * k), seed=7)
                out += list(ctx.items)
            pal = palB if k > 0.5 else pal
        # overlay: the warning toast, the credits
        ctx.begin(tv, f, fx)
        ctx.pal = pal
        self._overlay(ctx, tv)
        fl = min(fx['flash'], e.cfg['safety']['maxFlash'])
        if fl > 0.01:
            ctx.rect(-20, -20, VW + 40, VH + 40, fill=True, color=fx.get('flashColor') or pal['bloom'], alpha=fl * 0.75)
        out += list(ctx.items)
        out.append(self.vignette())
        return out

    def _overlay(self, ctx, t):
        from .components import toast
        e = self.env
        w_end = e.cfg['safety']['warningSeconds']
        if 0.9 < t < w_end:
            toast(ctx, {'x': VW / 2 - 260, 'y': 14, 'w': 520, 'h': 50}, 'This video contains flashing images', tone='info',
                  k=prog(t, 0.9, 1.3), out=ease_out(prog(t, w_end - 0.5, w_end)))
        a = prog(t, self.t_off + 1.6, self.t_off + 2.4) * (1 - prog(t, e.duration - 0.6, e.duration - 0.1))
        if a > 0:
            note = [('Unofficial fan-made video.  Not affiliated with, or endorsed by, Anthropic or Mili.', '#b8b6ae'),
                    ('Claude is a trademark of Anthropic.  Music: "world.execute(me);" by Mili.', '#7d7b73'),
                    ('Character silhouettes supplied by the maker of this video.  Interface drawn in code.', '#7d7b73')]
            for i, (s, col) in enumerate(note):
                ctx.text(s, VW / 2, 270 + i * 40, size=22, color=col, alpha=a, align='center', weight=500 if i == 0 else 400)

    def vignette(self):
        if self._vignette is None:
            w, h = 480, 160
            yy, xx = np.mgrid[0:h, 0:w]
            dx, dy = (xx / w - 0.5) * 2, (yy / h - 0.5) * 2
            r = np.sqrt((dx * 0.82) ** 2 + (dy * 0.95) ** 2)
            a = np.clip((r - 0.55) / 0.75, 0, 1) ** 1.6 * 255 * self.env.cfg['post']['vignette'] * 1.6
            arr = np.zeros((h, w, 4), dtype=np.uint8)
            arr[..., 3] = np.clip(a, 0, 255).astype(np.uint8)
            m = ImageMobject(arr)
            m.stretch_to_fit_width(VW / 100)
            m.stretch_to_fit_height(VH / 100)
            m.move_to([0, 0, 0])
            self._vignette = m
        return self._vignette

    # ---- helpers for tools ---------------------------------------------------------------------------------
    @property
    def start_time(self):
        return -self.env.preroll

    @property
    def end_time(self):
        return self.env.duration


def frame_group(film, t, group=None):
    g = group or Group()
    g.submobjects = film.frame(t)
    return g
