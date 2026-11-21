"""Escenas — «¿Y si frenar recargara tu auto?» (stheq.ia, motion graphics).

Hilo visual: un auto frena ante un semáforo y sus discos se ponen rojos (calor que se pierde) → se abre
el esquema batería → motor → rueda con la corriente fluyendo hacia la rueda → al soltar el acelerador
la rueda hace girar al motor, que pasa a llamarse «generador», y la corriente (roja) vuelve a la batería,
que se llena → ciudad vs carretera (≈ 32 % en ciudad, DOE) → el mismo auto vuelve a frenar ante el
semáforo, pero ahora la energía de las ruedas viaja a su batería (empalme con el inicio).
Sin fotos: todo se dibuja. Las respuestas aparecen cuando la voz las dice.
"""
from __future__ import annotations
import math
import numpy as np
import skia
from PIL import Image
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic, smooth
from reelforge import marca as L

TL = None; EP = {}; CHUNKS = []; CUE = {}
_IMG = {}
CAR_X, CAR_Y = 430, 930       # posición del auto en las escenas de calle
ROAD_Y = 1035
LIGHT_X = 880                 # dónde queda el semáforo cuando el auto se detiene
WR = 62                       # radio de rueda del auto


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


# =============================================================== movimiento del auto
def remaining(t, t0, t1, D):
    """Distancia que le falta al auto para detenerse. Velocidad constante antes de t0 y frenado
    uniforme entre t0 y t1 (sin saltos de velocidad)."""
    T_ = max(1e-3, t1 - t0)
    v0 = 2 * D / T_
    if t < t0: return D + v0 * (t0 - t)
    u = clamp((t - t0) / T_)
    return D * (1 - u) ** 2


# =============================================================== objetos
def wheel(P, x, y, r, rot, a=1.0, glow=0.0, rim=None):
    if a <= 0: return
    with P.layer(a):
        P.circle(x, y, r, (0.05, 0.05, 0.05), 1)
        P.circle(x, y, r, rim or L.FG, 1, stroke=r * 0.17)
        disc = lerp_c(L.GRAY, L.RED, glow)
        if glow > 0:
            P.circle(x, y, r * 0.9, L.RED, 0.55 * glow, blur=r * 0.35)
        P.circle(x, y, r * 0.55, disc, 1, stroke=r * 0.1)
        for k in range(5):
            ang = rot + k * 2 * math.pi / 5
            P.line(x + math.cos(ang) * r * 0.16, y + math.sin(ang) * r * 0.16,
                   x + math.cos(ang) * r * 0.62, y + math.sin(ang) * r * 0.62, L.FG, 1, w=r * 0.09)
        P.circle(x, y, r * 0.14, L.FG, 1)


