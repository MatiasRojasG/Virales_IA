"""Escenas — «¿Cómo supo tu auto que ibas a chocar?» (stheq.ia, motion graphics).

Hilo visual: dos autos de perfil en una carretera; la cámara sigue al auto de adelante.
Gancho: el auto de adelante enciende las luces de freno, tú vas mirando el celular y la distancia se achica; tu auto
frena solo → «?» → la escena retrocede: un corchete mide la «distancia» y una flecha la «rapidez» → el sensor delantero
lanza ondas que rebotan y vuelven → el corchete se achica (fantasma del anterior) → la cuenta como fracción:
distancia ÷ rapidez = segundos → ejemplo: 30 m ÷ 50 km/h ≈ 2,2 s → cuenta regresiva: aviso (triángulo), frenado
automático y barra de fuerza de freno que se completa → barras: choques por alcance sin y con frenado automático
(−50 %, IIHS) → lluvia y niebla: las ondas se pierden; «tú» → cierre: se repite la escena y frena; el último cuadro
vuelve al estado del cuadro 0 (empalme).
"""
from __future__ import annotations
import math
import numpy as np
import skia
from PIL import Image
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic
from reelforge import marca as L

TL = None; EP = {}; CHUNKS = []; CUE = {}
_IMG = {}
GAPK = []; SPDK = []; _OFF = None
FPS_INT = 120

ROAD_Y = 1050           # línea de las ruedas
X_AH = 800              # centro del auto de adelante (fijo en pantalla)
HALF = 120              # medio largo de un auto (escala 0.8)
SC = 1.25               # zoom de la escena de la carretera


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


# =============================================================== cabecera de marca
def header(P, a=1.0):
    if "logo" not in _IMG:
        im = Image.open(C.ROOT / "assets" / "marca" / "logo_blanco.png").convert("RGBA")
        h = 44; w = round(im.width * h / im.height)
        im = im.resize((w * 2, h * 2), Image.LANCZOS)
        _IMG["logo"] = (skia.Image.fromarray(np.array(im), colorType=skia.kRGBA_8888_ColorType), w, h)
    img, w, h = _IMG["logo"]
    P.img(img, 64, 256, 64 + w, 256 + h, a, nearest=False)
    P.text(L.NAME, 64 + w + 18, 288, 26, L.FG, 0.85 * a, face=C.FONT_BOLD, align="left", tracking=1.5)
    P.text(EP.get("fecha", ""), 1016, 288, 24, L.FG, 0.7 * a, face=C.FONT_SEMI, align="right", tracking=2)


# =============================================================== utilidades de tiempo
def keyed(t, keys):
    """Interpolación suave entre fotogramas clave [(t, v), ...]."""
    if t <= keys[0][0]: return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t <= t1:
            return lerp(v0, v1, in_out_cubic((t - t0) / max(t1 - t0, 1e-6)))
    return keys[-1][1]


def gap(t): return keyed(t, GAPK)
def x_me(t): return X_AH - 2 * HALF - gap(t)


def road_off(t):
    i = int(clamp(t * FPS_INT, 0, len(_OFF) - 1))
    return _OFF[i]


