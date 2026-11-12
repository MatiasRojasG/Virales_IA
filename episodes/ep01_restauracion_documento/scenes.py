"""Escenas del Episodio 1. Cada escena es una función draw(P, t, sh) sincronizada
con palabras del guion mediante TL.t(beat, palabra)."""
from __future__ import annotations
import json, math
import numpy as np
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import image
from reelforge.ease import (clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back,
                            in_out_cubic, out_quint, smooth)
from reelforge.mathtex import Equation

TL = None          # Timeline
D = {}             # datos del experimento
SHOTS = []         # (t0, t1, fn)
CHUNKS = []
EP = {}

PAPER255 = np.array([int(v * 255) for v in C.PAPER], np.uint8)
INK255 = np.array([int(v * 255) for v in C.INK], np.uint8)


def doc_rgba(b):
    rgb = np.where(b[..., None] == 1, INK255, PAPER255)
    return np.dstack([rgb, np.full(b.shape, 255, np.uint8)])


# ---------------------------------------------------------------- utilidades
def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


DOC_W = 960
DOC_CX, DOC_CY = 540, 790


def doc_rect(scale=1.0, cx=DOC_CX, cy=DOC_CY):
    h, w = D["orig"].shape
    dw = DOC_W * scale; dh = dw * h / w
    return cx - dw / 2, cy - dh / 2, cx + dw / 2, cy + dh / 2


def card(P, x0, y0, x1, y1, a=1.0):
    P.rect(x0 + 6, y0 + 22, x1 - 6, y1 + 30, (0, 0, 0), 0.55 * a, radius=26, blur=28)
    P.rect(x0 - 14, y0 - 14, x1 + 14, y1 + 14, C.PAPER, a, radius=22)


def draw_doc(P, key, x0, y0, x1, y1, a=1.0, clip=None):
    im = image(key, D["rgba"][key])
    if clip is None:
        P.img(im, x0, y0, x1, y1, a)
    else:
        with P.clip_rect(*clip):
            P.img(im, x0, y0, x1, y1, a)


def counter(v, dec=0, suffix="%"):
    s = f"{v:.{dec}f}".replace(".", ",")
    return s + suffix


# ---------------------------------------------------------------- escenas
def sc_hook(P, t, sh):
    t0 = sh[0]
    x0, y0, x1, y1 = doc_rect()
    # pequeño "glitch" de entrada
    shake = 10 * math.sin(t * 90) * (1 - clamp(t / 0.35))
    s_in = lerp(1.06, 1.0, prog(t, 0, 0.6))
    with P.transform(shake, 0, s_in, cx=DOC_CX, cy=DOC_CY):
        card(P, x0, y0, x1, y1)
        draw_doc(P, "obs", x0, y0, x1, y1)
        # barrido del OCR (rosado = falla)
        ts, te = T("hook", "Ningún"), T("hook", "leerlo", end=True)
        if ts - 0.1 < t < te + 0.4:
            u = clamp((t - ts) / (te - ts))
            yy = lerp(y0, y1, u)
            a = window(t, ts - 0.1, te + 0.4, 0.15, 0.3)
            P.rect(x0 - 14, y0 - 14, x1 + 14, yy, C.PINK, 0.10 * a)
            P.line(x0 - 14, yy, x1 + 14, yy, C.PINK, a, w=5, glow=True)
        # restauración: barrido cyan de izquierda a derecha
        tw = T("hook", "idea")
        u = prog(t, tw, tw + 1.1, in_out_cubic)
        if u > 0:
            xx = lerp(x0 - 14, x1 + 14, u)
            draw_doc(P, "lab", x0, y0, x1, y1, clip=(x0 - 14, y0 - 14, xx, y1 + 14))
            if u < 1:
                P.line(xx, y0 - 30, xx, y1 + 30, C.CYAN, 1, w=6, glow=True)
    # titular superior: contador 0→15 %
    v = 15 * prog(t, 0.05, 1.2, out_cubic)
    a = 1 - prog(t, sh[1] - 0.6, sh[1])
    P.text(counter(v), 540, 455, 150, C.CYAN, a, face=C.FONT_BLACK, glow=0.8)
    P.text("DE LOS PÍXELES INVERTIDOS", 540, 525, 40, C.WHITE, a * prog(t, 0.3, 0.8), face=C.FONT_BOLD, tracking=3)
    # chips de estado bajo el documento
    ts = T("hook", "Ningún")
    ac = window(t, ts, T("hook", "idea") + 0.2, 0.25, 0.25)
    P.pill("LECTOR OCR:  SIN TEXTO ÚTIL", 540, y1 + 95, 34, C.PINK, ac * out_back(prog(t, ts, ts + 0.4)))
    tw = T("hook", "idea")
    ac2 = prog(t, tw + 0.9, tw + 1.3)
    P.pill("RESTAURADO CON UNA RED DE MARKOV", 540, y1 + 95, 34, C.CYAN, ac2)


