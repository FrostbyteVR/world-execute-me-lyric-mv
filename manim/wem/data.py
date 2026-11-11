"""Everything the film is timed and coloured by, read from the SAME files the browser renderer reads:

    config.json                 palettes, timing offsets, typing speed, safety (pre-roll, flash range)
    data/audio_features.json    beat grid, onsets, per-frame levels
    data/lyrics.json            line times + your own lyric text (made by `node tools/fill_lyrics.mjs`; never committed)
    data/lyric_timing.json      line times without text (used, with placeholder text, when lyrics.json is missing)
    docs/v4/chat_script.json    the written conversation
    docs/v4/errors.json         the texts of the error dialogs
    src/scenes/cues.js          the word / drum cues that do not sit on the beat grid
    STORYBOARD.md               the shot list (id, cut time, lines, colour state, transition), generated from the JS code

Nothing here is copied by hand: if the maintainer moves a cue or a cut in the JS project, the Manim port follows.
"""
import json
import math
import os
import re
import sys

from .util import clamp, pulse, set_seed

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def path(p):
    return os.path.join(ROOT, p)


def read_json(p, default=None):
    try:
        with open(path(p), encoding='utf-8') as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return default


def warn(msg):
    print(f'[wem] {msg}', file=sys.stderr)


# ------------------------------------------------------------------------------------------------ palettes
ROLES = ['bg', 'panel', 'raised', 'line', 'text', 'sub', 'mute', 'me', 'meHot', 'meDim', 'err', 'errDim', 'bloom']
ALIAS = {'fg': 'text', 'mid': 'sub', 'dim': 'mute', 'faint': 'line', 'accent': 'text', 'alt': 'me'}


def parse_hex(h):
    m = re.fullmatch(r'#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6})', h or '')
    if not m:
        return None
    s = m.group(1)
    if len(s) == 3:
        s = ''.join(c * 2 for c in s)
    n = int(s, 16)
    return ((n >> 16) & 255, (n >> 8) & 255, n & 255)


class Palette(dict):
    """role -> (r, g, b) 0..255, plus .glow / .sat scalars and .name."""

    def __init__(self, name, roles, glow=1.0, sat=1.0):
        super().__init__(roles)
        self.name, self.glow, self.sat = name, glow, sat
        for old, role in ALIAS.items():
            self[old] = self[role]


def build_palettes(defs):
    out = {}
    for name, d in defs.items():
        if name.startswith('_'):
            continue
        roles = {r: parse_hex(d.get(r, d['text'])) for r in ROLES}
        out[name] = Palette(name, roles, d.get('glow', 1.0), d.get('sat', 1.0))
    return out


def mix_pal(a, b, k):
    if k <= 0 or a is b:
        return a
    if k >= 1:
        return b
    roles = {r: tuple(a[r][i] + (b[r][i] - a[r][i]) * k for i in range(3)) for r in ROLES}
    return Palette(f'{a.name}>{b.name}', roles, a.glow + (b.glow - a.glow) * k, a.sat + (b.sat - a.sat) * k)


def pal_track(keys):
    """Keyframes [(time, name, fade?), ...] -> function(t) returning a palette spec (src/engine/palette.js palTrack)."""
    def f(t):
        i = 0
        while i + 1 < len(keys) and t >= keys[i + 1][0] - (keys[i + 1][2] if len(keys[i + 1]) > 2 else 0):
            i += 1
        cur = keys[i]
        fade = cur[2] if len(cur) > 2 else 0
        if i > 0 and fade and t < cur[0]:
            return (keys[i - 1][1], cur[1], (t - (cur[0] - fade)) / fade)
        return cur[1]
    return f