# =============================================================== piezas
def car(P, x, y, a=1.0, brake=0.0, sensor=0.0, outline=None, glow_cabin=0.0):
    """Auto de perfil mirando a la derecha; (x, y) = centro, línea de ruedas."""
    if a <= 0: return
    col = outline or L.FG
    with P.layer(a):
        P.rect(x - 112, y + 6, x + 112, y + 22, L.BG, 0.6, radius=10, blur=10)
        cab = skia.Path()
        cab.moveTo(x - 78, y - 66); cab.lineTo(x - 46, y - 114); cab.lineTo(x + 38, y - 114); cab.lineTo(x + 80, y - 66)
        cab.close()
        P.c.drawPath(cab, paint(L.CARD, 1))
        P.c.drawPath(cab, paint(col, 1, 5))
        # ventanas
        win = skia.Path()
        win.moveTo(x - 62, y - 70); win.lineTo(x - 40, y - 104); win.lineTo(x - 6, y - 104); win.lineTo(x - 6, y - 70); win.close()
        P.c.drawPath(win, paint(L.DIM, 1))
        win2 = skia.Path()
        win2.moveTo(x + 4, y - 70); win2.lineTo(x + 4, y - 104); win2.lineTo(x + 34, y - 104); win2.lineTo(x + 62, y - 70); win2.close()
        P.c.drawPath(win2, paint(L.DIM, 1))
        if glow_cabin > 0:
            P.c.drawPath(win, paint(L.RED, glow_cabin * 0.8))
        P.rect(x - HALF, y - 70, x + HALF, y - 22, L.CARD, 1, radius=22)
        P.rect(x - HALF, y - 70, x + HALF, y - 22, col, 1, stroke=5, radius=22)
        for wx in (x - 72, x + 72):
            P.circle(wx, y - 20, 25, L.BG, 1)
            P.circle(wx, y - 20, 25, col, 1, stroke=5)
            P.circle(wx, y - 20, 8, L.GRAY, 1)
        # faro delantero
        P.rect(x + HALF - 14, y - 60, x + HALF - 2, y - 46, L.FG, 0.9, radius=4)
        # luz de freno
        P.rect(x - HALF + 2, y - 62, x - HALF + 14, y - 44, lerp_c(L.DIM, L.RED, brake), 1, radius=4)
        if brake > 0:
            P.circle(x - HALF + 4, y - 53, 34, L.RED, 0.45 * brake, blur=16)
        if sensor > 0:
            P.circle(x + HALF + 2, y - 38, 18, L.RED, 0.5 * sensor, blur=10)
            P.circle(x + HALF + 2, y - 38, 8, L.RED, sensor)


def phone_icon(P, x, y, a, s=1.0, crossed=0.0):
    if a <= 0: return
    with P.layer(a):
        P.circle(x, y, 60 * s, L.FG, 0.12, blur=20)
        P.rect(x - 26 * s, y - 46 * s, x + 26 * s, y + 46 * s, L.BG, 1, radius=10 * s)
        P.rect(x - 26 * s, y - 46 * s, x + 26 * s, y + 46 * s, L.FG, 1, stroke=5, radius=10 * s)
        P.rect(x - 17 * s, y - 34 * s, x + 17 * s, y + 30 * s, L.GRAY, 0.6, radius=4 * s)
        if crossed > 0:
            P.line(x - 50 * s, y - 50 * s, x - 50 * s + 100 * s * crossed, y - 50 * s + 100 * s * crossed, L.RED, 1, w=10)


def road(P, t, a=1.0):
    if a <= 0: return
    with P.layer(a):
        P.rect(-20, ROAD_Y + 4, 1100, ROAD_Y + 150, L.CARD, 0.55)
        P.line(-20, ROAD_Y + 4, 1100, ROAD_Y + 4, L.GRAY, 0.8, w=4)
        off = road_off(t) % 160
        for k in range(-1, 9):
            x0 = k * 160 - off
            P.line(x0, ROAD_Y + 80, x0 + 80, ROAD_Y + 80, L.FG, 0.55, w=8)


def wave_arc(P, cx, cy, r, a, start, sweep, w=5, col=None):
    if a <= 0 or r <= 2: return
    P.c.drawArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), start, sweep, False, paint(col or L.FG, a, w))