def car(P, x, y, s=1.0, a=1.0, rot=0.0, glow=0.0, batt=0.6, batt_red=0.0, batt_a=1.0):
    """Auto eléctrico de perfil, mirando a la derecha, con su batería bajo el piso."""
    if a <= 0: return
    with P.layer(a):
        P.rect(x - 250 * s, y + 70 * s, x + 250 * s, y + 92 * s, (0, 0, 0), 0.6, radius=10, blur=14)
        pth = skia.Path()
        pth.moveTo(x - 255 * s, y + 40 * s)
        pth.lineTo(x - 255 * s, y - 40 * s)
        pth.quadTo(x - 250 * s, y - 70 * s, x - 200 * s, y - 75 * s)
        pth.lineTo(x - 140 * s, y - 80 * s)
        pth.quadTo(x - 90 * s, y - 165 * s, x - 10 * s, y - 165 * s)
        pth.lineTo(x + 70 * s, y - 165 * s)
        pth.quadTo(x + 130 * s, y - 160 * s, x + 175 * s, y - 85 * s)
        pth.quadTo(x + 255 * s, y - 70 * s, x + 262 * s, y - 25 * s)
        pth.lineTo(x + 262 * s, y + 40 * s)
        pth.close()
        P.c.drawPath(pth, paint(L.FG, 1))
        # ventanas
        win = skia.Path()
        win.moveTo(x - 118 * s, y - 85 * s); win.quadTo(x - 78 * s, y - 148 * s, x - 15 * s, y - 148 * s)
        win.lineTo(x + 66 * s, y - 148 * s); win.quadTo(x + 115 * s, y - 140 * s, x + 148 * s, y - 85 * s); win.close()
        P.c.drawPath(win, paint(L.BG, 0.92))
        P.line(x + 20 * s, y - 150 * s, x + 20 * s, y - 85 * s, L.FG, 1, w=10 * s)
        P.rect(x + 238 * s, y - 40 * s, x + 262 * s, y - 20 * s, L.GRAY, 1, radius=6)          # faro
        P.rect(x - 256 * s, y - 40 * s, x - 240 * s, y - 15 * s, L.RED, 0.5 + 0.5 * glow, radius=5)  # luz de freno
        if glow > 0:
            P.circle(x - 250 * s, y - 28 * s, 40 * s, L.RED, 0.45 * glow, blur=18)
        # batería bajo el piso
        if batt_a > 0:
            bx0, bx1, by0, by1 = x - 150 * s, x + 150 * s, y + 8 * s, y + 38 * s
            P.rect(bx0, by0, bx1, by1, L.BG, batt_a * 0.95, radius=8 * s)
            fill_c = lerp_c(L.FG, L.RED, batt_red)
            P.rect(bx0 + 5 * s, by0 + 5 * s, bx0 + 5 * s + (bx1 - bx0 - 10 * s) * clamp(batt), by1 - 5 * s, fill_c, batt_a, radius=5 * s)
            for k in range(1, 6):
                xx = lerp(bx0, bx1, k / 6)
                P.line(xx, by0 + 3, xx, by1 - 3, L.BG, batt_a, w=3)
            if batt_red > 0:
                P.rect(bx0 - 6, by0 - 6, bx1 + 6, by1 + 6, L.RED, 0.35 * batt_red, radius=12, blur=10)
        for wx in (-160, 168):
            wheel(P, x + wx * s, y + 45 * s, WR * s, rot, 1, glow)


def road(P, offset, a=1.0):
    if a <= 0: return
    with P.layer(a):
        P.line(40, ROAD_Y, 1040, ROAD_Y, L.GRAY, 1, w=5)
        sp = 170
        off = offset % sp
        for k in range(-1, 8):
            x0 = 40 + k * sp - off
            x0c, x1c = max(40, x0), min(1040, x0 + 80)
            if x1c > x0c:
                P.line(x0c, ROAD_Y + 70, x1c, ROAD_Y + 70, L.DIM, 1, w=7)


def traffic_light(P, x, a=1.0):
    if a <= 0 or x > 1200: return
    with P.layer(a):
        P.line(x, ROAD_Y, x, 640, L.GRAY, 1, w=12)
        P.rect(x - 44, 500, x + 44, 700, L.CARD, 1, radius=20)
        P.rect(x - 44, 500, x + 44, 700, L.GRAY, 1, stroke=4, radius=20)
        P.circle(x, 545, 25, L.RED, 0.25, blur=16)
        P.circle(x, 545, 22, L.RED, 1)
        P.circle(x, 600, 22, L.DIM, 1)
        P.circle(x, 655, 22, L.DIM, 1)


def heat(P, x, y, t, amt, seed=0):
    """Ondas de calor que suben desde un disco de freno."""
    if amt <= 0: return
    for k in range(3):
        xx = x + (k - 1) * 26
        pth = skia.Path()
        for j in range(15):
            u = j / 14
            yy = y - 70 - u * 150
            x_ = xx + math.sin(u * 8 - t * 7 + k + seed) * 10
            (pth.moveTo if j == 0 else pth.lineTo)(x_, yy)
        P.c.drawPath(pth, paint(L.RED, 0.75 * amt * (0.6 + 0.4 * math.sin(t * 5 + k)), stroke=5))


