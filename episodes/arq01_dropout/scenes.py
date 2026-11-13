"""Escenas — «¿Por qué apagar neuronas hace más lista a una red?»

Sin títulos ni banners: el video abre con la prueba de práctica perfecta (hook) y cierra con
la prueba real aprobada (empalme). Toda la parte técnica ocurre sobre UN mapa (humedad × presión)
y UNA red dibujada; las fronteras son las de las redes realmente entrenadas en experiment.py.
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint, vignette, vband, image, LINEAR, CUBIC
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic, smooth

TL = None; EP = {}; CHUNKS = []; CUE = {}; D = {}
RAIN, DRY = C.CYAN, C.VIOLET
BOX = (130, 560, 950, 1220)          # mapa en pantalla


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def fmtp(v):
    return f"{v * 100:.0f} %"


# =============================================================== prueba (hook y cierre)
def exam(P, x, y, a, s, marks, score, score_col, label):
    if a <= 0: return
    with P.layer(a):
        with P.transform(0, 0, s, cx=x, cy=y):
            P.rect(x - 190, y - 250, x + 190, y + 250, (0, 0, 0), 0.5, radius=22, blur=20)
            P.rect(x - 190, y - 250, x + 190, y + 250, C.PAPER, 1, radius=22)
            P.text(label, x, y - 195, 30, C.INK, 1, face=C.FONT_BOLD)
            for k, ok in enumerate(marks):
                yy = y - 130 + k * 62
                P.line(x - 140, yy, x + 60, yy, (0.75, 0.78, 0.84), 1, w=10)
                if ok is None: continue
                if ok:
                    P.line(x + 95, yy, x + 110, yy + 15, C.CYAN, 1, w=8); P.line(x + 110, yy + 15, x + 140, yy - 18, C.CYAN, 1, w=8)
                else:
                    P.line(x + 98, yy - 14, x + 132, yy + 16, C.PINK, 1, w=8); P.line(x + 132, yy - 14, x + 98, yy + 16, C.PINK, 1, w=8)
            P.text(score, x, y + 215, 64, score_col, 1, face=C.FONT_BLACK)


def pruebas(P, t):
    c = CUE
    a = 1 - prog(t, c["pu0"] - 0.3, c["pu0"] + 0.4)
    a_end = prog(t, c["cie0"], c["cie0"] + 0.5)
    if a > 0:
        # práctica: perfecta desde el cuadro 0
        n_ok = 6
        marks = [True if t >= 0.08 * k else None for k in range(n_ok)]
        mvp = prog(t, c["real"] - 0.5, c["real"] + 0.3, in_out_cubic)
        exam(P, lerp(540, 300, mvp), 860, a, lerp(1.0, 0.85, mvp), marks,
             "10 / 10" if t > 0.5 else "", C.CYAN, "práctica")
        ar = prog(t, c["real"] - 0.4, c["real"] + 0.2)
        if ar > 0:
            mr = [k in (1, 4) if t > c["reprueba"] - 0.2 + 0.1 * k else None for k in range(6)]
            exam(P, 780, 860, a * ar, 0.85, mr, "3 / 10" if t > c["reprueba"] + 0.4 else "", C.PINK, "prueba real")
    if a_end > 0:
        mr = [True if t > c["entender"] - 0.3 + 0.1 * k else None for k in range(6)]
        exam(P, 540, 860, a_end, 1.0, mr, "8 / 10" if t > c["entender"] + 0.4 else "", C.CYAN, "prueba real")


# =============================================================== la red dibujada
LAYERS = [2, 6, 6, 1]


def net_pos(cx=540, cy=880, w=720, h=520):
    pos = []
    for li, n in enumerate(LAYERS):
        x = cx - w / 2 + w * li / (len(LAYERS) - 1)
        pos.append([(x, cy + (k - (n - 1) / 2) * (h / 6)) for k in range(n)])
    return pos


def red(P, t):
    c = CUE
    a = window(t, c["pu0"] - 0.1, c["da0"] + 0.3, 0.5, 0.4) + window(t, c["por0"] - 0.1, c["res0"] + 0.3, 0.5, 0.5)
    a = clamp(a)
    if a <= 0: return
    pos = net_pos()
    # ¿qué neuronas están apagadas?
    off = set()
    if c["apagar"] - 0.2 < t < c["da0"]:
        off = {(1, 1), (1, 4), (2, 2), (2, 5)}
    if c["dr_apag"] < t < c["dr_util"] + 0.2:
        k = int((t - c["dr_apag"]) * 4)                 # cada «paso» cambia el sorteo
        rng = np.random.default_rng(k)
        off = {(li, j) for li in (1, 2) for j in range(6) if rng.random() < 0.5}
    star = (1, 2)
    t_star = c["especial"]
    a_star = window(t, t_star - 0.3, c["dr0"] + 0.2, 0.4, 0.4)
    lean = window(t, c["apoyan"] - 0.3, c["dr0"] + 0.2, 0.4, 0.4)
    useful = prog(t, c["dr_util"] - 0.2, c["dr_util"] + 0.6) * (1 - prog(t, c["res0"] - 0.3, c["res0"]))
    with P.layer(a):
        for li in range(len(LAYERS) - 1):
            for i, (x0, y0) in enumerate(pos[li]):
                for j, (x1, y1) in enumerate(pos[li + 1]):
                    dead = (li, i) in off or (li + 1, j) in off
                    w = 2.0; al = 0.35
                    if lean > 0 and (li, i) == star:
                        w = 2 + 6 * lean; al = 0.35 + 0.5 * lean
                    P.line(x0, y0, x1, y1, C.VIOLET, 0.08 if dead else al, w=w)
        for li, layer in enumerate(pos):
            for j, (x, y) in enumerate(layer):
                dead = (li, j) in off
                r = 34 if li in (1, 2) else 30
                col = C.CYAN if li in (1, 2) else C.WHITE
                if (li, j) == star and a_star > 0:
                    P.glow_circle(x, y, r + 6 * pulse(t, t_star, 0.8), C.PINK, a_star, spread=1.8)
                g = useful if li in (1, 2) and not dead else 0
                P.circle(x, y, r, C.BG2, 1)
                if g > 0: P.glow_circle(x, y, r * 0.75, C.CYAN, 0.8 * g, spread=1.6)
                P.circle(x, y, r, (0.25, 0.28, 0.36) if dead else col, 1, stroke=4)
                if dead:
                    P.line(x - 16, y - 16, x + 16, y + 16, C.PINK, 1, w=5); P.line(x + 16, y - 16, x - 16, y + 16, C.PINK, 1, w=5)
        P.text("humedad", pos[0][0][0], pos[0][0][1] - 50, 24, C.GRAY, 1, face=C.FONT_MED)
        P.text("presión", pos[0][1][0], pos[0][1][1] + 62, 24, C.GRAY, 1, face=C.FONT_MED)
        P.text("¿lluvia?", pos[3][0][0], pos[3][0][1] - 50, 24, C.GRAY, 1, face=C.FONT_MED)
        P.text("especialista en casos raros", pos[1][2][0] + 40, pos[1][2][1] - 60, 26, C.PINK, a_star, face=C.FONT_SEMI, align="left")
        ad = window(t, c["dr_apag"], c["dr_util"] + 0.3, 0.3, 0.3)
        P.text("en cada paso, otra mitad apagada", 540, 560, 30, C.WHITE, ad, face=C.FONT_SEMI)
        P.pill("DROPOUT", 540, 1240, 44, C.CYAN, out_back(prog(t, c["dr_name"] - 0.2, c["dr_name"] + 0.3)))


# =============================================================== el mapa (humedad × presión)
def to_xy(p):
    return lerp(BOX[0], BOX[2], (p[0] + 1) / 2), lerp(BOX[3], BOX[1], (p[1] + 1) / 2)


def region(P, key, a):
    if a <= 0: return
    im = image(key, D["rgba"][key])
    p = skia.Paint(); p.setAlphaf(clamp(a))
    P.c.drawImageRect(im, skia.Rect(*BOX), LINEAR, p)


def mapa(P, t):
    c = CUE
    a = window(t, c["da0"] - 0.1, c["por0"] + 0.3, 0.5, 0.4) + window(t, c["res0"] - 0.1, c["cie0"] + 0.3, 0.5, 0.4)
    a = clamp(a)
    if a <= 0: return
    X, y, f = D["Xtr"], D["ytr"], D["ftr"]
    with P.layer(a):
        P.rect(BOX[0] - 16, BOX[1] - 16, BOX[2] + 16, BOX[3] + 16, C.BG2, 0.9, radius=24)
        # frontera: sin dropout crece por etapas reales del entrenamiento; luego se reemplaza por la con dropout
        snaps = D["snaps"]
        if t > c["todos"] - 0.3 and t < c["res0"]:
            u = prog(t, c["todos"] - 0.3, c["islas"] + 1.2, lambda v: v)
            k = min(len(snaps) - 1, int(u * (len(snaps) - 1) + 0.0001))
            region(P, f"A{snaps[k]}", 0.9)
        if t >= c["res0"]:
            m = prog(t, c["simple"] - 0.5, c["simple"] + 0.6, in_out_cubic)
            region(P, f"A{snaps[-1]}", 0.9 * (1 - m))
            region(P, f"B{snaps[-1]}", 0.9 * m)
        # días conocidos
        for i in range(len(X)):
            ti = c["da_pts"] + 0.006 * i
            ai = prog(t, ti, ti + 0.25)
            if ai <= 0: continue
            x, yy = to_xy(X[i])
            P.circle(x, yy, 9, RAIN if y[i] else DRY, ai)
            P.circle(x, yy, 9, C.WHITE, ai * 0.6, stroke=2)
            if f[i]:
                ar = prog(t, c["raros"] - 0.2, c["raros"] + 0.3) * (1 - prog(t, c["nuevos"] - 0.3, c["nuevos"]))
                if ar > 0: P.circle(x, yy, 16 + 4 * pulse(t, c["raros"], 0.8), C.PINK, ar, stroke=3)
        P.text("humedad →", BOX[2], BOX[3] + 46, 26, C.GRAY, 1, face=C.FONT_MED, align="right")
        P.text("presión ↑", BOX[0], BOX[1] - 30, 26, C.GRAY, 1, face=C.FONT_MED, align="left")
        # días nuevos (muestra de los 5.000 de prueba), con aciertos y errores de la red sin dropout
        an = window(t, c["nuevos"] - 0.2, c["porq_end"], 0.3, 0.3) * (1 if t < c["res0"] else 0)
        an2 = prog(t, c["nuevo_mas"] - 0.3, c["nuevo_mas"] + 0.3) * (t >= c["res0"])
        for k, (p, lab, okA, okB) in enumerate(zip(D["Xte"], D["yte"], D["okA"], D["okB"])):
            for alpha, ok in ((an, okA), (an2, okB)):
                if alpha <= 0: continue
                x, yy = to_xy(p)
                if ok:
                    P.circle(x, yy, 5, C.WHITE, alpha * 0.8)
                else:
                    P.line(x - 7, yy - 7, x + 7, yy + 7, C.PINK, alpha, w=3); P.line(x + 7, yy - 7, x - 7, yy + 7, C.PINK, alpha, w=3)
        R = D["res"]["mean"]
        ak = prog(t, c["todos"] + 0.5, c["todos"] + 1.0) * (1 if t < c["res0"] else 0)
        P.text(f"días conocidos: acierta {fmtp(R['train_nodrop'])}", 540, 500, 32, C.CYAN, ak, face=C.FONT_BOLD)
        P.text(f"días nuevos: acierta {fmtp(R['test_nodrop'])}", 540, 1290, 30, C.PINK, an, face=C.FONT_BOLD)
        P.pill("SOBREAJUSTE", 540, 1180, 40, C.PINK, out_back(prog(t, c["sobre"] - 0.2, c["sobre"] + 0.3)) * (1 if t < c["res0"] else 0))
        # comparación final
        ac = prog(t, c["conocidos"] - 0.3, c["conocidos"] + 0.3) * (t >= c["res0"])
        if ac > 0:
            P.text(f"conocidos: {fmtp(R['train_nodrop'])} → {fmtp(R['train_drop'])}", 540, 500, 30, C.WHITE, ac, face=C.FONT_BOLD)
            P.text(f"nuevos: {fmtp(R['test_nodrop'])} → {fmtp(R['test_drop'])}", 540, 1290, 32, C.CYAN, an2, face=C.FONT_BOLD)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D
    TL, EP, D = tl, episode, data
    D["rgba"] = {}
    snaps = sorted(int(k[1:]) for k in D if k.startswith("A") and k[1:].isdigit())
    D["snaps"] = snaps
    for pre in ("A", "B"):
        for s in snaps:
            pr = np.flipud(D[f"{pre}{s}"])                 # fila 0 = presión alta (arriba)
            a8 = np.zeros(pr.shape + (4,), np.uint8)
            rain = pr > 0.5
            a8[rain] = [0, 217, 255, 70]; a8[~rain] = [155, 92, 255, 55]
            # borde de la frontera, más marcado
            edge = np.zeros_like(rain)
            edge[1:, :] |= rain[1:, :] != rain[:-1, :]; edge[:, 1:] |= rain[:, 1:] != rain[:, :-1]
            a8[edge] = [245, 247, 250, 230]
            D["rgba"][f"{pre}{s}"] = a8
    c = {}
    c["real"] = T("hook", "real"); c["reprueba"] = T("hook", "reprueba")
    c["pu0"] = T("puente"); c["apagar"] = T("puente", "apagar")
    c["da0"] = T("datos"); c["da_pts"] = T("datos", "punto"); c["raros"] = T("datos", "raros")
    c["todos"] = T("memoriza", "casi"); c["islas"] = T("memoriza", "islas"); c["nuevos"] = T("memoriza", "nuevos")
    c["sobre"] = T("memoriza", "sobreajuste")
    c["por0"] = T("porque"); c["especial"] = T("porque", "especializan"); c["apoyan"] = T("porque", "apoyan")
    c["porq_end"] = T("porque")
    c["dr0"] = T("dropout"); c["dr_apag"] = T("dropout", "apagamos"); c["dr_util"] = T("dropout", "útil")
    c["dr_name"] = T("dropout", "dropout")
    c["res0"] = T("resultado"); c["simple"] = T("resultado", "simple"); c["conocidos"] = T("resultado", "conocidos")
    c["nuevo_mas"] = T("resultado", "nuevos")
    c["cie0"] = T("cierre"); c["entender"] = T("cierre", "entender")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    P.background(t, accent=0.2 * window(t, c["res0"], c["cie0"], 0.5, 0.5))
    pruebas(P, t)
    red(P, t)
    mapa(P, t)
    ad = window(t, c["da0"], c["cie0"], 0.4, 0.4)
    P.text("Datos simulados · resultados de un experimento propio (promedio de 5 simulaciones)", 540, 1320, 21, C.GRAY,
           ad * 0.9, face=C.FONT_MED)
    vignette(P, 0.45)
    vband(P, 1250, C.H, 0.0, 0.85)
    SUB.draw(P, CHUNKS, t)


def draw_cover(P, t=0.0):
    P.background(1.0, accent=0.6)
    pos = net_pos(cy=1000)
    off = {(1, 1), (1, 4), (2, 2), (2, 5)}
    for li in range(len(LAYERS) - 1):
        for i, (x0, y0) in enumerate(pos[li]):
            for j, (x1, y1) in enumerate(pos[li + 1]):
                dead = (li, i) in off or (li + 1, j) in off
                P.line(x0, y0, x1, y1, C.VIOLET, 0.08 if dead else 0.4, w=2)
    for li, layer in enumerate(pos):
        for j, (x, y) in enumerate(layer):
            dead = (li, j) in off
            P.circle(x, y, 34, C.BG2, 1); P.circle(x, y, 34, (0.25, 0.28, 0.36) if dead else C.CYAN, 1, stroke=4)
            if dead:
                P.line(x - 16, y - 16, x + 16, y + 16, C.PINK, 1, w=5); P.line(x + 16, y - 16, x - 16, y + 16, C.PINK, 1, w=5)
    P.text("¿APAGAR NEURONAS", 540, 420, 84, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("LA HACE MÁS LISTA?", 540, 520, 84, C.CYAN, 1, face=C.FONT_BLACK, glow=0.5)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.4)] + [(0.15 + 0.12 * k, "tick", 0.6) for k in range(6)] + [
        (0.9, "ding", 0.6), (c["real"] - 0.3, "whoosh", 0.5), (c["reprueba"] + 0.3, "thump", 0.7),
        (c["pu0"], "whoosh", 0.5), (c["apagar"], "pop_low", 0.6), (c["da0"], "whoosh", 0.5),
        (c["da_pts"], "riser", 0.4), (c["raros"], "pop", 0.6), (c["todos"], "riser", 0.4),
        (c["islas"], "pop", 0.5), (c["nuevos"], "pop_low", 0.6), (c["sobre"], "thump", 0.6),
        (c["por0"], "whoosh", 0.5), (c["especial"], "pop", 0.5), (c["dr0"], "whoosh", 0.5),
        (c["dr_util"], "swell", 0.6), (c["dr_name"], "ding", 0.7), (c["res0"], "whoosh", 0.5),
        (c["simple"], "riser", 0.4), (c["nuevo_mas"], "ding", 0.7), (c["cie0"], "whoosh_down", 0.5),
        (c["entender"] + 0.4, "ding", 0.8)] + [(c["dr_apag"] + 0.25 * k, "tick", 0.35) for k in range(12)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["dr0"], "pulse": (c["res0"], c["cie0"]), "quiet": [(c["por0"], c["dr0"])]}
