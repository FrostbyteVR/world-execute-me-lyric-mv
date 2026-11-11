"""Wireframe geometry, outlines and type helpers (src/engine/geom.js, shapes.js, type.js)."""
import math

from .util import TAU, clamp, ease_out, lerp, prog, rand

PHI = (1 + 5 ** 0.5) / 2
N = 180


def _norm(v):
    l = math.sqrt(sum(c * c for c in v)) or 1
    return [c / l for c in v]


def rot(p, rx, ry, rz=0.0):
    x, y, z = p
    c, s = math.cos(rx), math.sin(rx)
    y, z = y * c - z * s, y * s + z * c
    c, s = math.cos(ry), math.sin(ry)
    x, z = x * c + z * s, -x * s + z * c
    if rz:
        c, s = math.cos(rz), math.sin(rz)
        x, y = x * c - y * s, x * s + y * c
    return [x, y, z]


def project(p, cam):
    d = cam.get('dist', 4)
    k = d / (d + p[2])
    return [cam['cx'] + p[0] * k * cam['scale'], cam['cy'] + p[1] * k * cam['scale'], k]


def _mesh(raw):
    verts = [_norm(v) for v in raw]
    dist = lambda a, b: math.dist(a, b)
    mn = min(dist(verts[i], verts[j]) for i in range(len(verts)) for j in range(i + 1, len(verts)))
    edges = [(i, j) for i in range(len(verts)) for j in range(i + 1, len(verts)) if dist(verts[i], verts[j]) < mn * 1.01]
    return {'verts': verts, 'edges': edges, 'segs': [(verts[i], verts[j]) for i, j in edges]}


def _signs(v):
    out = [[]]
    for c in v:
        out = [o + [0] for o in out] if c == 0 else [o + [s] for o in out for s in (c, -c)]
    return out


def _cyc(v):
    return [v, [v[2], v[0], v[1]], [v[1], v[2], v[0]]]


MESH = {
    'cube': _mesh(_signs([1, 1, 1])),
    'octa': _mesh([s for v in _cyc([1, 0, 0]) for s in _signs(v)]),
    'icosa': _mesh([s for v in _cyc([0, 1, PHI]) for s in _signs(v)]),
}


def draw_segs(ctx, segs, cam, r=(0, 0, 0), color='text', alpha=1.0, width=2.2, grow=None):
    if alpha <= 0.003:
        return
    d = cam.get('dist', 4)
    k_far, k_near = d / (d + 1), d / (d - 1)
    for i, (a, b) in enumerate(segs):
        a, b = rot(a, *r), rot(b, *r)
        g = grow(i) if grow else 1
        if g <= 0:
            continue
        if g < 1:
            b = [lerp(a[c], b[c], g) for c in range(3)]
        pa, pb = project(a, cam), project(b, cam)
        depth = 0.3 + 0.7 * clamp(((pa[2] + pb[2]) / 2 - k_far) / (k_near - k_far))
        ctx.line(pa[0], pa[1], pb[0], pb[1], color=color, alpha=alpha * depth, width=width)


def sphere_glyphs(ctx, cx, cy, r, t, spin=0.6, n=140, size=16, colors=('meDim', 'me', 'meHot'), alpha=1.0, chars='.:o0#', seed=5):
    """A turning sphere of characters (the ASCII world of the browser film, reduced)."""
    for i in range(n):
        u, v = rand(seed, i, 1), rand(seed, i, 2)
        th, ph = TAU * u, math.acos(2 * v - 1)
        p = [math.sin(ph) * math.cos(th), math.cos(ph), math.sin(ph) * math.sin(th)]
        q = rot(p, 0.35, spin * t)
        if q[2] > 0.25:
            continue
        k = 4 / (4 + q[2])
        depth = clamp((0.25 - q[2]) / 1.25)
        ch = chars[min(len(chars) - 1, int(depth * len(chars)))]
        ctx.text(ch, cx + q[0] * r * k, cy + q[1] * r * k, size=size * (0.7 + 0.5 * depth), font='mono',
                 color=colors[min(2, int(depth * 3))], alpha=alpha * (0.4 + 0.6 * depth), align='center')


# ---- outlines ---------------------------------------------------------------------------------------------
def resample(verts, n=N):
    m = len(verts)
    seg = [math.dist(verts[i], verts[(i + 1) % m]) for i in range(m)]
    total = sum(seg)
    out, i, acc = [], 0, 0.0
    for k in range(n):
        d = k / n * total
        while acc + seg[i] < d:
            acc += seg[i]
            i += 1
        u = (d - acc) / (seg[i] or 1)
        a, b = verts[i], verts[(i + 1) % m]
        out.append((lerp(a[0], b[0], u), lerp(a[1], b[1], u)))
    return out


def _spline(ctrl, n=N):
    dense, m = [], len(ctrl)
    for i in range(m):
        p0, p1, p2, p3 = ctrl[(i - 1) % m], ctrl[i], ctrl[(i + 1) % m], ctrl[(i + 2) % m]
        for s in range(12):
            t = s / 12
            t2, t3 = t * t, t * t * t
            dense.append(tuple(0.5 * (2 * p1[c] + (-p0[c] + p2[c]) * t + (2 * p0[c] - 5 * p1[c] + 4 * p2[c] - p3[c]) * t2 +
                                      (-p0[c] + 3 * p1[c] - 3 * p2[c] + p3[c]) * t3) for c in (0, 1)))
    return resample(dense, n)


def _param(fn, n=N):
    return [fn(i / n) for i in range(n)]


def _heart(u):
    a = u * TAU
    return (16 * math.sin(a) ** 3 / 17, -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a)) / 17 - 0.12)