def battery(P, x, y, w, h, f, a=1.0, red=0.0, label=None):
    if a <= 0: return
    with P.layer(a):
        P.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, L.FG, 1, stroke=6, radius=16)
        P.rect(x - 26, y - h / 2 - 20, x + 26, y - h / 2, L.FG, 1, radius=5)
        hh = (h - 28) * clamp(f)
        col = lerp_c(L.FG, L.RED, red)
        P.rect(x - w / 2 + 14, y + h / 2 - 14 - hh, x + w / 2 - 14, y + h / 2 - 14, col, 1, radius=8)
        if red > 0:
            P.rect(x - w / 2 - 8, y - h / 2 - 8, x + w / 2 + 8, y + h / 2 + 8, L.RED, 0.35 * red, radius=22, blur=14)
        if label:
            P.text(label, x, y + h / 2 + 62, 34, L.GRAY, 1, face=C.FONT_BOLD, tracking=1)


def motor(P, x, y, r, rot, a=1.0, gen=0.0):
    """Motor eléctrico: carcasa, bobinas y rotor. gen>0 lo tiñe de rojo (modo generador)."""
    if a <= 0: return
    col = lerp_c(L.FG, L.RED, gen)
    with P.layer(a):
        if gen > 0:
            P.circle(x, y, r * 1.35, L.RED, 0.25 * gen, blur=30)
        P.circle(x, y, r, L.CARD, 1)
        P.circle(x, y, r, col, 1, stroke=10)
        for k in range(8):                      # bobinas fijas
            ang = k * math.pi / 4
            P.circle(x + math.cos(ang) * r * 0.8, y + math.sin(ang) * r * 0.8, r * 0.1, L.GRAY, 1)
        for k in range(3):                      # rotor
            ang = rot + k * 2 * math.pi / 3
            P.line(x - math.cos(ang) * r * 0.55, y - math.sin(ang) * r * 0.55,
                   x + math.cos(ang) * r * 0.55, y + math.sin(ang) * r * 0.55, col, 1, w=r * 0.16)
        P.circle(x, y, r * 0.16, L.FG, 1)


def dots(P, x0, x1, y, phase, rgb, a=1.0, n=6, r=11):
    """Cargas que viajan por un cable de x0 a x1; phase en «espacios» recorridos."""
    if a <= 0: return
    for k in range(n):
        u = ((k + phase) / n) % 1.0
        x = lerp(x0, x1, u)
        edge = min(u, 1 - u) * 8
        P.circle(x, y, r, rgb, a * clamp(edge), blur=0)
        P.circle(x, y, r * 2.2, rgb, 0.18 * a * clamp(edge), blur=8)


_INT = {}
def integ(fn, key, t0, t, n=240):
    """∫ fn(τ) dτ de t0 a t (trapecios), para fases continuas aunque la velocidad cambie."""
    if t <= t0: return 0.0
    k = (key, round(t, 4))
    if k in _INT: return _INT[k]
    xs = np.linspace(t0, t, n)
    ys = np.array([fn(x) for x in xs])
    v = float(np.trapezoid(ys, xs)) if hasattr(np, "trapezoid") else float(np.trapz(ys, xs))
    if len(_INT) > 4000: _INT.clear()
    _INT[k] = v
    return v