def waves(P, t, t0, xs, xr, y, a, broken=0.0, period=0.9):
    """Pulsos del sensor (xs) que rebotan en la parte trasera del otro auto (xr) y vuelven."""
    if a <= 0 or t < t0: return
    d = max(xr - xs, 10)
    for k in range(3):
        u = ((t - t0) / period + k / 3) % 1.0
        if u < 0.5:
            r = d * (u / 0.5)
            wave_arc(P, xs, y, r, a * (1 - 0.3 * u) * (1 - broken), -22, 44, w=6, col=L.RED)
            if broken > 0:
                for j in range(5):
                    ang = math.radians(-40 + j * 20 + 15 * math.sin(t * 3 + j))
                    rr = r * (0.7 + 0.3 * ((j * 37) % 5) / 5)
                    P.circle(xs + rr * math.cos(ang), y + rr * math.sin(ang), 5, L.RED, a * broken * 0.6)
        else:
            r = d * ((u - 0.5) / 0.5)
            wave_arc(P, xr, y, r, a * 0.75 * (1 - broken), 158, 44, w=5, col=L.FG)


def bracket(P, x0, x1, y, a, label=None, col=None, la=1.0):
    if a <= 0: return
    c = col or L.FG
    P.line(x0, y, x1, y, c, a, w=5)
    P.line(x0, y - 18, x0, y + 18, c, a, w=5)
    P.line(x1, y - 18, x1, y + 18, c, a, w=5)
    if label:
        P.pill(label, (x0 + x1) / 2, y + 52, 30, c, a * la, fill_a=0.08)


def warn_tri(P, x, y, s, a):
    if a <= 0: return
    pth = skia.Path(); pth.moveTo(x, y - 52 * s); pth.lineTo(x + 58 * s, y + 46 * s); pth.lineTo(x - 58 * s, y + 46 * s); pth.close()
    P.c.drawPath(pth, paint(L.RED, a))
    P.text("!", x, y + 34 * s, 70 * s, L.WHITE, a, face=C.FONT_BLACK)


def check(P, x, y, s, a, col=None):
    if a <= 0: return
    pth = skia.Path(); pth.moveTo(x - 30 * s, y); pth.lineTo(x - 8 * s, y + 24 * s); pth.lineTo(x + 34 * s, y - 26 * s)
    P.c.drawPath(pth, paint(col or L.FG, a, 12 * s))


def ring(P, x, y, r, frac, a, col=None, label=None):
    if a <= 0: return
    P.circle(x, y, r, L.DIM, a, stroke=12)
    P.c.drawArc(skia.Rect(x - r, y - r, x + r, y + r), -90, 360 * clamp(frac), False, paint(col or L.RED, a, 12))
    if label:
        P.text(label, x, y + 26, 76, col or L.RED, a, face=C.FONT_BLACK)


def fmt(v):
    return f"{v:.1f}".replace(".", ",") + " s"