# ------------------------------------------------------------------------------------------------ audio features
class Features:
    """Beat grid and audio levels; every lookup is a pure function of t (src/engine/features.js)."""

    def __init__(self, d, cfg):
        self.d = d
        self.fps = d['meta']['fps']
        self.n = d['meta']['frames']
        self.duration = d['meta']['duration']
        self.period = d['grid']['period']
        self.t0 = d['grid']['t0']
        self.down = d['downbeatPhase']
        self.on_t = d['onsets']['t']
        self.on_s = d['onsets']['s']
        self.r = cfg['reactive']

    def series(self, name, t):
        a = self.d[name]
        x = clamp(t * self.fps, 0, self.n - 1)
        i = int(x)
        k = x - i
        return a[i] * (1 - k) + a[min(i + 1, self.n - 1)] * k

    def env(self, name, t, release=8, window=0.5):
        a = self.d[name]
        end = int(clamp(t * self.fps, 0, self.n - 1))
        start = max(0, end - math.ceil(window * self.fps))
        m = 0.0
        for i in range(start, end + 1):
            m = max(m, a[i] * math.exp(-release * (t - i / self.fps)))
        return max(m, self.series(name, t))

    def beat_time(self, i):
        return self.t0 + i * self.period

    def beat_index(self, t):
        return math.floor((t - self.t0) / self.period + 1e-6)

    def bar_time(self, n):
        return self.beat_time(self.down + 4 * n)

    def snap_half(self, t):
        return self.t0 + round((t - self.t0) / (self.period / 2)) * (self.period / 2)

    def snap_to_beat(self, t, tol=0.09):
        b = self.beat_time(round((t - self.t0) / self.period))
        return b if abs(b - t) <= tol else t

    def onset_index(self, t):
        lo, hi, r = 0, len(self.on_t) - 1, -1
        while lo <= hi:
            m = (lo + hi) >> 1
            if self.on_t[m] <= t:
                r, lo = m, m + 1
            else:
                hi = m - 1
        return r

    def sample(self, time):
        """Everything a shot usually needs at time t (as features.sample() in the JS engine)."""
        f = {'t': time}
        if time < 0:
            f.update(rms=0, low=0, mid=0, high=0, lowEnv=0, beat=self.beat_index(time), beatPhase=0, sinceBeat=0,
                     beatInBar=0, bar=-1, sinceBar=0, beatPulse=0, barPulse=0, onsetPulse=0, onsetStrength=0)
            return f
        t = time
        beat = self.beat_index(t)
        since_beat = t - self.beat_time(beat)
        rel = beat - self.down
        bar = math.floor(rel / 4)
        since_bar = t - self.bar_time(bar)
        started = t >= self.t0
        oi = self.onset_index(t)
        since_on = t - self.on_t[oi] if oi >= 0 else 1e9
        on_s = self.on_s[oi] if oi >= 0 else 0
        f.update(
            rms=self.series('rms', t), low=self.series('low', t), mid=self.series('mid', t), high=self.series('high', t),
            lowEnv=self.env('low', t, 7), beat=beat, beatPhase=since_beat / self.period, sinceBeat=since_beat,
            beatInBar=rel % 4, bar=bar, sinceBar=since_bar,
            beatPulse=pulse(since_beat, self.r['beatDecay']) if started else 0,
            barPulse=pulse(since_bar, self.r['beatDecay'] * 0.6) if started else 0,
            onsetStrength=on_s, onsetPulse=on_s * pulse(since_on, self.r['onsetDecay']),
        )
        return f


# ------------------------------------------------------------------------------------------------ lyrics
def _placeholder(line):
    """No lyric text in the repository: a line of dots with the line's word / letter counts, so layouts still work."""
    words, letters = max(1, line.get('words', 1)), max(1, line.get('letters', 4))
    base, extra = divmod(letters, words)
    return ' '.join('·' * (base + (1 if i < extra else 0)) for i in range(words))


class Lyrics:
    def __init__(self, cfg, features):
        data = read_json(cfg['paths']['lyrics'])
        self.placeholder = data is None
        if data is None:
            data = read_json('data/lyric_timing.json')
            for ln in data['lines']:
                ln['text'] = _placeholder(ln)
            warn('data/lyrics.json not found: lyric lines are drawn as dots. Put your lyric file into 音頻&歌詞/ '
                 'and run `node tools/fill_lyrics.mjs` (see the README).')
        self.lines = data['lines']
        self.sections = data.get('sections', [])
        self.typing = cfg['typing']
        self.offset = cfg['timing'].get('lyricOffset', 0) or 0
        tol = cfg['timing'].get('keywordSnap', 0) or 0
        self.starts = [features.snap_to_beat(l['start'], tol) if l.get('emphasis') and tol > 0 else l['start']
                       for l in self.lines]

    def text(self, i):
        return self.lines[i]['text']

    def start(self, i):
        return self.starts[i] + self.offset

    def end(self, i):
        return self.lines[i]['end'] + self.offset

    def index_at(self, t):
        r = -1
        for i in range(len(self.lines)):
            if self.start(i) <= t:
                r = i
            else:
                break
        return r

    def typed(self, i, t):
        """How many characters of line i are typed at time t."""
        n = len(self.lines[i]['text'])
        dur = min(n / self.typing['charsPerSec'], (self.end(i) - self.start(i)) * self.typing['maxFraction'])
        k = clamp((t - self.start(i)) / max(dur, 1e-3))
        return int(k * n + 1e-6)