def _ink_crop():
    o = D["orig"]
    ys, xs = np.where(o[: o.shape[0] // 4])
    x0, y0 = int(xs.min()), int(ys.min())
    return x0 - 4, y0 - 3, 30          # esquina superior izq. y tamaño del recorte


def camera(P, key, cx, cy, z, vp, overlay=None, a=1.0):
    """Dibuja la imagen `key` con cámara centrada en (cx,cy) (px imagen), zoom z,
    recortada al viewport vp=(x0,y0,x1,y1). overlay(P, z) dibuja en coords imagen."""
    h, w = D["orig"].shape
    vx0, vy0, vx1, vy1 = vp
    P.c.save()
    P.c.clipRect(__import__("skia").Rect(vx0, vy0, vx1, vy1), doAntiAlias=True)
    P.c.translate((vx0 + vx1) / 2, (vy0 + vy1) / 2)
    P.c.scale(z, z)
    P.c.translate(-cx, -cy)
    P.rect(-8, -8, w + 8, h + 8, C.PAPER, a, radius=6)
    P.img(image(key, D["rgba"][key]), 0, 0, w, h, a)
    if overlay: overlay(P, z)
    P.c.restore()


def sc_problema(P, t, sh):
    t0 = T("problema")
    h, w = D["orig"].shape
    cx0, cy0, n = _ink_crop()
    z0 = DOC_W / w
    vp = (90, 340, 990, 1240)
    z1 = 900 / n
    u = prog(t, t0 + 0.2, t0 + 2.0, in_out_cubic)
    z = z0 * (z1 / z0) ** u
    # el punto objetivo se mueve linealmente en pantalla
    uc = 1 - (1 / z - 1 / z1) / (1 / z0 - 1 / z1)
    cx = lerp(w / 2, cx0 + n / 2, uc)
    cy = lerp(h / 2, cy0 + n / 2, uc)
    orig, obs = D["orig"], D["obs"]
    t_ip = T("problema", "tinta"); t_pi = T("problema", "papel", 1)
    t_pp = T("problema", "píxel")

    def overlay(P, z):
        ga = prog(t, t0 + 1.6, t0 + 2.2)
        if ga <= 0: return
        lw = 1.6 / z
        for k in range(n + 1):
            P.line(cx0 + k, cy0, cx0 + k, cy0 + n, C.BG, 0.35 * ga, w=lw, cap="butt")
            P.line(cx0, cy0 + k, cx0 + n, cy0 + k, C.BG, 0.35 * ga, w=lw, cap="butt")
        a1 = prog(t, t_ip, t_ip + 0.4); a2 = prog(t, t_pi, t_pi + 0.4)
        for yy in range(cy0, cy0 + n):
            for xx in range(cx0, cx0 + n):
                if orig[yy, xx] != obs[yy, xx]:
                    ink_lost = orig[yy, xx] == 1
                    aa = a1 if ink_lost else a2
                    if aa > 0:
                        col = C.PINK if ink_lost else C.VIOLET
                        P.rect(xx + 0.08, yy + 0.08, xx + 0.92, yy + 0.92, col, aa, stroke=5 / z)
        # escaneo "píxel a píxel": un cursor que salta sin poder decidir
        if t > t_pp - 0.1:
            k = int((t - t_pp) / 0.28)
            path = [(cx0 + 6 + 3 * k % n, cy0 + 9 + (k * 7) % (n - 10)) for k in range(0, 40)]
            px, py = path[min(k, len(path) - 1)]
            ac = window(t, t_pp - 0.1, sh[1], 0.2, 0.3)
            P.rect(px - 0.15, py - 0.15, px + 1.15, py + 1.15, C.CYAN, ac, stroke=7 / z)
            P.text("?", px + 0.5, py - 0.6, 2.4, C.CYAN, ac, face=C.FONT_BLACK)

    camera(P, "obs", cx, cy, z, vp, overlay)
    # leyenda
    a1 = prog(t, t_ip, t_ip + 0.4); a2 = prog(t, t_pi, t_pi + 0.4)
    P.pill("tinta → papel", 300, 1300, 36, C.PINK, a1)
    P.pill("papel → tinta", 780, 1300, 36, C.VIOLET, a2)


# ---------- malla sintética 7x7 para explicar la idea ----------
GN = 7
CELL = 118
GRID_CX, GRID_CY = 540, 790
PATTERN = np.zeros((GN, GN), int)
PATTERN[:, :2] = 1
PATTERN[3, 4] = 1          # punto negro aislado
ISO = (3, 4)


def gpos(r, c, cell=CELL, cx=GRID_CX, cy=GRID_CY):
    return cx + (c - (GN - 1) / 2) * cell, cy + (r - (GN - 1) / 2) * cell


def neighbors(r, c):
    return [(r + dr, c + dc) for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1))
            if 0 <= r + dr < GN and 0 <= c + dc < GN]


