"""Escenas — «¿Por qué la IA siempre dice 7?»

Chat (hook) → multitud que responde → muro de frases humanas que alimenta al modelo →
barras de probabilidad → «elige siempre la más alta» (7,7,7) → las barras se enrollan en una
RULETA que gira → 200 giros reales: bolitas que caen y arman el histograma → vuelve el chat (loop).
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint, vignette, vband, font
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic, smooth, in_cubic

TL = None; EP = {}; CHUNKS = []; CUE = {}; D = {}
AMBER = (1.0, 0.72, 0.3)
NUMCOL = [C.VIOLET] * 10
NUMCOL[6] = C.CYAN


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def fmtp(v):
    return f"{v * 100:.0f} %"


# =============================================================== chat
def bubble(P, x0, y, text, a, me, size=40, s=1.0, glow=0.0):
    if a <= 0: return
    f = font(size, C.FONT_SEMI)
    w = f.measureText(text) + 60; h = size + 44
    x = x0 if not me else x0 - w
    col = C.VIOLET if me else (0.16, 0.18, 0.26)
    with P.transform(0, 0, s, cx=x + w / 2, cy=y + h / 2):
        if glow > 0: P.rect(x - 10, y - 10, x + w + 10, y + h + 10, C.CYAN, 0.4 * glow * a, radius=40, blur=24)
        P.rect(x, y, x + w, y + h, col, a, radius=h / 2)
        P.text(text, x + w / 2, y + h / 2 + size * 0.36, size, C.WHITE, a, face=C.FONT_SEMI)


def chat(P, t, a, seven_glow=0.0):
    if a <= 0: return
    c = CUE
    with P.layer(a):
        P.rect(90, 470, 990, 1250, (0.08, 0.10, 0.16), 0.95, radius=40)
        P.circle(150, 530, 22, C.CYAN, 1); P.text("IA", 150, 539, 22, C.BG, 1, face=C.FONT_BLACK)
        P.text("Asistente", 190, 540, 30, C.WHITE, 1, face=C.FONT_BOLD, align="left")
        P.line(90, 590, 990, 590, C.WHITE, 0.08, w=2)
        q = "Dime un número del 1 al 10"
        n = int(clamp((t - 0.05) / 0.9) * len(q)) if t < 5 else len(q)
        bubble(P, 950, 640, q[:max(1, n)], 1, True, 38)
        # «escribiendo…» y luego el 7
        ty = prog(t, 1.0, 1.2) * (1 - prog(t, c["siete"] - 0.15, c["siete"]))
        if ty > 0:
            P.rect(130, 790, 290, 870, (0.16, 0.18, 0.26), ty, radius=40)
            for k in range(3):
                P.circle(170 + k * 40, 830 - 8 * max(0, math.sin(t * 9 - k)), 9, C.WHITE, ty)
        s7 = out_back(prog(t, c["siete"] - 0.1, c["siete"] + 0.35))
        if s7 > 0:
            bubble(P, 130, 790, "7", 1, False, 90, s=s7, glow=seven_glow)


# =============================================================== multitud
def multitud(P, t):
    c = CUE
    a = window(t, c["hum0"] - 0.1, c["piensa"] + 0.2, 0.4, 0.5)
    if a <= 0: return
    rng = np.random.default_rng(3)
    ans = rng.choice(10, 30, p=D["p"]) + 1
    with P.layer(a):
        for k in range(30):
            r_, col_ = divmod(k, 6)
            x = 180 + col_ * 144; y = 640 + r_ * 130
            ak = prog(t, c["hum0"] + 0.04 * k, c["hum0"] + 0.04 * k + 0.3)
            P.circle(x, y - 22, 18, (0.55, 0.6, 0.72), ak)
            P.rect(x - 26, y, x + 26, y + 40, (0.55, 0.6, 0.72), ak, radius=18)
            ab = prog(t, c["favorito"] - 1.2 + 0.03 * k, c["favorito"] - 0.9 + 0.03 * k)
            if ab > 0:
                n = ans[k]; hot = n == 7
                P.rect(x + 8, y - 86, x + 62, y - 42, C.CYAN if hot else (0.2, 0.22, 0.3), ab, radius=14)
                P.text(str(n), x + 35, y - 54, 30, C.BG if hot else C.WHITE, ab, face=C.FONT_BLACK)
        af = prog(t, c["favorito"] - 0.1, c["favorito"] + 0.3)
        P.text(f"«7»: {int((ans == 7).sum())} de 30", 540, 1290, 36, C.CYAN, af, face=C.FONT_BOLD)


# =============================================================== muro de textos humanos
FRASES = ["mi número de la suerte es el 7", "los 7 días de la semana", "piensa un número... el 7",
          "7 maravillas del mundo", "los 7 colores del arcoíris", "la camiseta número 7",
          "elijo el 3", "el 7 siempre me trae suerte", "7 notas musicales", "a las 7 en punto"]


def textos(P, t):
    c = CUE
    a = window(t, c["pre0"] - 0.1, c["prob0"] + 0.3, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        # caja del modelo
        am = prog(t, c["pre0"] + 0.2, c["pre0"] + 0.7)
        P.rect(330, 1010, 750, 1130, C.BG2, am, radius=26)
        P.rect(330, 1010, 750, 1130, C.CYAN, am, stroke=3, radius=26)
        P.text("modelo de lenguaje", 540, 1060, 34, C.WHITE, am, face=C.FONT_BOLD)
        P.text("¿qué palabra viene?", 540, 1100, 26, C.GRAY, am, face=C.FONT_MED)
        ap = prog(t, c["adivina"] - 0.4, c["adivina"] + 0.2)
        for k, fr in enumerate(FRASES):
            tk = c["adivina"] - 0.2 + 0.18 * k                      # aparecen en cascada
            tf = c["personas"] - 0.3 + 0.08 * k                      # y vuelan juntas al modelo
            ai = prog(t, tk, tk + 0.3)
            u = clamp((t - tf) / 0.9)
            if ai <= 0 or ap <= 0: continue
            x0 = 300 + (k % 2) * 480; y0 = 580 + (k // 2) * 78
            x = lerp(x0, 540, in_cubic(u)); y = lerp(y0, 1060, in_cubic(u))
            s_ = lerp(1, 0.3, in_cubic(u))
            al = ap * ai * (1 - prog(u, 0.8, 1.0))
            with P.transform(0, 0, s_, cx=x, cy=y):
                hot = "7" in fr
                P.text(fr, x, y, 27, C.CYAN if hot else C.WHITE, al, face=C.FONT_SEMI)
        P.text("textos escritos por personas", 540, 510, 30, C.GRAY, ap, face=C.FONT_MED)


# =============================================================== barras → ruleta → histograma
BX0, BX1, BY = 140, 940, 1150


def bar_geom(i):
    w = (BX1 - BX0) / 10
    return BX0 + i * w + w / 2, w * 0.7


def barras(P, t):
    c = CUE
    a = window(t, c["prob0"] - 0.1, c["rul0"] + 0.9, 0.4, 0.3)
    if a <= 0: return
    p = np.array(D["p"]); hmax = 520
    roll = prog(t, c["rul0"] + 0.1, c["rul0"] + 0.9, in_out_cubic)        # las barras se enrollan
    with P.layer(a * (1 - roll)):
        for i in range(10):
            x, w = bar_geom(i)
            g = prog(t, c["prob0"] + 0.06 * i, c["prob0"] + 0.06 * i + 0.6, out_back)
            h = hmax * p[i] / p.max() * g
            hot = i == 6 and t > c["ventaja"] - 0.2
            col = C.CYAN if hot else C.VIOLET
            if hot: P.rect(x - w / 2 - 8, BY - h - 8, x + w / 2 + 8, BY + 8, C.CYAN, 0.35, radius=12, blur=18)
            P.rect(x - w / 2, BY - h, x + w / 2, BY, col, 1, radius=10)
            P.text(str(i + 1), x, BY + 50, 36, C.WHITE, 1, face=C.FONT_BOLD)
            P.text(fmtp(p[i]), x, BY - h - 18, 24, C.WHITE, prog(t, c["prob0"] + 0.8, c["prob0"] + 1.2), face=C.FONT_SEMI)
        # greedy: flecha que siempre cae en el 7 → 7 7 7 7
        ag = window(t, c["gr0"] - 0.1, c["rul0"] + 0.2, 0.3, 0.3)
        if ag > 0:
            x, w = bar_geom(6)
            P.arrow(x, 520, x, BY - hmax - 70, AMBER, ag, w=8, head=28)
            P.text("siempre el más alto", x, 500, 30, AMBER, ag, face=C.FONT_BOLD)
            n7 = int(clamp((t - c["gr0"]) / 0.45) * 6)
            P.text("  ".join(["7"] * max(0, n7)), 540, 1290, 48, C.CYAN, ag, face=C.FONT_BLACK)


WX, WY, WR = 540, 860, 330


def ruleta(P, t):
    c = CUE
    a = window(t, c["rul0"] + 0.3, c["res0"] + 0.3, 0.6, 0.6)
    if a <= 0: return
    p = np.array(D["p"])
    # giro: aceleración y frenado; se detiene en la primera muestra real
    t_spin = c["giremos"]
    first = D["draws"][0] - 1
    starts = np.concatenate([[0], np.cumsum(p)[:-1]]) * 360
    target = 360 * 5 + (360 - (starts[first] + p[first] * 180)) - 90
    u = prog(t, c["rul0"] + 0.9, t_spin, out_cubic)
    rot = target * u + 900 * prog(t, t_spin, c["ganando"] - 0.2, lambda v: v)    # sigue girando con cada tirada
    sh = prog(t, t_spin - 0.3, t_spin + 0.5, in_out_cubic)
    WY_, WR_ = lerp(WY, 520, sh), lerp(WR, 160, sh)
    a *= 1 - prog(t, c["ganando"] - 0.4, c["ganando"])
    with P.layer(a):
        grow = out_back(prog(t, c["rul0"] + 0.3, c["rul0"] + 1.0))
        R = WR_ * grow; WYc = WY_
        rect = skia.Rect(WX - R, WYc - R, WX + R, WYc + R)
        for i in range(10):
            st = starts[i] + rot; sw = p[i] * 360
            pth = skia.Path(); pth.moveTo(WX, WYc); pth.arcTo(rect, st, sw, False); pth.close()
            P.c.drawPath(pth, paint(C.CYAN if i == 6 else lerp_c(C.VIOLET, (0.25, 0.22, 0.4), (i % 2) * 0.5), 1))
            P.c.drawPath(pth, paint(C.BG, 1, stroke=4))
            mid = math.radians(st + sw / 2)
            P.text(str(i + 1), WX + 0.72 * R * math.cos(mid), WYc + 0.72 * R * math.sin(mid) + 12,
                   34 if sw > 25 else 26, C.BG if i == 6 else C.WHITE, 1, face=C.FONT_BLACK)
        P.circle(WX, WYc, 40, C.BG2, 1); P.circle(WX, WYc, 40, C.WHITE, 1, stroke=4)
        # indicador arriba
        pth = skia.Path(); pth.moveTo(WX - 26, WYc - R - 46); pth.lineTo(WX + 26, WYc - R - 46); pth.lineTo(WX, WYc - R + 8); pth.close()
        P.c.drawPath(pth, paint(AMBER, 1))
        # perilla de temperatura
        at = prog(t, c["temp"] - 0.3, c["temp"] + 0.2) * (1 - prog(t, c["giremos"] - 0.2, c["giremos"] + 0.2))
        if at > 0:
            kx, ky = 900, 1250
            P.circle(kx, ky, 46, C.BG2, at); P.circle(kx, ky, 46, AMBER, at, stroke=5)
            ang = -2.4 + 1.6 * math.sin((t - c["temp"]) * 2.2) * 0.5 + 1.2
            P.line(kx, ky, kx + 32 * math.cos(ang), ky + 32 * math.sin(ang), AMBER, at, w=7)
            P.text("temperatura", kx - 70, ky + 10, 30, AMBER, at, face=C.FONT_BOLD, align="right")
            P.text("baja: casi siempre 7 · alta: más sorpresas", 540, 470, 28, AMBER, at, face=C.FONT_SEMI)


def histograma(P, t):
    c = CUE
    a = window(t, c["giremos"] - 0.1, c["cie0"] + 0.5, 0.4, 0.5)
    if a <= 0: return
    draws = D["draws"]; n = len(draws)
    t0 = c["giremos"] + 0.4; dur = (c["ganando"] - 0.2) - t0
    shown = int(clamp((t - t0) / dur) * n) if t > t0 else 0
    cnt = np.zeros(10, int)
    hy, r = 1230, 7.5
    with P.layer(a):
        P.line(BX0 - 20, hy + 14, BX1 + 20, hy + 14, C.DIM, 1, w=3)
        for i in range(10):
            x, _ = bar_geom(i)
            P.text(str(i + 1), x, hy + 56, 32, C.CYAN if i == 6 else C.WHITE, 1, face=C.FONT_BOLD)
        for k in range(min(n, shown + 3)):
            i = draws[k] - 1
            x, w = bar_geom(i)
            col_k = cnt[i]; cnt[i] += 1
            cols = 3
            row, cc = divmod(col_k, cols)
            tx = x + (cc - 1) * (2.2 * r); ty = hy - row * 2.2 * r
            tk = t0 + dur * k / n
            u = clamp((t - tk) / 0.35)
            if u <= 0: continue
            y = lerp(700, ty, out_cubic(u)) if u < 1 else ty
            P.circle(tx, y, r, C.CYAN if i == 6 else C.VIOLET, 1)
        ag = prog(t, c["ganando"] - 0.2, c["ganando"] + 0.3)
        if ag > 0:
            k7 = D["counts"][6]
            P.text(f"7: {k7} de 200", 540, hy - 70 * 2.2 * 0 - 600, 0, C.CYAN, 0)
            P.pill(f"el 7 salió {k7} de 200 veces", 540, 560, 44, C.CYAN, out_back(ag))
        P.text(f"giros: {min(shown, n)}", 860, 470, 30, C.WHITE, prog(t, t0, t0 + 0.3) * (1 - ag), face=C.FONT_SEMI)


def herencia(P, t):
    """Cierre: el 7 del chat y, detrás, la multitud que lo eligió."""
    c = CUE
    a = prog(t, c["heredo"] - 0.3, c["heredo"] + 0.4)
    if a <= 0: return
    with P.layer(a * 0.5):
        for k in range(14):
            x = 120 + k * 64; y = 1300
            P.circle(x, y - 22, 16, (0.55, 0.6, 0.72), 1)
            P.rect(x - 22, y, x + 22, y + 34, (0.55, 0.6, 0.72), 1, radius=16)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D
    TL, EP, D = tl, episode, data
    c = {}
    c["siete"] = T("hook", "siete"); c["coinc"] = T("hook", "Coincidencia")
    c["hum0"] = T("humanos"); c["favorito"] = T("humanos", "favorito")
    c["pre0"] = T("predice"); c["piensa"] = T("predice", "piensa"); c["adivina"] = T("predice", "Adivina")
    c["personas"] = T("predice", "personas")
    c["prob0"] = T("probas"); c["ventaja"] = T("probas", "ventaja")
    c["gr0"] = T("greedy"); c["rul0"] = T("ruleta"); c["temp"] = T("ruleta", "temperatura")
    c["giremos"] = T("ruleta", "Giremos")
    c["res0"] = T("resultado"); c["ganando"] = T("resultado", "ganando")
    c["cie0"] = T("cierre"); c["heredo"] = T("cierre", "heredó")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    P.background(t, accent=0.3 * pulse(t, c["siete"], 1.4) + 0.3 * window(t, c["ganando"], c["cie0"], 0.4, 0.4))
    a_chat = (1 - prog(t, c["hum0"] - 0.3, c["hum0"] + 0.2)) + prog(t, c["cie0"] - 0.1, c["cie0"] + 0.4)
    chat(P, t if t < c["cie0"] - 0.2 else 10, clamp(a_chat), seven_glow=pulse(t, c["coinc"], 1.0) + pulse(t, c["heredo"], 1.2))
    multitud(P, t)
    textos(P, t)
    barras(P, t)
    ruleta(P, t)
    histograma(P, t)
    herencia(P, t)
    vignette(P, 0.45)
    vband(P, 1250, C.H, 0.0, 0.85)
    SUB.draw(P, CHUNKS, t)


def draw_cover(P, t=0.0):
    P.background(1.0, accent=0.6)
    P.text("¿POR QUÉ LA IA", 540, 360, 96, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("SIEMPRE DICE", 540, 465, 96, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("7", 540, 900, 520, C.CYAN, 1, face=C.FONT_BLACK, glow=0.8)
    P.text("?", 830, 760, 200, C.WHITE, 1, face=C.FONT_BLACK)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.4)] + [(0.05 + 0.04 * k, "tick", 0.25) for k in range(0, 24, 3)]
    cues += [(c["siete"], "pop", 0.8), (c["siete"] + 0.05, "ding", 0.6), (c["coinc"], "riser", 0.4),
             (c["hum0"] - 0.2, "whoosh", 0.5), (c["favorito"], "ding", 0.5), (c["pre0"], "whoosh", 0.5),
             (c["personas"], "pop", 0.5), (c["prob0"], "whoosh", 0.5), (c["ventaja"], "pop", 0.6),
             (c["gr0"], "thump", 0.5), (c["rul0"], "whoosh", 0.6), (c["temp"], "pop", 0.5),
             (c["giremos"], "riser", 0.5), (c["ganando"], "ding", 0.8), (c["cie0"] - 0.1, "whoosh_down", 0.5),
             (c["heredo"], "swell", 0.7)]
    t0 = c["giremos"] + 0.4; dur = (c["ganando"] - 0.2) - t0
    cues += [(t0 + dur * k / 40, "tick", 0.3) for k in range(40)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["prob0"], "pulse": (c["rul0"], c["cie0"]), "quiet": [(c["coinc"], c["hum0"])]}
