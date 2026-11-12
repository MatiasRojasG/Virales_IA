"""Escenas de ejemplo: una función por beat, sincronizada con palabras vía T(beat, palabra)."""
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.ease import prog, out_back, clamp, lerp, out_cubic, smooth
from reelforge.mathtex import Equation

TL = None; EP = {}; SHOTS = []; CHUNKS = []


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def sc_hook(P, t, sh):
    tc = T("hook", "causa")
    for k, x in enumerate((360, 720)):
        P.node(x, 800, 80, fill=C.INK, ring=C.WHITE, a=out_back(prog(t, 0.1 * k, 0.1 * k + 0.5)))
    P.arrow(360, 800, 720, 800, C.WHITE, prog(t, tc - 0.2, tc), w=7, gap=95, frac=prog(t, tc - 0.2, tc + 0.3))
    P.text("?", 540, 690, 120, C.PINK, out_back(prog(t, tc, tc + 0.4)), face=C.FONT_BLACK)


EQ = Equation([r"\psi(y_i, y_j)", "=", (r"\psi(y_j, y_i)", C.VIOLET)])


def sc_idea(P, t, sh):
    t0 = T("idea")
    for k, x in enumerate((360, 720)):
        P.node(x, 800, 80, fill=C.INK, ring=C.WHITE)
    P.line(440, 800, 640, 800, C.VIOLET, 1, w=8, frac=prog(t, t0, t0 + 0.6), glow=True)
    EQ.draw(P, 540, 1100, size=90, reveal=prog(t, T("idea", "simétrica"), T("idea", "simétrica") + 1.0, lambda v: v))


SCENES = [("hook", sc_hook), ("idea", sc_idea)]


def setup(tl, data, episode):
    global TL, EP, SHOTS, CHUNKS
    TL, EP = tl, episode
    SHOTS = []
    for k, (bid, fn) in enumerate(SCENES):
        t0 = tl.t(bid) if k else 0.0
        t1 = tl.t(SCENES[k + 1][0]) if k + 1 < len(SCENES) else tl.duration
        SHOTS.append((t0, t1, fn))
    CHUNKS = tl.chunks(SUB.measure)


FADE = 0.28


def draw_frame(P, t):
    P.background(t)
    for (t0, t1, fn) in SHOTS:
        if t < t0 - 0.01 or t > t1 + FADE: continue
        a = min(prog(t, t0, t0 + FADE) if t0 > 0 else 1.0,
                1 - prog(t, t1, t1 + FADE, smooth) if t1 < TL.duration else 1.0)
        s = lerp(1.035, 1.0, out_cubic(clamp((t - t0) / 0.6)))
        with P.layer(a):
            with P.transform(0, 0, s, cx=540, cy=800):
                fn(P, t, (t0, t1))
    P.circle(C.SAFE_LEFT + 10, 262, 8, C.CYAN, 1)
    P.text(EP["tag"], C.SAFE_LEFT + 34, 273, 28, C.GRAY, 1, face=C.FONT_BOLD, align="left", tracking=2)
    SUB.draw(P, CHUNKS, t)
    P.rect(0, C.H - 8, C.W * t / TL.duration, C.H, C.CYAN, 0.8)


def draw_cover(P, t=1.0):
    P.background(t, accent=0.6)
    P.text(EP["title"].upper(), 540, 600, 90, C.CYAN, 1, face=C.FONT_BLACK, glow=0.6)


def sfx_cues(tl):
    return [(0.0, "thump", 1.0)] + [(tl.t(b) - 0.15, "whoosh", 0.8) for b, _ in SCENES[1:]]