# =============================================================== escenas
def street_hook(P, t):
    c = CUE
    a = 1 - prog(t, c["m0"] - 0.45, c["m0"] + 0.15, in_out_cubic)
    if a <= 0: return
    d = remaining(t, 0.0, c["stop1"], 460)
    with P.layer(a):
        road(P, -d * 1.0)
        traffic_light(P, LIGHT_X + d, 1)
        g = prog(t, c["frenas"] - 0.1, c["frenas"] + 0.5) * (1 - 0.6 * prog(t, c["m0"] - 1.2, c["m0"]))
        g = max(g, 0.25 + 0.25 * math.sin(t * 6)) if t < c["frenas"] else g
        car(P, CAR_X, CAR_Y, 1.0, 1, rot=-d * 2.4 / WR, glow=g, batt=0.55, batt_a=0.0)
        # líneas de velocidad mientras se mueve
        sp = clamp((d / 460) ** 0.5)
        for k in range(4):
            yy = CAR_Y - 120 + k * 45
            xx = CAR_X - 300 - ((t * 900 + k * 130) % 220)
            P.line(xx, yy, xx - 90 * sp, yy, L.GRAY, 0.6 * sp, w=4)
        h = prog(t, c["calor"] - 0.3, c["calor"] + 0.4) * (1 - prog(t, c["guardar"] + 0.2, c["m0"]))
        heat(P, CAR_X - 160, CAR_Y + 45, t, max(h, 0.6 * prog(t, c["pastillas"] - 0.2, c["pastillas"] + 0.4)), 0)
        heat(P, CAR_X + 168, CAR_Y + 45, t, max(h, 0.6 * prog(t, c["pastillas"] - 0.2, c["pastillas"] + 0.4)), 2)
        ca = prog(t, c["calor"] - 0.1, c["calor"] + 0.35, lambda x: x)
        if ca > 0:
            with P.transform(0, (1 - out_back(ca)) * 20, 1):
                P.text("CALOR", CAR_X, 1230, 84, L.RED, ca, face=C.FONT_BLACK, tracking=4)
        q = prog(t, c["guardar"] - 0.1, c["guardar"] + 0.4, lambda x: x)
        if q > 0:
            P.text("?", CAR_X, 690 + 10 * math.sin(t * 3), 150, L.RED, out_back(q), face=C.FONT_BLACK)


# esquema batería → motor → rueda
BX, MX, WX, DY = 190, 540, 880, 880


def v_forward(t):
    c = CUE
    return 2.2 * prog(t, c["manda"] - 0.2, c["manda"] + 0.4) * (1 - prog(t, c["suelta"], c["suelta"] + 0.6, smooth))


def v_back(t):
    c = CUE
    return 2.2 * prog(t, c["gen"] - 0.2, c["gen"] + 0.5) * (1 - 0.35 * prog(t, c["frena"], c["frena"] + 1.0, smooth))


def w_wheel(t):
    c = CUE
    on = prog(t, c["girar"] - 0.2, c["girar"] + 0.5)
    slow = 1 - 0.55 * prog(t, c["frena"], c["frena"] + 1.2, smooth)
    return 5.0 * on * slow