# =============================================================== escenas
def road_scene(P, t):
    c = CUE
    a = 1 - window(t, c["r0"] - 0.1, c["li0"] + 0.25, 0.4, 0.45)
    if a <= 0: return
    xm = x_me(t); xr = X_AH - HALF; xf = xm + HALF
    with P.layer(a), P.transform(0, 0, SC, cx=540, cy=ROAD_Y):
        road(P, t)
        # luces de freno del auto de adelante
        b_ah = max(1 - prog(t, c["s0"] - 0.4, c["s0"]),
                   window(t, c["ac0"] - 0.2, c["r0"], 0.3, 0.3),
                   window(t, c["ci0"] - 0.2, c["end"] + 1.0, 0.3, 0.4))
        # mis luces de freno
        b_me = max(window(t, c["solo"] - 0.1, c["s0"] - 0.3, 0.15, 0.3),
                   window(t, c["frenael"] - 0.05, c["r0"], 0.15, 0.3),
                   window(t, c["frenó"] - 0.05, c["end"] - 0.5, 0.15, 0.4))
        sens = max(window(t, c["sensor"] - 0.2, c["cu0"], 0.3, 0.4), window(t, c["midió"] - 0.2, c["end"] - 0.6, 0.3, 0.4),
                   window(t, c["li0"], c["fallar"] + 0.8, 0.3, 0.4))
        car(P, X_AH, ROAD_Y, 1, brake=b_ah)
        tu = prog(t, c["tú"] - 0.15, c["tú"] + 0.2) * (1 - prog(t, c["ci0"] - 0.3, c["ci0"]))
        car(P, xm, ROAD_Y, 1, brake=b_me, sensor=sens, outline=lerp_c(L.FG, L.RED, tu), glow_cabin=tu)
        # marcas de frenado
        sk = max(window(t, c["solo"], c["s0"] - 0.3, 0.3, 0.3), window(t, c["frenael"], c["r0"], 0.3, 0.3),
                 window(t, c["frenó"], c["end"] - 0.5, 0.3, 0.3))
        if sk > 0:
            P.line(xm - 160, ROAD_Y + 2, xm - 60, ROAD_Y + 2, L.GRAY, sk * 0.8, w=7)
        # celular (distracción)
        pa = max((1 - prog(t, c["s0"] - 0.4, c["s0"])) * (t < c["s0"]),
                 window(t, c["tú"] - 0.3, c["ci0"], 0.3, 0.3),
                 prog(t, c["end"] - 0.9, c["end"] - 0.2))
        cr = prog(t, c["tú"] + 0.1, c["tú"] + 0.45) * (1 - prog(t, c["ci0"] - 0.3, c["ci0"]))
        phone_icon(P, xm - 10, ROAD_Y - 230 + 5 * math.sin(t * 2.5), pa, 0.95, crossed=cr)
        q = window(t, c["chocar"] - 0.2, c["s0"] - 0.05, 0.25, 0.3) + window(t, c["ci0"] - 0.1, c["midió"], 0.25, 0.3)
        if q > 0:
            P.text("?", (xf + xr) / 2, ROAD_Y - 220 + 6 * math.sin(t * 3), 170, L.RED, min(q, 1), face=C.FONT_BLACK)
        # distancia y rapidez
        da = window(t, c["distancia"] - 0.2, c["cu0"] + 0.3, 0.3, 0.4) + window(t, c["e_dist"] - 0.2, c["ac0"] + 0.4, 0.3, 0.4) * 0
        da = window(t, c["distancia"] - 0.2, c["ac0"] - 0.1, 0.3, 0.4)
        lab = "distancia"
        if t > c["treinta"] - 0.1: lab = "30 m"
        hi = pulse(t, c["e_dist"] - 0.1, 0.8) + pulse(t, c["treinta"] - 0.1, 0.8)
        bracket(P, xf + 6, xr - 6, ROAD_Y + 50, da, lab, col=lerp_c(L.FG, L.RED, clamp(hi)))
        # fantasma: la distancia anterior (rapidez)
        ga = window(t, c["otra"] - 0.1, c["cu0"] + 0.2, 0.3, 0.4)
        if ga > 0:
            g_old = gap(c["otra"] - 0.15)
            bracket(P, xr - 6 - g_old, xr - 6, ROAD_Y + 130, ga * 0.5, None, col=L.GRAY)
            sa = prog(t, c["achica"] - 0.15, c["achica"] + 0.3)
            P.arrow(xr - g_old - 6, ROAD_Y + 160, xf + 6, ROAD_Y + 160, L.RED, ga * sa, w=6, head=20)
        ra = window(t, c["acercan"] - 0.2, c["ac0"] - 0.1, 0.3, 0.4)
        if ra > 0:
            ln = 150 * prog(t, c["acercan"] - 0.2, c["acercan"] + 0.4)
            P.arrow(xm - 40, ROAD_Y - 170, xm - 40 + ln, ROAD_Y - 170, L.RED, ra, w=8, head=26)
            rl = "rapidez" if t < c["cincuenta"] - 0.1 else "50 km/h"
            P.pill(rl, xm + 30, ROAD_Y - 235, 30, L.RED, ra * prog(t, c["acercan"], c["acercan"] + 0.3), fill_a=0.1)
        P.pill("radar", xf + 10, ROAD_Y - 150, 28, L.GRAY, window(t, c["radar"] - 0.2, c["e_dist"], 0.3, 0.4), fill_a=0.06)
        # ondas del sensor
        wa = max(window(t, c["lanza"] - 0.2, c["cu0"] + 0.2, 0.3, 0.4), window(t, c["midió"] - 0.2, c["frenó"] + 0.2, 0.3, 0.4),
                 window(t, c["li0"], c["tú"] - 0.2, 0.3, 0.4))
        broken = prog(t, c["lluvia"] - 0.1, c["fallar"] + 0.1)
        waves(P, t, c["lanza"] - 0.25 if t < c["ac0"] else c["midió"] - 0.25 if t > c["ci0"] else c["li0"],
              xf + 4, xr, ROAD_Y - 38, wa, broken=broken)
        if t > c["li0"] - 0.5 and t < c["ci0"]:
            limite_fx(P, t, xf, xr)


