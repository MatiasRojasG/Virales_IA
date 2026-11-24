"""Escenas — «¿Por qué tu batería dura menos cada año?» (stheq.ia, motion graphics).

Hilo visual: un celular y la barra del día (sol → luna). Al inicio el celular ya muere a media tarde (el
problema); vuelve a ser nuevo y llega a la noche; «dos años después» la barra se corta en la tarde → «?» →
corte de la batería por dentro: puntos de litio que viajan a la izquierda al cargar y vuelven al usar → en
cada viaje uno queda atrapado en una capa roja que crece junto a la placa → la batería (ícono) se encoge →
termómetro y «100 %» con reloj: la capa crece más rápido → batería grande: contador de 1.000 cargas y la carga
baja hasta la marca del 80 % → celular con la opción «Límite 80 %»: carga y se detiene → vuelta al corte:
un punto más queda atrapado cada día → el celular y la barra del día otra vez, enchufado de noche (empalme).
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

NDOT = 24
TRAP_ORDER = [4, 13, 19, 7, 22, 1, 10, 16, 2, 21, 8, 14, 5, 18, 11, 23]   # orden en que quedan atrapados


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
def bolt(P, x, y, s, rgb, a):
    if a <= 0: return
    pth = skia.Path()
    pts = [(0.15, -1), (-0.55, 0.12), (-0.05, 0.12), (-0.2, 1), (0.55, -0.15), (0.05, -0.15)]
    for k, (u, v) in enumerate(pts):
        (pth.moveTo if k == 0 else pth.lineTo)(x + u * s, y + v * s)
    pth.close(); P.c.drawPath(pth, paint(rgb, a))


def battery_icon(P, cx, cy, w, h, level, a=1.0, fill=None, outline=None, shrink=1.0, ghost=0.0):
    """Ícono horizontal de batería. shrink < 1 encoge la carcasa desde la derecha (capacidad perdida)."""
    if a <= 0: return
    fill = fill or L.FG; outline = outline or L.FG
    x0 = cx - w / 2; ww = w * shrink
    with P.layer(a):
        if ghost > 0:   # contorno original, punteado
            pe = skia.DashPathEffect.Make([14, 12], 0)
            pnt = paint(L.GRAY, ghost, stroke=5); pnt.setPathEffect(pe)
            P.c.drawRRect(skia.RRect.MakeRectXY(skia.Rect.MakeLTRB(x0, cy - h / 2, x0 + w, cy + h / 2), h * 0.18, h * 0.18), pnt)
        P.rect(x0, cy - h / 2, x0 + ww, cy + h / 2, outline, 1, stroke=max(5, h * 0.06), radius=h * 0.18)
        P.rect(x0 + ww + 6, cy - h * 0.2, x0 + ww + 6 + h * 0.12, cy + h * 0.2, outline, 1, radius=4)
        pad = max(10, h * 0.11)
        lv = clamp(level)
        if lv > 0.002:
            P.rect(x0 + pad, cy - h / 2 + pad, x0 + pad + (ww - 2 * pad) * lv, cy + h / 2 - pad, fill, 1, radius=h * 0.08)


def phone(P, cx, cy, s=1.0, a=1.0, level=1.0, low=0.0, t=0.0, plug=0.0, pct=True):
    """Celular de frente con un ícono de batería en la pantalla. low: tiñe de rojo (batería baja)."""
    if a <= 0: return
    w, h = 320 * s, 620 * s
    col = lerp_c(L.FG, L.RED, low)
    with P.layer(a):
        P.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, L.CARD, 1, radius=48 * s)
        P.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, L.FG, 1, stroke=7 * s, radius=48 * s)
        P.rect(cx - 40 * s, cy - h / 2 + 22 * s, cx + 40 * s, cy - h / 2 + 40 * s, L.BG, 1, radius=9 * s)
        blink = 1.0 if low < 0.5 else 0.55 + 0.45 * abs(math.cos(t * 4))
        battery_icon(P, cx - 8 * s, cy - 60 * s, 190 * s, 92 * s, level, blink, fill=col, outline=L.FG)
        if pct:
            P.text(f"{int(round(100 * clamp(level)))} %", cx, cy + 70 * s, 64 * s, col, blink, face=C.FONT_BLACK)
        if plug > 0:   # cable de carga desde abajo
            P.line(cx, cy + h / 2 + 8 * s, cx, cy + h / 2 + 200 * s, L.GRAY, plug, w=10 * s)
            P.rect(cx - 22 * s, cy + h / 2 + 4 * s, cx + 22 * s, cy + h / 2 + 58 * s, L.FG, plug, radius=8 * s)
            bolt(P, cx, cy + 165 * s, 26 * s, L.RED, plug * (0.6 + 0.4 * math.sin(t * 5)))


DB_Y, DB_X0, DB_X1 = 1185, 250, 830


def day_bar(P, frac, a=1.0, col=None, t=0.0, moon_glow=0.0):
    """Barra del día: sol (mañana) → luna (noche). frac = hasta dónde llega la batería."""
    if a <= 0: return
    col = col or L.FG
    with P.layer(a):
        L.sun(P, DB_X0 - 70, DB_Y, 26, 1, t)
        if moon_glow > 0:
            P.circle(DB_X1 + 70, DB_Y, 60, L.FG, 0.18 * moon_glow, blur=18)
        L.moon(P, DB_X1 + 70, DB_Y, 28, 1)
        P.line(DB_X0, DB_Y, DB_X1, DB_Y, L.DIM, 1, w=16)
        f = clamp(frac)
        if f > 0.005:
            P.line(DB_X0, DB_Y, lerp(DB_X0, DB_X1, f), DB_Y, col, 1, w=16)
        P.line(540, DB_Y + 22, 540, DB_Y + 34, L.GRAY, 0.8, w=4)
        P.text("tarde", 540, DB_Y + 72, 32, L.GRAY, 0.9, face=C.FONT_SEMI)


def thermometer(P, x, y, s, level, a):
    if a <= 0: return
    with P.layer(a):
        P.rect(x - 22 * s, y - 170 * s, x + 22 * s, y + 20 * s, L.FG, 1, stroke=6 * s, radius=22 * s)
        P.circle(x, y + 40 * s, 42 * s, L.FG, 1, stroke=6 * s)
        P.circle(x, y + 40 * s, 30 * s, L.RED, 1)
        P.rect(x - 11 * s, lerp(y + 10 * s, y - 155 * s, clamp(level)), x + 11 * s, y + 20 * s, L.RED, 1, radius=11 * s)


def clock(P, x, y, r, t, a, speed=6.0):
    if a <= 0: return
    P.circle(x, y, r, L.BG, a); P.circle(x, y, r, L.FG, a, stroke=6)
    ang = -math.pi / 2 + t * speed
    P.line(x, y, x + math.cos(ang) * r * 0.72, y + math.sin(ang) * r * 0.72, L.RED, a, w=6)
    P.line(x, y, x + math.cos(ang / 12) * r * 0.45, y + math.sin(ang / 12) * r * 0.45, L.FG, a, w=6)


# --------------------------------------------------------------- corte de la batería
XS_W, XS_H = 780, 480


def dot_home(i, side):
    col, row = i % 3, i // 3
    y = -XS_H / 2 + 70 + row * 50
    x = (-230 + col * 42) if side == 0 else (146 + col * 42)
    return x, y


def charge_state(t):
    """1 = litio a la izquierda (cargado), 0 = a la derecha (en uso). Devuelve (estado, oscilando)."""
    c = CUE
    s = 0.0
    s = lerp(s, 1.0, prog(t, c["cargas"] - 0.1, c["lado"] + 0.2, in_out_cubic))
    s = lerp(s, 0.0, prog(t, c["usas"] - 0.1, c["vuelve"] + 0.2, in_out_cubic))
    osc = prog(t, c["ir"] - 0.2, c["ir"] + 0.4)
    return s, osc


def trap_times():
    c = CUE
    ts = [c["atrapado"] - 0.25, c["capa"] + 0.2, c["vuelve2"] - 0.6,
          c["encoge"] - 1.2, c["encoge"] - 0.2, c["poco"] + 0.1]
    k0, k1 = c["crece"] - 0.3, c["c_rapido"] + 0.6
    ts += [lerp(k0, k1, j / 5) for j in range(6)]
    ts += [c["dia"] - 0.4, c["dia"] + 0.2]
    return ts


def battery_xs(P, cx, cy, s, t, a=1.0, hot=0.0, label=None, hi=0.0):
    """Corte de la batería: dos placas, puntos de litio que van y vienen y la capa que los atrapa."""
    if a <= 0: return
    c = CUE
    with P.layer(a), P.transform(0, 0, s, cx=cx, cy=cy):
        x0, x1, y0, y1 = cx - XS_W / 2, cx + XS_W / 2, cy - XS_H / 2, cy + XS_H / 2
        P.rect(x0, y0, x1, y1, L.CARD, 0.6, radius=36)
        P.rect(x0, y0, x1, y1, lerp_c(L.FG, L.RED, hot), 1, stroke=7, radius=36)
        # placas
        for px in (x0 + 40, x1 - 120):
            P.rect(px, y0 + 36, px + 80, y1 - 36, L.DIM, 1, radius=10)
            for k in range(7):
                yy = y0 + 70 + k * 56
                P.line(px + 14, yy, px + 66, yy, L.GRAY, 0.5, w=3)
        # separador
        for k in range(10):
            yy = y0 + 40 + k * 42
            P.line(cx, yy, cx, yy + 20, L.GRAY, 0.6, w=4)
        # capa que atrapa litio (junto a la placa izquierda)
        tts = trap_times()
        ntr = sum(1 for tt in tts if t >= tt)
        grow = sum(clamp((t - tt) / 0.5) for tt in tts)
        thick = 4 * grow
        if thick > 0.5:
            lx = x0 + 120
            P.rect(lx, y0 + 36, lx + thick, y1 - 36, L.RED, 0.85, radius=4)
            P.rect(lx, y0 + 36, lx + thick, y1 - 36, L.RED, 0.35 * hi, blur=14)
        # puntos de litio
        st, osc = charge_state(t)
        for i in range(NDOT):
            ap = prog(t, c["litio"] - 0.35 + 0.012 * i, c["litio"] + 0.1 + 0.012 * i)
            if ap <= 0: continue
            jt = None
            if i in TRAP_ORDER:
                j = TRAP_ORDER.index(i)
                if j < len(tts): jt = tts[j]
            lag = 0.035 * (i % 6)
            so = 0.5 - 0.5 * math.cos((t - c["ir"] - lag) * 2 * math.pi / 2.4)
            si = lerp(st, so, osc)
            xl, yl = dot_home(i, 0); xr, yr = dot_home(i, 1)
            x = lerp(xr, xl, smooth(si)); y = lerp(yr, yl, si) + 10 * math.sin(math.pi * si) * math.sin(i)
            rgb = L.FG; r = 13
            if jt is not None and t >= jt - 0.6:
                u = prog(t, jt - 0.6, jt, in_out_cubic)           # viaja a la capa y se pega
                tx = -XS_W / 2 + 120 + 4 * (TRAP_ORDER.index(i) + 1) - 2
                x = lerp(x, tx, u) if u < 1 else tx
                y = lerp(y, yl, u)
                rgb = lerp_c(L.FG, L.RED, u); r = lerp(13, 9, u)
            P.circle(cx + x, cy + y, r * out_back(ap), rgb, ap)
            if jt is not None and t >= jt:
                ring = window(t, jt, jt + 1.4, 0.15, 0.5) * (1.0 if TRAP_ORDER.index(i) == 0 else 0.6)
                if ring > 0:
                    P.circle(x0 + 120 + 4 * (TRAP_ORDER.index(i) + 1) - 2, cy + y, 30, L.RED, ring, stroke=5)
        if label:
            txt, la = label
            P.text(txt, cx, y0 - 30, 44, L.FG, la, face=C.FONT_BOLD)
    return ntr


# =============================================================== escenas
def hook_level(t):
    """(nivel del celular, fracción de la barra, rojo, etiqueta) en el gancho."""
    c = CUE
    # 0) el problema: muere a media tarde
    r = prog(t, 0.25, 0.75, in_out_cubic)          # rebobina: vuelve a ser nuevo
    if r < 1:
        return lerp(0.04, 1.0, r), lerp(0.5, 0.0, r), 1 - r, ("nuevo" if r > 0.5 else None)
    if t < c["dos"] - 0.1:   # 1) nuevo: llega a la noche
        u = prog(t, c["llegaba"] - 0.1, c["sobra"] + 0.4, in_out_cubic)
        return lerp(1.0, 0.38, u), u, 0.0, "nuevo"
    u = prog(t, c["llega2"] - 0.2, c["tarde"] + 0.3, in_out_cubic)
    return lerp(1.0, 0.0, u), 0.5 * u, prog(t, c["tarde"] - 0.2, c["tarde"] + 0.3), "2 años después"


def hook_scene(P, t):
    c = CUE
    a = 1 - prog(t, c["v0"] - 0.35, c["v0"] + 0.15, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        lv, fr, red, lab = hook_level(t)
        phone(P, 540, 790, 0.8, 1, lv, low=red, t=t)
        day_bar(P, fr, 1, col=lerp_c(L.FG, L.RED, red), t=t, moon_glow=prog(t, c["noche"] - 0.2, c["noche"] + 0.3) * (1 - prog(t, c["dos"] - 0.3, c["dos"])))
        if lab == "nuevo":
            P.pill("nuevo", 540, 505, 34, L.FG, prog(t, 0.45, 0.8))
        elif lab:
            P.pill("2 años después", 540, 505, 34, L.RED, prog(t, c["dos"] - 0.1, c["dos"] + 0.25))
        q = prog(t, c["paso"] - 0.15, c["paso"] + 0.3, lambda u: u)
        if q > 0:
            P.text("?", 800, 700 + 6 * math.sin(t * 3), 150, L.RED, out_back(q) * clamp(q * 2), face=C.FONT_BLACK)


def xs_scene(P, t):
    """Corte de la batería: desde «viaje» hasta el final de «calor»."""
    c = CUE
    a = window(t, c["v0"] - 0.3, c["d0"] + 0.05, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        sh = prog(t, c["e0"] - 0.1, c["e0"] + 0.6, in_out_cubic)      # se achica y sube para dejar espacio
        cy = lerp(860, 740, sh); s = lerp(1.0, 0.74, sh)
        hot = prog(t, c["calor"] - 0.2, c["calor"] + 0.6) * 0.9
        # etiqueta del modo (cargando / usando)
        lab = None
        st, osc = charge_state(t)
        la1 = window(t, c["cargas"] - 0.15, c["usas"] - 0.15, 0.25, 0.25)
        la2 = window(t, c["usas"] - 0.15, c["ir"] - 0.1, 0.25, 0.25)
        if la1 > 0: lab = ("cargando  ←", la1)
        elif la2 > 0: lab = ("usando  →", la2)
        hi = pulse(t, c["capa"] - 0.1, 1.2) + pulse(t, c["c_rapido"] - 0.2, 1.4)
        battery_xs(P, 540, cy, s, t, 1, hot=hot, label=lab, hi=hi)
        # «energía»: rayo que late con el ir y venir
        ea = window(t, c["energia"] - 0.2, c["t0"] + 0.2, 0.3, 0.4)
        if ea > 0:
            bolt(P, 540, 1180, 60 * (1 + 0.08 * math.sin(t * 2 * math.pi / 1.2)), L.FG, ea)
        # «no vuelve»: cruz junto al primer punto atrapado
        nv = window(t, c["vuelve2"] - 0.1, c["e0"] - 0.1, 0.2, 0.35)
        if nv > 0:
            P.text("✕", 230, 700, 60, L.RED, nv, face=C.FONT_BLACK)
            P.text("atrapado", 330, 1180, 44, L.RED, nv, face=C.FONT_BOLD)
        # «se encoge»: la capacidad
        ca = window(t, c["menos"] - 0.3, c["k0c"] - 0.05, 0.35, 0.35)
        if ca > 0:
            shr = lerp(1.0, 0.72, prog(t, c["encoge"] - 0.3, c["poco"] + 0.6, in_out_cubic))
            shr = lerp(shr, 1.0, 0) if t < c["menos"] else shr
            battery_icon(P, 520, 1120, 520, 130, 1.0, ca, fill=L.FG, outline=L.FG, shrink=shr, ghost=prog(t, c["encoge"] - 0.3, c["encoge"]))
            P.text("capacidad", 540, 1255, 40, L.GRAY, ca, face=C.FONT_SEMI)
        # calor y 100 %
        ka = window(t, c["calor"] - 0.25, c["d0"] + 0.05, 0.35, 0.35)
        if ka > 0:
            thermometer(P, 300, 1130, 0.75, prog(t, c["calor"] - 0.2, c["calor"] + 0.8, out_cubic), ka)
        ha = window(t, c["cien"] - 0.35, c["d0"] + 0.05, 0.35, 0.35)
        if ha > 0:
            battery_icon(P, 720, 1110, 250, 110, 1.0, ha, fill=L.RED, outline=L.FG)
            P.text("100 %", 720, 1235, 46, L.RED, ha, face=C.FONT_BLACK)
            clock(P, 880, 1000, 46, t, ha)


def dato_scene(P, t):
    c = CUE
    a = window(t, c["d0"] - 0.3, c["l0"] + 0.05, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        cnt = prog(t, c["mil"] - 0.1, c["ideales"] + 0.3, in_out_cubic)
        lv = lerp(1.0, 0.8, cnt)
        bx, by, bw, bh = 520, 790, 640, 260
        battery_icon(P, bx, by, bw, bh, lv, 1, fill=L.FG, outline=L.FG)
        ma = prog(t, c["p80"] - 0.15, c["p80"] + 0.3)
        if ma > 0:
            pad = 28; xm = bx - bw / 2 + pad + (bw - 2 * pad) * 0.8
            P.line(xm, by - bh / 2 - 30, xm, by + bh / 2 + 30, L.RED, ma, w=7)
            with P.transform(0, 0, 0.85 + 0.15 * out_back(ma), cx=xm, cy=590):
                P.text("80 %", xm, 610, 84, L.RED, ma, face=C.FONT_BLACK)
        ca = prog(t, c["mil"] - 0.3, c["mil"] + 0.1)
        if ca > 0:
            n = int(round(1000 * cnt))
            P.text(f"{n:,}".replace(",", "."), 540, 1110, 120, L.RED if cnt >= 1 else L.FG, ca, face=C.FONT_BLACK)
            P.text("cargas completas", 540, 1185, 46, L.FG, ca, face=C.FONT_BOLD)
            ia = prog(t, c["ideales"] - 0.2, c["ideales"] + 0.2)
            P.text("en condiciones ideales", 540, 1250, 36, L.GRAY, ia, face=C.FONT_SEMI)


def limit_scene(P, t):
    c = CUE
    a = window(t, c["l0"] - 0.3, c["k0"] + 0.05, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        on = prog(t, c["opcion"] - 0.1, c["opcion"] + 0.3, in_out_cubic)
        fill = prog(t, c["cargar"] - 0.2, c["lim80"] + 0.2, in_out_cubic)
        lv = lerp(0.25, 0.8, fill)
        cx, cy = 540, 800
        phone(P, cx, cy, 1.0, 1, lv, low=0.0, t=t, plug=prog(t, c["cargar"] - 0.4, c["cargar"]))
        # fila de ajuste con interruptor
        ry = cy + 175
        P.text("Límite 80 %", cx - 130, ry + 12, 32, L.FG, 1, face=C.FONT_BOLD, align="left")
        sx = cx + 95
        P.rect(sx - 34, ry - 20, sx + 34, ry + 20, lerp_c(L.DIM, L.RED, on), 1, radius=20)
        P.circle(lerp(sx - 14, sx + 14, on), ry, 16, L.FG, 1)
        if on > 0:
            P.circle(sx, ry, 60, L.RED, 0.25 * pulse(t, c["opcion"] - 0.1, 1.0), blur=10)
        # «menos horas al cien»
        ha = prog(t, c["horas"] - 0.2, c["horas"] + 0.2)
        if ha > 0:
            P.text("100 %", 850, 640, 54, L.GRAY, ha, face=C.FONT_BLACK)
            sk = prog(t, c["horas"], c["cien2"] + 0.2, out_cubic)
            P.line(780, 625, lerp(780, 920, sk), 605, L.RED, ha, w=7)


def end_scene(P, t):
    c = CUE
    a = prog(t, c["k0"] - 0.3, c["k0"] + 0.2, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        sw = prog(t, c["tu2"] - 0.35, c["tu2"] + 0.15, in_out_cubic)    # del corte al celular (empalme)
        if sw < 1:
            with P.layer(1 - sw):
                battery_xs(P, 540, 820, 0.95, t, 1, hi=pulse(t, c["litio2"] - 0.1, 1.2))
                da = prog(t, c["dia"] - 0.3, c["dia"] + 0.1)
                if da > 0:
                    nd = 1 + int(max(0.0, t - c["dia"]) * 3)
                    P.text(f"día {nd}", 540, 1180, 50, L.RED, da, face=C.FONT_BLACK)
        if sw > 0:
            with P.layer(sw):
                plug = prog(t, c["cargando"] - 0.3, c["cargando"] + 0.1)
                lv = lerp(0.6, 1.0, prog(t, c["cargando"], c["noche2"] + 0.4))
                phone(P, 540, 790, 0.8, 1, lv, low=prog(t, c["noche2"] - 0.2, c["noche2"] + 0.3) * 0.0, t=t, plug=plug)
                mg = prog(t, c["noche2"] - 0.2, c["noche2"] + 0.3)
                day_bar(P, 1.0, 1, col=L.FG, t=t, moon_glow=mg)
                if mg > 0:
                    clock(P, 800, 640, 48, t, mg, speed=9)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["recien"] = T("hook", "Recién"); c["llegaba"] = T("hook", "llegaba"); c["noche"] = T("hook", "noche")
    c["sobra"] = T("hook", "sobra"); c["dos"] = T("hook", "Dos"); c["llega2"] = T("hook", "llega", which=1)
    c["tarde"] = T("hook", "tarde"); c["paso"] = T("hook", "pasó")
    c["v0"] = T("viaje"); c["litio"] = T("viaje", "litio"); c["cargas"] = T("viaje", "cargas")
    c["lado"] = T("viaje", "lado"); c["usas"] = T("viaje", "usas"); c["vuelve"] = T("viaje", "vuelve")
    c["ir"] = T("viaje", "ir"); c["energia"] = T("viaje", "energía")
    c["t0"] = T("trampa"); c["atrapado"] = T("trampa", "atrapado"); c["capa"] = T("trampa", "capa")
    c["vuelve2"] = T("trampa", "vuelve")
    c["e0"] = T("encoge"); c["menos"] = T("encoge", "menos"); c["encoge"] = T("encoge", "encoge")
    c["poco"] = T("encoge", "poco")
    c["k0c"] = T("calor"); c["calor"] = T("calor", "calor"); c["cien"] = T("calor", "cien")
    c["crece"] = T("calor", "crece"); c["c_rapido"] = T("calor", "rápido", which=1)
    c["d0"] = T("dato"); c["p80"] = T("dato", "80%"); c["mil"] = T("dato", "1.000"); c["ideales"] = T("dato", "ideales")
    c["l0"] = T("limite"); c["opcion"] = T("limite", "opción"); c["cargar"] = T("limite", "cargar")
    c["lim80"] = T("limite", "80%"); c["horas"] = T("limite", "horas"); c["cien2"] = T("limite", "cien")
    c["k0"] = T("cierre"); c["litio2"] = T("cierre", "litio"); c["dia"] = T("cierre", "día")
    c["tu2"] = T("cierre", "tú", which=1); c["cargando"] = T("cierre", "cargando"); c["noche2"] = T("cierre", "noche")
    c["end"] = tl.duration
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["capa"] - 0.2, 1.3) + 0.5 * pulse(t, c["p80"] - 0.2, 1.3) + 0.4 * pulse(t, c["dia"] - 0.2, 1.3)
    L.background(P, t, glow=glow)
    hook_scene(P, t)
    xs_scene(P, t)
    dato_scene(P, t)
    limit_scene(P, t)
    end_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    P.text("¿POR QUÉ TU BATERÍA", 540, 560, 84, L.FG, 1, face=C.FONT_BLACK)
    P.text("DURA MENOS?", 540, 665, 96, L.RED, 1, face=C.FONT_BLACK)
    phone(P, 540, 905, 0.6, 1, 0.04, low=1.0, t=0.0)
    day_bar(P, 0.5, 1, col=L.RED, t=0.0)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (0.25, "rewind", 0.35), (c["noche"], "ding", 0.35),
            (c["dos"], "whoosh_down", 0.35), (c["tarde"], "thump", 0.5), (c["paso"], "pop", 0.45),
            (c["v0"] - 0.3, "whoosh", 0.4), (c["litio"], "pop", 0.35), (c["cargas"], "whoosh", 0.3),
            (c["usas"], "whoosh_down", 0.3), (c["energia"], "ding", 0.45),
            (c["atrapado"] - 0.25, "pop_low", 0.5), (c["capa"], "tick", 0.35), (c["vuelve2"], "thump", 0.45),
            (c["menos"], "tick", 0.3), (c["encoge"], "whoosh_down", 0.4),
            (c["calor"] - 0.3, "riser", 0.3), (c["cien"], "tick", 0.35), (c["crece"], "pop_low", 0.4),
            (c["d0"] - 0.3, "whoosh", 0.4), (c["p80"], "ding", 0.55), (c["mil"], "riser", 0.3),
            (c["l0"] - 0.3, "whoosh", 0.35), (c["opcion"], "pop", 0.45), (c["lim80"], "ding", 0.5),
            (c["k0"] - 0.3, "whoosh", 0.35), (c["dia"], "pop_low", 0.4), (c["tu2"] - 0.3, "whoosh", 0.35),
            (c["noche2"], "ding", 0.5)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["atrapado"], "pulse": (c["d0"], c["k0"]), "quiet": [(c["paso"] - 0.1, c["v0"] + 0.2)]}