def _tomato(u):
    a = u * TAU
    dip = math.exp(-(min(u, 1 - u) * 9) ** 2)
    return (math.sin(a), -math.cos(a) * 0.86 + dip * 0.14)


SHAPE = {
    'circle': _param(lambda u: (math.sin(u * TAU), -math.cos(u * TAU))),
    'heart': _param(_heart),
    'eggplant': _spline([(0.02, -0.8), (0.26, -0.6), (0.46, -0.12), (0.58, 0.36), (0.42, 0.8), (0.0, 0.96), (-0.42, 0.8),
                         (-0.58, 0.36), (-0.44, -0.12), (-0.22, -0.6)]),
    'tomato': _param(_tomato),
    'cat': _spline([(0, -0.5), (0.3, -0.6), (0.66, -1.0), (0.84, -0.4), (0.96, 0.1), (0.62, 0.62), (0, 0.82), (-0.62, 0.62),
                    (-0.96, 0.1), (-0.84, -0.4), (-0.66, -1.0), (-0.3, -0.6)]),
}


def hull_outline(points, n=N):
    p = sorted(points, key=lambda q: (q[0], q[1]))
    cross = lambda o, a, b: (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    def half(lst):
        h = []
        for q in lst:
            while len(h) >= 2 and cross(h[-2], h[-1], q) <= 0:
                h.pop()
            h.append(q)
        h.pop()
        return h
    hull = half(p) + half(p[::-1])
    top = min(range(len(hull)), key=lambda i: hull[i][1])
    return resample(hull[top:] + hull[:top], n)


def place(shape, cx=0.0, cy=0.0, r=1.0, rot_=0.0, sx=1.0, sy=1.0):
    pts = SHAPE[shape] if isinstance(shape, str) else shape
    c, s = math.cos(rot_), math.sin(rot_)
    return [(cx + (x * sx * c - y * sy * s) * r, cy + (x * sx * s + y * sy * c) * r) for x, y in pts]


def morph(a, b, k):
    if k <= 0:
        return a
    if k >= 1:
        return b
    return [(lerp(p[0], q[0], k), lerp(p[1], q[1], k)) for p, q in zip(a, b)]


def trace(pts, k):
    if k >= 1:
        return pts
    x = max(0.0, k) * len(pts)
    n = int(x)
    out = list(pts[:n + 1])
    if n + 1 < len(pts) and out:
        a, b, u = pts[n], pts[n + 1], x - n
        out.append((lerp(a[0], b[0], u), lerp(a[1], b[1], u)))
    return out


def in_poly(pts, x, y):
    inside, j = False, len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


# ---- type --------------------------------------------------------------------------------------------------
def big(ctx, s, cx, cy, size=None, max_w=None, font='serif', weight=700, color='me', alpha=1.0, spacing_em=0.0, max_size=2000, stroke=0.0, italic=False):
    """A word centred on (cx, baseline cy), fitted to max_w when no size is given."""
    sz = size if size is not None else ctx.fit(s, max_w, font=font, weight=weight, spacing_em=spacing_em, max_size=max_size, italic=italic)
    sp = spacing_em * sz
    ctx.text(s, cx + sp / 2, cy, size=sz, font=font, weight=weight, color=color, alpha=alpha, align='center', spacing=sp, stroke=stroke, italic=italic)
    return sz


def slam(ctx, s, t, t0, cx, cy, size=None, max_w=None, step=0.03, times=None, font='serif', weight=900, color='me', hot='meHot',
         alpha=1.0, spacing_em=0.01, start=2.2, settle=0.14, max_size=2000):
    """Characters slam in one by one: oversized and bright, then settled."""
    sz = size if size is not None else ctx.fit(s, max_w, font=font, weight=weight, spacing_em=spacing_em, max_size=max_size)
    sp = spacing_em * sz
    o = dict(size=sz, weight=weight, font=font)
    x0 = cx - (ctx.measure(s, spacing=sp, **o) - sp) / 2
    for i, ch in enumerate(s):
        ti = times[i] if times else t0 + i * step
        if t >= ti and ch != ' ':
            w = ctx.measure(ch, **o)
            x = x0 + ctx.measure(s[:i + 1], **o) + i * sp - w / 2
            k = ease_out(prog(t, ti, ti + settle))
            with ctx.at(x, cy, scale=start + (1 - start) * k):
                ctx.text(ch, 0, 0, align='center', color=hot if k < 1 else color, alpha=alpha * (0.35 + 0.65 * k), **o)
    return sz


def on_path(ctx, s, path, start=0.0, size=30, weight=600, color='me', alpha=1.0, font='serif', spacing_em=0.06, reveal=10 ** 9, alpha_fn=None):
    """Text along a path: path(d) -> (x, y, angle) at distance d."""
    o = dict(size=size, weight=weight, font=font)
    sp = spacing_em * size
    end = start
    for i, ch in enumerate(s):
        end = start + ctx.measure(s[:i + 1], **o) + (i + 1) * sp
        if i < reveal and ch != ' ':
            x, y, a = path(end - (ctx.measure(ch, **o) + sp) / 2)
            with ctx.at(x, y, rot=a):
                ctx.text(ch, 0, 0, align='center', color=color, alpha=alpha * (alpha_fn(i) if alpha_fn else 1), **o)
    return end - start


def scramble(s, key, bucket, amount=1.0):
    G = 'ABCDEFGHIKLMNOPRSTUVXYZ0123456789#/<>[]%$'
    return ''.join(G[int(rand(key, i, bucket, 1) * len(G))] if ch != ' ' and rand(key, i, bucket) < amount else ch for i, ch in enumerate(s))
