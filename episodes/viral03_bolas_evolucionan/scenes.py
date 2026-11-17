"""Escenas — «Nadie les enseñó a sobrevivir».

Un solo escenario, estilo «satisfying»: un círculo, un engranaje que gira y bolas que se copian
al tocarlo. Todo lo que se mueve sale de la simulación REAL (experiment.py). El color de cada bola
es su «giro hacia el centro» heredado (violeta = casi no gira, cyan = gira mucho). El tiempo de
la simulación se acelera suavemente para que cada fase coincida con la voz.
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge import audio as AU
from reelforge.draw import paint, vignette, vband
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic
import experiment as X

TL = None; EP = {}; CHUNKS = []; CUE = {}; D = {}
CX, CY, R, RB = X.CX, X.CY, X.R, X.RB
FPS_SIM = X.FPS
WARP = {}


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def bcol(a):
    return lerp_c(C.VIOLET, C.CYAN, in_out_cubic(clamp(a / 0.75)))


# =============================================================== tiempo de simulación
def build_warp(dur):
    c = CUE
    anchors = [(0.0, 0.0), (c["crecer"], 23.0), (c["susp0"], 34.0), (c["cyan"], 50.5)]
    anchors.append((dur, anchors[-1][1] + (dur - anchors[-1][0]) * 0.9))
    vt, st = np.array(anchors).T
    g = np.arange(0, dur + 2, 1 / 240)
    s = np.interp(g, vt, st, right=st[-1] + (g[-1] - vt[-1]) * 0.9)
    k = int(0.9 * 240)
    pad = np.r_[s[0] - (s[1] - s[0]) * np.arange(k, 0, -1), s, s[-1] + (s[-1] - s[-2]) * np.arange(1, k + 1)]
    s = np.convolve(pad, np.ones(2 * k + 1) / (2 * k + 1), mode="same")[k:-k]
    s = np.maximum.accumulate(np.maximum(s, 0))
    WARP["g"], WARP["s"] = g, s
    WARP["v"] = np.gradient(s, g)
    slopes = np.diff(st) / np.diff(vt)
    print("velocidad de la simulación por tramo:", np.round(slopes, 2))


def S(t):
    return float(np.interp(t, WARP["g"], WARP["s"]))


def speed(t):
    return float(np.interp(t, WARP["g"], WARP["v"]))


def vt_of(sim_t):
    return float(np.interp(sim_t, WARP["s"], WARP["g"]))


# =============================================================== arena y engranaje
def gear(P, x, y, ang, glow, a=1.0):
    n, r0, r1 = 14, 64, X.RG
    pth = skia.Path()
    for i in range(n * 4):
        th = ang + 2 * math.pi * i / (n * 4)
        r = r1 if i % 4 in (1, 2) else r0
        (pth.moveTo if i == 0 else pth.lineTo)(x + r * math.cos(th), y + r * math.sin(th))
    pth.close()
    if glow > 0:
        P.c.drawPath(pth, paint(C.CYAN, 0.45 * glow * a, blur=18))
    P.c.drawPath(pth, paint((0.62, 0.67, 0.78), a))
    P.c.drawPath(pth, paint(lerp_c(C.WHITE, C.CYAN, glow), 0.9 * a, stroke=3))
    P.circle(x, y, 30, (0.36, 0.40, 0.50), a)
    P.circle(x, y, 13, C.BG, a)
    for k in range(5):
        th = ang + 2 * math.pi * k / 5
        P.circle(x + 46 * math.cos(th), y + 46 * math.sin(th), 5, (0.36, 0.40, 0.50), a)


def arena(P, t, s):
    c = CUE
    hw = math.degrees(X.half_width(s))
    P.circle(CX, CY, R, C.WHITE, 0.95, stroke=7)
    rect = skia.Rect(CX - R, CY - R, CX + R, CY + R)
    hi = pulse(t, c["rosado"], 0.9) + 0.6 * window(t, c["crece0"], c["ventaja0"], 0.4, 0.6)
    P.c.drawArc(rect, 90 - hw, 2 * hw, False, paint(C.PINK, 0.35 + 0.35 * hi, 26, blur=14))
    P.c.drawArc(rect, 90 - hw, 2 * hw, False, paint(C.PINK, 1.0, 11))


# =============================================================== bolas
def balls(P, t, s):
    Pm, tr = D["P"], D["traits"]
    nf = len(Pm)
    f = min(nf - 1, int(round(s * FPS_SIM)))
    cur = Pm[f]
    alive = np.where(np.isfinite(cur[:, 0]))[0]
    sp = speed(t)
    step = max(1, int(round(1.4 * sp)))
    # estelas
    for k in range(1, 6):
        f0, f1 = max(0, f - k * step), max(0, f - (k - 1) * step)
        a0, a1 = Pm[f0], Pm[f1]
        al = 0.30 * (1 - (k - 1) / 5)
        for i in alive:
            if not (np.isfinite(a0[i, 0]) and np.isfinite(a1[i, 0])): continue
            if abs(a0[i, 0] - a1[i, 0]) + abs(a0[i, 1] - a1[i, 1]) > 140: continue
            P.line(a0[i, 0], a0[i, 1], a1[i, 0], a1[i, 1], bcol(tr[i]), al, w=RB * 1.1 * (1 - 0.13 * k))
    # nacimientos: anillo que se expande
    B = D["births"]
    win = 0.35 * sp * FPS_SIM
    lo, hi = np.searchsorted(B[:, 0], f - win), np.searchsorted(B[:, 0], f, side="right")
    for b in B[lo:hi]:
        u = clamp((f - b[0]) / max(win, 1))
        P.circle(b[3], b[4], RB + 26 * out_cubic(u), bcol(b[5]), 0.7 * (1 - u), stroke=4)
    # bolas
    for i in alive:
        x, y = cur[i]; col = bcol(tr[i])
        P.circle(x, y, RB * 1.9, col, 0.16, blur=8)
        P.circle(x, y, RB, col, 1)
        P.circle(x - RB * 0.35, y - RB * 0.35, RB * 0.32, C.WHITE, 0.75)
    # muertes: estallido rosado
    Dd = D["deaths"]
    win = 0.45 * sp * FPS_SIM
    lo, hi = np.searchsorted(Dd[:, 0], f - win), np.searchsorted(Dd[:, 0], f, side="right")
    for d in Dd[lo:hi]:
        u = clamp((f - d[0]) / max(win, 1))
        x, y = d[2], d[3]
        nx, ny = (x - CX) / R, (y - CY) / R
        P.circle(x, y, RB * (1 + 1.4 * out_cubic(u)), C.PINK, 0.8 * (1 - u), stroke=3)
        for k in range(6):
            th = math.atan2(-ny, -nx) + (k - 2.5) * 0.45
            r = 10 + 46 * out_cubic(u)
            P.circle(x + r * math.cos(th), y + r * math.sin(th), 4 * (1 - u), C.PINK, 1 - u)
    # brillo del engranaje si hubo una copia hace muy poco
    lo = np.searchsorted(B[:, 0], f - 0.18 * sp * FPS_SIM)
    return 1.0 if hi_any(B, lo, f) else 0.0


def hi_any(B, lo, f):
    return lo < len(B) and B[lo, 0] <= f


# =============================================================== textos de apoyo
def leyenda(P, t):
    c = CUE
    a = window(t, c["gira"] - 0.2, c["nombre0"] - 0.1, 0.4, 0.4)
    if a <= 0: return
    x0, x1, y = 330, 750, 430
    sh = skia.GradientShader.MakeLinear([(x0, 0), (x1, 0)], [skia.Color4f(*C.VIOLET, a), skia.Color4f(*C.CYAN, a)])
    p = skia.Paint(AntiAlias=True, Shader=sh)
    P.c.drawRoundRect(skia.Rect(x0, y - 9, x1, y + 9), 9, 9, p)
    P.text("gira poco", x0 - 20, y + 10, 30, C.VIOLET, a, face=C.FONT_BOLD, align="right")
    P.text("gira mucho", x1 + 20, y + 10, 30, C.CYAN, a, face=C.FONT_BOLD, align="left")


def receta(P, t):
    c = CUE
    a = window(t, c["nombre0"] - 0.1, c["real0"], 0.3, 0.4)
    if a <= 0: return
    for k, (w, col) in enumerate([("copiar", C.WHITE), ("cambiar", C.VIOLET), ("sobrevivir", C.CYAN)]):
        ak = a * prog(t, c[f"rec{k}"] - 0.1, c[f"rec{k}"] + 0.25)
        P.pill(w, 250 + k * 290, 430, 36, col, ak)


def antena(P, t):
    """Antena «doblada» de estilo evolutivo (dibujo simbólico, no la geometría exacta)."""
    c = CUE
    a = window(t, c["real0"] - 0.1, c["cierre0"], 0.4, 0.5)
    if a <= 0: return
    u = prog(t, c["antena"] - 0.2, c["antena"] + 1.1, in_out_cubic)
    pts = [(0, 0), (0, -120), (60, -150), (20, -210), (90, -250), (40, -300), (-30, -280), (-10, -350),
           (60, -380), (10, -440)]
    bx, by = CX, CY + 220
    P.rect(bx - 120, by - 6, bx + 120, by + 10, (0.62, 0.67, 0.78), a, radius=5)
    L = [(bx + x, by + y) for x, y in pts]
    n = len(L) - 1; m = u * n
    for i in range(n):
        fr = clamp(m - i)
        if fr <= 0: break
        (x0, y0), (x1, y1) = L[i], L[i + 1]
        P.line(x0, y0, x1, y1, lerp_c(C.VIOLET, C.CYAN, i / n), a, w=9, frac=fr, glow=True)
    # destino: el espacio
    ae = a * prog(t, c["espacio"] - 0.1, c["espacio"] + 0.6)
    if ae > 0:
        rng = np.random.default_rng(3)
        for k in range(40):
            x, y = rng.uniform(120, 960), rng.uniform(500, 1250)
            P.circle(x, y, rng.uniform(1.5, 3.5), C.WHITE, ae * (0.4 + 0.6 * abs(math.sin(t * 2 + k))))


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D
    TL, EP, D = tl, episode, data
    c = {}
    c["rosado"] = T("hook", "rosado"); c["desaparece"] = T("hook", "desaparece")
    c["preg0"] = T("pregunta")
    c["copias0"] = T("copias"); c["cambio"] = T("copias", "cambio"); c["gira"] = T("copias", "gira")
    c["azar0"] = T("azar"); c["violetas"] = T("azar", "violetas")
    c["crece0"] = T("crece"); c["crecer"] = T("crece", "crecer")
    c["ventaja0"] = T("ventaja"); c["mas"] = T("ventaja", "más"); c["heredan"] = T("ventaja", "heredan")
    c["susp0"] = T("suspenso")
    c["revela0"] = T("revela"); c["cyan"] = T("revela", "cyan")
    c["nombre0"] = T("nombre"); c["genetico"] = T("nombre", "genético")
    c["rec0"] = T("nombre", "Copiar"); c["rec1"] = T("nombre", "cambiar"); c["rec2"] = T("nombre", "sobrevive")
    c["real0"] = T("real"); c["antena"] = T("real", "antena"); c["espacio"] = T("real", "espacio")
    c["cierre0"] = T("cierre"); c["volver"] = T("cierre", "volver")
    CUE = c
    build_warp(tl.duration)
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    s = S(t)
    P.background(t, accent=0.5 * window(t, c["cyan"] - 0.2, c["nombre0"], 0.3, 0.8)
                 + 0.4 * window(t, c["volver"] - 0.2, TL.duration + 1, 0.4, 0.4))
    dim = 1 - 0.8 * window(t, c["real0"] - 0.1, c["cierre0"], 0.45, 0.5)
    with P.layer(dim):
        arena(P, t, s)
        g = balls(P, t, s)
        gear(P, CX, CY, X.GEAR_W * s, max(g * 0.8, pulse(t, c["volver"], 1.2)))
    antena(P, t)
    leyenda(P, t)
    receta(P, t)
    vignette(P, 0.45)
    vband(P, 1300, C.H, 0.0, 0.85)
    SUB.draw(P, CHUNKS, t)


def draw_cover(P, t=0.0):
    tc = vt_of(44.0)
    P.background(1.0, accent=0.6)
    arena(P, -10, 44.0)
    balls(P, tc, 44.0)
    gear(P, CX, CY, 0.3, 0.6)
    P.text("NADIE LES ENSEÑÓ", 540, 330, 88, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("A SOBREVIVIR", 540, 430, 96, C.CYAN, 1, face=C.FONT_BLACK, glow=0.5)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


# =============================================================== audio
NOTES = [659.3, 784.0, 880.0, 987.8, 1174.7, 1318.5]          # pentatónica: el tono sube con el giro
for _k, _f in enumerate(NOTES):
    AU.SFX[f"blip{_k}"] = (lambda f=_f: AU.sfx_pop(f, 0.09))


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.35)]
    last = -1
    for b in D["births"]:
        tv = vt_of(b[0] / FPS_SIM)
        if tv > tl.duration: break
        if tv - last < 0.07: continue
        k = min(len(NOTES) - 1, int(clamp(b[5] / 0.8) * len(NOTES)))
        g = 0.16 * (1 - 0.6 * window(tv, c["real0"], tl.duration + 1, 0.3, 0.3))
        cues.append((tv, f"blip{k}", g)); last = tv
    last = -1
    for d in D["deaths"]:
        tv = vt_of(d[0] / FPS_SIM)
        if tv > tl.duration: break
        if tv - last < 0.15: continue
        cues.append((tv, "pop_low", 0.13)); last = tv
    cues += [(c["rosado"], "tick", 0.5), (c["preg0"], "riser", 0.3), (c["crecer"] - 0.4, "riser", 0.45),
             (c["susp0"], "whoosh", 0.4), (c["cyan"], "ding", 0.7), (c["genetico"], "pop", 0.5),
             (c["antena"], "whoosh", 0.4), (c["espacio"], "swell", 0.4), (c["volver"], "ding", 0.6)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["copias0"], "pulse": (c["crece0"], c["cyan"]), "quiet": [(c["susp0"] + 0.3, c["cyan"] - 0.05)]}