# ------------------------------------------------------------------------------------------------ cues
def load_cues():
    """src/scenes/cues.js -> {name: seconds}. The JS file stays the one place a cue is corrected by ear."""
    out = {}
    try:
        src = open(path('src/scenes/cues.js'), encoding='utf-8').read()
    except OSError:
        return out
    for m in re.finditer(r"(?<![\w'])([A-Za-z][A-Za-z0-9_]*):\s*\[\s*(-?[0-9.]+)\s*,\s*'", src):
        out[m.group(1)] = float(m.group(2))
    return out


# ------------------------------------------------------------------------------------------------ shot list
_ROW = re.compile(r'^\|\s*(−?\d+:\d+\.\d+)-(\d+:\d+\.\d+)\s*\|[^|]*\|\s*`([^`]+)`\s*\|\s*([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|')


def _secs(s):
    neg = s.startswith('−') or s.startswith('-')
    m, sec = s.lstrip('−-').split(':')
    v = int(m) * 60 + float(sec)
    return -v if neg else v


def _transition(s):
    """'push, 0.5 拍' | 'cut, flash 0.9' | 'zoom, 2 拍 start' -> {'type', 'beats', 'align', 'flash'}"""
    s = s.strip()
    out = {'type': s.split(',')[0].strip() or 'cut', 'beats': 0.0, 'align': 'end', 'flash': 0.0}
    m = re.search(r'([0-9.]+)\s*拍', s)
    if m:
        out['beats'] = float(m.group(1))
    m = re.search(r'flash\s*([0-9.]+)', s)
    if m:
        out['flash'] = float(m.group(1))
    if re.search(r'\bstart\b', s):
        out['align'] = 'start'
    elif re.search(r'\bcenter\b', s):
        out['align'] = 'center'
    if out['type'] not in ('cut', 'push', 'zoom', 'scan', 'fade', 'glitch', 'slices'):
        out['type'] = 'cut'
    return out


def load_shot_list(features):
    """[{id, at, until, lines, state, layout, moment, enter}] from STORYBOARD.md, cut times snapped to the half-beat grid."""
    shots = []
    for raw in open(path('STORYBOARD.md'), encoding='utf-8'):
        m = _ROW.match(raw)
        if not m:
            continue
        a, b, sid, lines, moment, layout, state, enter = m.groups()
        at, until = _secs(a), _secs(b)
        for k in ('at', 'until'):
            v = at if k == 'at' else until
            s = features.snap_half(v)
            if v >= 0 and abs(s - v) < 0.012:
                v = s
            if k == 'at':
                at = v
            else:
                until = v
        ln = None
        mm = re.match(r'\s*(\d+)(?:-(\d+))?', lines)
        if mm:  # the storyboard counts lines from 1, the code from 0
            ln = (int(mm.group(1)) - 1, int(mm.group(2) or mm.group(1)) - 1)
        shots.append({'id': sid, 'at': at, 'until': until, 'lines': ln, 'state': state.strip(),
                      'layout': layout.strip(), 'moment': moment.strip(), 'enter': _transition(enter)})
    shots.sort(key=lambda s: s['at'])
    return shots


# ------------------------------------------------------------------------------------------------ the bundle
class Env:
    """What every section file receives (the `env` of src/scenes)."""

    def __init__(self):
        self.cfg = read_json('config.json')
        set_seed(self.cfg['seed'])
        self.features = Features(read_json(self.cfg['paths']['features']), self.cfg)
        self.lyrics = Lyrics(self.cfg, self.features)
        self.script = read_json(self.cfg['paths']['script'], {})
        self.errors = read_json(self.cfg['paths']['errors'], {})
        self.palettes = build_palettes(self.cfg['palettes'])
        self.spot = {k: {r: parse_hex(v) for r, v in d.items()} for k, d in self.cfg.get('spot', {}).items() if not k.startswith('_')}
        self.cues = load_cues()
        self.shots = load_shot_list(self.features)
        self.preroll = self.cfg['safety'].get('preroll', 0) or 0
        self.duration = self.features.duration
        f = self.features
        self.P = f.period

    # time helpers of src/scenes/kit.js cues()
    def T(self, i):
        return self.lyrics.start(i)

    def H(self, i):
        return self.features.snap_half(self.lyrics.start(i))

    def B(self, n):
        return self.features.bar_time(n)

    def Bt(self, b):
        return self.features.beat_time(b)

    def text(self, i):
        return self.lyrics.text(i)

    def cue(self, name, default=None):
        return self.cues.get(name, default)

    def shot(self, sid):
        for s in self.shots:
            if s['id'] == sid:
                return s
        return None