def sc_idea(P, t, sh):
    t0 = T("idea")
    tv = T("idea", "vecinos"); tc = T("idea", "compartir")
    ta = T("idea", "aislado"); tr = T("idea", "ruido")
    for r in range(GN):
        for c in range(GN):
            x, y = gpos(r, c)
            d = math.hypot(r - 3, c - 3)
            u = out_back(prog(t, t0 + 0.05 * d, t0 + 0.05 * d + 0.45, lambda v: v))
            s = (CELL - 12) * u / 2
            col = C.INK if PATTERN[r, c] else C.PAPER
            P.rect(x - s, y - s, x + s, y + s, col, 1, radius=10)
            P.rect(x - s, y - s, x + s, y + s, C.DIM, 0.6, stroke=2, radius=10)
    # pares vecinos que comparten color
    pairs = [((1, 0), (1, 1)), ((5, 0), (6, 0)), ((1, 4), (1, 5)), ((5, 3), (5, 4)), ((2, 6), (3, 6))]
    for k, (p1, p2) in enumerate(pairs):
        a = window(t, tv + 0.15 * k, ta - 0.2, 0.3, 0.3)
        if a <= 0: continue
        x1, y1 = gpos(*p1); x2, y2 = gpos(*p2)
        P.line(x1, y1, x2, y2, C.VIOLET, a, w=10, frac=prog(t, tv + 0.15 * k, tv + 0.15 * k + 0.4), glow=True)
        P.circle(x1, y1, 12, C.VIOLET, a); P.circle(x2, y2, 12, C.VIOLET, a)
    # punto aislado
    x, y = gpos(*ISO)
    ai = prog(t, ta, ta + 0.3)
    if ai > 0:
        for (r, c) in neighbors(*ISO):
            xn, yn = gpos(r, c)
            P.rect(xn - 53, yn - 53, xn + 53, yn + 53, C.VIOLET, ai * 0.9, stroke=5, radius=10)
        pr = pulse(t, ta, 0.6) + pulse(t, ta + 0.6, 0.6)
        P.rect(x - 62 - 10 * pr, y - 62 - 10 * pr, x + 62 + 10 * pr, y + 62 + 10 * pr, C.PINK, ai, stroke=7, radius=14)
    ar = prog(t, tr, tr + 0.35)
    if ar > 0:
        jitter = 6 * math.sin(t * 70) * (1 - clamp((t - tr) / 0.5))
        P.pill("¿RUIDO?", x + jitter, y - 120, 38, C.PINK, out_back(ar))
    P.text("Cada cuadrado es un píxel", 540, 330, 40, C.GRAY, prog(t, t0 + 0.3, t0 + 0.8) * (1 - prog(t, tv, tv + 0.4)), face=C.FONT_MED)


def sc_grafo(P, t, sh):
    t0 = T("grafo")
    tcausa = T("grafo", "causa"); tgr = T("grafo", "grafo"); tmk = T("grafo", "Markov")
    tcada = T("grafo", "cada"); tesc = T("grafo", "escáner")
    m = prog(t, t0 + 0.1, t0 + 1.0, in_out_cubic)          # cuadrados -> nodos
    cell = CELL
    # aristas (aparecen como onda desde el centro)
    for r in range(GN):
        for c in range(GN):
            for (r2, c2) in ((r, c + 1), (r + 1, c)):
                if r2 >= GN or c2 >= GN: continue
                d = math.hypot((r + r2) / 2 - 3, (c + c2) / 2 - 3)
                u = prog(t, tgr + 0.06 * d, tgr + 0.06 * d + 0.35)
                if u <= 0: continue
                x1, y1 = gpos(r, c); x2, y2 = gpos(r2, c2)
                P.line(x1, y1, x2, y2, C.VIOLET, 0.85, w=5, frac=u)
    # capa observada (desplazada, en cyan), unida a cada nodo
    ao = prog(t, tesc - 0.6, tesc + 0.1)
    off = (34, -34)
    for r in range(GN):
        for c in range(GN):
            x, y = gpos(r, c)
            if ao > 0:
                ox, oy = x + off[0] * ao, y + off[1] * ao
                P.line(x, y, ox, oy, C.CYAN, 0.9 * ao, w=3)
                col = C.INK if D["obs_pattern"][r, c] else C.PAPER
                P.rect(ox - 13, oy - 13, ox + 13, oy + 13, col, ao, radius=3)
                P.rect(ox - 13, oy - 13, ox + 13, oy + 13, C.CYAN, ao, stroke=2.5, radius=3)
            s = lerp((cell - 12) / 2, 25, m)
            rad = lerp(10, s, m)
            col = C.INK if PATTERN[r, c] else C.PAPER
            ring = C.WHITE if PATTERN[r, c] else C.DIM
            P.rect(x - s, y - s, x + s, y + s, col, 1, radius=rad)
            P.rect(x - s, y - s, x + s, y + s, ring, 0.9 * m + 0.4, stroke=3, radius=rad)
    # flecha "causal" que se tacha
    ac = window(t, tcausa - 0.3, tgr - 0.1, 0.25, 0.3)
    if ac > 0:
        x1, y1 = gpos(2, 2); x2, y2 = gpos(2, 3)
        P.arrow(x1, y1 - 70, x2, y2 - 70, C.WHITE, ac, w=6, head=24, frac=prog(t, tcausa - 0.3, tcausa + 0.1))
        xm, ym = (x1 + x2) / 2, y1 - 70
        ux = prog(t, tcausa + 0.3, tcausa + 0.6)
        if ux > 0:
            P.line(xm - 30, ym - 30, xm - 30 + 60 * ux, ym - 30 + 60 * ux, C.PINK, ac, w=9)
            P.line(xm + 30, ym - 30, xm + 30 - 60 * ux, ym - 30 + 60 * ux, C.PINK, ac, w=9)
    P.pill("GRAFO NO DIRIGIDO", 540, 330, 38, C.VIOLET, prog(t, tgr, tgr + 0.4) * (1 - prog(t, tmk - 0.1, tmk + 0.2)))
    P.pill("RED DE MARKOV", 540, 330, 38, C.VIOLET, prog(t, tmk, tmk + 0.4))
    al = prog(t, tesc - 0.4, tesc + 0.2)
    P.rich([("● ", C.WHITE), ("etiqueta del píxel   ", C.GRAY), ("■ ", C.CYAN), ("lo que vio el escáner", C.GRAY)],
           540, 1270, 34, al, face=C.FONT_MED)


