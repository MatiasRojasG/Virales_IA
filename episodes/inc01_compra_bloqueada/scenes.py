"""Escenas — «¿Por qué tu banco bloqueó tu café?»

Hilo visual continuo: el celular con la compra bloqueada se convierte en UN punto, que se
multiplica en 1.000 compras. Esos mismos puntos se reordenan para mostrar las alarmas, la
comparación de grupos, la fracción de Bayes y la segunda señal. Un medidor persistente arriba
("¿qué tan probable es que fuera fraude?") registra la respuesta: parece casi seguro → 1 de 6 → 8 de 10.
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
from reelforge.mathtex import Equation

TL = None; EP = {}; CHUNKS = []; CUE = {}; D = {}

N = 1000
NFRAUD = 10
NFALSE = 49
GRAY = (0.62, 0.66, 0.74)


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def fmt(v, dec=0):
    return f"{v:.{dec}f}".replace(".", ",")


# =============================================================== layouts de los 1.000 puntos
def grid_layout():
    cols, rows = 40, 25
    xs = np.linspace(84, 996, cols); ys = np.linspace(610, 1170, rows)
    X, Y = np.meshgrid(xs, ys)
    return np.stack([X.ravel(), Y.ravel()], 1)


def cluster_layout(idx_order, cx=540, cy=860, cols=10, sp=56):
    """Posiciones para un subconjunto ordenado (resto: en su lugar de la grilla)."""
    pos = D["grid"].copy()
    n = len(idx_order)
    rows = math.ceil(n / cols)
    for k, i in enumerate(idx_order):
        r, c = divmod(k, cols)
        pos[i] = (cx + (c - (cols - 1) / 2) * sp, cy + (r - (rows - 1) / 2) * sp)
    return pos


def compare_layout():
    pos = np.zeros((N, 2))
    for k, i in enumerate(D["fraud"]):
        r, c = divmod(k, 2)
        pos[i] = (200 + c * 44, 760 + r * 44)
    normal = D["normal"]
    cols = 33
    for k, i in enumerate(normal):
        r, c = divmod(k, cols)
        pos[i] = (420 + c * 17, 640 + r * 17)
    return pos


def fraction_layout():
    pos = D["grid"].copy()
    alarms = list(D["fraud"]) + list(D["false"])
    for k, i in enumerate(alarms):
        r, c = divmod(k, 30)
        pos[i] = (540 + (c - 14.5) * 30, 760 + r * 32)
    return pos


def ease_morph(a, b, t, t0, dur=1.3, stagger=0.5, seed=0):
    """Interpola cada punto con un pequeño desfase propio (movimiento orgánico)."""
    if t <= t0: return a
    rng = D["phase"]
    u = np.clip((t - t0 - rng * stagger) / dur, 0, 1)
    u = u * u * (3 - 2 * u)
    return a + (b - a) * u[:, None]


# =============================================================== escenas
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


def meter(P, t):
    """Medidor persistente: ¿qué tan probable es que fuera fraude?"""
    c = CUE
    a = window(t, c["m_on"] - 0.3, c["cierre0"] + 0.5, 0.4, 0.5)
    if a <= 0: return
    x0, x1, y = 140, 940, 470
    # valor: parece (~97 %) → realidad (1/6) → con 2 señales (≈ 80 %)
    v = 0.97 * out_cubic(prog(t, c["m_on"], c["m_on"] + 0.9))
    if t > c["m_real"]:
        v = lerp(0.97, D["p1"], spring((t - c["m_real"]) * 1.2, freq=7, damp=4.5))
    if t > c["m_two"]:
        v = lerp(D["p1"], D["p2"], spring((t - c["m_two"]) * 1.2, freq=7, damp=4.5))
    wob = 0.03 * math.sin(t * 9) * window(t, c["dif0"], c["sim0"], 0.3, 0.3)
    v = clamp(v + wob)
    with P.layer(a):
        P.text("¿Qué tan probable es que fuera fraude?", 540, 400, 34, C.WHITE, 1, face=C.FONT_SEMI)
        P.rect(x0, y - 9, x1, y + 9, C.DIM, 1, radius=9)
        col = C.PINK if t < c["m_real"] else (C.CYAN if t > c["m_two"] else C.VIOLET)
        P.rect(x0, y - 9, x0 + (x1 - x0) * v, y + 9, col, 1, radius=9)
        P.glow_circle(x0 + (x1 - x0) * v, y, 15, col, 1)
        for k, lab in ((0, "0"), (0.5, "50 %"), (1, "100 %")):
            P.text(lab, lerp(x0, x1, k), y + 46, 24, C.GRAY, 1, face=C.FONT_MED)
        if t < c["m_real"]:
            lab = "lo que parece: casi seguro"
        elif t < c["m_two"]:
            lab = "en realidad: 1 de cada 6  (≈ 17 %)"
        else:
            lab = "con dos señales: ≈ 8 de cada 10"
        P.text(lab, lerp(x0, x1, clamp(v, 0.22, 0.78)), y - 32, 28, col, 1, face=C.FONT_BOLD)


def detector(P, t):
    """Intuición: 99 de 100 fraudes atrapados; 5 de 100 normales marcados."""
    c = CUE
    a = window(t, c["int0"] - 0.1, c["sim0"] + 0.1, 0.4, 0.5)
    if a <= 0: return
    with P.layer(a):
        for blk, (cx, title, col, nhit, t_scan) in enumerate(
                [(300, "100 fraudes", C.VIOLET, 99, c["d99"]), (780, "100 compras normales", GRAY, 5, c["d5"])]):
            ab = prog(t, t_scan - 0.5, t_scan - 0.1)
            if ab <= 0: continue
            P.text(title, cx, 650, 32, C.WHITE, ab, face=C.FONT_SEMI)
            hits = D["hit99"] if nhit == 99 else D["hit5"]
            for k in range(100):
                r, cc = divmod(k, 10)
                x, y = cx + (cc - 4.5) * 34, 720 + r * 34
                P.circle(x, y, 11, col, ab)
                if k in hits:
                    u = prog(t, t_scan + 0.012 * k, t_scan + 0.012 * k + 0.2)
                    if u > 0:
                        P.circle(x, y, 11 + 5 * u, C.PINK, ab * u, stroke=3.5)
            u = prog(t, t_scan + 1.2, t_scan + 1.6)
            txt = "atrapa 99" if nhit == 99 else "se equivoca con 5"
            P.pill(txt, cx, 1100, 32, C.PINK, ab * u)


def dots(P, t):
    c = CUE
    a = window(t, c["sim0"] - 0.2, c["usos0"] + 0.2, 0.3, 0.5)
    if a <= 0: return
    grid = D["grid"]
    # nacimiento: los 1.000 puntos brotan desde el centro (donde se encogió el celular)
    born = np.clip((t - c["sim0"] - D["phase"] * 0.9) / 0.6, 0, 1)
    born = born * born * (3 - 2 * born)
    center = np.array([540, 900.0])
    pos = center + (grid - center) * born[:, None]
    pos = ease_morph(pos, D["L_cluster"], t, c["solo_al"], 1.2, 0.6)
    pos = ease_morph(pos, D["L_compare"], t, c["porq0"], 1.3, 0.6)
    pos = ease_morph(pos, D["L_frac"], t, c["bay0"], 1.3, 0.6)
    pos = ease_morph(pos, D["L_cluster"], t, c["sol0"], 1.2, 0.5)
    is_fraud, is_false = D["is_fraud"], D["is_false"]
    is_alarm = is_fraud | is_false
    # transparencias por fase
    alpha = np.ones(N)
    dim_others = window(t, c["solo_al"], c["porq0"] + 0.4, 0.6, 0.6) + window(t, c["bay0"], c["usos0"], 0.6, 0.3)
    alpha[~is_alarm] = 1 - 0.94 * clamp(dim_others)
    sec = D["second"]
    if t > c["sol_sig"] + 1.0:
        f2 = prog(t, c["sol_sig"] + 1.0, c["sol_sig"] + 1.8)
        alpha[is_false & ~sec] *= 1 - 0.85 * f2
    radius = np.full(N, 8.0)
    big = window(t, c["solo_al"] + 0.3, c["porq0"] + 0.3, 0.8, 0.6) + window(t, c["sol0"], c["usos0"], 0.8, 0.3)
    radius[is_alarm] = 8 + 10 * clamp(big)
    small = window(t, c["porq0"] + 0.3, c["bay0"] + 0.4, 0.8, 0.6)
    radius[~is_alarm & ~is_fraud] -= 2.5 * small
    radius[is_alarm] = np.maximum(radius[is_alarm], 8 + 4 * window(t, c["bay0"] + 0.3, c["sol0"], 0.8, 0.5))
    # color: fraudes se revelan violeta
    fr_on = prog(t, c["diez"] - 0.1, c["diez"] + 0.5)
    t_catch, t_false = c["atrapa"], c["equivoca"]
    with P.layer(a):
        for i in range(N):
            if born[i] <= 0: continue
            x, y = pos[i]; r = radius[i]
            col = lerp_c(GRAY, C.VIOLET, fr_on) if is_fraud[i] else GRAY
            P.circle(x, y, r, col, alpha[i] * born[i])
            # primera alarma
            if is_fraud[i]:
                ta = t_catch + 0.12 * D["rank"][i]
            elif is_false[i]:
                ta = t_false + 0.035 * D["rank"][i]
            else:
                continue
            u = prog(t, ta, ta + 0.25)
            if u > 0:
                P.circle(x, y, r + 4 + 6 * (1 - u), C.PINK, alpha[i] * u, stroke=3.5)
            # segunda señal
            if t > c["sol_sig"] and (is_fraud[i] or sec[i]):
                u2 = prog(t, c["sol_sig"] + 0.05 * D["rank"][i], c["sol_sig"] + 0.05 * D["rank"][i] + 0.3)
                if u2 > 0:
                    ra = alpha[i] * u2 * (0.5 if D["half"][i] else 1)
                    P.circle(x, y, r + 11, C.CYAN, ra, stroke=3.5)
        # contadores y rótulos
        a_cnt = window(t, c["diez"], c["solo_al"] + 0.2, 0.3, 0.3)
        n_al = 0
        if t > t_catch: n_al += min(NFRAUD, int((t - t_catch) / 0.12) + 1)
        if t > t_false: n_al += min(NFALSE, int((t - t_false) / 0.035) + 1)
        P.text(f"fraudes: {NFRAUD if fr_on > 0 else 0}", 300, 570, 34, C.VIOLET, a_cnt, face=C.FONT_BOLD)
        P.text(f"alarmas: {n_al}", 780, 570, 34, C.PINK, a_cnt * prog(t, t_catch - 0.2, t_catch), face=C.FONT_BOLD)
        P.text("1.000 compras", 540, 570, 34, C.WHITE, window(t, c["sim0"] + 0.3, c["diez"], 0.3, 0.3), face=C.FONT_BOLD)
        # descubrimiento
        ad = window(t, c["solo_al"] + 0.6, c["porq0"] + 0.2, 0.4, 0.4)
        if ad > 0:
            P.text("59 alarmas", 540, 600, 40, C.PINK, ad, face=C.FONT_BOLD)
            av = prog(t, c["diez_eran"] - 0.2, c["diez_eran"] + 0.3) * ad
            P.text("10 eran fraude", 540, 1080, 40, C.VIOLET, av, face=C.FONT_BOLD)
            a6 = prog(t, c["m_real"] - 0.2, c["m_real"] + 0.3) * ad
            P.text("1 de cada 6", 540, 1180, 92, C.CYAN, out_back(a6), face=C.FONT_BLACK, glow=0.5)
        # comparación de grupos
        ap = window(t, c["porq0"] + 0.4, c["bay0"] + 0.2, 0.4, 0.4)
        if ap > 0:
            P.text("10 fraudes", 222, 700, 30, C.VIOLET, ap, face=C.FONT_BOLD)
            P.text("990 compras normales", 694, 610, 30, C.WHITE, ap, face=C.FONT_BOLD)
            ab = prog(t, c["error"] - 0.2, c["error"] + 0.8, out_cubic) * ap
            P.text("alarmas reales", 140, 1200, 28, C.VIOLET, ab, face=C.FONT_SEMI, align="left")
            P.rect(380, 1185, 380 + 10 * 9 * ab, 1207, C.VIOLET, ap, radius=11)
            P.text("10", 380 + 90 * ab + 16, 1206, 28, C.VIOLET, ab, face=C.FONT_BOLD, align="left")
            P.text("falsas alarmas", 140, 1245, 28, C.PINK, ab, face=C.FONT_SEMI, align="left")
            P.rect(380, 1230, 380 + 49 * 9 * ab, 1252, C.PINK, ap, radius=11)
            P.text("49", 380 + 441 * ab + 16, 1251, 28, C.PINK, ab, face=C.FONT_BOLD, align="left")
        # fracción con los mismos puntos: copias de los 10 fraudes suben al numerador
        af = window(t, c["bay0"] + 0.5, c["sol0"] + 0.2, 0.5, 0.4)
        if af > 0:
            uq = prog(t, c["arriba"] - 0.3, c["arriba"] + 0.6, in_out_cubic)
            for k, i in enumerate(D["fraud"]):
                x0_, y0_ = pos[i]
                x1_, y1_ = 540 + (k - 4.5) * 40, 640
                uk = clamp(uq * 1.4 - k * 0.04)
                x_, y_ = lerp(x0_, x1_, uk), lerp(y0_, y1_, uk) - 60 * math.sin(math.pi * uk)
                P.circle(x_, y_, radius[i], C.VIOLET, af * prog(t, c["arriba"] - 0.3, c["arriba"]))
            P.line(80, 702, 1000, 702, C.WHITE, af * prog(t, c["bay0"] + 0.9, c["bay0"] + 1.4), w=4)
            P.text("alarmas que sí son fraude", 540, 590, 30, C.VIOLET, af * prog(t, c["arriba"] - 0.2, c["arriba"] + 0.2), face=C.FONT_SEMI)
            P.text("todas las alarmas", 540, 850, 30, C.PINK, af * prog(t, c["abajo"] - 0.2, c["abajo"] + 0.2), face=C.FONT_SEMI)
        # segunda señal
        as_ = window(t, c["sol_sig"] + 1.6, c["usos0"] + 0.2, 0.4, 0.4)
        if as_ > 0:
            P.text("vuelven a sonar: 10 fraudes y, en promedio, 2,5 normales", 540, 1150, 28, C.WHITE, as_, face=C.FONT_MED)
            P.text("10 de ≈ 12,5  →  ≈ 8 de cada 10", 540, 1210, 40, C.CYAN, as_, face=C.FONT_BOLD)
        a_ind = window(t, c["sol_sig"] - 0.2, c["usos0"] + 0.2, 0.4, 0.4)
        P.text("(suponiendo que ambas señales se equivocan de forma independiente)", 540, 1258, 24, C.GRAY,
               a_ind, face=C.FONT_MED)


EQ = {}


def bayes_formula(P, t):
    c = CUE
    a = window(t, c["tasa"] - 0.6, c["sol0"] + 0.1, 0.5, 0.4)
    if a <= 0: return
    if not EQ:
        EQ["L"] = Equation([r"P(\mathrm{fraude} \mid \mathrm{alarma})", "="])
        EQ["N"] = Equation([r"P(\mathrm{alarma} \mid \mathrm{fraude})", r"\times", (r"P(\mathrm{fraude})", C.CYAN)])
        EQ["D"] = Equation([(r"P(\mathrm{alarma})", C.PINK)])
    with P.layer(a):
        P.rect(70, 930, 1010, 1240, C.BG2, 0.95, radius=28)
        y_n, y_d, y_l = 1010, 1110, 1060
        EQ["L"].draw(P, 300, y_l, size=46)
        EQ["N"].draw(P, 735, y_n, size=44, glow={2: pulse(t, c["tasa"], 1.2) + 0.3})
        P.line(475, y_l, 995, y_l, C.WHITE, 1, w=3)
        EQ["D"].draw(P, 735, y_d, size=44)
        P.text("0,99 × 0,01  /  0,0594  ≈  0,17", 540, 1205, 32, C.WHITE, prog(t, c["tasa"] + 0.8, c["tasa"] + 1.3), face=C.FONT_BOLD)
        at = prog(t, c["tasa"] - 0.2, c["tasa"] + 0.3)
        x, y = EQ["N"].part_center(2, 735, y_n, 44)
        P.pill("tasa base: 10 de cada 1.000", x - 60, 960, 26, C.CYAN, out_back(at))


def usos(P, t):
    c = CUE
    a = window(t, c["usos0"] - 0.1, c["cierre0"] + 0.3, 0.5, 0.5)
    if a <= 0: return
    with P.layer(a):
        for k, (cy, ts, title, sub) in enumerate([(760, c["u_med"], "Exámenes médicos", "positivo no siempre = enfermo"),
                                                  (1060, c["u_fab"], "Alarmas de fábrica", "evento raro → muchas falsas alarmas")]):
            ak = prog(t, ts - 0.3, ts + 0.2)
            if ak <= 0: continue
            s = 0.85 + 0.15 * out_back(prog(t, ts - 0.3, ts + 0.3))
            with P.transform(0, 0, s, cx=270, cy=cy):
                P.rect(150, cy - 120, 390, cy + 120, C.BG2, ak, radius=28)
                P.rect(150, cy - 120, 390, cy + 120, C.WHITE, 0.15 * ak, stroke=2, radius=28)
                if k == 0:   # tubo de ensayo con un "+"
                    P.rect(245, cy - 80, 295, cy + 70, C.WHITE, ak, stroke=5, radius=24)
                    P.rect(250, cy + 5, 290, cy + 65, C.CYAN, 0.8 * ak, radius=20)
                    P.text("+", 335, cy - 40, 64, C.PINK, ak, face=C.FONT_BLACK)
                else:        # campana de alarma
                    P.c.drawArc(skia.Rect(210, cy - 70, 330, cy + 50), 180, 180, False, paint(C.PINK, ak, stroke=9))
                    P.line(210, cy - 10, 210, cy + 40, C.PINK, ak, w=9)
                    P.line(330, cy - 10, 330, cy + 40, C.PINK, ak, w=9)
                    P.line(190, cy + 42, 350, cy + 42, C.PINK, ak, w=9)
                    P.circle(270, cy + 62, 12, C.PINK, ak)
            P.text(title, 450, cy - 6, 40, C.WHITE, ak, face=C.FONT_BOLD, align="left")
            P.text(sub, 450, cy + 40, 28, C.GRAY, ak, face=C.FONT_MED, align="left")
        P.text("el mismo cálculo, en otros contextos", 540, 580, 30, C.GRAY, prog(t, c["usos0"], c["usos0"] + 0.5), face=C.FONT_MED)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D
    TL, EP = tl, episode
    rng = np.random.default_rng(11)
    fraud = rng.choice(N, NFRAUD, replace=False)
    normal = np.setdiff1d(np.arange(N), fraud)
    false = rng.choice(normal, NFALSE, replace=False)
    D = {"fraud": fraud, "normal": normal, "false": false}
    D["is_fraud"] = np.isin(np.arange(N), fraud)
    D["is_false"] = np.isin(np.arange(N), false)
    D["phase"] = rng.random(N)
    rank = np.zeros(N)
    rank[fraud] = np.arange(NFRAUD); rank[false] = np.arange(NFALSE)
    D["rank"] = rank
    # segunda señal: en promedio 2,5 de las 49 → 2 llenas + 1 a media opacidad
    sec_idx = false[:3]
    D["second"] = np.isin(np.arange(N), sec_idx)
    D["half"] = np.isin(np.arange(N), sec_idx[2:])
    D["hit99"] = set(range(100)) - {57}
    D["hit5"] = {7, 23, 48, 66, 91}
    D["p1"] = 0.99 * 0.01 / (0.99 * 0.01 + 0.05 * 0.99)
    D["p2"] = 0.99 * D["p1"] / (0.99 * D["p1"] + 0.05 * (1 - D["p1"]))
    D["grid"] = grid_layout()
    alarms = list(fraud) + list(false)
    D["L_cluster"] = cluster_layout(alarms, cx=540, cy=830, cols=10, sp=50)
    D["L_compare"] = compare_layout()
    D["L_frac"] = fraction_layout()

    c = {}
    c["int0"] = T("intuicion"); c["d99"] = T("intuicion", "99"); c["d5"] = T("intuicion", "5")
    c["m_on"] = T("intuicion", "fraude", 1)
    c["dif0"] = T("dificultad"); c["comun"] = T("dificultad", "común")
    c["sim0"] = T("simulacion"); c["diez"] = T("simulacion", "diez")
    c["atrapa"] = T("simulacion", "atrapa"); c["equivoca"] = T("simulacion", "49")
    c["solo_al"] = T("descubrir", "alarmas"); c["diez_eran"] = T("descubrir", "diez")
    c["m_real"] = T("descubrir", "Una")
    c["porq0"] = T("porque"); c["error"] = T("porque", "error")
    c["bay0"] = T("bayes"); c["arriba"] = T("bayes", "Arriba"); c["abajo"] = T("bayes", "Abajo")
    c["tasa"] = T("bayes", "tasa")
    c["sol0"] = T("solucion"); c["sol_sig"] = T("solucion", "segunda"); c["m_two"] = T("solucion", "ocho")
    c["usos0"] = T("usos"); c["u_med"] = T("usos", "examen"); c["u_fab"] = T("usos", "alarmas")
    c["cierre0"] = T("cierre"); c["raro"] = T("cierre", "raro")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    P.background(t, accent=0.25 * window(t, c["m_real"], c["porq0"], 0.5, 0.5))
    # celular: abre el video (cuadro 0) y vuelve al final (empalme)
    a_ph = (1 - prog(t, c["int0"] - 0.3, c["int0"] + 0.3)) + prog(t, c["cierre0"] - 0.2, c["cierre0"] + 0.5)
    s_ph = lerp(1.0, 0.85, prog(t, c["int0"] - 0.3, c["int0"] + 0.3)) if t < c["cierre0"] - 0.2 \
        else lerp(0.9, 1.0, out_cubic(prog(t, c["cierre0"] - 0.2, c["cierre0"] + 0.6)))
    phone(P, t, clamp(a_ph), s_ph * 1.12, cy=960)
    headline(P, clamp(1 - prog(t, c["int0"] - 0.4, c["int0"]) + prog(t, c["cierre0"] - 0.1, c["cierre0"] + 0.4)),
             1.0 + 0.1 * (1 - out_back(prog(t, 0, 0.35))))
    # el celular se encoge hasta ser UN punto antes de multiplicarse
    ap = window(t, c["dif0"] + 0.2, c["sim0"] + 0.3, 0.4, 0.3)
    if ap > 0:
        P.text("?", 540, 920, 230, C.CYAN, out_back(prog(t, c["comun"] - 0.2, c["comun"] + 0.3)) * ap, face=C.FONT_BLACK, glow=0.8)
        P.text("¿qué tan común es el fraude?", 540, 1060, 36, C.WHITE, prog(t, c["comun"], c["comun"] + 0.4) * ap, face=C.FONT_SEMI)
    detector(P, t)
    dots(P, t)
    bayes_formula(P, t)
    usos(P, t)
    meter(P, t)
    ad = window(t, c["int0"] + 0.4, c["usos0"], 0.4, 0.4)
    P.text("Ejemplo ilustrativo con números redondos (no son datos de un banco real)", 540, 1290, 23, C.GRAY,
           ad * 0.9, face=C.FONT_MED)
    vignette(P, 0.45)
    vband(P, 1230, C.H, 0.0, 0.85)
    P.circle(C.SAFE_LEFT + 10, 262, 8, C.CYAN, 1)
    P.text(EP["tag"], C.SAFE_LEFT + 34, 273, 26, C.WHITE, 0.85, face=C.FONT_BOLD, align="left", tracking=2)
    SUB.draw(P, CHUNKS, t)
    P.rect(0, C.H - 8, C.W * t / TL.duration, C.H, C.CYAN, 0.8)


def draw_cover(P, t=0.0):
    P.background(1.0, accent=0.6)
    phone(P, 2.0, 1.0, 0.95, cy=980)
    P.text("¿POR QUÉ TU BANCO", 540, 380, 80, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("BLOQUEÓ TU CAFÉ?", 540, 475, 88, C.PINK, 1, face=C.FONT_BLACK, glow=0.5)
    P.pill("spoiler: no es que el detector sea malo", 540, 1440, 32, C.CYAN)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "thump", 1.0), (0.02, "pop_low", 0.8), (0.0, "swell", 0.4),
            (c["int0"] - 0.3, "whoosh", 0.5), (c["d99"], "riser", 0.3), (c["m_on"], "ding", 0.5),
            (c["dif0"], "whoosh_down", 0.5), (c["comun"], "pop_low", 0.6),
            (c["sim0"], "swell", 0.6), (c["diez"], "pop", 0.6),
            (c["solo_al"], "whoosh", 0.6), (c["m_real"], "thump", 0.7), (c["m_real"] + 0.1, "ding", 0.7),
            (c["porq0"], "whoosh", 0.5), (c["bay0"], "whoosh", 0.5), (c["tasa"], "pop", 0.6),
            (c["sol0"], "whoosh", 0.5), (c["sol_sig"], "riser", 0.5), (c["m_two"], "ding", 0.8),
            (c["usos0"], "whoosh", 0.5), (c["u_med"], "pop", 0.5), (c["u_fab"], "pop", 0.5),
            (c["cierre0"], "whoosh_down", 0.5), (c["raro"], "ding", 0.7)]
    cues += [(c["atrapa"] + 0.12 * k, "tick", 0.6) for k in range(NFRAUD)]
    cues += [(c["equivoca"] + 0.035 * k, "tick", 0.35) for k in range(0, NFALSE, 2)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["sim0"], "pulse": (c["sol0"], c["usos0"]),
            "quiet": [(c["dif0"] - 0.2, c["sim0"])]}
