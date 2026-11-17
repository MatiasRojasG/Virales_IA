"""Escenas — «La IA que descartaba currículums de mujeres» (blanco y negro, acento rojo puntual).

Un solo objeto guía la historia: el currículum. Aparece escaneado (hook), recibe estrellas
(contexto), se multiplica en diez años de currículums (datos), revela la palabra castigada
(revela), alimenta un patrón que se copia (porque), se resuelve en una línea de tiempo (final)
y termina en una cinta que repite el sesgo cada vez más rápido (enseña). El último cuadro
vuelve exactamente al primero (loop).
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint, vignette, vband
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic, smooth, in_cubic

TL = None; EP = {}; CHUNKS = []; CUE = {}; D = {}
K = (0.0, 0.0, 0.0); WH = (0.97, 0.97, 0.97); G1 = (0.66, 0.66, 0.66); G2 = (0.36, 0.36, 0.36)
G3 = (0.16, 0.16, 0.16); G4 = (0.09, 0.09, 0.09); INK = (0.08, 0.08, 0.08); RED = (1.0, 0.27, 0.27)
CX, CY = 540, 860                      # centro del currículum principal
DUR = 1.0


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


# ------------------------------------------------------------------ primitivas
def star_path(x, y, r):
    p = skia.Path()
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.45
        a = -math.pi / 2 + k * math.pi / 5
        (p.moveTo if k == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
    p.close(); return p


def stars(P, x, y, value, a=1.0, r=34, col=WH, gap=88):
    """value: 0..5 (admite fracciones). Estrellas vacías en gris, llenas en col."""
    for k in range(5):
        sx = x + (k - 2) * gap
        pth = star_path(sx, y, r)
        P.c.drawPath(pth, paint(G2, a, stroke=4))
        f = clamp(value - k)
        if f > 0:
            P.c.save(); P.c.clipRect(skia.Rect(sx - r, y - r, sx - r + 2 * r * f, y + r))
            P.c.drawPath(pth, paint(col, a)); P.c.restore()


def doc(P, x, y, s=1.0, a=1.0, fill=WH, ink=G1, rows=6, photo=True):
    w, h = 210 * s, 280 * s
    P.rect(x - w, y - h, x + w, y + h, fill, a, radius=18 * s)
    if photo:
        P.circle(x - w + 70 * s, y - h + 75 * s, 36 * s, ink, a)
        P.line(x - w + 130 * s, y - h + 62 * s, x + w - 40 * s, y - h + 62 * s, ink, a, w=14 * s)
        P.line(x - w + 130 * s, y - h + 96 * s, x + w - 110 * s, y - h + 96 * s, ink, a * 0.7, w=10 * s)
    for k in range(rows):
        yy = y - h + 175 * s + k * 58 * s
        x1 = x + w - 40 * s - (90 * s if k % 3 == 2 else 0)
        P.line(x - w + 40 * s, yy, x1, yy, ink, a * 0.8, w=11 * s)


def mini(P, x, y, s, a, col):
    P.rect(x - 16 * s, y - 21 * s, x + 16 * s, y + 21 * s, col, a, radius=3 * s)
    P.circle(x - 7 * s, y - 12 * s, 4 * s, K, a * 0.5)
    for k in range(3): P.line(x - 10 * s, y + k * 7 * s, x + 10 * s, y + k * 7 * s, K, a * 0.35, w=2.4 * s)


def xmark(P, x, y, r, a, w=26, col=RED):
    P.line(x - r, y - r, x + r, y + r, col, a, w=w); P.line(x + r, y - r, x - r, y + r, col, a, w=w)


def person(P, x, y, s, a, col=WH):
    P.circle(x, y - 46 * s, 30 * s, col, a)
    pth = skia.Path(); pth.addRRect(skia.RRect.MakeRectXY(skia.Rect(x - 52 * s, y - 6 * s, x + 52 * s, y + 70 * s), 40 * s, 40 * s))
    P.c.drawPath(pth, paint(col, a))


def chip(P, x, y, s, a, col=WH):
    P.rect(x - 46 * s, y - 46 * s, x + 46 * s, y + 46 * s, col, a, radius=10 * s, stroke=6 * s)
    P.rect(x - 22 * s, y - 22 * s, x + 22 * s, y + 22 * s, col, a, radius=4 * s)
    for k in range(-1, 2):
        o = k * 26 * s
        for (x0, y0, x1, y1) in ((x + o, y - 46 * s, x + o, y - 66 * s), (x + o, y + 46 * s, x + o, y + 66 * s),
                                 (x - 46 * s, y + o, x - 66 * s, y + o), (x + 46 * s, y + o, x + 66 * s, y + o)):
            P.line(x0, y0, x1, y1, col, a, w=5 * s)


def beam(P, t, x0, x1, y0, y1, a):
    """Haz de escaneo periódico: misma posición en t=0 y t=DUR (loop exacto)."""
    if a <= 0: return
    u = 0.5 - 0.5 * math.cos(2 * math.pi * 3 * t / DUR)
    y = lerp(y0, y1, u)
    P.c.save(); P.c.clipRect(skia.Rect(x0 - 40, y0 - 40, x1 + 40, y1 + 40))
    P.rect(x0 - 30, y - 50, x1 + 30, y + 50, WH, 0.10 * a, blur=26)
    P.line(x0 - 30, y, x1 + 30, y, WH, 0.95 * a, w=4)
    P.c.restore()


def backdrop(P, t):
    c = P.c
    c.clear(skia.ColorBLACK)
    r = 1050 + 50 * math.sin(2 * math.pi * t / DUR)
    sh = skia.GradientShader.MakeRadial((C.W * 0.5, C.H * 0.44), r,
                                        [skia.Color4f(0.11, 0.11, 0.11, 1).toColor(), skia.Color4f(0, 0, 0, 1).toColor()])
    c.drawPaint(skia.Paint(Shader=sh))
    p = paint(WH, 0.04)
    off = (t * 6) % 60
    for y in range(-60, C.H + 60, 60):
        for x in range(0, C.W + 60, 60):
            c.drawCircle(x, y + off, 1.5, p)


# ------------------------------------------------------------------ escenas
def s_cv(P, t):
    """Currículum principal: hook → contexto → (vuelve en revela) → cierre."""
    c = CUE
    a_hook = 1 - prog(t, c["datos0"] - 0.1, c["datos0"] + 0.5)
    a_end = prog(t, c["cierre0"] + 0.05, DUR - 0.3, in_out_cubic)
    a = max(a_hook, a_end)
    if a <= 0.001: return
    # en contexto el CV se achica y sube para dejar espacio a las estrellas
    u = prog(t, c["ctx0"], c["ctx0"] + 0.8, in_out_cubic) * (1 - a_end)
    s = lerp(1.0, 0.78, u); y = lerp(CY, CY - 60, u)
    # leve respiración (periódica para el loop)
    s *= 1 + 0.008 * math.sin(2 * math.pi * 2 * t / DUR)
    # hook: CV se desplaza a la derecha cuando aparecen persona y máquina
    sh = window(t, c["persona"] - 0.3, c["ctx0"], 0.5, 0.6, in_out_cubic) * (1 - a_end)
    x = CX + 150 * sh
    sc = s * lerp(1, 0.72, sh)
    with P.layer(a):
        doc(P, x, y, sc)
        beam(P, t, x - 210 * sc, x + 210 * sc, y - 280 * sc, y + 280 * sc, 1 - prog(t, c["ctx0"], c["ctx0"] + 0.4) + a_end)
        # X roja en «descartarte»
        ax = window(t, c["descartar"], c["ctx0"] + 0.1, 0.12, 0.35)
        if ax > 0:
            k = 1 + 0.5 * (1 - out_cubic(prog(t, c["descartar"], c["descartar"] + 0.22)))
            xmark(P, x, y, 150 * sc * k, ax, w=30 * sc)
    # persona / máquina
    ap = window(t, c["persona"] - 0.1, c["ctx0"], 0.35, 0.5) * (1 - a_end)
    am = window(t, c["maquina"] - 0.1, c["ctx0"], 0.35, 0.5) * (1 - a_end)
    if ap > 0:
        person(P, 230, 760, 1.25, ap * (1 - 0.65 * prog(t, c["maquina"], c["maquina"] + 0.3)))
    if am > 0:
        chip(P, 230, 1010, 1.1 * out_back(prog(t, c["maquina"] - 0.1, c["maquina"] + 0.3)), am)
        P.arrow(330, 1010, 400, 960, WH, am * prog(t, c["maquina"] + 0.2, c["maquina"] + 0.6), w=5, head=18)
    # contexto: año y estrellas
    ay = window(t, c["y2014"] - 0.2, c["datos0"] + 0.2, 0.4, 0.4)
    if ay > 0:
        P.text("2014", 540, 520 + 20 * (1 - out_cubic(prog(t, c["y2014"] - 0.2, c["y2014"] + 0.4))), 120, WH, ay,
               face=C.FONT_BLACK, tracking=-2)
    ast = window(t, c["estrellas"] - 0.5, c["datos0"] + 0.1, 0.4, 0.4)
    if ast > 0:
        v = 5 * prog(t, c["estrellas"] - 0.3, c["estrellas"] + 0.6, in_out_cubic)
        v = lerp(v, 4, prog(t, c["producto"] - 0.3, c["producto"] + 0.4))
        stars(P, 540, 1225, v, ast)


GRID = (10, 9)                       # columnas × filas de currículums en «datos»


def grid_pos(i):
    cols, rows = GRID
    r, q = divmod(i, cols)
    return 150 + q * 87, 560 + r * 84


def s_datos(P, t):
    c = CUE
    a = window(t, c["datos0"] - 0.2, c["porque0"] + 0.4, 0.4, 0.5)
    if a <= 0: return
    cols, rows = GRID; n = cols * rows
    women = D["women"]
    to_center = prog(t, c["conclusion"] - 0.1, c["conclusion"] + 0.9, in_out_cubic)
    tint = prog(t, c["hombres"] - 0.2, c["hombres"] + 0.5)
    for i in range(n):
        x, y = grid_pos(i)
        # caen en cascada
        d0 = c["datos0"] + 0.02 * i
        u = prog(t, d0, d0 + 0.55, out_cubic)
        if u <= 0: continue
        yy = y - 220 * (1 - u)
        col = lerp_c(WH, G2 if i in women else WH, tint)
        # en «conclusión» todo se absorbe al modelo (centro)
        xx = lerp(x, 540, to_center); yy = lerp(yy, 900, to_center)
        mini(P, xx, yy, 1.35 * (1 - 0.7 * to_center), a * u * (1 - to_center), col)
    al = window(t, c["anos"] - 0.2, c["conclusion"], 0.3, 0.4)
    P.pill("10 años", 540, 495, 40, WH, al, fill_a=0.10)
    lg = window(t, c["hombres"], c["conclusion"], 0.4, 0.4)
    if lg > 0:
        P.rect(300, 1290, 330, 1320, WH, lg, radius=4); P.text("hombres", 345, 1316, 34, WH, lg, face=C.FONT_BOLD, align="left")
        P.rect(600, 1290, 630, 1320, G2, lg, radius=4); P.text("mujeres", 645, 1316, 34, G1, lg, face=C.FONT_BOLD, align="left")


def brain(P, t, x, y, s, a, red=0.0):
    """Modelo: nodos conectados que laten."""
    if a <= 0: return
    nodes = D["nodes"]
    for (i, j) in D["edges"]:
        (x0, y0), (x1, y1) = nodes[i], nodes[j]
        P.line(x + x0 * s, y + y0 * s, x + x1 * s, y + y1 * s, G2, a * 0.8, w=3)
    for k, (nx, ny) in enumerate(nodes):
        pl = 0.5 + 0.5 * math.sin(t * 4 + k)
        P.circle(x + nx * s, y + ny * s, (10 + 4 * pl) * s, lerp_c(WH, RED, red * (k % 3 == 0)), a)


def s_revela(P, t):
    c = CUE
    # modelo que absorbió los datos
    ab = window(t, c["conclusion"] + 0.3, c["femenino"] - 0.2, 0.5, 0.6)
    brain(P, t, 540, 880, 1.0 + 0.1 * pulse(t, c["conclusion"] + 0.9, 0.6), ab)
    a = window(t, c["femenino"] - 0.5, c["porque0"] + 0.1, 0.45, 0.45)
    if a <= 0: return
    u = out_back(prog(t, c["femenino"] - 0.5, c["femenino"] + 0.1))
    with P.layer(a), P.transform(0, 0, lerp(0.85, 1.0, u), cx=540, cy=880):
        x0, x1, y0, y1 = 150, 930, 560, 1080
        P.rect(x0, y0, x1, y1, WH, 1, radius=22)
        P.circle(x0 + 80, y0 + 85, 42, G1)
        P.line(x0 + 150, y0 + 70, x1 - 60, y0 + 70, G1, 1, w=16); P.line(x0 + 150, y0 + 110, x1 - 220, y0 + 110, G1, 0.7, w=11)
        P.line(x0 + 50, y0 + 190, x1 - 50, y0 + 190, G1, 0.6, w=11); P.line(x0 + 50, y0 + 240, x1 - 160, y0 + 240, G1, 0.6, w=11)
        f = 44
        P.text("Capitana del club", x0 + 50, y0 + 340, f, INK, 1, face=C.FONT_BOLD, align="left")
        w1 = P.text_width("de ajedrez ", f, C.FONT_BOLD); w2 = P.text_width("femenino", f, C.FONT_BOLD)
        hl = prog(t, c["femenino_dicho"] - 0.1, c["femenino_dicho"] + 0.45, in_out_cubic)
        # segunda línea: «de ajedrez femenino»
        P.text("de ajedrez", x0 + 50, y0 + 410, f, INK, 1, face=C.FONT_BOLD, align="left")
        hx2 = x0 + 50 + w1
        if hl > 0:
            P.rect(hx2 - 8, y0 + 370, hx2 - 8 + (w2 + 16) * hl, y0 + 426, RED, 0.92, radius=8)
        P.text("femenino", hx2, y0 + 410, f, lerp_c(INK, WH, hl), 1, face=C.FONT_BOLD, align="left")
    # nota que baja
    an = window(t, c["femenino"] - 0.3, c["porque0"] + 0.1, 0.4, 0.4)
    if an > 0:
        drop = prog(t, c["nota"] - 0.1, c["nota"] + 0.8, in_out_cubic)
        v = lerp(4, 2, drop)
        stars(P, 540, 1215, v, an, col=lerp_c(WH, RED, drop))
        if drop > 0:
            P.arrow(905, 1170, 905, 1270, RED, an * drop, w=6, head=20)


def s_porque(P, t):
    c = CUE
    a = window(t, c["porque0"] - 0.1, c["final0"] + 0.1, 0.45, 0.45)
    if a <= 0: return
    women = D["col_women"]
    cp = prog(t, c["patron"] - 0.3, c["patron"] + 1.0, in_out_cubic)
    with P.layer(a):
        # pasado (izquierda) → modelo → decisiones (derecha)
        P.text("pasado", 220, 560, 36, G1, 1, face=C.FONT_BOLD)
        P.text("decisiones", 860, 560, 36, G1, 1, face=C.FONT_BOLD)
        for r in range(8):
            for q in range(3):
                i = r * 3 + q
                col = G2 if i in women else WH
                mini(P, 160 + q * 60, 640 + r * 78, 1.05, 1, col)
                # copia: las decisiones reproducen exactamente la misma figura
                f = clamp(cp * 24 - i)
                if f > 0:
                    mini(P, 800 + q * 60, 640 + r * 78, 1.05, f, G3 if i in women else WH)
                    if i in women: xmark(P, 800 + q * 60, 640 + r * 78, 13, f, w=5)
        brain(P, t, 540, 900, 0.75, 1, red=cp)
        P.arrow(310, 900, 420, 900, WH, 1, w=5, head=18); P.arrow(660, 900, 760, 900, WH, cp, w=5, head=18)
        # «nadie le pidió»: regla vacía tachada
        ar = window(t, c["porque0"], c["patron"] - 0.2, 0.3, 0.3)
        if ar > 0:
            P.rect(400, 1120, 680, 1200, G4, ar, radius=14); P.rect(400, 1120, 680, 1200, G2, ar, radius=14, stroke=3)
            P.text("discriminar", 540, 1172, 34, G1, ar, face=C.FONT_MONO_B)
            P.line(420, 1160, 420 + 240 * prog(t, c["pidio"], c["pidio"] + 0.4), 1160, RED, ar, w=5)


def s_final(P, t):
    c = CUE
    a = window(t, c["final0"] - 0.1, c["ensena0"] + 0.1, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        y = 700
        lx = prog(t, c["final0"] - 0.1, c["final0"] + 0.6, in_out_cubic)
        P.line(180, y, 180 + 720 * lx, y, G2, 1, w=5)
        pts = [("2014", 220, c["final0"]), ("2015", 540, c["corregir"]), ("2017", 860, c["y2017"])]
        for lab, x, tt in pts:
            u = out_back(prog(t, tt - 0.2, tt + 0.3))
            if u <= 0: continue
            col = RED if lab == "2017" and t > c["abandono"] else WH
            P.circle(x, y, 16 * u, col, 1)
            P.text(lab, x, y - 50, 46, col, clamp(u), face=C.FONT_BLACK)
        # modelo que se apaga y se desarma en «abandonó»
        dz = prog(t, c["abandono"] - 0.1, c["abandono"] + 0.9, in_cubic)
        if dz < 1:
            ab = prog(t, c["final0"], c["final0"] + 0.5)
            nodes = D["nodes"]
            for (i, j) in D["edges"]:
                (x0, y0), (x1, y1) = nodes[i], nodes[j]
                P.line(540 + x0 * .8, 930 + y0 * .8, 540 + x1 * .8, 930 + y1 * .8, G2, ab * (1 - dz), w=3)
            for k, (nx, ny) in enumerate(nodes):
                fall = dz * dz * (300 + 40 * (k % 5))
                P.circle(540 + nx * .8, 930 + ny * .8 + fall, 11, WH, ab * (1 - dz))
        # los reclutadores: persona por delante del chip
        ah = window(t, c["reclut"] - 0.2, c["ensena0"] + 0.1, 0.4, 0.4)
        if ah > 0:
            chip(P, 690, 1020, 0.7, ah * 0.45, G1)
            person(P, 430, 990, 1.5, ah)
            P.text("decide", 430, 1150, 34, WH, ah * prog(t, c["solo"] - 0.2, c["solo"] + 0.3), face=C.FONT_BOLD)


def s_ensena(P, t):
    c = CUE
    a = window(t, c["ensena0"] - 0.1, c["cierre0"] + 0.3, 0.45, 0.4)
    if a <= 0: return
    women = D["belt_women"]
    t0 = c["ensena0"]
    # posición acumulada de la cinta: velocidad que crece en «más rápido»
    def pos(tt):
        t1 = c["rapido"]
        base = 260 * (tt - t0)
        extra = 0.0
        if tt > t1: extra = 520 * (tt - t1) ** 2 / 1.0
        # frena al llegar el cierre
        return base + extra
    tt = min(t, c["cierre0"] + 0.4)
    off = pos(tt)
    spacing = 180
    yb = 940
    with P.layer(a):
        # cinta
        P.rect(60, yb + 80, 1020, yb + 104, G3, 1, radius=12)
        for k in range(14):
            x = (k * 80 - off) % 1120 - 40
            P.line(x, yb + 84, x + 30, yb + 100, G2, 1, w=4)
        # embudo de entrada (lo que le das) y sello (el modelo)
        brain(P, t, 540, 600, 0.55, prog(t, t0, t0 + 0.5))
        P.line(540, 690, 540, yb - 120, G2, 1, w=4)
        stamp_y = yb - 120 + 60 * max(0.0, math.sin(off / spacing * 2 * math.pi)) ** 8
        P.rect(470, stamp_y - 40, 610, stamp_y + 10, WH, 1, radius=8)
        inj = prog(t, c["injusto"] - 0.2, c["injusto"] + 0.4)
        for k in range(-2, 9):
            idx = int(math.floor(off / spacing)) + k
            x = 540 + (idx * spacing - off) + 0 * k
            if x < -80 or x > 1160: continue
            fem = (idx % 7) in (1, 4)
            col = G2 if fem else WH
            doc(P, x, yb - 20, 0.24, 1, fill=col, ink=G2 if not fem else G3, rows=3)
            # los que ya pasaron por el sello (x < 540) y son «femenino» quedan marcados
            if fem and x < 540 and inj > 0:
                xmark(P, x, yb - 20, 36, inj, w=9)
        P.pill("lo que le das", 540, 520, 34, WH, window(t, c["das"] - 0.2, c["injusto"], 0.3, 0.3), fill_a=0.10)


# ------------------------------------------------------------------ composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D, DUR
    TL, EP = tl, episode
    DUR = tl.duration
    # subtítulos en blanco y negro: palabra clave blanca pura, resto gris claro
    C.CYAN = (1.0, 1.0, 1.0); C.WHITE = (0.80, 0.80, 0.80); C.BG = (0.0, 0.0, 0.0)
    rng = np.random.default_rng(7)
    n = GRID[0] * GRID[1]
    D = {"women": set(rng.choice(n, size=n // 6, replace=False).tolist()),
         "col_women": {2, 9, 13, 20},
         "belt_women": set()}
    # red pequeña para el «modelo»
    nodes = []
    for li, m in enumerate((3, 4, 4, 2)):
        for j in range(m):
            nodes.append(((li - 1.5) * 110, (j - (m - 1) / 2) * 90))
    edges = []
    starts = [0, 3, 7, 11, 13]
    for li in range(3):
        for i in range(starts[li], starts[li + 1]):
            for j in range(starts[li + 1], starts[li + 2]):
                edges.append((i, j))
    D["nodes"], D["edges"] = nodes, edges
    c = {}
    c["persona"] = T("hook", "persona"); c["maquina"] = T("hook", "máquina"); c["descartar"] = T("hook", "descartarte")
    c["ctx0"] = T("contexto"); c["y2014"] = T("contexto", "2014"); c["estrellas"] = T("contexto", "estrellas")
    c["producto"] = T("contexto", "producto")
    c["datos0"] = T("datos"); c["anos"] = T("datos", "diez"); c["hombres"] = T("datos", "hombres")
    c["revela0"] = T("revela"); c["conclusion"] = T("revela", "conclusión"); c["femenino"] = T("revela", "palabra")
    c["femenino_dicho"] = T("revela", "femenino"); c["nota"] = T("revela", "bajaba")
    c["porque0"] = T("porque"); c["pidio"] = T("porque", "discriminar"); c["patron"] = T("porque", "patrón")
    c["final0"] = T("final"); c["corregir"] = T("final", "corregirla"); c["y2017"] = T("final", "2017")
    c["abandono"] = T("final", "abandonó"); c["reclut"] = T("final", "reclutadores"); c["solo"] = T("final", "solo")
    c["ensena0"] = T("ensena"); c["das"] = T("ensena", "das"); c["injusto"] = T("ensena", "injusto")
    c["rapido"] = T("ensena", "rápido")
    c["cierre0"] = T("cierre")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    backdrop(P, t)
    s_cv(P, t)
    s_datos(P, t)
    s_revela(P, t)
    s_porque(P, t)
    s_final(P, t)
    s_ensena(P, t)
    vignette(P, 0.35)
    vband(P, 1300, C.H, 0.0, 0.8, rgb=K)
    SUB.draw(P, CHUNKS, t)


def draw_cover(P, t=0.0):
    backdrop(P, 0.0)
    doc(P, CX, CY + 40, 0.9)
    xmark(P, CX, CY + 40, 150, 1, w=30)
    P.text("LA IA QUE", 540, 400, 96, WH, 1, face=C.FONT_BLACK)
    P.text("DESCARTABA", 540, 505, 96, WH, 1, face=C.FONT_BLACK)
    P.text("A LAS MUJERES", 540, 1420, 88, RED, 1, face=C.FONT_BLACK)
    vignette(P, 0.35)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.35), (c["persona"], "pop", 0.35), (c["maquina"], "tick", 0.6),
            (c["descartar"], "thump", 0.8), (c["ctx0"], "whoosh", 0.4), (c["estrellas"], "tick", 0.4),
            (c["datos0"], "whoosh", 0.45), (c["hombres"], "pop_low", 0.5), (c["conclusion"], "riser", 0.4),
            (c["femenino_dicho"], "pop", 0.6), (c["nota"], "whoosh_down", 0.5), (c["porque0"], "whoosh", 0.35),
            (c["patron"], "riser", 0.35), (c["final0"], "whoosh", 0.35), (c["abandono"], "pop_low", 0.6),
            (c["ensena0"], "whoosh", 0.4), (c["injusto"], "thump", 0.5), (c["rapido"], "riser", 0.45),
            (c["cierre0"], "rewind", 0.45)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["datos0"], "pulse": (c["revela0"], c["porque0"]),
            "quiet": [(c["femenino"] - 0.2, c["nota"] + 0.4)]}
