"""Escenas — «¿Tu auto sabe que te estás durmiendo?» (stheq.ia, motion graphics).

Hilo visual: un ojo cansado sobre una carretera de noche; el párpado baja y la pantalla se oscurece → vista
desde arriba: el auto avanza 28 m en un segundo con los ojos cerrados y se desvía hacia el borde; contador de
91.000 choques → cara del conductor con una cámara en la columna del volante; se apaga la luz y la cara
desaparece; la luz infrarroja (rayos rojos) la hace visible para la cámara → primer plano del ojo: un parpadeo
rápido no cuenta; un párpado que baja lento y se queda cerrado, sí; barras de un minuto que se llenan →
PERCLOS → medidor que sube y alerta «¡descansa!» → anillo de estrellas de la UE con «julio 2026» → vuelta al
ojo sobre la carretera: el ojo y un reloj; el párpado vuelve a bajar (empalme con el inicio).
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
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic, smooth, in_cubic
from reelforge import marca as L

TL = None; EP = {}; CHUNKS = []; CUE = {}
_IMG = {}

EYE_X, EYE_Y = 540, 640


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


# =============================================================== objetos
def eye(P, x, y, s=1.0, o=1.0, a=1.0, col=None, iris_col=None, glow=0.0):
    """Ojo almendrado; o = apertura (1 abierto, 0 cerrado). El párpado superior baja hasta el inferior."""
    if a <= 0: return
    col = col or L.FG
    w, H = 170 * s, 80 * s
    yb = y + 1.1 * H                       # control del párpado inferior
    yt = lerp(y + 0.75 * H, y - 2.0 * H, clamp(o))
    top = skia.Path(); top.moveTo(x - w, y); top.quadTo(x, yt, x + w, y)
    full = skia.Path(); full.moveTo(x - w, y); full.quadTo(x, yt, x + w, y); full.quadTo(x, yb, x - w, y); full.close()
    with P.layer(a):
        if glow > 0:
            P.c.drawPath(full, paint(col, 0.35 * glow, blur=22))
        if o > 0.04:
            P.c.save(); P.c.clipPath(full, doAntiAlias=True)
            P.c.drawPath(full, paint(L.CARD, 1))
            P.circle(x, y + 6 * s, 58 * s, iris_col or L.GRAY, 1)
            P.circle(x, y + 6 * s, 25 * s, L.BG, 1)
            P.circle(x + 18 * s, y - 12 * s, 9 * s, L.FG, 0.8)
            P.c.restore()
        bot = skia.Path(); bot.moveTo(x - w, y); bot.quadTo(x, yb, x + w, y)
        P.c.drawPath(bot, paint(col, 0.7, stroke=5 * s))
        P.c.drawPath(top, paint(col, 1, stroke=8 * s))
        if o < 0.35:                       # pestañas del párpado cerrado
            k = 1 - o / 0.35
            for i in range(5):
                u = 0.2 + 0.15 * i
                px = lerp(x - w, x + w, u); py = (1 - u) ** 2 * y + 2 * u * (1 - u) * yt + u * u * y
                P.line(px, py, px + (u - 0.5) * 30 * s, py + 26 * s, col, k, w=4 * s)


def road(P, t, a=1.0, speed=1.0, y0=900, y1=1300):
    """Carretera en perspectiva, de noche, con líneas que avanzan."""
    if a <= 0: return
    with P.layer(a):
        pth = skia.Path(); pth.moveTo(500, y0); pth.lineTo(580, y0); pth.lineTo(980, y1); pth.lineTo(100, y1); pth.close()
        P.c.drawPath(pth, paint(L.CARD, 1))
        P.line(500, y0, 100, y1, L.FG, 0.8, w=5); P.line(580, y0, 980, y1, L.FG, 0.8, w=5)
        ph = (t * 0.55 * speed) % 1.0
        for k in range(6):
            u0 = (k / 6 + ph) % 1.0; u1 = min(1.0, u0 + 0.07)
            ya = y0 + (y1 - y0) * u0 ** 2; yb = y0 + (y1 - y0) * u1 ** 2
            P.line(540, ya, 540, yb, L.FG, 0.85 * smooth(clamp(u0 * 4)), w=3 + 12 * u0)
        P.line(380, y0 - 4, 700, y0 - 4, L.DIM, 0.6, w=2)


def car_top(P, x, y, a=1.0, rot=0.0):
    if a <= 0: return
    with P.layer(a), P.transform(0, 0, 1.0, rot, cx=x, cy=y):
        P.rect(x - 85, y - 42, x + 85, y + 42, L.FG, 1, radius=20)
        P.rect(x - 20, y - 34, x + 38, y + 34, L.CARD, 1, radius=10)
        P.rect(x + 50, y - 30, x + 72, y + 30, L.DIM, 1, radius=6)
        P.circle(x + 82, y - 30, 7, L.FG, 1); P.circle(x + 82, y + 30, 7, L.FG, 1)


def face(P, x, y, a=1.0, col=None, o=1.0):
    if a <= 0: return
    col = col or L.FG
    with P.layer(a):
        P.c.drawOval(skia.Rect.MakeLTRB(x - 170, y - 215, x + 170, y + 215), paint(col, 1, stroke=8))
        hair = skia.Path(); hair.moveTo(x - 168, y - 40); hair.quadTo(x - 150, y - 250, x, y - 218)
        hair.quadTo(x + 150, y - 250, x + 168, y - 40); hair.quadTo(x + 60, y - 150, x - 168, y - 40); hair.close()
        P.c.drawPath(hair, paint(col, 0.85))
        eye(P, x - 72, y - 5, 0.38, o, 1, col=col)
        eye(P, x + 72, y - 5, 0.38, o, 1, col=col)
        P.line(x, y + 25, x - 14, y + 85, col, 0.8, w=5); P.line(x - 14, y + 85, x + 10, y + 88, col, 0.8, w=5)
        P.c.drawArc(skia.Rect.MakeLTRB(x - 55, y + 95, x + 55, y + 150), 20, 140, False, paint(col, 0.8, stroke=6))


def camera(P, x, y, a=1.0, led=0.0, t=0.0):
    if a <= 0: return
    with P.layer(a):
        P.rect(x - 90, y - 38, x + 90, y + 38, L.CARD, 1, radius=16)
        P.rect(x - 90, y - 38, x + 90, y + 38, L.FG, 1, stroke=5, radius=16)
        P.circle(x, y, 24, L.BG, 1); P.circle(x, y, 24, L.FG, 1, stroke=4); P.circle(x, y, 9, L.GRAY, 1)
        for dx in (-62, 62):
            P.circle(x + dx, y, 10, L.DIM, 1)
            if led > 0:
                fl = 0.75 + 0.25 * math.sin(t * 14 + dx)
                P.circle(x + dx, y, 10, L.RED, led * fl)
                P.circle(x + dx, y, 22, L.RED, 0.35 * led * fl, blur=10)


def steering(P, x, y, a=1.0):
    if a <= 0: return
    P.c.drawArc(skia.Rect.MakeLTRB(x - 330, y - 160, x + 330, y + 500), 200, 140, False, paint(L.GRAY, a, stroke=26))


def star(P, x, y, r, rgb, a):
    pth = skia.Path()
    for k in range(10):
        rr = r if k % 2 == 0 else r * 0.42
        ang = -math.pi / 2 + k * math.pi / 5
        (pth.moveTo if k == 0 else pth.lineTo)(x + math.cos(ang) * rr, y + math.sin(ang) * rr)
    pth.close(); P.c.drawPath(pth, paint(rgb, a))


def alert(P, x, y, s, a):
    if a <= 0: return
    with P.layer(a), P.transform(0, 0, s, cx=x, cy=y):
        P.circle(x, y, 120, L.RED, 0.16); P.circle(x, y, 120, L.RED, 1, stroke=10)
        P.text("!", x, y + 52, 150, L.RED, 1, face=C.FONT_BLACK)


def blackout(P, a):
    if a > 0: P.rect(0, 330, 1080, 1340, L.BG, a)


# =============================================================== escenas
def openness_hook(t):
    c = CUE
    o = 0.62 - 0.08 * math.sin(t * 1.3)                          # cansado
    o = lerp(o, 0.32, prog(t, c["pesan"] - 0.2, c["pesan"] + 0.8, in_out_cubic))
    o = lerp(o, 0.0, prog(t, c["cierras"] - 0.1, c["segundo1"] + 0.3, in_out_cubic))
    o = lerp(o, 0.75, prog(t, c["dar"] - 0.5, c["dar"] + 0.1, out_cubic))   # se despierta de golpe
    return o


def hook_scene(P, t):
    c = CUE
    a = 1 - prog(t, c["s0"] - 0.35, c["s0"] + 0.15, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        o = openness_hook(t)
        road(P, t, 1, speed=1.0)
        eye(P, EYE_X, EYE_Y, 1.25, o)
        dark = prog(t, c["cierras"] + 0.1, c["segundo1"] + 0.4) * (1 - prog(t, c["dar"] - 0.5, c["dar"]))
        blackout(P, 0.85 * dark)
        q = prog(t, c["dar"] - 0.05, c["dar"] + 0.4, lambda u: u)
        if q > 0:
            P.text("?", 860, 690 + 6 * math.sin(t * 3), 130, L.RED, out_back(q) * clamp(q * 2), face=C.FONT_BLACK)


def second_scene(P, t):
    c = CUE
    a = window(t, c["s0"] - 0.3, c["c0"] + 0.1, 0.4, 0.45)
    if a <= 0: return
    with P.layer(a):
        ra_all = 1 - prog(t, c["estados"] - 0.35, c["estados"] + 0.05, in_out_cubic)
        if ra_all > 0:
            with P.layer(ra_all):
                ry0, ry1 = 820, 1060
                P.rect(0, ry0, 1080, ry1, L.CARD, 1)
                P.line(0, ry0, 1080, ry0, L.FG, 0.8, w=5); P.line(0, ry1, 1080, ry1, L.FG, 0.8, w=5)
                scroll = (t * 260) % 160
                for k in range(9):
                    xx = -160 + k * 160 - scroll
                    P.line(xx, (ry0 + ry1) / 2, xx + 80, (ry0 + ry1) / 2, L.FG, 0.6, w=6)
                u = prog(t, c["avanzas"] - 0.1, c["m28"] + 0.45, in_out_cubic)
                x = lerp(150, 880, u)
                drift = 75 * smooth(clamp((u - 0.35) / 0.65))
                cy = 995 - drift
                car_top(P, x, cy, 1, rot=-6 * smooth(clamp((u - 0.3) / 0.5)))
                eye(P, x, 740, 0.42, 0.0 if u > 0 else 0.5, 1)
                ra = prog(t, c["avanzas"] - 0.1, c["avanzas"] + 0.3)
                if ra > 0:
                    yb = 1130
                    P.line(150, yb, x, yb, L.RED, ra, w=6)
                    P.line(150, yb - 22, 150, yb + 22, L.RED, ra, w=6); P.line(x, yb - 22, x, yb + 22, L.RED, ra, w=6)
                    n = int(round(28 * u))
                    P.text(f"{n} m", (150 + x) / 2, yb + 85, 68, L.RED, ra, face=C.FONT_BLACK)
                    P.text("1 segundo con los ojos cerrados", 540, 620, 42, L.FG, ra, face=C.FONT_BOLD)
        k = prog(t, c["estados"], c["n91"] + 0.4, out_cubic)
        if k > 0:
            fade = prog(t, c["estados"] - 0.15, c["estados"] + 0.2)
            val = int(round(91000 * k / 1000.0)) * 1000
            s = f"{val:,}".replace(",", ".")
            with P.transform(0, 0, 0.9 + 0.1 * out_back(fade), cx=540, cy=880):
                P.text(s, 540, 920, 170, L.RED, fade, face=C.FONT_BLACK)
            P.text("choques por sueño en un año", 540, 1040, 46, L.FG, fade * prog(t, c["somnol"] - 0.2, c["somnol"] + 0.2), face=C.FONT_BOLD)
            P.text("EE.\u00a0UU. · estimación de la NHTSA", 540, 1110, 36, L.GRAY, fade * prog(t, c["somnol"] - 0.2, c["somnol"] + 0.2), face=C.FONT_SEMI)


def camera_scene(P, t):
    c = CUE
    a = window(t, c["c0"] - 0.3, c["p0"] + 0.1, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        dark = prog(t, c["oscuro"] - 0.2, c["oscuro"] + 0.3)
        ir = prog(t, c["infra"] - 0.2, c["infra"] + 0.5)
        fx, fy = 540, 760
        # rayos infrarrojos
        if ir > 0:
            for k in range(9):
                tx = fx - 160 + k * 40; ty = fy - 60 + 30 * math.sin(k)
                ph = (t * 1.6 + k * 0.13) % 1.0
                P.line(540, 1100, tx, ty, L.RED, 0.28 * ir, w=3)
                px, py = lerp(540, tx, ph), lerp(1100, ty, ph)
                P.circle(px, py, 5, L.RED, 0.8 * ir * (1 - ph))
        fa = 1 - 0.9 * dark * (1 - ir)
        fcol = lerp_c(L.FG, L.RED, 0.55 * ir)
        face(P, fx, fy, fa, col=fcol, o=0.85)
        steering(P, 540, 1150, 1)
        cam_a = prog(t, c["camara"] - 0.2, c["camara"] + 0.3)
        with P.transform(0, 0, 0.8 + 0.2 * out_back(cam_a), cx=540, cy=1100):
            camera(P, 540, 1100, cam_a, led=ir, t=t)
        la = prog(t, c["infra"] - 0.05, c["infra"] + 0.35)
        if la > 0:
            P.text("luz infrarroja", 540, 1240, 50, L.RED, la, face=C.FONT_BOLD)
        # «oscuro»: la cara desaparece
        if dark > 0 and ir < 1:
            P.text("?", 540, 800, 120, L.GRAY, dark * (1 - ir) * clamp((t - c["como"] + 0.1) * 3), face=C.FONT_BLACK)


def eye_open_p(t):
    """Apertura del ojo en primer plano: parpadeo rápido, luego cierre lento y sostenido."""
    c = CUE
    o = 1.0
    tb = c["rapido"] - 0.1
    if tb <= t <= tb + 0.32:
        o = abs(math.cos(math.pi * (t - tb) / 0.32))
    o = min(o, 1 - 0.9 * prog(t, c["lento"] - 0.2, c["lento"] + 1.0, in_out_cubic))
    o = min(1.0, max(o, prog(t, c["cuenta"] - 0.3, c["cuenta"] + 0.1)))
    return o


def eyelid_scene(P, t):
    c = CUE
    a = window(t, c["p0"] - 0.3, c["a0"] - 0.05, 0.45, 0.4)
    if a <= 0: return
    with P.layer(a):
        bars_on = prog(t, c["cuenta"] - 0.3, c["cuenta"] + 0.3, in_out_cubic)
        ey = lerp(720, 600, bars_on); es = lerp(1.6, 1.15, bars_on)
        o = eye_open_p(t) if bars_on < 1 else 0.55 + 0.45 * abs(math.cos(t * 0.9))
        closed = prog(t, c["cerrados"] - 0.2, c["cerrados"] + 0.2) * (1 - bars_on)
        eye(P, 540, ey, es, o, 1, col=lerp_c(L.FG, L.RED, closed), glow=closed)
        # etiquetas
        bl = window(t, c["rapido"] - 0.15, c["lento"] - 0.3, 0.2, 0.3)
        if bl > 0:
            P.text("parpadeo: no cuenta", 540, 1000, 46, L.GRAY, bl, face=C.FONT_BOLD)
        sl = window(t, c["lento"] - 0.1, c["cuenta"] - 0.2, 0.3, 0.3)
        if sl > 0:
            dur = max(0.0, t - (c["cerrados"] - 0.2))
            P.text("cerrado", 540, 1000, 52, L.RED, sl, face=C.FONT_BLACK)
            if t > c["cerrados"] - 0.2:
                P.text(f"{dur:.1f} s".replace(".", ","), 540, 1080, 46, L.FG, sl, face=C.FONT_BOLD)
        # barras de un minuto
        if bars_on > 0:
            P.text("1 minuto", 540, 830, 40, L.GRAY, bars_on, face=C.FONT_BOLD)
            fill = prog(t, c["cuenta"], c["casi"] + 0.6, lambda u: u)
            closed_set = (5, 6, 7, 13, 14, 20, 21, 22, 27)
            nfill = int(fill * 30 + 0.999)
            ncl = 0
            for i in range(30):
                x = 160 + i * 25.5
                if i < nfill:
                    cl = i in closed_set; ncl += cl
                    h = 170 if cl else 120
                    P.rect(x, 1040 - h, x + 18, 1040, L.RED if cl else L.DIM, bars_on, radius=6)
                else:
                    P.rect(x, 1030, x + 18, 1040, L.DIM, 0.5 * bars_on, radius=4)
            pc = round(100 * ncl / 30)
            P.text(f"ojos casi cerrados: {pc} %", 540, 1130, 50, L.FG, bars_on * prog(t, c["casi"] - 0.3, c["casi"] + 0.2), face=C.FONT_BLACK)
            pa = prog(t, c["perclos"] - 0.1, c["perclos"] + 0.35)
            if pa > 0:
                P.pill("PERCLOS", 540, 1235, 50, L.RED, out_back(pa), face=C.FONT_BLACK)


def alert_scene(P, t):
    c = CUE
    a = window(t, c["a0"] - 0.05, c["k0"] + 0.1, 0.4, 0.45)
    if a <= 0: return
    with P.layer(a):
        eu = prog(t, c["europa"] - 0.3, c["europa"] + 0.2, in_out_cubic)
        g = 1 - eu
        if g > 0:
            gx, gy, r = 540, 1060, 260
            P.c.drawArc(skia.Rect.MakeLTRB(gx - r, gy - r, gx + r, gy + r), 180, 180, False, paint(L.DIM, g, stroke=26))
            P.c.drawArc(skia.Rect.MakeLTRB(gx - r, gy - r, gx + r, gy + r), 315, 45, False, paint(L.RED, g, stroke=26))
            v = prog(t, c["sube"] - 0.3, c["avisa"] + 0.1, in_out_cubic)
            ang = math.radians(180 + 155 * v + 4 * math.sin(t * 9) * v)
            P.line(gx, gy, gx + math.cos(ang) * (r - 40), gy + math.sin(ang) * (r - 40), L.FG, g, w=10)
            P.circle(gx, gy, 20, L.FG, g)
            al = prog(t, c["avisa"] - 0.1, c["avisa"] + 0.35)
            alert(P, 540, 620, 0.7 + 0.3 * out_back(al) + 0.04 * math.sin(t * 10) * al, al * g)
            ds = prog(t, c["descansar"] - 0.1, c["descansar"] + 0.3)
            P.text("¡descansa!", 540, 1180, 60, L.RED, ds * g, face=C.FONT_BLACK)
        if eu > 0:
            for k in range(12):
                ang = -math.pi / 2 + k * math.pi / 6
                sa = clamp(eu * 1.5 - k * 0.04)
                star(P, 540 + math.cos(ang) * 150, 720 + math.sin(ang) * 150, 22, L.FG, sa)
            ja = prog(t, c["julio"] - 0.1, c["julio"] + 0.35)
            with P.transform(0, 0, 0.85 + 0.15 * out_back(ja), cx=540, cy=1000):
                P.text("julio 2026", 540, 1020, 96, L.RED, ja, face=C.FONT_BLACK)
            na = prog(t, c["nuevo"] - 0.1, c["nuevo"] + 0.3)
            P.text("todo auto nuevo en la UE", 540, 1110, 44, L.FG, na, face=C.FONT_BOLD)
            ca = prog(t, c["distraes"] - 0.15, c["distraes"] + 0.3)
            if ca > 0:
                camera(P, 540, 1215, ca, led=ca, t=t)
            P.text("UE", 540, 742, 52, L.FG, eu, face=C.FONT_BLACK)


def end_scene(P, t):
    c = CUE
    a = prog(t, c["k0"] - 0.3, c["k0"] + 0.2, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        road(P, t, 1, speed=1.0)
        o = 0.62 - 0.08 * math.sin(t * 1.3)
        o = lerp(o, 1.0, prog(t, c["parpados"] - 0.2, c["parpados"] + 0.3))
        o = lerp(o, 0.62, prog(t, c["porque"] - 0.3, c["porque"] + 0.5, in_out_cubic))
        hl = window(t, c["parpados"] - 0.1, c["porque"] - 0.2, 0.3, 0.4)
        eye(P, EYE_X, EYE_Y, 1.25, o, col=lerp_c(L.FG, L.RED, hl), glow=hl)
        # reloj: «cuenta el tiempo»
        ca = window(t, c["tiempo"] - 0.1, c["porque"] + 0.2, 0.3, 0.4)
        if ca > 0:
            cx, cy = 870, 470 + 330
            P.circle(cx, cy, 70, L.BG, ca); P.circle(cx, cy, 70, L.RED, ca, stroke=7)
            ang = -math.pi / 2 + (t - c["tiempo"]) * 4
            P.line(cx, cy, cx + math.cos(ang) * 50, cy + math.sin(ang) * 50, L.RED, ca, w=6)
            P.line(cx, cy, cx, cy - 36, L.FG, ca, w=6)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["pesan"] = T("hook", "pesan"); c["cierras"] = T("hook", "cierras"); c["segundo1"] = T("hook", "segundo")
    c["dar"] = T("hook", "dar")
    c["s0"] = T("segundo"); c["avanzas"] = T("segundo", "avanzas"); c["m28"] = T("segundo", "28"); c["nada"] = T("segundo", "nada")
    c["estados"] = T("segundo", "estados"); c["n91"] = T("segundo", "91.000"); c["somnol"] = T("segundo", "sueño")
    c["c0"] = T("camara"); c["camara"] = T("camara", "cámara"); c["oscuro"] = T("camara", "noche")
    c["como"] = T("camara", "cómo"); c["infra"] = T("camara", "infrarroja")
    c["p0"] = T("parpados"); c["rapido"] = T("parpados", "rápido"); c["lento"] = T("parpados", "lento")
    c["cerrados"] = T("parpados", "cerrados"); c["cuenta"] = T("parpados", "cuenta"); c["casi"] = T("parpados", "casi")
    c["perclos"] = T("parpados", "PERCLOS")
    c["a0"] = T("alerta"); c["sube"] = T("alerta", "sube"); c["avisa"] = T("alerta", "avisa")
    c["descansar"] = T("alerta", "descansa"); c["europa"] = T("alerta", "Europa"); c["julio"] = T("alerta", "2026")
    c["nuevo"] = T("alerta", "nuevo"); c["distraes"] = T("alerta", "distraes")
    c["k0"] = T("cierre"); c["parpados"] = T("cierre", "párpados")
    c["tiempo"] = T("cierre", "tiempo"); c["porque"] = T("cierre", "porque")
    c["end"] = tl.duration
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["infra"] - 0.2, 1.3) + 0.5 * pulse(t, c["perclos"] - 0.2, 1.3) + 0.4 * pulse(t, c["parpados"] - 0.2, 1.3)
    L.background(P, t, glow=glow)
    hook_scene(P, t)
    second_scene(P, t)
    camera_scene(P, t)
    eyelid_scene(P, t)
    alert_scene(P, t)
    end_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    road(P, 0.3, 1, y0=1000, y1=1400)
    eye(P, 540, 860, 1.4, 0.45, col=L.RED, glow=0.6)
    P.text("¿TU AUTO SABE", 540, 560, 96, L.FG, 1, face=C.FONT_BLACK)
    P.text("QUE TE DUERMES?", 540, 670, 96, L.RED, 1, face=C.FONT_BLACK)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (c["cierras"], "whoosh_down", 0.35), (c["dar"], "pop", 0.45),
            (c["s0"] - 0.3, "whoosh", 0.4), (c["avanzas"], "riser", 0.3), (c["nada"], "thump", 0.5),
            (c["n91"], "ding", 0.5),
            (c["c0"] - 0.3, "whoosh", 0.4), (c["camara"], "pop", 0.4), (c["oscuro"], "whoosh_down", 0.3),
            (c["infra"] - 0.4, "riser", 0.3), (c["infra"], "ding", 0.6),
            (c["p0"] - 0.3, "whoosh", 0.35), (c["rapido"], "tick", 0.4), (c["cerrados"], "pop_low", 0.45),
            (c["cuenta"], "tick", 0.3), (c["perclos"], "ding", 0.6),
            (c["a0"] - 0.3, "whoosh", 0.35), (c["avisa"], "thump", 0.5), (c["europa"] - 0.3, "whoosh", 0.35),
            (c["julio"], "pop", 0.45), (c["k0"] - 0.3, "whoosh", 0.35), (c["parpados"], "pop", 0.4),
            (c["tiempo"], "ding", 0.6)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["infra"], "pulse": (c["a0"], c["k0"]), "quiet": [(c["cierras"] - 0.2, c["s0"] + 0.2)]}