def limite_fx(P, t, xf, xr):
    c = CUE
    ra = window(t, c["lluvia"] - 0.2, c["ci0"] - 0.1, 0.3, 0.4)
    if ra > 0:
        for k in range(46):
            x = (k * 97 + 13) % 1100
            y = 470 + ((t * 900 + k * 173) % 760)
            P.line(x, y, x - 10, y + 36, L.GRAY, ra * 0.55, w=3)
    fa = window(t, c["niebla"] - 0.2, c["ci0"] - 0.1, 0.4, 0.4)
    if fa > 0:
        for k in range(3):
            P.rect(-100 + 60 * math.sin(t * 0.6 + k), 820 + k * 90, 1180, 980 + k * 90, L.GRAY, fa * 0.16, radius=80, blur=40)
    fl = window(t, c["fallar"] - 0.15, c["tú"] - 0.1, 0.25, 0.3)
    if fl > 0:
        cx = (xf + xr) / 2; cy = ROAD_Y - 40
        P.line(cx - 40, cy - 40, cx + 40, cy + 40, L.RED, fl, w=11)
        P.line(cx + 40, cy - 40, cx - 40, cy + 40, L.RED, fl, w=11)
    P.pill("tú", x_me(t) - 10, ROAD_Y - 330, 40, L.RED, window(t, c["tú"] - 0.15, c["ci0"], 0.25, 0.35), fill_a=0.12)


def formula_scene(P, t):
    c = CUE
    a = window(t, c["cu0"] - 0.2, c["ac0"] - 0.05, 0.4, 0.35)
    if a <= 0: return
    y0 = 590
    num_a = prog(t, c["f_dist"] - 0.15, c["f_dist"] + 0.25)
    den_a = prog(t, c["f_rap"] - 0.15, c["f_rap"] + 0.25)
    res_a = prog(t, c["segundos"] - 0.15, c["segundos"] + 0.3)
    e30 = prog(t, c["treinta"] - 0.1, c["treinta"] + 0.25)
    e50 = prog(t, c["cincuenta"] - 0.1, c["cincuenta"] + 0.25)
    e2 = prog(t, c["dos"] - 0.15, c["dos"] + 0.3)
    with P.layer(a):
        fx = 300
        P.text("distancia", fx, y0 - 30 - 20 * (1 - num_a), 66, L.FG, num_a * (1 - e30), face=C.FONT_BOLD)
        P.text("30 m", fx, y0 - 30, 80, L.FG, e30, face=C.FONT_BLACK)
        P.line(fx - 170, y0, fx - 170 + 340 * den_a, y0, L.FG, max(num_a, den_a) * 0.9, w=6)
        P.text("rapidez", fx, y0 + 80 + 20 * (1 - den_a), 66, L.FG, den_a * (1 - e50), face=C.FONT_BOLD)
        P.text("50 km/h", fx, y0 + 85, 72, L.FG, e50, face=C.FONT_BLACK)
        P.text("=", 560, y0 + 26, 90, L.FG, res_a, face=C.FONT_BLACK)
        with P.transform(0, 0, 0.8 + 0.2 * out_back(res_a), cx=790, cy=y0):
            P.text("segundos", 790, y0 + 22, 66, L.RED, res_a * (1 - e2), face=C.FONT_BLACK)
            P.text("para chocar", 790, y0 + 90, 40, L.GRAY, res_a * (1 - e2), face=C.FONT_SEMI)
        with P.transform(0, 0, 0.7 + 0.3 * out_back(e2), cx=790, cy=y0):
            P.text("≈ " + fmt(2.16), 790, y0 + 34, 100, L.RED, e2, face=C.FONT_BLACK)