def diagram(P, t):
    c = CUE
    a = window(t, c["m0"] - 0.2, c["d0"] + 0.15, 0.5, 0.5)
    if a <= 0: return
    with P.layer(a):
        fb = 0.7 - 0.08 * prog(t, c["manda"], c["suelta"]) + 0.2 * prog(t, c["vb"] - 0.2, c["frena"] + 1.2, smooth)
        red = prog(t, c["vb"] - 0.3, c["vb"] + 0.4) * 0.9
        battery(P, BX, DY, 150, 270, fb, prog(t, c["m0"] - 0.1, c["m0"] + 0.4), red, "BATERÍA")
        # cables
        wa = prog(t, c["m0"], c["m0"] + 0.5)
        P.line(BX + 75, DY, MX - 115, DY, L.DIM, wa, w=8)
        P.line(MX + 115, DY, WX - 115, DY, L.GRAY, wa, w=14)       # eje
        rot_w = integ(w_wheel, "w", c["m0"], t)
        gen = prog(t, c["gen"] - 0.15, c["gen"] + 0.45)
        motor(P, MX, DY, 115, rot_w * 1.6, prog(t, c["mot"] - 0.4, c["mot"] + 0.1), gen)
        wheel(P, WX, DY, 115, rot_w, prog(t, c["m0"] + 0.1, c["m0"] + 0.6), glow=0.0,
              rim=lerp_c(L.FG, L.RED, prog(t, c["ruedas"] - 0.1, c["ruedas"] + 0.4) * (1 - prog(t, c["vb"], c["vb"] + 0.6))))
        # etiqueta motor → generador
        la = prog(t, c["mot"] - 0.2, c["mot"] + 0.3)
        P.text("MOTOR", MX, DY + 177, 34, L.GRAY, la * (1 - gen), face=C.FONT_BOLD, tracking=1)
        if gen > 0:
            with P.transform(0, 0, 0.85 + 0.15 * out_back(gen), cx=MX, cy=DY + 165):
                P.text("GENERADOR", MX, DY + 177, 38, L.RED, gen, face=C.FONT_BLACK, tracking=1)
        # corriente hacia el motor (blanca) y de vuelta (roja)
        ph_f = integ(v_forward, "f", c["m0"], t)
        fa = prog(t, c["manda"] - 0.2, c["manda"] + 0.3) * (1 - prog(t, c["suelta"] + 0.2, c["suelta"] + 0.9))
        dots(P, BX + 85, MX - 125, DY, ph_f, L.FG, fa)
        ph_b = integ(v_back, "b", c["m0"], t)
        dots(P, MX - 125, BX + 85, DY, ph_b, L.RED, prog(t, c["gen"] - 0.1, c["gen"] + 0.4))
        # flecha: la rueda empuja al motor
        ra = prog(t, c["ruedas"] - 0.1, c["ruedas"] + 0.4) * (1 - prog(t, c["vb"], c["vb"] + 0.5))
        if ra > 0:
            P.arrow(WX - 40, DY - 190, MX + 60, DY - 190, L.RED, ra, w=8, head=28)
            P.text("la rueda empuja", (WX + MX) / 2 + 10, DY - 225, 32, L.RED, ra, face=C.FONT_BOLD)
        # flecha de energía hacia la batería
        ba = prog(t, c["vb"] - 0.1, c["vb"] + 0.4)
        if ba > 0:
            P.arrow(MX - 60, DY - 190, BX + 40, DY - 190, L.RED, ba, w=8, head=28)
            P.text("energía", (MX + BX) / 2, DY - 225, 32, L.RED, ba, face=C.FONT_BOLD)
        # el esfuerzo frena la rueda: arco en contra del giro
        fr = prog(t, c["frena"] - 0.1, c["frena"] + 0.4)
        if fr > 0:
            rr = 150
            P.c.drawArc(skia.Rect(WX - rr, DY - rr, WX + rr, DY + rr), 200, -110 * fr, False, paint(L.RED, fr, stroke=8))
            ang = math.radians(200 - 110 * fr)
            hx, hy = WX + rr * math.cos(ang), DY + rr * math.sin(ang)
            P.circle(hx, hy, 10, L.RED, fr)
            P.text("frena", WX, DY + 225, 36, L.RED, fr, face=C.FONT_BLACK)
        pa = prog(t, c["frg"] - 0.1, c["frg"] + 0.4, lambda x: x)
        if pa > 0:
            P.pill("frenado regenerativo", 540, 1240, 46, L.RED, out_back(pa), face=C.FONT_BOLD)


def city(P, x, y, a):
    for k, (w, h) in enumerate([(60, 150), (70, 210), (55, 120), (65, 180)]):
        xx = x - 140 + k * 72
        P.rect(xx, y - h, xx + w, y, L.CARD, a)
        P.rect(xx, y - h, xx + w, y, L.GRAY, a, stroke=3)
        for j in range(int(h / 40)):
            P.rect(xx + 14, y - h + 18 + j * 40, xx + w - 14, y - h + 30 + j * 40, L.DIM, a)
    P.line(x - 160, y, x + 160, y, L.GRAY, a, w=4)
    for k in range(3):                       # semáforos
        lx = x - 110 + k * 110
        P.circle(lx, y + 36, 13, L.RED, a)


