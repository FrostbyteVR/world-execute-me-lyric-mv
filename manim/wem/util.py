"""Small math / easing helpers and the seeded, stateless randomness of src/engine/util.js and prng.js.

Everything is a pure function of its arguments, so any frame can be rendered on its own (as in the browser
renderer, a frame never depends on the frames rendered before it)."""
import math

TAU = math.pi * 2


def clamp(x, a=0.0, b=1.0):
    if x != x:  # NaN
        return a
    return a if x < a else b if x > b else x


def lerp(a, b, k):
    return a + (b - a) * k


def prog(t, a, b):
    """0..1 progress of t inside [a, b], clamped."""
    if b == a:
        return 1.0 if t >= b else 0.0
    return clamp((t - a) / (b - a))


def smooth(k):
    return k * k * (3 - 2 * k)


def ease_out(k):
    return 1 - (1 - k) ** 3


def ease_in(k):
    return k * k * k


def ease_in_out(k):
    return 4 * k * k * k if k < 0.5 else 1 - (-2 * k + 2) ** 3 / 2


def ease_back(k):
    c = 1.70158
    return 1 + (c + 1) * (k - 1) ** 3 + c * (k - 1) ** 2


def pulse(since, decay):
    """Exponential decay envelope: 1 at since = 0, 0 before the event."""
    return 0.0 if since < 0 else math.exp(-decay * since)


def window01(t, a, b, fin=0.2, fout=0.2):
    return min(prog(t, a, a + fin), 1 - prog(t, b - fout, b))


def timecode(t):
    a = abs(t)
    m = int(a // 60)
    s = a - m * 60
    return f"{'-' if t < 0 else ''}{m:02d}:{s:06.3f}"


# ---- seeded randomness (same hash as src/engine/prng.js) -------------------------------------------------
_M32 = 0xFFFFFFFF
_SEED = 1


def set_seed(s):
    global _SEED
    _SEED = int(s) & _M32


def _imul(a, b):
    return ((a & _M32) * (b & _M32)) & _M32


def _mix(h):
    h &= _M32
    h ^= h >> 16
    h = _imul(h, 0x7FEB352D)
    h ^= h >> 15
    h = _imul(h, 0x846CA68B)
    h ^= h >> 16
    return h & _M32


def hash_u32(*keys):
    h = (_SEED ^ 0x9E3779B9) & _M32
    for k in keys:
        h = _mix((h + _imul(math.floor(k) + 0x7F4A7C15, 0x85EBCA6B)) & _M32)
    return h


def rand(*keys):
    """Uniform float in [0, 1) from integer keys."""
    return hash_u32(*keys) / 4294967296.0


def rand_range(a, b, *keys):
    return a + (b - a) * rand(*keys)


def noise1(x, seed=0):
    i = math.floor(x)
    f = x - i
    u = f * f * (3 - 2 * f)
    return rand(seed, i) * (1 - u) + rand(seed, i + 1) * u