def actua_scene(P, t):
    c = CUE
    a = window(t, c["ac0"] - 0.05, c["r0"], 0.35, 0.4)
    if a <= 0: return
    # cuenta regresiva: de 2,2 s hasta frenar
    v = keyed(t, [(c["ac0"] - 0.2, 2.16), (c["avisa"], 1.5), (c["frenael"], 0.8), (c["frenael"] + 0.6, 0.6)])
    stop = prog(t, c["frenael"] + 0.4, c["frenael"] + 0.8)
    with P.layer(a):
        ra = 1 - prog(t, c["fuerza"] - 0.4, c["fuerza"])
        col = lerp_c(L.RED, L.FG, stop)
        ring(P, 540, 620, 125, v / 2.16, ra, col=col, label=fmt(v) if stop < 0.5 else None)
        check(P, 540, 620, 1.6, ra * stop)
        wa = prog(t, c["avisa"] - 0.15, c["avisa"] + 0.15) * (1 - prog(t, c["frenael"] - 0.3, c["frenael"]))
        blink = 0.55 + 0.45 * (1 if (t * 4) % 1 < 0.6 else 0)
        warn_tri(P, 250, 600, 1.0, wa * blink)
        P.pill("aviso", 250, 720, 30, L.RED, wa, fill_a=0.1)
        # fuerza de freno: tu pie + lo que completa el auto
        fa = window(t, c["fuerza"] - 0.45, c["r0"] + 0.1, 0.35, 0.4)
        if fa > 0:
            x0, x1, y = 190, 890, 650
            P.text("fuerza de freno", 540, 560, 40, L.GRAY, fa, face=C.FONT_SEMI)
            P.rect(x0, y - 34, x1, y + 34, L.FG, fa, stroke=5, radius=16)
            me = 0.35 * prog(t, c["suave"] - 0.2, c["suave"] + 0.3)
            P.rect(x0 + 8, y - 26, x0 + 8 + (x1 - x0 - 16) * me, y + 26, L.FG, fa, radius=10)
            ext = prog(t, c["fuerza"] - 0.05, c["fuerza"] + 0.5, out_cubic)
            xa = x0 + 8 + (x1 - x0 - 16) * me
            P.rect(xa, y - 26, xa + (x1 - 8 - xa) * ext, y + 26, L.RED, fa, radius=10)
            P.text("tu pie", x0 + 8 + (x1 - x0 - 16) * 0.175, y + 90, 34, L.FG, fa * prog(t, c["suave"], c["suave"] + 0.3), face=C.FONT_BOLD)
            P.text("el auto", xa + (x1 - 8 - xa) * 0.5, y + 90, 34, L.RED, fa * ext, face=C.FONT_BOLD)