# ---------- foco en un nodo: las dos voces ----------
FX, FY = 540, 700
NR = 220


def focus_layout():
    nb = [(FX, FY - NR), (FX, FY + NR), (FX - NR, FY), (FX + NR, FY)]
    obs = (FX + 150, FY - 150)
    return nb, obs


EQ = None


def eq_h():
    global EQ
    if EQ is None:
        EQ = Equation([r"h_i", "=", (r"\alpha\, u_i", C.CYAN), "+", (r"\beta \sum_{j \sim i} s_j", C.VIOLET)])
    return EQ


def draw_focus(P, t, a, center_fill, center_label, nb_fill, obs_fill, cyan_hi=0.0, vio_hi=(0, 0, 0, 0),
               center_ring=C.WHITE, labels=True):
    nb, (ox, oy) = focus_layout()
    for k, (x, y) in enumerate(nb):
        hi = vio_hi[k]
        P.line(FX, FY, x, y, C.VIOLET, a * (0.75 + 0.25 * hi), w=6 + 6 * hi, glow=hi > 0.05)
    P.line(FX, FY, ox, oy, C.CYAN, a * (0.8 + 0.2 * cyan_hi), w=5 + 6 * cyan_hi, glow=cyan_hi > 0.05)
    for k, (x, y) in enumerate(nb):
        P.node(x, y, 52, fill=nb_fill, ring=C.VIOLET, a=a, ring_w=5, glow=vio_hi[k],
               label="s" + "ⱼ" if False else None)
        if labels:
            if x == FX:
                P.text("vecino", x - 72, y + 10, 28, C.GRAY, a * 0.9, face=C.FONT_MED, align="right")
            else:
                P.text("vecino", x, y + 95, 28, C.GRAY, a * 0.9, face=C.FONT_MED)
    # nodo observado (cuadrado)
    P.rect(ox - 34, oy - 34, ox + 34, oy + 34, obs_fill, a, radius=6)
    P.rect(ox - 34, oy - 34, ox + 34, oy + 34, C.CYAN, a, stroke=5, radius=6)
    if cyan_hi > 0.05:
        P.rect(ox - 50, oy - 50, ox + 50, oy + 50, C.CYAN, 0.35 * a * cyan_hi, blur=18, radius=10)
    if labels:
        P.text("sensor", ox + 60, oy + 10, 30, C.CYAN, a, face=C.FONT_SEMI, align="left")
    P.node(FX, FY, 70, fill=center_fill, ring=center_ring, a=a, ring_w=6, label=center_label,
           label_rgb=C.CYAN if center_label == "?" else C.WHITE, label_size=60)
    # etiquetas de peso
    P.text("α", (FX + ox) / 2 + 38, (FY + oy) / 2 + 30, 54, C.CYAN, a, face=C.FONT_BOLD)
    P.text("β", FX - NR / 2, FY - 22, 50, C.VIOLET, a, face=C.FONT_BOLD)


def sc_voces(P, t, sh):
    t0 = T("voces")
    ts = T("voces", "sensor"); tv = T("voces", "vecinos")
    tp = T("voces", "positiva"); tn = T("voces", "negativa")
    a = prog(t, t0, t0 + 0.5)
    chi = pulse(t, ts, 0.9) + prog(t, ts, ts + 0.3) * 0.2 * (1 - prog(t, tv, tv + 0.3))
    vhi = tuple(pulse(t, tv + 0.12 * k, 0.8) for k in range(4))
    draw_focus(P, t, a, C.BG2, None, C.BG2, C.BG2, chi, vhi)
    P.text("píxel i", FX - 95, FY - 95, 30, C.WHITE, a, face=C.FONT_MED, align="right")
    eq = eq_h()
    pp = [prog(t, t0 + 0.3, t0 + 0.8, lambda v: v)] * 2 + [prog(t, ts - 0.1, ts + 0.4, lambda v: v)] \
        + [prog(t, tv - 0.2, tv + 0.3, lambda v: v)] * 2
    eq.draw(P, 540, 1090, size=88, part_prog=pp, glow={2: chi, 4: max(vhi)})
    P.text("u, s = −1 (papel)  o  +1 (tinta)", 540, 385, 30, C.GRAY, prog(t, ts, ts + 0.5), face=C.FONT_MED)
    P.pill("h > 0  →  tinta", 300, 1250, 36, C.WHITE, out_back(prog(t, tp, tp + 0.35)), fill_a=0.08)
    P.pill("h < 0  →  papel", 780, 1250, 36, C.WHITE, out_back(prog(t, tn, tn + 0.35)), fill_a=0.08)


