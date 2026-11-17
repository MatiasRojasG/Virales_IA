"""Escenas — «Misma edad, distinta piel».

Hilo visual: dos «lupas» de piel (brazo por dentro / dorso de la mano). La lupa del dorso se abre
en un corte de piel donde la luz UV rompe la red de colágeno; luego 903 puntos se dividen en dos
grupos que se condensan otra vez en dos lupas de dorso de mano (el estudio). El cierre vuelve a la
composición del inicio.
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic, smooth
from reelforge import marca as L

TL = None; EP = {}; CHUNKS = []; CUE = {}
LX, RX, LY, LR = 300, 780, 830, 205          # lupas
PALE = lerp_c(L.SKIN, L.WHITE, 0.16)          # piel poco expuesta
DERMIS = L.hx("#2B1E1B")
FIBER = L.hx("#EADBC8")
BROWN = L.hx("#7E5636")


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


# =============================================================== piel en lupa
_rng_cache = {}


def _tex(seed):
    if seed not in _rng_cache:
        r = np.random.default_rng(seed)
        _rng_cache[seed] = {
            "fine": [(r.uniform(-1, 1), r.uniform(-1, 1), r.choice([-1, 1]), r.uniform(0.05, 0.12)) for _ in range(70)],
            "pores": [(r.uniform(-1, 1), r.uniform(-1, 1), r.uniform(1.2, 2.6)) for _ in range(90)],
            "wr": [(r.uniform(-0.75, 0.75), r.uniform(0.6, 1.0), r.uniform(0, 6.28), r.uniform(0.0, 0.35)) for _ in range(7)],
            "spots": [(r.uniform(-0.75, 0.75), r.uniform(-0.75, 0.75), r.uniform(0.04, 0.11), r.uniform(0, 0.6)) for _ in range(13)],
        }
    return _rng_cache[seed]


def skin_patch(P, x, y, r, age=0.0, a=1.0, seed=1, tone=None, ring=0.0, ring_rgb=None):
    """Lupa con textura de piel. age 0 → lisa y pareja; 1 → arrugas, manchas y tono desigual."""
    if a <= 0 or r <= 2: return
    tone = tone or L.SKIN
    tx = _tex(seed)
    c = P.c
    with P.layer(a):
        c.save()
        pth = skia.Path(); pth.addCircle(x, y, r)
        c.clipPath(pth, doAntiAlias=True)
        base = lerp_c(tone, lerp_c(L.SKIN2, (0.62, 0.5, 0.36), 0.4), 0.35 * age)
        sh = skia.GradientShader.MakeRadial((x - r * 0.3, y - r * 0.35), r * 1.6,
                                            [L.color4(lerp_c(base, L.WHITE, 0.12)), L.color4(lerp_c(base, (0, 0, 0), 0.22))])
        c.drawPaint(skia.Paint(Shader=sh))
        # tono desigual con la edad
        for (u, v, s, k) in tx["spots"][:6]:
            P.circle(x + u * r, y + v * r, r * 0.45, L.SKIN2, 0.10 * age, blur=r * 0.15)
        # microrelieve: rombos finos (siempre)
        for (u, v, sg, ln) in tx["fine"]:
            x0, y0 = x + u * r, y + v * r
            d = ln * r
            P.line(x0 - d, y0 - sg * d * 0.55, x0 + d, y0 + sg * d * 0.55, L.SKIN2, 0.22 + 0.18 * age, w=1.6 + 1.2 * age)
        for (u, v, rr) in tx["pores"]:
            P.circle(x + u * r, y + v * r, rr * r / 205, L.SKIN2, 0.35)
        # arrugas: crecen en largo y profundidad
        if age > 0.02:
            for (u, v, ph, d0) in tx["wr"]:
                e = clamp((age - d0) / 0.5)
                if e <= 0: continue
                yy = y + (u * 0.9) * r
                half = r * 0.85 * v * e
                w = skia.Path(); w.moveTo(x - half, yy)
                n = 6
                for k in range(1, n + 1):
                    xx = x - half + 2 * half * k / n
                    w.lineTo(xx, yy + math.sin(ph + k * 1.3) * r * 0.025)
                c.drawPath(w, paint(lerp_c(L.SKIN2, BROWN, 0.5), 0.75 * e, stroke=(2.5 + 4.5 * e) * r / 205))
                c.drawPath(w, paint(lerp_c(tone, L.WHITE, 0.3), 0.25 * e, stroke=1.5 * r / 205))
        # manchas solares
        for (u, v, s, d0) in tx["spots"]:
            e = clamp((age - d0 * 0.6 - 0.15) / 0.4)
            if e > 0:
                P.circle(x + u * r, y + v * r, s * r * (0.6 + 0.4 * e), BROWN, 0.55 * e, blur=s * r * 0.25)
        # brillo
        P.circle(x - r * 0.35, y - r * 0.4, r * 0.35, L.WHITE, 0.07, blur=r * 0.2)
        c.restore()
        P.circle(x, y, r, L.INK, 0.18, stroke=3)
        if ring > 0:
            rgb = ring_rgb or L.INK
            P.circle(x, y, r + 10, rgb, 0.9 * ring, stroke=5)
            P.circle(x, y, r + 10, rgb, 0.25 * ring, stroke=16, blur=10)


# =============================================================== íconos
def sun(P, x, y, r, a=1.0, t=0.0):
    if a <= 0: return
    P.circle(x, y, r * 2.4, L.INK, 0.10 * a, blur=r * 0.8)
    for k in range(12):
        ang = k * math.pi / 6 + t * 0.35
        P.line(x + math.cos(ang) * r * 1.3, y + math.sin(ang) * r * 1.3,
               x + math.cos(ang) * r * 1.62, y + math.sin(ang) * r * 1.62, L.INK, a, w=r * 0.13)
    P.circle(x, y, r, L.INK, a)


def beams(P, x0, y0, x1, y1, t, a, n=5, spread=70, rgb=None):
    """Haces de luz con trazos que avanzan (de (x0,y0) hacia (x1,y1))."""
    if a <= 0: return
    rgb = rgb or L.INK
    ang = math.atan2(y1 - y0, x1 - x0); nx, ny = -math.sin(ang), math.cos(ang)
    L_ = math.hypot(x1 - x0, y1 - y0)
    for k in range(n):
        off = (k - (n - 1) / 2) * spread / max(1, n - 1) * 2
        ax, ay = x0 + nx * off * 0.3, y0 + ny * off * 0.3
        bx, by = x1 + nx * off, y1 + ny * off
        P.line(ax, ay, bx, by, rgb, 0.10 * a, w=3)
        ph = (t * 1.3 + k * 0.37) % 1.0
        for j in range(3):
            u = (ph + j / 3) % 1.0
            u0, u1 = u, min(1, u + 0.12)
            P.line(lerp(ax, bx, u0), lerp(ay, by, u0), lerp(ax, bx, u1), lerp(ay, by, u1), rgb, a * (0.35 + 0.65 * math.sin(math.pi * u)), w=5)


def cloud(P, x, y, s, a):
    if a <= 0: return
    with P.layer(a):
        for (dx, dy, r) in [(-70, 10, 55), (-10, -25, 72), (60, 5, 58), (0, 30, 60), (-60, 35, 40), (75, 35, 40)]:
            P.circle(x + dx * s, y + dy * s, r * s, L.hx("#B5B2AC"), 1)
        P.circle(x - 20 * s, y - 35 * s, 40 * s, L.WHITE, 0.35, blur=12)


def hand(P, x, y, s=1.0, a=1.0):
    """Dorso de mano estilizado, dedos hacia arriba."""
    if a <= 0: return
    with P.layer(a):
        P.rect(x - 55 * s, y + 60 * s, x + 55 * s, y + 200 * s, L.SKIN2, 1, radius=26 * s)   # muñeca
        for k, (dx, h) in enumerate([(-54, 120), (-18, 150), (18, 145), (54, 115)]):
            P.rect(x + (dx - 16) * s, y - (60 + h) * s, x + (dx + 16) * s, y - 20 * s, L.SKIN, 1, radius=16 * s)
        with P.transform(0, 0, 1, rot=-38, cx=x - 80 * s, cy=y + 10 * s):
            P.rect(x - 98 * s, y - 95 * s, x - 62 * s, y + 20 * s, L.SKIN, 1, radius=18 * s)
        P.rect(x - 78 * s, y - 60 * s, x + 78 * s, y + 90 * s, L.SKIN, 1, radius=40 * s)
        for dx in (-54, -18, 18, 54):
            P.line(x + dx * s * 0.7, y - 30 * s, x + dx * s * 0.45, y + 40 * s, L.SKIN2, 0.35, w=4 * s)


def dab(P, x, y, t, t0, a=1.0):
    """Toque de protector: gota que aparece y se expande en un anillo."""
    u = clamp((t - t0) / 0.5)
    if u <= 0 or a <= 0: return
    fade = 1 - 0.55 * clamp((t - t0 - 0.6) / 0.8)              # el protector se esparce
    P.circle(x, y, 17 * out_back(u) * (1 + 0.5 * (1 - fade)), lerp_c(L.WHITE, L.SKIN, 0.15), 0.9 * a * fade, blur=2)
    v = clamp((t - t0) / 0.9)
    if v < 1: P.circle(x, y, 18 + 55 * out_cubic(v), L.INK, (1 - v) * a, stroke=4)


# =============================================================== 1 · lupas del inicio / cierre
def lenses_intro(P, t):
    c = CUE
    # visible desde el cuadro 0; la lupa derecha se abre hacia el corte de piel
    a = 1 - prog(t, c["uv"] - 0.3, c["uv"] + 0.3)
    if a <= 0: return
    ringL = window(t, 0.25, c["dorso"], 0.3, 0.3)
    ringR = window(t, c["dorso"] - 0.05, c["exact"], 0.25, 0.3)
    vie = pulse(t, c["vieja"], 0.9)
    m = in_out_cubic(prog(t, c["uv"] - 0.5, c["uv"] + 0.4))
    # piel del dorso: algo envejecida desde el inicio
    skin_patch(P, LX, LY, LR, 0.0, a * (1 - m), seed=3, tone=PALE, ring=ringL)
    rx, ry, rr = lerp(RX, 540, m), lerp(LY, 860, m), lerp(LR, 340, m)
    skin_patch(P, rx, ry, rr * (1 + 0.04 * vie), 0.62, a, seed=7, ring=max(ringR, vie))
    la = a * (1 - m)
    P.text("brazo, por dentro", LX, LY + LR + 70, 36, L.INK if ringL > 0.3 else L.GRAY, la, face=C.FONT_BOLD)
    P.text("dorso de la mano", RX, LY + LR + 70, 36, L.INK if ringR > 0.3 or vie > 0.3 else L.GRAY, la, face=C.FONT_BOLD)
    # «misma edad»
    ae = window(t, c["exact"] - 0.1, c["sol0"] + 0.4, 0.35, 0.4)
    if ae > 0:
        P.text("=", 540, LY + 30, 110, L.INK, ae, face=C.FONT_BLACK)
        P.pill("misma edad", 540, LY - LR - 50, 36, L.INK, ae, bg=False, fill_a=0.06)
    av = window(t, c["vieja"] - 0.05, c["sol0"] + 0.3, 0.3, 0.4)
    if av > 0:
        P.text("?", RX + LR - 10, LY - LR + 30 + 6 * math.sin(t * 5), 130, L.RED, out_back(av), face=C.FONT_BLACK, glow=0.6)
    # el sol: ilumina solo el dorso
    asun = window(t, c["solw"] - 0.25, c["uv"] + 0.6, 0.45, 0.5)
    if asun > 0:
        sx, sy = lerp(640, 540, m), lerp(540, 470, m)
        beams(P, sx + 30, sy + 40, rx, ry - rr * 0.9, t, asun * 0.9, n=4, spread=60)
        sun(P, sx, sy, 50 * (0.6 + 0.4 * out_back(prog(t, c["solw"] - 0.25, c["solw"] + 0.25))), asun, t)
        # el brazo, a la sombra
        P.circle(LX, LY, LR, L.BG, 0.4 * asun * (1 - m))


def lenses_end(P, t):
    c = CUE
    a = prog(t, c["cie0"] - 0.35, c["cie0"] + 0.35)
    if a <= 0: return
    ae = window(t, c["anos"] - 0.4, TL.duration + 5, 0.35, 0.3)
    skin_patch(P, LX, LY, LR, 0.0, a, seed=3, tone=PALE, ring=window(t, c["cie0"], c["cie_mano"], 0.3, 0.3))
    skin_patch(P, RX, LY, LR, 0.62, a, seed=7, ring=window(t, c["cie_mano"] - 0.1, c["anos"], 0.3, 0.3))
    P.text("brazo, por dentro", LX, LY + LR + 70, 36, L.GRAY, a, face=C.FONT_BOLD)
    P.text("dorso de la mano", RX, LY + LR + 70, 36, L.GRAY, a, face=C.FONT_BOLD)
    if ae > 0:
        P.text("=", 540, LY + 30, 110, L.INK, ae, face=C.FONT_BLACK)
        P.pill("misma edad", 540, LY - LR - 50, 36, L.INK, ae, bg=False, fill_a=0.06)
    asun = prog(t, c["solf"] - 0.3, c["solf"] + 0.3)
    if asun > 0:
        beams(P, 670, 470, RX, LY - LR * 0.9, t, asun * 0.9, n=4, spread=60)
        sun(P, 640, 440, 50 * out_back(asun), asun, t)
        P.circle(LX, LY, LR, L.BG, 0.4 * asun)


# =============================================================== 2 · corte de piel y colágeno
def _mesh():
    r = np.random.default_rng(11)
    pts = {}
    nx, ny = 9, 6
    for i in range(nx):
        for j in range(ny):
            pts[(i, j)] = (-0.82 + 1.64 * i / (nx - 1) + r.uniform(-0.06, 0.06), -0.05 + 0.85 * j / (ny - 1) + r.uniform(-0.05, 0.05))
    edges = []
    for (i, j), p in pts.items():
        for di, dj in ((1, 0), (0, 1), (1, 1), (1, -1)):
            q = pts.get((i + di, j + dj))
            if q is None: continue
            if (di, dj) in ((1, 1), (1, -1)) and r.random() < 0.55: continue
            edges.append((p, q, r.uniform(0, 1), r.uniform(0, 6.28)))
    return edges


MESH = _mesh()


def xsection(P, t):
    c = CUE
    a = prog(t, c["uv"] - 0.25, c["uv"] + 0.35) * (1 - prog(t, c["duda0"] - 0.2, c["duda0"] + 0.4))
    if a <= 0: return
    x, y, r = 540, 860, 340
    # daño acumulado: algo con los primeros rayos, mucho «año tras año»
    dmg = 0.18 * prog(t, c["uv"] + 0.3, c["colw"] + 0.6, smooth) + 0.52 * prog(t, c["acum"], c["duda0"], smooth)
    with P.layer(a):
        cv = P.c; cv.save()
        pth = skia.Path(); pth.addCircle(x, y, r); cv.clipPath(pth, doAntiAlias=True)
        cv.drawColor(L.color4(DERMIS))
        # epidermis (banda superior con borde ondulado)
        top = y - r * 0.45
        ep = skia.Path(); ep.moveTo(x - r, y - r); ep.lineTo(x + r, y - r); ep.lineTo(x + r, top)
        for k in range(0, 41):
            xx = x + r - 2 * r * k / 40
            ep.lineTo(xx, top + math.sin(k * 0.9) * 10)
        ep.close()
        cv.drawPath(ep, paint(L.SKIN, 1))
        P.line(x - r, y - r * 0.82, x + r, y - r * 0.82, L.SKIN2, 0.5, w=6)
        # red de colágeno
        hi = pulse(t, c["colw"], 1.2)
        for (p, q, th, ph) in MESH:
            x0, y0 = x + p[0] * r, y + p[1] * r
            x1, y1 = x + q[0] * r, y + q[1] * r
            broken = dmg > th * 0.95
            if not broken:
                mx, my = (x0 + x1) / 2, (y0 + y1) / 2 + 9 * math.sin(t * 1.6 + ph)
                w = skia.Path(); w.moveTo(x0, y0); w.quadTo(mx, my, x1, y1)
                col = lerp_c(FIBER, L.INK, hi)
                cv.drawPath(w, paint(col, 0.85, stroke=6))
            else:
                k = clamp((dmg - th * 0.95) / 0.08)
                f = 0.42 - 0.17 * k
                P.line(x0, y0 + 8 * k, lerp(x0, x1, f), lerp(y0, y1, f) + 22 * k, FIBER, 0.35, w=5)
                P.line(x1, y1 + 8 * k, lerp(x1, x0, f), lerp(y1, y0, f) + 22 * k, FIBER, 0.35, w=5)
        for (p, q, th, ph) in MESH:
            P.circle(x + p[0] * r, y + p[1] * r, 6, FIBER, 0.6)
        # rayos UV que entran desde arriba
        au = prog(t, c["uv"] - 0.1, c["uv"] + 0.4)
        for k in range(6):
            xx = x - r * 0.75 + k * r * 0.3
            ph = (t * 0.9 + k * 0.29) % 1.0
            y0 = y - r - 40; y1 = y + r * 0.55
            yy = lerp(y0, y1, ph)
            P.line(xx, yy - 70, xx, yy, L.RED, au * math.sin(math.pi * ph), w=6, glow=True)
        cv.restore()
        P.circle(x, y, r, L.INK, 0.18, stroke=3)
        if hi > 0.01 or t > c["colw"]:
            P.rect(x - 112, y + r * 0.72 - 32, x + 112, y + r * 0.72 + 32, DERMIS, prog(t, c["colw"] - 0.1, c["colw"] + 0.3), radius=32)
            P.pill("colágeno", x, y + r * 0.72, 34, FIBER, prog(t, c["colw"] - 0.1, c["colw"] + 0.3) * 0.95, fill_a=0.08, bg=False)
    # años que pasan
    ay = a * prog(t, c["acum"] - 0.2, c["acum"] + 0.2)
    if ay > 0:
        n = 20; filled = n * prog(t, c["acum"], c["duda0"] - 0.1, lambda u: u)
        for k in range(n):
            xx = 290 + k * 500 / (n - 1)
            on = clamp(filled - k)
            P.circle(xx, 1255, 8, L.INK if on > 0.5 else L.DIM, ay)
        P.text("años", 250, 1265, 30, L.GRAY, ay, face=C.FONT_BOLD, align="right")


# =============================================================== 3 · la duda
def doubt(P, t):
    c = CUE
    a = prog(t, c["duda0"] - 0.1, c["duda0"] + 0.5) * (1 - prog(t, c["est0"] - 0.1, c["est0"] + 0.35))
    if a <= 0: return
    u = prog(t, c["duda0"], c["est0"], lambda v: v)
    s = 0.95 + 0.04 * u
    with P.layer(a):
        L.head(P, 540, 860, s, wrinkles=0.25 * u, spots=0.2 * u)
        # reloj que corre rápido: pasan años
        cx, cy, r = 260, 620, 62
        P.circle(cx, cy, r, L.CARD, 1); P.circle(cx, cy, r, L.GRAY, 1, stroke=5)
        ang = t * 9
        P.line(cx, cy, cx + 44 * math.sin(ang), cy - 44 * math.cos(ang), L.INK, 1, w=6)
        P.line(cx, cy, cx + 28 * math.sin(ang / 12), cy - 28 * math.cos(ang / 12), L.INK, 1, w=7)
        aq = prog(t, c["sirve"] - 0.5, c["sirve"] + 0.0)
        if aq > 0:
            P.text("?", 820, 700 + 6 * math.sin(t * 5), 170, L.RED, out_back(aq), face=C.FONT_BLACK, glow=0.6)


# =============================================================== 4 · el estudio: 903 personas
N = 903
GA = math.pi * (3 - math.sqrt(5))


def _phyllo(i, n, cx, cy, R):
    rr = R * math.sqrt((i + 0.5) / n); th = i * GA
    return cx + rr * math.cos(th), cy + rr * math.sin(th)


DOTS = []
for _i in range(N):
    g = _i % 2
    j = _i // 2
    ng = (N + 1) // 2 if g == 0 else N // 2
    DOTS.append((_phyllo(_i, N, 540, 860, 330), _phyllo(j, ng, LX if g == 0 else RX, LY, 230), g))


def study(P, t):
    c = CUE
    a = prog(t, c["est0"] - 0.1, c["est0"] + 0.3)
    fold = in_out_cubic(prog(t, c["manos"] - 0.6, c["manos"] + 0.3))
    a *= 1 - fold * 0.999
    if a <= 0: return
    split = prog(t, c["diario"] - 0.4, c["diario"] + 0.9, in_out_cubic)
    k_in = c["est0"] + 0.1                                   # la espiral crece desde el inicio de la frase
    span = max(1.3, c["n903"] + 0.5 - k_in)
    with P.layer(a):
        for i, ((x0, y0), (x1, y1), g) in enumerate(DOTS):
            ap = clamp((t - (k_in + span * i / N)) / 0.25)
            if ap <= 0: continue
            d = clamp(split * 1.25 - 0.25 * (i / N))
            x, y = lerp(x0, x1, in_out_cubic(d)), lerp(y0, y1, in_out_cubic(d))
            # al final se contraen hacia la lupa
            cx = LX if g == 0 else RX
            x, y = lerp(x, cx + (x - cx) * LR / 230, fold), lerp(y, LY + (y - LY) * LR / 230, fold)
            col = lerp_c(L.INK, L.INK if g == 0 else L.DIM, d)
            P.circle(x, y, 6.5 * out_back(ap), col, 0.95)
        an = window(t, c["n903"] - 0.1, c["diario"] + 0.2, 0.3, 0.4)
        P.pill("903 personas", 540, 1250, 38, L.INK, an, bg=False, fill_a=0.06)
        al = prog(t, c["diario"] + 0.2, c["diario"] + 0.6)
        ar = prog(t, c["otra"], c["otra"] + 0.4)
        P.text("todos los días", LX, LY + 300, 36, L.INK, al, face=C.FONT_BOLD)
        P.text("cuando querían", RX, LY + 300, 36, L.GRAY, ar, face=C.FONT_BOLD)
    timebar(P, t, a_mul=1.0)


def timebar(P, t, a_mul=1.0):
    c = CUE
    a = a_mul * window(t, c["anios"] - 0.3, c["pct"] - 0.2, 0.3, 0.5)
    if a <= 0: return
    f = prog(t, c["anios"], c["manos"] + 0.2, lambda u: u)
    x0, x1, y = 200, 880, 545
    P.rect(x0, y - 7, x1, y + 7, L.CARD, a, radius=7)
    P.rect(x0, y - 7, lerp(x0, x1, f), y + 7, L.INK, a, radius=7)
    P.circle(lerp(x0, x1, f), y, 13, L.INK, a)
    P.text("4,5 años", 540, y - 34, 34, L.INK, a, face=C.FONT_BOLD)


# =============================================================== 5 · resultado
def result(P, t):
    c = CUE
    a = prog(t, c["manos"] - 0.4, c["manos"] + 0.3) * (1 - prog(t, c["rut0"] - 0.2, c["rut0"] + 0.3))
    if a <= 0: return
    lapse = prog(t, c["res0"] + 0.1, c["casi"] + 0.9, smooth)
    move = in_out_cubic(prog(t, c["pct"] - 0.4, c["pct"] + 0.3))
    y = lerp(LY, 950, move); r = lerp(LR, 175, move)
    ok = prog(t, c["casi"] - 0.1, c["casi"] + 0.4)
    skin_patch(P, LX, y, r, 0.12 + 0.06 * lapse, a, seed=21, ring=ok)
    skin_patch(P, RX, y, r, 0.12 + 0.5 * lapse, a, seed=7)
    # anillo de tiempo alrededor de cada lupa mientras pasan los 4,5 años
    al = window(t, c["res0"], c["casi"] + 1.2, 0.2, 0.4) * a
    if al > 0:
        for xx in (LX, RX):
            P.c.drawArc(skia.Rect(xx - r - 22, y - r - 22, xx + r + 22, y + r + 22), -90, 360 * lapse, False,
                        paint(L.INK, 0.35 * al, stroke=4))
    P.text("todos los días", LX, y + r + 70, 36, L.INK, a, face=C.FONT_BOLD)
    P.text("cuando querían", RX, y + r + 70, 36, L.GRAY, a, face=C.FONT_BOLD)
    ap = prog(t, c["pct"] - 0.15, c["pct"] + 0.35) * a
    if ap > 0:
        s = 0.85 + 0.15 * out_back(clamp((t - c["pct"] + 0.15) / 0.45))
        with P.transform(0, 0, s, cx=540, cy=640):
            P.text("24 %", 540, 670, 150, L.RED, ap, face=C.FONT_BLACK, glow=0.5)
        P.text("menos probabilidad de envejecimiento visible", 540, 740, 38, L.INK, prog(t, c["pct"] + 0.5, c["pct"] + 1.1) * a, face=C.FONT_SEMI)


# =============================================================== 6 · rutina
def routine(P, t):
    c = CUE
    a = prog(t, c["rut0"] - 0.1, c["rut0"] + 0.4) * (1 - prog(t, c["cie0"] - 0.35, c["cie0"] + 0.25))
    if a <= 0: return
    to_face = in_out_cubic(prog(t, c["cara"] - 0.7, c["cara"] - 0.1))
    with P.layer(a):
        # frasco
        drop = out_back(prog(t, c["rut0"] - 0.1, c["rut0"] + 0.5, lambda u: u))
        side = in_out_cubic(prog(t, c["manana"] - 0.3, c["manana"] + 0.4))
        bx = lerp(540, 330, side); by = lerp(700, 880, drop)
        with P.layer(1 - to_face):
            L.bottle(P, bx, by, 1.25, 1, label="FPS 30+")
            # «no es caro»
            ap = window(t, c["rut0"] + 0.2, c["manana"], 0.3, 0.3)
            if ap > 0:
                P.pill("$$$", 790, 760, 64, L.INK, ap, fill_a=0.06, bg=False)
                cr = prog(t, c["caro"] - 0.1, c["caro"] + 0.25)
                P.line(715, 800, 715 + 150 * cr, 800 - 80 * cr, L.RED, ap, w=9)
            # amanecer y nube
            am = prog(t, c["manana"] - 0.1, c["manana"] + 0.5)
            if am > 0:
                hz = 1080
                P.line(600, hz, 950, hz, L.DIM, am, w=4)
                sy = lerp(hz + 40, 820, out_cubic(prog(t, c["manana"], c["manana"] + 1.0)))
                P.c.save(); P.c.clipRect(skia.Rect(560, 420, 1000, hz - 2))
                sun(P, 775, sy, 62, am, t)
                cl = in_out_cubic(prog(t, c["nublado"] - 0.4, c["nublado"] + 0.3))
                if cl > 0:
                    beams(P, 775, sy + 40, 775, hz - 10, t, cl * 0.9, n=4, spread=80)
                    cloud(P, lerp(1100, 775, cl), sy + 10, 1.0, 1)
                P.c.restore()
        # cara, cuello y manos
        if to_face > 0:
            with P.layer(to_face):
                hx_, hy = 400, 800
                L.head(P, hx_, hy, 0.95)
                hand(P, 790, 980, 1.05)
                dab(P, hx_ - 70, hy + 40, t, c["cara"]); dab(P, hx_ + 75, hy + 35, t, c["cara"] + 0.12)
                dab(P, hx_, hy - 120, t, c["cara"] + 0.24)
                dab(P, hx_, hy + 175, t, c["cuello"])
                dab(P, 790, 1000, t, c["manos2"]); dab(P, 760, 930, t, c["manos2"] + 0.12)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["dorso"] = T("hook", "dorso"); c["exact"] = T("hook", "exactamente"); c["vieja"] = T("hook", "vieja")
    c["sol0"] = T("sol"); c["solw"] = T("sol", "sol")
    c["col0"] = T("colageno"); c["uv"] = T("colageno", "ultravioleta"); c["colw"] = T("colageno", "colágeno")
    c["acum"] = T("colageno", "acumula")
    c["duda0"] = T("duda"); c["sirve"] = T("duda", "sirve")
    c["est0"] = T("estudio"); c["n903"] = T("estudio", "903"); c["diario"] = T("estudio", "todos")
    c["otra"] = T("estudio", "otra"); c["anios"] = T("estudio", "cuatro"); c["manos"] = T("estudio", "manos")
    c["res0"] = T("resultado"); c["casi"] = T("resultado", "casi"); c["pct"] = T("resultado", "24")
    c["rut0"] = T("rutina"); c["caro"] = T("rutina", "caro"); c["manana"] = T("rutina", "cada")
    c["nublado"] = T("rutina", "nublado"); c["cara"] = T("rutina", "cara"); c["cuello"] = T("rutina", "cuello")
    c["manos2"] = T("rutina", "manos")
    c["cie0"] = T("cierre"); c["cie_mano"] = T("cierre", "mano"); c["anos"] = T("cierre", "años"); c["solf"] = T("cierre", "sol")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.6 * window(t, c["solw"] - 0.3, c["uv"] + 0.5, 0.4, 0.6) + 0.6 * window(t, c["pct"] - 0.2, c["rut0"], 0.3, 0.5) \
        + 0.5 * prog(t, c["solf"] - 0.3, c["solf"] + 0.4)
    L.background(P, t, glow=glow)
    lenses_intro(P, t)
    xsection(P, t)
    doubt(P, t)
    study(P, t)
    result(P, t)
    routine(P, t)
    lenses_end(P, t)
    L.vignette(P, 0.5)
    L.title(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.7)
    skin_patch(P, LX, 900, LR, 0.0, 1, seed=3, tone=PALE)
    skin_patch(P, RX, 900, LR, 0.62, 1, seed=7, ring=1)
    beams(P, 905, 690, RX + 40, 900 - LR * 0.9, 0.3, 0.9, n=3, spread=40)
    sun(P, 920, 660, 38, 1, 0.3)
    P.text("=", 540, 930, 110, L.INK, 1, face=C.FONT_BLACK)
    P.text("brazo, por dentro", LX, 900 + LR + 70, 36, L.GRAY, 1, face=C.FONT_BOLD)
    P.text("dorso de la mano", RX, 900 + LR + 70, 36, L.INK, 1, face=C.FONT_BOLD)
    P.text("MISMA EDAD.", 540, 440, 104, L.INK, 1, face=C.FONT_BLACK)
    P.text("DISTINTA PIEL.", 540, 555, 104, L.RED, 1, face=C.FONT_BLACK, glow=0.4)
    L.vignette(P, 0.4)
    L.title(P)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.35), (c["dorso"], "pop", 0.45), (c["exact"], "tick", 0.6), (c["vieja"], "pop_low", 0.5),
            (c["solw"] - 0.25, "whoosh", 0.45), (c["solw"], "ding", 0.45),
            (c["uv"] - 0.3, "whoosh", 0.5), (c["colw"], "pop", 0.45)]
    n = 20
    for k in range(n):
        cues.append((lerp(c["acum"], c["duda0"] - 0.1, k / n), "tick", 0.18))
    cues += [(c["sirve"] - 0.6, "riser", 0.35), (c["est0"] + 0.1, "swell", 0.4), (c["diario"] - 0.4, "whoosh", 0.4),
             (c["anios"], "tick", 0.5), (c["manos"] - 0.4, "whoosh_down", 0.4), (c["casi"], "ding", 0.55),
             (c["pct"] - 0.1, "thump", 0.6), (c["pct"] - 0.05, "ding", 0.7),
             (c["rut0"] + 0.2, "thump", 0.45), (c["caro"], "pop_low", 0.45), (c["manana"], "swell", 0.35),
             (c["nublado"] - 0.3, "whoosh", 0.35), (c["cara"], "pop", 0.4), (c["cuello"], "pop", 0.4),
             (c["manos2"], "pop", 0.4), (c["cie0"] - 0.3, "whoosh_down", 0.4), (c["solf"], "ding", 0.6),
             (c["solf"] - 0.2, "swell", 0.4)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["est0"], "pulse": (c["res0"], c["rut0"]), "quiet": [(c["duda0"], c["est0"])]}