def highway(P, x, y, a):
    P.line(x - 160, y, x - 30, y - 200, L.GRAY, a, w=5)
    P.line(x + 160, y, x + 30, y - 200, L.GRAY, a, w=5)
    for k in range(4):
        u0, u1 = k / 4, k / 4 + 0.12
        P.line(x, y - 200 * u0, x, y - 200 * u1, L.FG, a, w=lerp(8, 3, u0))


def dato(P, t):
    c = CUE
    a = window(t, c["d0"] - 0.2, c["ci0"] + 0.15, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        ca = prog(t, c["ciudad"] - 0.3, c["ciudad"] + 0.3)
        city(P, 300, 760, ca)
        P.text("CIUDAD", 300, 870, 38, L.FG, ca, face=C.FONT_BLACK, tracking=2)
        ha = prog(t, c["carretera"] - 0.3, c["carretera"] + 0.3)
        highway(P, 780, 760, ha)
        P.text("CARRETERA", 780, 870, 38, L.FG, ha, face=C.FONT_BLACK, tracking=2)
        # barras (energía recuperada): la de ciudad crece con la cifra
        base = 1225
        bu = prog(t, c["p32"] - 0.3, c["p32"] + 0.7, in_out_cubic)
        P.line(120, base, 960, base, L.GRAY, ca, w=4)
        h32 = 180 * bu
        P.rect(300 - 80, base - h32, 300 + 80, base, L.RED, ca, radius=10)
        k = prog(t, c["p32"] - 0.05, c["p32"] + 0.35, lambda x: x)
        if k > 0:
            with P.transform(0, 0, 0.8 + 0.2 * out_back(k), cx=300, cy=base - 230):
                P.text("≈ 32 %", 300, base - 215, 76, L.FG, clamp(k * 1.5), face=C.FONT_BLACK)
        ea = prog(t, c["enchufe"] - 0.2, c["enchufe"] + 0.4)
        P.text("de la energía del enchufe", 300, base + 48, 30, L.GRAY, ea, face=C.FONT_BOLD)
        mu = prog(t, c["mucho"] - 0.2, c["mucho"] + 0.5, in_out_cubic)
        P.rect(780 - 80, base - 40 * mu, 780 + 80, base, L.GRAY, ha * clamp(mu * 3), radius=8)
        P.text("mucho menos", 780, base - 75, 48, L.FG, prog(t, c["mucho"], c["mucho"] + 0.35), face=C.FONT_BLACK)


def street_end(P, t):
    c = CUE
    a = prog(t, c["ci0"] - 0.2, c["ci0"] + 0.35)
    if a <= 0: return
    d = remaining(t, c["entonces"], c["stop2"], 460)
    with P.layer(a):
        road(P, -d)
        traffic_light(P, LIGHT_X + d, 1)
        braking = prog(t, c["entonces"], c["entonces"] + 0.5) * (1 - prog(t, c["stop2"] - 0.2, c["stop2"] + 0.4))
        fill = 0.55 + 0.2 * prog(t, c["entonces"] + 0.2, c["stop2"], smooth)
        red = prog(t, c["vuelveb"] - 0.3, c["vuelveb"] + 0.4)
        car(P, CAR_X, CAR_Y, 1.0, 1, rot=-d * 2.4 / WR, glow=0.25 * braking, batt=fill, batt_red=max(0.6 * braking, red))
        # discos de freno: resaltados cuando la voz los nombra
        fa = window(t, c["frenos"] - 0.15, c["gastan"] + 0.7, 0.35, 0.4)
        for wx in (-160, 168):
            P.circle(CAR_X + wx, CAR_Y + 45, WR + 18, L.FG, fa, stroke=5)
        P.text("menos desgaste", CAR_X + 4, 1230, 46, L.FG, window(t, c["gastan"] - 0.1, c["entonces"] + 0.2, 0.35, 0.4), face=C.FONT_BOLD)
        # la energía de las ruedas viaja a la batería (puntos rojos)
        if braking > 0:
            for wx in (-160, 168):
                for k in range(5):
                    u = ((t * 1.6 + k / 5) % 1.0)
                    sx, sy = CAR_X + wx, CAR_Y + 45
                    ex, ey = CAR_X + wx * 0.35, CAR_Y + 23
                    P.circle(lerp(sx, ex, u), lerp(sy, ey, u) - 30 * math.sin(math.pi * u), 9, L.RED, braking * (1 - u))
        sp = clamp((d / 460) ** 0.5) * prog(t, c["ci0"], c["ci0"] + 0.4)
        for k in range(4):
            yy = CAR_Y - 120 + k * 45
            xx = CAR_X - 300 - ((t * 900 + k * 130) % 220)
            P.line(xx, yy, xx - 90 * sp, yy, L.GRAY, 0.6 * sp, w=4)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["frenas"] = T("hook", "frenas"); c["pastillas"] = T("hook", "pastillas"); c["calor"] = T("hook", "calor")
    c["guardar"] = T("hook", "guardar"); c["stop1"] = T("hook", "pierde") + 0.4
    c["m0"] = T("motor"); c["manda"] = T("motor", "manda"); c["mot"] = T("motor", "motor"); c["girar"] = T("motor", "girar")
    c["suelta"] = T("reves", "acelerador"); c["ruedas"] = T("reves", "ruedas"); c["gen"] = T("reves", "generador")
    c["vb"] = T("vuelve", "batería"); c["frena"] = T("vuelve", "frena"); c["frg"] = T("vuelve", "regenerativo")
    c["d0"] = T("dato"); c["ciudad"] = T("dato", "ciudad"); c["p32"] = T("dato", "32")
    c["enchufe"] = T("dato", "enchufe"); c["carretera"] = T("dato", "carretera"); c["mucho"] = T("dato", "mucho")
    c["ci0"] = T("cierre"); c["frenos"] = T("cierre", "frenos"); c["gastan"] = T("cierre", "gastan")
    c["entonces"] = T("cierre", "entonces"); c["vuelveb"] = T("cierre", "batería")
    c["stop2"] = c["vuelveb"] - 0.1
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["gen"] - 0.2, 1.3) + 0.5 * pulse(t, c["p32"] - 0.2, 1.3) + 0.6 * prog(t, c["vuelveb"] - 0.2, c["vuelveb"] + 0.6)
    L.background(P, t, glow=glow)
    street_hook(P, t)
    diagram(P, t)
    dato(P, t)
    street_end(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    with P.transform(0, 200):
        road(P, 0)
        traffic_light(P, LIGHT_X)
        car(P, CAR_X, CAR_Y + 20, 1.0, 1, rot=0.3, glow=0.7, batt=0.75, batt_red=1.0)
    P.text("FRENA...", 540, 560, 110, L.FG, 1, face=C.FONT_BLACK)
    P.text("Y SE RECARGA", 540, 680, 100, L.RED, 1, face=C.FONT_BLACK)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.35), (c["frenas"], "whoosh_down", 0.45), (c["calor"], "thump", 0.5),
            (c["guardar"], "pop_low", 0.5),
            (c["m0"] - 0.3, "whoosh", 0.4), (c["manda"], "pop", 0.35), (c["girar"], "tick", 0.5),
            (c["suelta"], "whoosh_down", 0.35), (c["ruedas"], "pop", 0.45), (c["gen"] - 0.4, "riser", 0.3), (c["gen"], "ding", 0.6),
            (c["vb"], "pop", 0.45), (c["frena"], "thump", 0.45), (c["frg"], "ding", 0.55),
            (c["d0"] - 0.25, "whoosh", 0.4), (c["p32"], "ding", 0.6), (c["mucho"], "pop_low", 0.4),
            (c["ci0"] - 0.2, "whoosh_down", 0.4), (c["entonces"], "swell", 0.35), (c["vuelveb"], "ding", 0.65)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["gen"], "pulse": (c["d0"], c["ci0"]), "quiet": [(c["guardar"] - 0.2, c["m0"] + 0.2)]}