def sc_ejemplo(P, t, sh):
    t0 = T("ejemplo")
    ts = T("ejemplo", "sensor"); tnum = T("ejemplo", "+0,87")
    tv = T("ejemplo", "vecinos"); tneg = T("ejemplo", "−4,8")
    tg = T("ejemplo", "Gana"); tr = T("ejemplo", "desaparece")
    alpha = D["alpha"]; beta = D["beta"]
    a = 1.0
    flip = prog(t, tg + 0.25, tg + 0.55)
    center_fill = lerp_c(C.INK, C.PAPER, flip)
    chi = pulse(t, ts, 0.9)
    vhi = tuple(pulse(t, tv + 0.18 * k, 0.6) for k in range(4))
    draw_focus(P, t, a, center_fill, None, C.PAPER, C.INK, chi, vhi, center_ring=C.PINK if flip < 0.5 else C.CYAN)
    if flip > 0:
        ring = out_cubic(clamp((t - tg - 0.25) / 0.7))
        P.circle(FX, FY, 70 + 120 * ring, C.CYAN, (1 - ring) * 0.9, stroke=6)
    # cálculo
    y_eq = 1030
    a1 = prog(t, ts - 0.1, ts + 0.3)
    P.rich([("α · (+1) = ", C.WHITE), (f"+{alpha:.2f}".replace(".", ","), C.CYAN)], 540, y_eq, 54, a1, face=C.FONT_BOLD)
    a2 = prog(t, tv - 0.1, tv + 0.3)
    nb_count = min(4, int(max(0, (t - tv)) / 0.18) + 1) if t > tv else 0
    val2 = -beta * nb_count
    P.rich([("β · (−1 −1 −1 −1) = ", C.WHITE), (f"{val2:+.1f}".replace(".", ",").replace("-", "−"), C.VIOLET)],
           540, y_eq + 80, 54, a2, face=C.FONT_BOLD)
    # barra de balance
    bx0, bx1, by = 140, 940, 1200
    vmin, vmax = -6.0, 2.0
    X = lambda v: lerp(bx0, bx1, (v - vmin) / (vmax - vmin))
    ab = prog(t, ts, ts + 0.4)
    if ab > 0:
        P.line(bx0, by, bx1, by, C.DIM, ab, w=6)
        P.line(X(0), by - 26, X(0), by + 26, C.WHITE, ab, w=4)
        P.text("papel", bx0, by - 30, 32, C.GRAY, ab, face=C.FONT_SEMI, align="left")
        P.text("tinta", bx1, by - 30, 32, C.GRAY, ab, face=C.FONT_SEMI, align="right")
        h = alpha * prog(t, ts, ts + 0.5) + val2 * 1.0 if t > tv else alpha * prog(t, ts, ts + 0.5)
        if t > tv:
            # suaviza la caída del indicador
            h = alpha - beta * 4 * prog(t, tv, tv + 0.9, out_cubic)
        col = C.CYAN if h > 0 else C.PINK
        P.line(X(0), by, X(h), by, col, ab, w=10)
        P.glow_circle(X(h), by, 16, col, ab)
        P.text(f"h = {h:+.2f}".replace(".", ",").replace("-", "−"), X(h), by + 66, 40, col, ab, face=C.FONT_BOLD)
    af = prog(t, tg + 0.3, tg + 0.7)
    P.pill("→ PAPEL: ERA RUIDO", 540, 380, 40, C.CYAN, out_back(af))
    P.text("α = ½·ln(0,85 / 0,15) ≈ 0,87     β = 1,2", 540, 390, 30, C.GRAY,
           prog(t, t0 + 0.3, t0 + 0.8) * (1 - af), face=C.FONT_MED)


def sc_iterar(P, t, sh):
    t0 = T("iterar")
    trep = T("iterar", "repetimos"); ticm = T("iterar", "ICM")
    hist = D["hist"]; errs = D["err_iter"]
    steps = [0, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30]
    step_dt = 0.62
    k = int(clamp((t - trep) / step_dt, 0, len(steps) - 1)) if t >= trep else 0
    frac = ((t - trep) / step_dt) % 1 if t >= trep and k < len(steps) - 1 else 1.0
    it_cur = steps[k] if t >= trep else 0
    it_next = steps[min(k + 1, len(steps) - 1)]
    x0, y0, x1, y1 = doc_rect(cy=760)
    card(P, x0, y0, x1, y1)
    key_cur = f"h{it_cur}"; key_next = f"h{it_next}"
    for kk in (key_cur, key_next):
        if kk not in D["rgba"]:
            D["rgba"][kk] = doc_rgba(hist[int(kk[1:])])
    draw_doc(P, key_cur, x0, y0, x1, y1)
    # barrido de la siguiente pasada
    if t >= trep and k < len(steps) - 1:
        u = out_cubic(clamp(frac / 0.7))
        yy = lerp(y0 - 14, y1 + 14, u)
        draw_doc(P, key_next, x0, y0, x1, y1, clip=(x0 - 14, y0 - 14, x1 + 14, yy))
        P.line(x0 - 14, yy, x1 + 14, yy, C.CYAN, 1 - clamp((u - 0.9) * 10), w=5, glow=True)
        shown = it_next if u > 0.5 else it_cur
    else:
        shown = it_cur
    # HUD
    P.pill("RECREACIÓN PROPIA · PYTHON", 540, 340, 30, C.GRAY, prog(t, t0, t0 + 0.4) * (1 - prog(t, ticm - 0.3, ticm)), fill_a=0.06)
    P.text(f"pasada {shown}", x0, y0 - 60, 44, C.WHITE, 1, face=C.FONT_BOLD, align="left")
    P.text(f"error {errs[shown] * 100:.1f}%".replace(".", ","), x1, y0 - 60, 44,
           C.CYAN if shown > 0 else C.PINK, 1, face=C.FONT_BOLD, align="right")
    # mini gráfico de error por pasada
    gx0, gx1, gy0, gy1 = 160, 920, 1080, 1260
    ag = prog(t, trep - 0.3, trep + 0.2)
    if ag > 0:
        P.line(gx0, gy1, gx1, gy1, C.DIM, ag, w=3)
        P.text("error por pasada", gx0, gy0 - 14, 28, C.GRAY, ag, face=C.FONT_MED, align="left")
        emax = errs[0]
        X = lambda i: lerp(gx0, gx1, math.log1p(i) / math.log1p(30))
        Y = lambda e: lerp(gy1, gy0 + 20, e / emax)
        pts = [(X(i), Y(errs[i])) for i in range(0, shown + 1)]
        for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
            P.line(xa, ya, xb, yb, C.CYAN, ag, w=5)
        for (xa, ya) in pts:
            P.circle(xa, ya, 7, C.CYAN, ag)
        P.text("0", X(0), gy1 + 40, 26, C.GRAY, ag, face=C.FONT_MED)
        P.text("30", X(30), gy1 + 40, 26, C.GRAY, ag, face=C.FONT_MED)
    ai = prog(t, ticm, ticm + 0.4)
    P.pill("ICM · Iterated Conditional Modes", 540, 340, 34, C.CYAN, out_back(ai))