def resultado_scene(P, t):
    c = CUE
    a = window(t, c["r0"] - 0.1, c["li0"] + 0.2, 0.4, 0.45)
    if a <= 0: return
    with P.layer(a):
        q = window(t, c["r0"] + 0.05, c["iihs"] - 0.1, 0.25, 0.3)
        P.text("?", 540, 820 + 6 * math.sin(t * 3), 220, L.RED, q, face=C.FONT_BLACK)
        ba = prog(t, c["iihs"] - 0.2, c["iihs"] + 0.3)
        P.pill("IIHS · EE. UU.", 540, 520, 30, L.GRAY, ba, fill_a=0.06)
        P.text("choques por alcance", 540, 610, 44, L.FG, prog(t, c["alcance"] - 0.6, c["alcance"]), face=C.FONT_BOLD)
        base = 1200
        h1 = 440 * prog(t, c["iihs"], c["iihs"] + 0.8)
        h2 = lerp(h1, 220, prog(t, c["mitad"] - 0.1, c["mitad"] + 0.6))
        P.rect(250, base - h1, 470, base, L.GRAY, ba * 0.8, radius=14)
        P.rect(610, base - h2, 830, base, L.RED, ba, radius=14)
        P.text("sin frenado", 360, base + 50, 32, L.FG, ba, face=C.FONT_SEMI)
        P.text("automático", 360, base + 88, 32, L.FG, ba, face=C.FONT_SEMI)
        P.text("con frenado", 720, base + 50, 32, L.FG, ba, face=C.FONT_SEMI)
        P.text("automático", 720, base + 88, 32, L.FG, ba, face=C.FONT_SEMI)
        ma = prog(t, c["mitad"] + 0.1, c["mitad"] + 0.5)
        with P.transform(0, 0, 0.8 + 0.2 * out_back(ma), cx=720, cy=base - 300):
            P.text("−50 %", 720, base - 270, 96, L.RED, ma, face=C.FONT_BLACK)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, GAPK, _OFF
    TL, EP = tl, episode
    c = {}
    c["frena"] = T("hook", "frena"); c["celular"] = T("hook", "celular"); c["solo"] = T("hook", "solo")
    c["chocar"] = T("hook", "chocar")
    c["s0"] = T("saber"); c["distancia"] = T("saber", "distancia"); c["acercan"] = T("saber", "acercan")
    c["e0"] = T("eco"); c["sensor"] = T("eco", "sensor"); c["radar"] = T("eco", "radar"); c["lanza"] = T("eco", "lanza")
    c["rebota"] = T("eco", "rebota"); c["e_dist"] = T("eco", "distancia")
    c["otra"] = T("rapidez", "otra"); c["achica"] = T("rapidez", "achica")
    c["cu0"] = T("cuenta"); c["f_dist"] = T("cuenta", "distancia"); c["f_rap"] = T("cuenta", "rapidez")
    c["segundos"] = T("cuenta", "segundos")
    c["ej0"] = T("ejemplo"); c["treinta"] = T("ejemplo", "treinta"); c["cincuenta"] = T("ejemplo", "cincuenta")
    c["dos"] = T("ejemplo", "dos")
    c["ac0"] = T("actua"); c["avisa"] = T("actua", "avisa"); c["frenael"] = T("actua", "frena")
    c["suave"] = T("actua", "suave"); c["fuerza"] = T("actua", "fuerza")
    c["r0"] = T("resultado"); c["iihs"] = T("resultado", "IIHS"); c["mitad"] = T("resultado", "mitad")
    c["alcance"] = T("resultado", "alcance")
    c["li0"] = T("limite"); c["lluvia"] = T("limite", "lluvia"); c["niebla"] = T("limite", "niebla")
    c["fallar"] = T("limite", "fallar"); c["tú"] = T("limite", "tú")
    c["ci0"] = T("cierre"); c["midió"] = T("cierre", "Midió"); c["frenó"] = T("cierre", "frenó")
    c["end"] = tl.duration
    CUE = c
    # distancia entre autos (px) y rapidez del camino (px/s)
    GAPK = [(0.0, 300), (c["solo"] + 0.1, 150), (c["solo"] + 0.7, 110),
            (c["s0"] - 0.35, 110), (c["s0"] + 0.35, 330), (c["cu0"], 270),
            (c["ac0"], 265), (c["frenael"] + 0.1, 160), (c["frenael"] + 0.8, 125),
            (c["li0"] - 0.3, 125), (c["li0"] + 0.2, 280), (c["ci0"] - 0.3, 270), (c["ci0"] + 0.2, 320),
            (c["frenó"] + 0.1, 160), (c["frenó"] + 0.7, 120), (c["end"] - 0.9, 120), (c["end"] - 0.05, 300)]
    spd = [(0.0, 900), (c["frena"], 900), (c["solo"] + 0.6, 0), (c["s0"] - 0.1, 0), (c["s0"] + 0.4, 520),
           (c["ac0"] + 0.2, 520), (c["frenael"] + 0.8, 0), (c["li0"] - 0.2, 0), (c["li0"] + 0.4, 520),
           (c["frenó"], 520), (c["frenó"] + 0.8, 0), (c["end"] - 0.9, 0), (c["end"], 900)]
    n = int(tl.duration * FPS_INT) + 2
    v = np.array([keyed(i / FPS_INT, spd) for i in range(n)])
    _OFF = np.cumsum(v) / FPS_INT
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["segundos"] - 0.2, 1.3) + 0.6 * pulse(t, c["dos"] - 0.2, 1.3) \
        + 0.5 * pulse(t, c["mitad"] - 0.1, 1.2)
    L.background(P, t, glow=glow)
    # el aviso, el frenado: un leve sacudón
    shake = 6 * pulse(t, c["solo"], 0.35) + 6 * pulse(t, c["frenael"] + 0.1, 0.35) + 5 * pulse(t, c["frenó"] + 0.1, 0.35)
    with P.transform(shake * math.sin(t * 70), 0):
        road_scene(P, t)
        formula_scene(P, t)
        actua_scene(P, t)
        resultado_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    P.text("¿CÓMO SUPO", 540, 540, 104, L.FG, 1, face=C.FONT_BLACK)
    P.text("TU AUTO QUE", 540, 650, 104, L.FG, 1, face=C.FONT_BLACK)
    P.text("IBAS A CHOCAR?", 540, 765, 100, L.RED, 1, face=C.FONT_BLACK)
    with P.transform(0, 130, SC, cx=540, cy=ROAD_Y):
        road(P, 0.0)
        car(P, X_AH, ROAD_Y, 1, brake=1.0)
        xm = X_AH - 2 * HALF - 230
        car(P, xm, ROAD_Y, 1, sensor=1.0)
        waves(P, 0.25, 0.0, xm + HALF + 4, X_AH - HALF, ROAD_Y - 38, 1.0)
        phone_icon(P, xm - 10, ROAD_Y - 220, 1.0, 0.95)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (c["frena"], "pop_low", 0.4), (c["celular"], "tick", 0.3),
            (c["solo"], "thump", 0.55), (c["chocar"], "pop", 0.4),
            (c["s0"] - 0.35, "rewind", 0.35), (c["distancia"], "tick", 0.35), (c["acercan"], "whoosh", 0.3),
            (c["sensor"], "pop", 0.35), (c["lanza"], "tick", 0.3), (c["rebota"], "tick", 0.3), (c["e_dist"], "pop", 0.4),
            (c["achica"], "pop_low", 0.4),
            (c["cu0"] - 0.2, "whoosh", 0.3), (c["f_dist"], "tick", 0.3), (c["f_rap"], "tick", 0.3),
            (c["segundos"], "ding", 0.55),
            (c["treinta"], "tick", 0.35), (c["cincuenta"], "tick", 0.35), (c["dos"], "ding", 0.55),
            (c["avisa"], "pop", 0.45), (c["avisa"] + 0.25, "pop", 0.35), (c["frenael"], "thump", 0.55),
            (c["fuerza"], "riser", 0.3),
            (c["r0"] - 0.2, "whoosh", 0.35), (c["mitad"], "ding", 0.6),
            (c["li0"] - 0.2, "whoosh", 0.3), (c["fallar"], "pop_low", 0.45), (c["tú"], "pop", 0.4),
            (c["ci0"] - 0.2, "whoosh", 0.35), (c["frenó"], "thump", 0.5)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["cu0"], "pulse": (c["ac0"], c["li0"]), "quiet": [(c["chocar"] - 0.1, c["s0"] + 0.2)]}
