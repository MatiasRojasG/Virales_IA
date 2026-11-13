"""Escenas — «¿Por qué tu banco bloqueó tu café?» (v2, guion simplificado sin cálculos)

Hilo visual: el celular bloqueado → la lista de compras del banco (una sospechosa) →
100 compras como puntos (1 fraude) → el detector marca 5 → solo 1 de esas 5 era fraude →
por qué (1 fraude frente a 99 normales) → Bayes como dos ingredientes → antes/después
de la alerta (tasa base) → de vuelta al celular: una alerta es una pista, no una prueba.
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint, font, vignette, vband, spring
from reelforge.ease import (clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back,
                            in_out_cubic, out_quint, smooth, in_cubic)

TL = None; EP = {}; CHUNKS = []; CUE = {}; D = {}
N = 100
GRAY = (0.62, 0.66, 0.74)
AMBER = (1.0, 0.72, 0.3)


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def headline(P, a, s=1.0):
    if a <= 0: return
    with P.transform(0, 0, s, cx=540, cy=400):
        P.text("¿POR QUÉ ME", 540, 375, 84, C.WHITE, a, face=C.FONT_BLACK)
        P.text("BLOQUEARON?", 540, 465, 92, C.PINK, a, face=C.FONT_BLACK, glow=0.5)


def phone(P, t, a, s=1.0, cx=540, cy=930):
    if a <= 0: return
    W_, H_ = 470, 780
    with P.layer(a):
        with P.transform(0, 0, s, cx=cx, cy=cy):
            x0, y0, x1, y1 = cx - W_ / 2, cy - H_ / 2, cx + W_ / 2, cy + H_ / 2
            P.rect(x0 - 6, y0 + 10, x1 + 6, y1 + 26, (0, 0, 0), 0.6, radius=58, blur=26)
            P.rect(x0, y0, x1, y1, (0.07, 0.08, 0.11), 1, radius=56)
            P.rect(x0, y0, x1, y1, C.WHITE, 0.14, stroke=2, radius=56)
            P.rect(x0 + 14, y0 + 14, x1 - 14, y1 - 14, (0.10, 0.12, 0.18), 1, radius=44)
            P.rect(cx - 50, y0 + 26, cx + 50, y0 + 44, (0, 0, 0), 1, radius=9)
            # tarjeta
            P.rect(x0 + 44, y0 + 180, x1 - 44, y0 + 400, C.VIOLET, 0.9, radius=22)
            P.rect(x0 + 44, y0 + 180, x1 - 44, y0 + 400, C.CYAN, 0.35, radius=22)
            P.rect(x0 + 74, y0 + 230, x0 + 134, y0 + 275, (0.95, 0.82, 0.45), 1, radius=8)
            P.text("•••• 4821", x0 + 74, y0 + 360, 34, C.WHITE, 1, face=C.FONT_BOLD, align="left", tracking=2)
            # transacción
            ty = y0 + 500
            P.circle(x0 + 86, ty, 30, (0.25, 0.2, 0.18), 1)
            P.rect(x0 + 72, ty - 12, x0 + 98, ty + 14, (0.95, 0.9, 0.85), 1, radius=4)     # taza
            P.circle(x0 + 101, ty, 8, (0.95, 0.9, 0.85), 1, stroke=3)
            P.text("Café · Lisboa", x0 + 134, ty - 4, 28, C.WHITE, 1, face=C.FONT_SEMI, align="left")
            P.text("hace un momento", x0 + 134, ty + 32, 24, C.GRAY, 1, face=C.FONT_MED, align="left")
            P.text("3,50 €", x1 - 40, ty + 8, 30, C.WHITE, 1, face=C.FONT_BOLD, align="right")
            P.line(x0 + 44, ty + 70, x1 - 44, ty + 70, C.WHITE, 0.08, w=2)
            P.text("Supermercado", x0 + 134, ty + 128, 30, C.GRAY, 0.6, face=C.FONT_SEMI, align="left")
            P.circle(x0 + 86, ty + 122, 30, (0.2, 0.22, 0.28), 0.6)
            # notificación de bloqueo (presente desde el cuadro 0, con temblor)
            shake = 10 * math.sin(t * 70) * (1 - clamp(t / 0.6)) if t < 1 else 0
            ny = y0 + 70
            P.rect(x0 + 24 + shake, ny, x1 - 24 + shake, ny + 120, C.PINK, 1, radius=26)
            P.rect(x0 + 24 + shake, ny, x1 - 24 + shake, ny + 120, (0, 0, 0), 0.15, radius=26)
            lx, ly = x0 + 74 + shake, ny + 60
            P.rect(lx - 18, ly - 6, lx + 18, ly + 22, C.WHITE, 1, radius=5)
            P.c.drawArc(skia.Rect(lx - 12, ly - 26, lx + 12, ly + 6), 180, 180, False, paint(C.WHITE, 1, stroke=5))
            P.text("Compra bloqueada", x0 + 110 + shake, ny + 52, 34, C.WHITE, 1, face=C.FONT_BOLD, align="left")
            P.text("Actividad sospechosa", x0 + 110 + shake, ny + 90, 26, C.WHITE, 0.9, face=C.FONT_MED, align="left")



# =============================================================== contexto: lista de compras
ROWS = [("Supermercado", "Santiago", "23.400 $"), ("Farmacia", "Santiago", "8.990 $"),
        ("Café", "Lisboa", "3,50 €"), ("Bencina", "Santiago", "30.000 $"), ("Streaming", "en línea", "6.500 $")]


def contexto(P, t):
    c = CUE
    a = window(t, c["ctx0"] - 0.2, c["ej0"] + 0.4, 0.5, 0.5)
    if a <= 0: return
    with P.layer(a):
        # mapa: de casa a otro país
        am = prog(t, c["pais"] - 0.4, c["pais"] + 0.2)
        if am > 0:
            x0, x1, y = 230, 850, 640
            P.circle(x0, y, 14, C.CYAN, am); P.text("Santiago", x0, y + 50, 28, C.WHITE, am, face=C.FONT_SEMI)
            P.circle(x1, y, 14, AMBER, am); P.text("Lisboa", x1, y + 50, 28, C.WHITE, am, face=C.FONT_SEMI)
            u = prog(t, c["pais"] - 0.2, c["pais"] + 1.0, in_out_cubic)
            pth = skia.Path(); pth.moveTo(x0, y)
            n = 40
            for k in range(1, int(n * u) + 1):
                s = k / n
                pth.lineTo(lerp(x0, x1, s), y - 150 * math.sin(math.pi * s))
            P.c.drawPath(pth, paint(C.WHITE, am * 0.8, stroke=3))
            if u > 0:
                s = u
                P.circle(lerp(x0, x1, s), y - 150 * math.sin(math.pi * s), 9, C.WHITE, am)
        # lista de compras con escáner
        y0 = 760
        scan = prog(t, c["ctx0"] + 0.6, c["ctx0"] + 2.6, in_out_cubic)
        for k, (what, where, amt) in enumerate(ROWS):
            yy = y0 + k * 96
            ak = prog(t, c["ctx0"] + 0.1 * k, c["ctx0"] + 0.1 * k + 0.4)
            flagged = k == 2 and scan > (k + 0.5) / len(ROWS)
            col_bg = lerp_c(C.BG2, (0.30, 0.20, 0.10), 1.0 if flagged else 0.0)
            P.rect(150, yy - 40, 930, yy + 40, col_bg, ak, radius=20)
            P.rect(150, yy - 40, 930, yy + 40, AMBER if flagged else C.WHITE, ak * (0.9 if flagged else 0.12),
                   stroke=3 if flagged else 2, radius=20)
            P.text(what, 190, yy - 2, 32, C.WHITE, ak, face=C.FONT_SEMI, align="left")
            P.text(where, 190, yy + 28, 24, C.GRAY, ak, face=C.FONT_MED, align="left")
            P.text(amt, 890, yy + 10, 30, C.WHITE, ak, face=C.FONT_BOLD, align="right")
            if flagged:
                P.pill("sospechosa", 640, yy + 2, 26, AMBER, ak * prog(t, c["ctx0"] + 1.6, c["ctx0"] + 2.0))
        if 0 < scan < 1:
            ys = lerp(y0 - 60, y0 + 4 * 96 + 60, scan)
            P.line(130, ys, 950, ys, C.CYAN, 1, w=4, glow=True)
        # sospechosa ≠ fraude
        an = prog(t, c["nosig"] - 0.2, c["nosig"] + 0.3)
        if an > 0:
            P.rect(240, 1180, 840, 1250, C.BG, 0.9 * an, radius=35)
            P.rich([("sospechosa ", AMBER), ("≠", C.WHITE), (" fraude", C.VIOLET)], 540, 1228, 44, an, face=C.FONT_BLACK)


# =============================================================== las 100 compras
def L_grid():
    xs = np.linspace(232, 848, 10); ys = np.linspace(590, 1190, 10)
    X, Y = np.meshgrid(xs, ys)
    return np.stack([X.ravel(), Y.ravel()], 1)


def L_five():
    pos = D["grid"].copy()
    for k, i in enumerate(D["order5"]):
        pos[i] = (540 + (k - 2) * 170, 860)
    return pos


def L_split():
    pos = np.zeros((N, 2))
    pos[D["fraud"]] = (250, 900)
    for k, i in enumerate(D["normals"]):
        r, cc = divmod(k, 9)
        pos[i] = (480 + cc * 50, 650 + r * 50)
    return pos


def morph(a, b, t, t0, dur=1.2, stagger=0.4):
    if t <= t0: return a
    u = np.clip((t - t0 - D["phase"] * stagger) / dur, 0, 1)
    u = u * u * (3 - 2 * u)
    return a + (b - a) * u[:, None]


def compras(P, t):
    c = CUE
    a = window(t, c["ej0"] - 0.1, c["bay_q"] + 0.3, 0.4, 0.6)
    if a <= 0: return
    grid = D["grid"]
    born = np.clip((t - c["ej0"] - D["phase"] * 0.8) / 0.5, 0, 1)
    born = born * born * (3 - 2 * born)
    src = np.array([540, 952.0])               # nace donde estaba la compra sospechosa
    pos = src + (grid - src) * born[:, None]
    pos = morph(pos, D["L5"], t, c["solo5"], 1.2, 0.3)
    pos = morph(pos, D["Lsplit"], t, c["exp_comun"], 1.3, 0.4)
    is_fraud = np.zeros(N, bool); is_fraud[D["fraud"]] = True
    is_flag = np.zeros(N, bool); is_flag[D["flag"]] = True
    alpha = np.ones(N)
    fade = window(t, c["solo5"], c["exp_comun"] + 0.3, 0.6, 0.6)
    alpha[~is_flag] = 1 - 0.92 * fade
    r = np.full(N, 26.0)
    big = window(t, c["solo5"] + 0.2, c["exp_comun"] + 0.4, 0.8, 0.6)
    r[is_flag] = 26 + 34 * big
    small = prog(t, c["exp_comun"] + 0.2, c["exp_comun"] + 1.2)
    r = r - (r - 19) * small * (~is_fraud) - (r - 30) * small * is_fraud
    fr_on = prog(t, c["una"] - 0.1, c["una"] + 0.4)
    with P.layer(a):
        for i in range(N):
            if born[i] <= 0: continue
            x, y = pos[i]
            col = lerp_c(GRAY, C.VIOLET, fr_on) if is_fraud[i] else GRAY
            P.circle(x, y, r[i], col, alpha[i] * born[i])
            if is_fraud[i] and fr_on > 0:
                P.circle(x, y, r[i] + 14 * pulse(t, c["una"], 0.8), C.VIOLET, 0.5 * pulse(t, c["una"], 0.8), stroke=4)
            if is_flag[i]:
                ta = c["ident"] + 0.6 if is_fraud[i] else c["cuatro"] + 0.25 * D["rank"][i]
                u = prog(t, ta, ta + 0.3)
                if u > 0:
                    P.circle(x, y, r[i] + 7 + 10 * (1 - u), C.PINK, alpha[i] * u, stroke=5)
        # textos
        P.text("100 compras", 540, 545, 40, C.WHITE, window(t, c["ej0"] + 0.3, c["det0"] + 0.2, 0.4, 0.3), face=C.FONT_BOLD)
        a1 = window(t, c["una"], c["det0"] + 0.5, 0.4, 0.4)
        if a1 > 0:
            P.pill("99 normales", 330, 1252, 30, C.WHITE, a1, fill_a=0.08)
            P.pill("1 fraude", 750, 1252, 30, C.VIOLET, a1)
        ap = window(t, c["frec"] - 0.2, c["det0"] + 0.4, 0.4, 0.4)
        P.text("1 de cada 100", 540, 545, 40, C.VIOLET, 0 * ap, face=C.FONT_BOLD)
        # escáner del detector
        if c["det0"] < t < c["cuatro"] + 1.8:
            u = prog(t, c["det0"] + 0.2, c["ident"] + 0.6, in_out_cubic)
            if 0 < u < 1:
                ys = lerp(560, 1260, u)
                P.line(150, ys, 930, ys, C.CYAN, 1, w=4, glow=True)
        ac = window(t, c["ident"] + 0.6, c["solo5"] + 0.3, 0.4, 0.4)
        n_flag = (1 if t > c["ident"] + 0.6 else 0) + min(4, max(0, int((t - c["cuatro"]) / 0.25) + 1) if t > c["cuatro"] else 0)
        P.text(f"marcadas como sospechosas: {n_flag}", 540, 545, 38, C.PINK, ac * (1 - window(t, c["ej0"], c["det0"], 0.1, 0.1)),
               face=C.FONT_BOLD)
        # descubrimiento: las 5 en fila
        ad = window(t, c["solo5"] + 0.5, c["exp_comun"] + 0.2, 0.4, 0.4)
        if ad > 0:
            P.text("las 5 compras sospechosas", 540, 680, 38, C.PINK, ad, face=C.FONT_BOLD)
            for k, i in enumerate(D["order5"]):
                x = 540 + (k - 2) * 170
                fr = is_fraud[i]
                al = prog(t, c["realmente"] - 0.2, c["realmente"] + 0.4) * ad
                P.text("fraude" if fr else "falsa alerta", x, 975, 28 if not fr else 32,
                       C.VIOLET if fr else C.GRAY, al, face=C.FONT_BOLD)
            a20 = prog(t, c["veinte"] - 0.3, c["veinte"] + 0.3) * ad
            P.text("1 de 5", 540, 1130, 110, C.CYAN, out_back(a20), face=C.FONT_BLACK, glow=0.5)
            P.text("= 20 %", 540, 1215, 54, C.WHITE, a20, face=C.FONT_BOLD)
        # explicación: 1 fraude frente a 99 normales
        ae = window(t, c["exp_comun"] + 0.4, c["bay_q"] + 0.2, 0.4, 0.4)
        if ae > 0:
            P.text("1 fraude", 250, 820, 32, C.VIOLET, ae, face=C.FONT_BOLD)
            P.text("99 compras normales", 680, 600, 32, C.WHITE, ae, face=C.FONT_BOLD)
            ab = prog(t, c["falsas"] - 0.6, c["falsas"] + 0.4, out_cubic) * ae
            P.text("alertas reales", 140, 1185, 30, C.VIOLET, ab, face=C.FONT_SEMI, align="left")
            P.rect(390, 1166, 390 + 90 * ab, 1192, C.VIOLET, ae, radius=13)
            P.text("1", 390 + 90 * ab + 18, 1190, 30, C.VIOLET, ab, face=C.FONT_BOLD, align="left")
            P.text("falsas alertas", 140, 1240, 30, C.PINK, ab, face=C.FONT_SEMI, align="left")
            P.rect(390, 1221, 390 + 360 * ab, 1247, C.PINK, ae, radius=13)
            P.text("4", 390 + 360 * ab + 18, 1245, 30, C.PINK, ab, face=C.FONT_BOLD, align="left")


# =============================================================== Bayes: una pregunta, dos ingredientes
def mini_grid(P, cx, cy, a, sp=22, r=7, highlight=(0,)):
    for k in range(100):
        rr, cc = divmod(k, 10)
        x, y = cx + (cc - 4.5) * sp, cy + (rr - 4.5) * sp
        P.circle(x, y, r, C.VIOLET if k in highlight else GRAY, a)


def bayes(P, t):
    c = CUE
    a = window(t, c["bay0"] - 0.1, c["tb0"] + 0.2, 0.5, 0.5)
    if a <= 0: return
    with P.layer(a):
        s = out_back(prog(t, c["bay0"] - 0.1, c["bay0"] + 0.4))
        with P.transform(0, 0, 0.85 + 0.15 * s, cx=540, cy=560):
            P.text("REGLA DE BAYES", 540, 585, 76, C.CYAN, 1, face=C.FONT_BLACK, glow=0.6)
        # la pregunta
        aq = prog(t, c["bay_q"] - 0.2, c["bay_q"] + 0.3)
        if aq > 0:
            P.rect(110, 650, 970, 790, C.BG2, 0.95 * aq, radius=26)
            P.rect(110, 650, 970, 790, C.PINK, 0.6 * aq, stroke=3, radius=26)
            P.text("Si una compra fue marcada como sospechosa...", 540, 708, 32, C.WHITE, aq, face=C.FONT_SEMI)
            P.text("¿qué probabilidad hay de que sea fraude?", 540, 755, 34, C.PINK, aq, face=C.FONT_BOLD)
        # dos ingredientes
        for k, (cx, ts, title, sub) in enumerate([(300, c["frecuente"], "¿Qué tan frecuente", "es el fraude?"),
                                                  (780, c["confiable"], "¿Qué tan confiable", "es el detector?")]):
            ak = prog(t, ts - 0.3, ts + 0.2)
            if ak <= 0: continue
            sc = 0.85 + 0.15 * out_back(prog(t, ts - 0.3, ts + 0.3))
            with P.transform(0, 0, sc, cx=cx, cy=1030):
                P.rect(cx - 215, 840, cx + 215, 1230, C.BG2, 0.95 * ak, radius=28)
                P.rect(cx - 215, 840, cx + 215, 1230, (C.VIOLET if k == 0 else C.CYAN), 0.6 * ak, stroke=3, radius=28)
                P.text(title, cx, 895, 30, C.WHITE, ak, face=C.FONT_BOLD)
                P.text(sub, cx, 933, 30, C.WHITE, ak, face=C.FONT_BOLD)
                if k == 0:
                    mini_grid(P, cx, 1080, ak, sp=22, r=7)
                    P.text("1 de cada 100", cx, 1210, 28, C.VIOLET, ak, face=C.FONT_SEMI)
                else:
                    # el detector: encuentra el fraude ✓ y se equivoca con 4 de 99
                    P.circle(cx - 110, 1020, 22, C.VIOLET, ak); P.circle(cx - 110, 1020, 32, C.PINK, ak, stroke=4)
                    P.text("lo encuentra", cx - 20, 1030, 28, C.WHITE, ak, face=C.FONT_SEMI, align="left")
                    for j in range(4):
                        P.circle(cx - 140 + j * 30, 1110, 11, GRAY, ak); P.circle(cx - 140 + j * 30, 1110, 17, C.PINK, ak, stroke=3)
                    P.text("pero se equivoca", cx - 10, 1104, 26, C.WHITE, ak, face=C.FONT_SEMI, align="left")
                    P.text("con 4 de 99", cx - 10, 1136, 26, C.WHITE, ak, face=C.FONT_SEMI, align="left")
                    P.text("normales", cx, 1210, 28, C.CYAN, ak, face=C.FONT_SEMI)
        if t > c["confiable"] + 0.6:
            ap = prog(t, c["confiable"] + 0.6, c["confiable"] + 1.0)
            P.text("+", 540, 1060, 70, C.WHITE, ap, face=C.FONT_BLACK)


# =============================================================== tasa base: antes y después de la alerta
def tasa_base(P, t):
    c = CUE
    a = window(t, c["tb0"] - 0.1, c["cie0"] + 0.05, 0.5, 0.4)
    if a <= 0: return
    with P.layer(a):
        s = out_back(prog(t, c["tb0"] - 0.1, c["tb0"] + 0.4))
        P.pill("TASA BASE", 540, 560, 44, C.VIOLET, s)
        P.text("la probabilidad antes de la alerta", 540, 640, 32, C.WHITE, prog(t, c["antes"] - 0.3, c["antes"] + 0.2),
               face=C.FONT_SEMI)
        # antes: 100 compras, 1 fraude
        ab = prog(t, c["antes"] - 0.2, c["antes"] + 0.4)
        if ab > 0:
            P.text("ANTES de la alerta", 290, 720, 30, C.GRAY, ab, face=C.FONT_BOLD)
            mini_grid(P, 290, 900, ab, sp=28, r=9)
            P.text("1 de cada 100", 290, 1080, 36, C.VIOLET, ab, face=C.FONT_BOLD)
        # después: las 5 alertas, 1 fraude
        ad = prog(t, c["despues"] - 0.3, c["despues"] + 0.3)
        if ad > 0:
            P.arrow(470, 900, 600, 900, C.PINK, ad, w=6, head=24)
            P.text("alerta", 535, 870, 26, C.PINK, ad, face=C.FONT_SEMI)
            P.text("DESPUÉS de la alerta", 800, 720, 30, C.GRAY, ad, face=C.FONT_BOLD)
            for k in range(5):
                x = 800 + (k - 2) * 52
                P.circle(x, 900, 20, C.VIOLET if k == 2 else GRAY, ad)
                P.circle(x, 900, 28, C.PINK, ad, stroke=3)
            P.text("1 de cada 5", 800, 1080, 36, C.CYAN, out_back(prog(t, c["unacinco"] - 0.2, c["unacinco"] + 0.3)) * ad
                   if t > c["unacinco"] - 0.2 else 0, face=C.FONT_BOLD)
        # medidor
        am = prog(t, c["cien"], c["cien"] + 0.4)
        if am > 0:
            x0, x1, y = 140, 940, 1180
            v = 0.01
            if t > c["unacinco"]:
                v = lerp(0.01, 0.20, spring((t - c["unacinco"]) * 1.2, freq=7, damp=4.5))
            P.text("probabilidad de que sea fraude", 540, 1150, 28, C.WHITE, am, face=C.FONT_SEMI)
            P.rect(x0, y + 10, x1, y + 28, C.DIM, am, radius=9)
            P.rect(x0, y + 10, x0 + (x1 - x0) * max(v, 0.012), y + 28, C.CYAN if v > 0.05 else C.VIOLET, am, radius=9)
            P.glow_circle(x0 + (x1 - x0) * v, y + 19, 14, C.CYAN if v > 0.05 else C.VIOLET, am)
            P.text("1 %" if v < 0.05 else "20 %", x0 + (x1 - x0) * v, y + 70, 30, C.WHITE, am, face=C.FONT_BOLD)


# =============================================================== cierre
def cierre_overlay(P, t):
    c = CUE
    a = prog(t, c["prueba"] - 0.2, c["prueba"] + 0.3)
    if a <= 0: return
    # pista, no prueba
    P.rect(150, 1180, 930, 1260, C.BG, 0.9 * a, radius=40)
    P.rich([("una alerta es una ", C.WHITE), ("pista", C.CYAN), (", no una ", C.WHITE), ("prueba", C.PINK)],
           540, 1233, 40, a, face=C.FONT_BOLD)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D
    TL, EP = tl, episode
    rng = np.random.default_rng(4)
    fraud = 47
    normals = [i for i in range(N) if i != fraud]
    false4 = [12, 38, 71, 86]
    D = {"fraud": fraud, "normals": np.array(normals), "flag": [fraud] + false4,
         "phase": rng.random(N)}
    rank = np.zeros(N); rank[false4] = np.arange(4)
    D["rank"] = rank
    D["order5"] = [12, 38, fraud, 71, 86]
    D["grid"] = L_grid(); D["L5"] = L_five(); D["Lsplit"] = L_split()

    c = {}
    c["ctx0"] = T("contexto"); c["pais"] = T("contexto", "país"); c["nosig"] = T("contexto", "significa")
    c["ej0"] = T("ejemplo"); c["una"] = T("ejemplo", "una"); c["frec"] = T("ejemplo", "frecuente")
    c["det0"] = T("detector"); c["ident"] = T("detector", "identifica"); c["cuatro"] = T("detector", "cuatro")
    c["cinco"] = T("detector", "cinco")
    c["solo5"] = T("descubrimiento", "esas"); c["realmente"] = T("descubrimiento", "realmente")
    c["veinte"] = T("descubrimiento", "veinte")
    c["exp0"] = T("explicacion"); c["exp_comun"] = T("explicacion", "común"); c["falsas"] = T("explicacion", "falsas")
    c["bay0"] = T("bayes"); c["bay_q"] = T("bayes", "marcada"); c["frecuente"] = T("bayes", "frecuente")
    c["confiable"] = T("bayes", "confiable")
    c["tb0"] = T("tasa_base"); c["antes"] = T("tasa_base", "antes"); c["cien"] = T("tasa_base", "cien")
    c["despues"] = T("tasa_base", "Después"); c["unacinco"] = T("tasa_base", "cinco")
    c["cie0"] = T("cierre"); c["prueba"] = T("cierre", "prueba"); c["bayes_end"] = T("cierre", "Bayes")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    P.background(t, accent=0.25 * window(t, c["veinte"] - 0.3, c["exp0"], 0.5, 0.5))
    a_ph = (1 - prog(t, c["ctx0"] - 0.3, c["ctx0"] + 0.3)) + prog(t, c["cie0"], c["cie0"] + 0.5)
    s_ph = lerp(1.0, 0.85, prog(t, c["ctx0"] - 0.3, c["ctx0"] + 0.3)) if t < c["cie0"] - 0.2 \
        else lerp(0.9, 1.0, out_cubic(prog(t, c["cie0"] - 0.2, c["cie0"] + 0.6)))
    phone(P, t, clamp(a_ph), s_ph * 1.12, cy=960)
    headline(P, clamp(1 - prog(t, c["ctx0"] - 0.4, c["ctx0"]) + prog(t, c["cie0"] + 0.05, c["cie0"] + 0.5)),
             1.0 + 0.1 * (1 - out_back(prog(t, 0, 0.35))))
    contexto(P, t)
    compras(P, t)
    bayes(P, t)
    tasa_base(P, t)
    cierre_overlay(P, t)
    ad = window(t, c["ej0"], c["cie0"], 0.4, 0.4)
    P.text("Ejemplo hipotético simplificado · no son datos reales de un banco", 540, 1305, 23, C.GRAY,
           ad * 0.9, face=C.FONT_MED)
    vignette(P, 0.45)
    vband(P, 1240, C.H, 0.0, 0.85)
    P.circle(C.SAFE_LEFT + 10, 262, 8, C.CYAN, 1)
    P.text(EP["tag"], C.SAFE_LEFT + 34, 273, 26, C.WHITE, 0.85, face=C.FONT_BOLD, align="left", tracking=2)
    SUB.draw(P, CHUNKS, t)
    P.rect(0, C.H - 8, C.W * t / TL.duration, C.H, C.CYAN, 0.8)


def draw_cover(P, t=0.0):
    P.background(1.0, accent=0.6)
    phone(P, 2.0, 1.0, 0.95, cy=980)
    P.text("¿POR QUÉ TU BANCO", 540, 380, 80, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("BLOQUEÓ TU CAFÉ?", 540, 475, 88, C.PINK, 1, face=C.FONT_BLACK, glow=0.5)
    P.pill("una alerta es una pista, no una prueba", 540, 1440, 32, C.CYAN)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "thump", 1.0), (0.02, "pop_low", 0.8), (0.0, "swell", 0.4),
            (c["ctx0"] - 0.3, "whoosh", 0.5), (c["ctx0"] + 1.7, "pop_low", 0.6), (c["pais"], "whoosh", 0.4),
            (c["nosig"], "pop", 0.5), (c["ej0"], "swell", 0.6), (c["una"], "pop", 0.7),
            (c["det0"] + 0.2, "riser", 0.3), (c["ident"] + 0.6, "pop_low", 0.7),
            (c["solo5"], "whoosh", 0.6), (c["veinte"], "thump", 0.7), (c["veinte"] + 0.1, "ding", 0.8),
            (c["exp_comun"], "whoosh", 0.5), (c["bay0"], "swell", 0.7), (c["bay_q"], "pop", 0.5),
            (c["frecuente"], "pop", 0.5), (c["confiable"], "pop", 0.5),
            (c["tb0"], "whoosh", 0.5), (c["despues"], "riser", 0.4), (c["unacinco"], "ding", 0.8),
            (c["cie0"], "whoosh_down", 0.5), (c["prueba"], "pop", 0.5), (c["bayes_end"], "ding", 0.7)]
    cues += [(c["cuatro"] + 0.25 * k, "tick", 0.7) for k in range(4)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["ej0"], "pulse": (c["bay0"], c["cie0"]),
            "quiet": [(c["solo5"] - 0.5, c["veinte"])]}