def bar_metric(P, y, label, v_from, v_to, u, good_down, a, src_note=None):
    x0, x1 = 140, 940
    P.text(label, x0, y - 40, 38, C.WHITE, a, face=C.FONT_SEMI, align="left")
    v = lerp(v_from, v_to, u)
    P.rect(x0, y, x1, y + 34, C.DIM, 0.6 * a, radius=17)
    col = C.CYAN
    P.rect(x0, y, x0 + (x1 - x0) * v / 100, y + 34, col, a, radius=17)
    # marca del valor inicial
    xf = x0 + (x1 - x0) * v_from / 100
    P.line(xf, y - 8, xf, y + 42, C.PINK, a * 0.9, w=4)
    P.text(counter(v_from, 1 if v_from % 1 else 0), xf, y + 86, 32, C.PINK, a * clamp(u * 3), face=C.FONT_BOLD)
    dec = 1 if (v_to % 1) else 0
    P.text(counter(v, dec), x1, y - 40, 54, C.CYAN, a, face=C.FONT_BLACK, align="right")


def sc_resultado(P, t, sh):
    t0 = T("resultado")
    te = T("resultado", "error"); t25 = T("resultado", "2,5%")
    tl_ = T("resultado", "lector"); t94 = T("resultado", "94%")
    P.pill("RESULTADOS DE LA CLASE", 540, 360, 34, C.WHITE, prog(t, t0, t0 + 0.4), fill_a=0.06)
    a1 = prog(t, te - 0.3, te + 0.2)
    bar_metric(P, 620, "Píxeles mal etiquetados", 15, 2.5, prog(t, t25 - 0.3, t25 + 0.6, in_out_cubic), True, a1)
    a2 = prog(t, tl_ - 0.3, tl_ + 0.2)
    bar_metric(P, 960, "Caracteres leídos por el OCR", 42, 94, prog(t, t94 - 0.3, t94 + 0.7, in_out_cubic), False, a2)
    P.text("Fuente: clase EPG4003, diapositivas 17–18", 540, 1240, 28, C.GRAY, a1, face=C.FONT_MED)


def sc_recreacion(P, t, sh):
    t0 = T("recreacion")
    terr = T("recreacion", "2,6%"); tnada = T("recreacion", "nada"); t91 = T("recreacion", "91%")
    P.pill("MI RECREACIÓN EN PYTHON", 540, 330, 34, C.CYAN, prog(t, t0, t0 + 0.4))
    x0, y0, x1, y1 = doc_rect(cy=700)
    card(P, x0, y0, x1, y1)
    # deslizador antes / después
    u = prog(t, t0 + 0.3, terr + 0.6, in_out_cubic)
    xs = lerp(x1 + 14, x0 - 14, u)
    draw_doc(P, "obs", x0, y0, x1, y1, clip=(x0 - 14, y0 - 14, xs, y1 + 14))
    draw_doc(P, "lab", x0, y0, x1, y1, clip=(xs, y0 - 14, x1 + 14, y1 + 14))
    P.line(xs, y0 - 40, xs, y1 + 40, C.CYAN, 1, w=6, glow=True)
    P.glow_circle(xs, (y0 + y1) / 2, 18, C.CYAN, 1)
    P.text("observado", x0, y1 + 60, 30, C.PINK, 1 - u, face=C.FONT_SEMI, align="left")
    P.text("restaurado", x1, y1 + 60, 30, C.CYAN, u, face=C.FONT_SEMI, align="right")
    e0, e1 = D["res"]["error_observed"] * 100, D["res"]["error_restored"] * 100
    ue = prog(t, terr - 0.2, terr + 0.6)
    y = 1100
    P.text("error de píxeles", 300, y - 50, 32, C.GRAY, prog(t, terr - 0.3, terr), face=C.FONT_MED)
    P.text(counter(lerp(e0, e1, ue), 1), 300, y + 30, 84, C.CYAN, prog(t, terr - 0.3, terr), face=C.FONT_BLACK)
    o0, o1 = D["res"]["ocr_acc_observed"] * 100, D["res"]["ocr_acc_restored"] * 100
    uo = prog(t, t91 - 0.3, t91 + 0.6)
    ao = prog(t, tnada - 0.3, tnada)
    P.text("caracteres OCR", 780, y - 50, 32, C.GRAY, ao, face=C.FONT_MED)
    P.text(counter(lerp(o0, o1, uo), 0), 780, y + 30, 84, C.CYAN if uo > 0 else C.PINK, ao, face=C.FONT_BLACK)
    P.text("otra tipografía y otro ruido que la clase · Tesseract (spa)", 540, 1230, 28, C.GRAY,
           prog(t, t0 + 0.5, t0 + 1.0), face=C.FONT_MED)


