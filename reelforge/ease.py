import math

def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_c(c1, c2, t):
    return tuple(lerp(x, y, t) for x, y in zip(c1, c2))

def smooth(t):                     # smoothstep
    t = clamp(t); return t * t * (3 - 2 * t)

def in_out_cubic(t):
    t = clamp(t); return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2

def out_cubic(t):
    t = clamp(t); return 1 - (1 - t) ** 3

def out_quint(t):
    t = clamp(t); return 1 - (1 - t) ** 5

def in_cubic(t):
    t = clamp(t); return t ** 3

def out_back(t, s=1.70158):
    t = clamp(t); return 1 + (s + 1) * (t - 1) ** 3 + s * (t - 1) ** 2

def out_elastic(t):
    t = clamp(t)
    if t in (0, 1): return t
    return 2 ** (-10 * t) * math.sin((t * 10 - .75) * 2 * math.pi / 3) + 1

def prog(t, t0, t1, fn=out_cubic):
    """Progreso eased de t entre t0 y t1 (0 antes, 1 después)."""
    if t1 <= t0: return 1.0 if t >= t0 else 0.0
    return fn((t - t0) / (t1 - t0))

def window(t, t0, t1, fin=0.35, fout=0.35, fn=out_cubic):
    """Envolvente 0→1→0: entra en [t0, t0+fin], sale en [t1-fout, t1]."""
    return min(prog(t, t0, t0 + fin, fn), 1 - prog(t, t1 - fout, t1, in_cubic))

def pulse(t, t0, dur=0.5):
    """Pulso 0→1→0 con forma de campana iniciado en t0."""
    x = (t - t0) / dur
    return math.sin(math.pi * x) ** 2 if 0 <= x <= 1 else 0.0