def sc_bordes(P, t, sh):
    t0 = T("bordes"); tb = T("bordes", "bordes"); tc = T("bordes", "compiten")
    orig, lab = D["orig"], D["lab"]
    h, w = orig.shape
    # recorte de la primera palabra
    cx, cy = 170, 40
    z0 = DOC_W / w; z1 = 2.9
    u = prog(t, t0, t0 + 1.0, in_out_cubic)
    z = z0 * (z1 / z0) ** u
    uc = 1 - (1 / z - 1 / z1) / (1 / z0 - 1 / z1)
    vp = (40, 420, 1040, 1180)
    err = np.argwhere(lab != orig)

    def overlay(P, z):
        ae = prog(t, tb - 0.2, tb + 0.3)
        if ae <= 0: return
        pr = pulse(t, tb, 0.7) + pulse(t, tc, 0.7)
        for (yy, xx) in err:
            P.rect(xx - 0.2 - 0.3 * pr, yy - 0.2 - 0.3 * pr, xx + 1.2 + 0.3 * pr, yy + 1.2 + 0.3 * pr,
                   C.PINK, ae, radius=0.3)

    camera(P, "lab", lerp(w / 2, cx, uc), lerp(h / 2, cy, uc), z, vp, overlay)
    P.pill("ERRORES QUE SOBREVIVEN", 540, 340, 34, C.PINK, prog(t, tb - 0.2, tb + 0.2))
    P.text("■ píxel mal etiquetado tras la restauración", 540, 1240, 30, C.GRAY, prog(t, tb, tb + 0.4), face=C.FONT_MED)


def mini_doc(P, cx, cy, a):
    P.rect(cx - 90, cy - 110, cx + 90, cy + 110, C.PAPER, a, radius=12)
    for k in range(6):
        P.line(cx - 60, cy - 70 + 28 * k, cx + 60 - (40 if k == 5 else 0), cy - 70 + 28 * k, C.INK, a, w=9)


def mini_med(P, cx, cy, a, t):
    P.circle(cx, cy, 105, C.DIM, a)
    P.circle(cx, cy, 105, C.GRAY, a, stroke=3)
    rr = 38 + 3 * math.sin(t * 3)
    P.circle(cx + 22, cy - 12, rr, C.PINK, a * 0.85)
    P.circle(cx + 22, cy - 12, rr + 10, C.CYAN, a, stroke=4)


def mini_sat(P, cx, cy, a):
    cols = [C.GREEN, (0.85, 0.75, 0.3), C.GRAY, (0.2, 0.45, 0.9)]
    rng = np.random.default_rng(1)
    lab = rng.integers(0, 4, (4, 4))
    lab[:2, :2] = 0; lab[2:, 2:] = 3; lab[:2, 2:] = 1
    s = 50
    for r in range(4):
        for c in range(4):
            x = cx - 2 * s + c * s; y = cy - 2 * s + r * s
            P.rect(x + 2, y + 2, x + s - 2, y + s - 2, cols[lab[r, c]], a * 0.85, radius=5)


def sc_cierre(P, t, sh):
    t0 = T("cierre"); ttum = T("cierre", "tumores"); tsat = T("cierre", "satélites")
    tprox = T("cierre", "Próximo"); tfl = T("cierre", "flechas")
    a_apps = 1 - prog(t, tprox - 0.2, tprox + 0.3)
    xs = [220, 540, 860]
    ys = 760
    labels = ["Documentos", "Resonancias", "Satélites"]
    starts = [t0, ttum, tsat]
    for k in range(3):
        a = prog(t, starts[k] - 0.2, starts[k] + 0.3) * a_apps
        if a <= 0: continue
        s = out_back(prog(t, starts[k] - 0.2, starts[k] + 0.3))
        with P.transform(0, 0, 0.9 * s, cx=xs[k], cy=ys):
            if k == 0: mini_doc(P, xs[k], ys, a)
            elif k == 1: mini_med(P, xs[k], ys, a, t)
            else: mini_sat(P, xs[k], ys, a)
        P.text(labels[k], xs[k], ys + 190, 34, C.WHITE, a, face=C.FONT_SEMI)
    # adelanto: DAG de 4 nodos con colisionadores
    ad = prog(t, tprox, tprox + 0.5)
    if ad > 0:
        pos = {"A": (380, 600), "B": (700, 600), "C": (700, 920), "D": (380, 920)}
        edges = [("A", "B"), ("A", "D"), ("C", "B"), ("C", "D")]
        for k, (u, v) in enumerate(edges):
            fr = prog(t, tprox + 0.2 + 0.2 * k, tprox + 0.6 + 0.2 * k)
            P.arrow(*pos[u], *pos[v], C.WHITE, ad, w=6, head=26, frac=fr, gap=62)
        for n, (x, y) in pos.items():
            P.node(x, y, 56, a=ad, label=n, label_size=48)
        aq = prog(t, tfl, tfl + 0.4)
        P.text("?", 540, 800, 170, C.PINK, out_back(aq) * ad, face=C.FONT_BLACK, glow=0.6)
        P.pill(EP["next"], 540, 1180, 40, C.CYAN, prog(t, tprox + 0.4, tprox + 0.9))


# ---------------------------------------------------------------- composición
SCENES = [("hook", sc_hook), ("problema", sc_problema), ("idea", sc_idea), ("grafo", sc_grafo),
          ("voces", sc_voces), ("ejemplo", sc_ejemplo), ("iterar", sc_iterar),
          ("resultado", sc_resultado), ("recreacion", sc_recreacion), ("bordes", sc_bordes),
          ("cierre", sc_cierre)]


def setup(tl, data, episode):
    global TL, D, SHOTS, CHUNKS, EP
    TL, D, EP = tl, data, episode
    D["rgba"] = {k: doc_rgba(D[k]) for k in ("orig", "obs", "lab")}
    # patrón observado de la malla sintética (algunos píxeles con ruido)
    op = PATTERN.copy()
    for (r, c) in [(0, 5), (5, 1), (6, 3), (1, 0)]:
        op[r, c] = 1 - op[r, c]
    D["obs_pattern"] = op
    SHOTS = []
    for k, (bid, fn) in enumerate(SCENES):
        t0 = tl.t(bid) if k > 0 else 0.0
        t1 = tl.t(SCENES[k + 1][0]) if k + 1 < len(SCENES) else tl.duration
        SHOTS.append((t0, t1, fn))
    CHUNKS = tl.chunks(SUB.measure)


FADE = 0.28


def draw_frame(P, t):
    accent = 0.0
    P.background(t, accent)
    for (t0, t1, fn) in SHOTS:
        if t < t0 - 0.01 or t > t1 + FADE: continue
        a_in = prog(t, t0, t0 + FADE, out_cubic) if t0 > 0 else 1.0
        a_out = 1 - prog(t, t1, t1 + FADE, smooth) if t1 < TL.duration else 1.0
        a = min(a_in, a_out)
        if a <= 0: continue
        # empuje de cámara sutil: entra con zoom 1.04→1 y sale a 0.97
        s = lerp(1.035, 1.0, out_cubic(clamp((t - t0) / 0.6))) * lerp(1.0, 0.97, clamp((t - t1) / FADE))
        with P.layer(a):
            with P.transform(0, 0, s, cx=540, cy=800):
                fn(P, t, (t0, t1))
    # etiqueta de serie
    P.circle(SAFE_X := C.SAFE_LEFT + 10, 262, 8, C.CYAN, 1)
    P.text(EP["tag"], SAFE_X + 24, 273, 28, C.GRAY, 1, face=C.FONT_BOLD, align="left", tracking=2)
    SUB.draw(P, CHUNKS, t)
    # barra de progreso fina
    P.rect(0, C.H - 8, C.W * t / TL.duration, C.H, C.CYAN, 0.8)


def sfx_cues(tl):
    T_ = tl.t
    cues = [(0.0, "thump", 1.0), (0.05, "riser", 0.4)]
    for k, (bid, _) in enumerate(SCENES[1:], 1):
        cues.append((T_(bid) - 0.15, "whoosh", 0.8))
    cues += [
        (T_("hook", "idea"), "riser", 0.6), (T_("hook", "idea") + 1.1, "ding", 0.8),
        (T_("problema", "tinta"), "pop", 0.6), (T_("problema", "papel", 1), "pop_low", 0.6),
        (T_("idea", "aislado"), "pop", 0.7), (T_("idea", "ruido"), "pop_low", 0.7),
        (T_("grafo", "causa") + 0.3, "pop_low", 0.7), (T_("grafo", "grafo"), "riser", 0.4),
        (T_("voces", "sensor"), "pop", 0.6), (T_("voces", "vecinos"), "pop", 0.6),
        (T_("ejemplo", "Gana") + 0.25, "ding", 0.7),
        (T_("iterar", "ICM"), "pop", 0.6),
        (T_("resultado", "94%"), "ding", 0.6), (T_("recreacion", "91%"), "ding", 0.6),
        (T_("bordes", "bordes"), "pop_low", 0.6),
        (T_("cierre", "Próximo"), "riser", 0.5),
    ]
    trep = T_("iterar", "repetimos")
    for k in range(11):
        cues.append((trep + 0.62 * k, "tick", 0.7))
    return cues


def draw_cover(P, t=3.0):
    """Portada 9:16: documento mitad ruido / mitad restaurado + titular."""
    P.background(t, accent=0.6)
    P.text("¿SE PUEDE LEER", 540, 470, 92, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("LO ILEGIBLE?", 540, 575, 92, C.CYAN, 1, face=C.FONT_BLACK, glow=0.7)
    x0, y0, x1, y1 = doc_rect(cy=900)
    card(P, x0, y0, x1, y1)
    xm = (x0 + x1) / 2
    draw_doc(P, "obs", x0, y0, x1, y1, clip=(x0 - 14, y0 - 14, xm, y1 + 14))
    draw_doc(P, "lab", x0, y0, x1, y1, clip=(xm, y0 - 14, x1 + 14, y1 + 14))
    P.line(xm, y0 - 40, xm, y1 + 40, C.CYAN, 1, w=6, glow=True)
    P.pill("15% DE RUIDO", x0 + 200, y1 + 90, 34, C.PINK)
    P.pill("RESTAURADO", x1 - 190, y1 + 90, 34, C.CYAN)
    P.text("Redes de Markov · EP 01", 540, 1330, 46, C.WHITE, 1, face=C.FONT_BOLD)
    P.text("OCR 42% → 94% (resultado de la clase)", 540, 1410, 40, C.VIOLET, 1, face=C.FONT_BOLD)
