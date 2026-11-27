"""Escenas — «¿Cómo sabe tu celular dónde está el suelo?» (stheq.ia, motion graphics).

Hilo visual: un celular. Gancho: gira a horizontal y la imagen de su pantalla se acomoda; aparece el suelo y una
flecha roja hacia abajo → zoom al chip (≈ 2 mm) que crece y se transforma en el acelerómetro por dentro: un marco,
una pesa colgada de dos resortes y, a los lados, dedos que se intercalan con dedos fijos → la gravedad (flecha roja)
baja la pesa y los resortes se estiran → los dedos se acercan, saltan chispas rojas en el espacio que se achica y un
medidor se llena → el celular vuelve, con «rayos X» en su centro: una pesa por cada dirección; al inclinarlo, la
pesa vertical vuelve al centro y la horizontal se corre; la imagen gira → caminar: la pesa rebota, una onda dibuja
cada paso y un contador sube → caída: el celular cae dando vueltas, la pesa flota al centro y el medidor baja a 0
→ cierre: vuelve la pesa con su flecha y todo se transforma en el celular del inicio (empalme).
"""
from __future__ import annotations
import math
import numpy as np
import skia
from PIL import Image
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic
from reelforge.draw import spring
from reelforge import marca as L

TL = None; EP = {}; CHUNKS = []; CUE = {}
_IMG = {}
CY = 820          # centro de la acción (antes del desplazamiento global de +45 px)
G_DY = 14.0       # cuánto baja la pesa con la gravedad (px, a escala 1)


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


# =============================================================== piezas
def stroke_path(P, pth, col, a, w):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=w,
                   StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join, Color=skia.Color4f(*col, a))
    P.c.drawPath(pth, p)


def fill_path(P, pth, col, a):
    P.c.drawPath(pth, skia.Paint(AntiAlias=True, Color=skia.Color4f(*col, a)))


def picture(P, cx, cy, s, a=1.0):
    """Imagen sencilla en la pantalla: cielo, sol, montañas y horizonte (sirve para ver qué lado es «arriba»)."""
    if a <= 0: return
    with P.layer(a):
        P.circle(cx + 60 * s, cy - 60 * s, 30 * s, L.RED, 1)
        m = skia.Path()
        m.moveTo(cx - 120 * s, cy + 50 * s); m.lineTo(cx - 40 * s, cy - 40 * s); m.lineTo(cx + 10 * s, cy + 10 * s)
        m.lineTo(cx + 50 * s, cy - 15 * s); m.lineTo(cx + 120 * s, cy + 50 * s); m.close()
        fill_path(P, m, L.FG, 0.9)
        P.line(cx - 130 * s, cy + 52 * s, cx + 130 * s, cy + 52 * s, L.FG, 1, w=5 * s)


def phone(P, cx, cy, w, h, rot=0.0, a=1.0, content_rot=0.0, content_a=1.0, xray=None, glow=0.0):
    """Celular centrado en (cx, cy) de tamaño w×h, girado rot grados. xray(P, cx, cy, s) dibuja el interior."""
    if a <= 0: return
    s = w / 300.0
    with P.layer(a), P.transform(0, 0, 1.0, rot, cx, cy):
        if glow > 0:
            P.rect(cx - w / 2 - 10, cy - h / 2 - 10, cx + w / 2 + 10, cy + h / 2 + 10, L.RED, 0.35 * glow, stroke=6, radius=56 * s)
        P.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, L.CARD, 1, radius=48 * s)
        P.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, L.GRAY, 1, stroke=5 * s, radius=48 * s)
        x0, y0, x1, y1 = cx - w / 2 + 14 * s, cy - h / 2 + 14 * s, cx + w / 2 - 14 * s, cy + h / 2 - 14 * s
        P.rect(x0, y0, x1, y1, L.BG, 1, radius=36 * s)
        P.rect(cx - 36 * s, y0 + 14 * s, cx + 36 * s, y0 + 34 * s, L.CARD, 1, radius=10 * s)
        with P.clip_rect(x0, y0, x1, y1):
            with P.transform(0, 0, 1.0, content_rot, cx, cy):
                picture(P, cx, cy, s * 0.95, content_a)
            if xray is not None:
                xray(P, cx, cy, s)


def zigzag(P, x, y0, y1, amp, n, col, a, w):
    pth = skia.Path(); pth.moveTo(x, y0)
    seg = (y1 - y0) / (n + 1)
    pth.lineTo(x, y0 + seg * 0.5)
    for k in range(n):
        pth.lineTo(x + (amp if k % 2 == 0 else -amp), y0 + seg * (k + 1))
    pth.lineTo(x, y1 - seg * 0.5); pth.lineTo(x, y1)
    stroke_path(P, pth, col, a, w)


def mems(P, cx, cy, s, dy, a=1.0, hl_spring=0.0, hl_fing=0.0, charge=0.0, frame_a=1.0, mass_col=None):
    """Acelerómetro por dentro (un eje, vertical): marco, pesa con resortes y dedos intercalados."""
    if a <= 0: return
    dy = dy * s
    with P.layer(a):
        with P.layer(frame_a):
            P.rect(cx - 340 * s, cy - 320 * s, cx + 340 * s, cy + 320 * s, L.CARD, 0.55, radius=22 * s)
            P.rect(cx - 340 * s, cy - 320 * s, cx + 340 * s, cy + 320 * s, L.DIM, 1, stroke=3 * s, radius=22 * s)
        # anclas y resortes
        for sg in (-1, 1):
            ya, yb = sorted((cy + sg * 320 * s, cy + sg * 288 * s))
            P.rect(cx - 60 * s, ya, cx + 60 * s, yb, L.GRAY, 1, radius=4 * s)
        col_s = lerp_c(L.GRAY, L.RED, hl_spring)
        zigzag(P, cx, cy - 290 * s, cy - 110 * s + dy, 42 * s, 7, col_s, 1, 7 * s)
        zigzag(P, cx, cy + 110 * s + dy, cy + 290 * s, 42 * s, 7, col_s, 1, 7 * s)
        # dedos fijos (anclados a barras laterales)
        fixed_col = lerp_c(L.DIM, L.GRAY, hl_fing)
        for sg in (-1, 1):
            bx = cx + sg * 300 * s
            P.rect(bx - 12 * s, cy - 210 * s, bx + 12 * s, cy + 210 * s, fixed_col, 1, radius=4 * s)
            for k in range(-2, 3):
                y = cy + k * 64 * s
                xa, xb = sorted((bx, cx + sg * 150 * s))
                P.rect(xa, y - 6 * s, xb, y + 6 * s, fixed_col, 1, radius=3 * s)
        # chispas en los espacios que se achican
        if charge > 0:
            close = clamp(dy / (G_DY * s))
            for sg in (-1, 1):
                for k in (-1.5, -0.5, 0.5, 1.5):
                    ym = cy + dy + k * 64 * s            # dedo móvil
                    yf = cy + (k + 0.5) * 64 * s         # dedo fijo de abajo
                    for j in range(4):
                        x = cx + sg * (165 + j * 30) * s
                        P.line(x, ym + 7 * s, x, yf - 7 * s, L.RED, charge * (0.35 + 0.65 * close), w=3 * s)
        # pesa con sus dedos móviles
        mc = mass_col or L.FG
        mov_col = lerp_c(L.FG, L.RED, 0.0)
        for sg in (-1, 1):
            for k in (-1.5, -0.5, 0.5, 1.5):
                y = cy + dy + k * 64 * s
                xa, xb = sorted((cx + sg * 110 * s, cx + sg * 272 * s))
                P.rect(xa, y - 6 * s, xb, y + 6 * s, mov_col, 1, radius=3 * s)
                if hl_fing > 0:
                    P.rect(xa - 3, y - 9 * s, xb + 3, y + 9 * s, L.RED, 0.6 * hl_fing, stroke=3, radius=5 * s)
        P.rect(cx - 120 * s, cy - 110 * s + dy, cx + 120 * s, cy + 110 * s + dy, mc, 1, radius=14 * s)
        for k in range(3):   # textura de agujeros de la pesa (como en los chips reales)
            for j in range(3):
                P.circle(cx + (j - 1) * 60 * s, cy + dy + (k - 1) * 55 * s, 9 * s, L.CARD, 0.8)


def gauge(P, cx, y, w, frac, a=1.0, col=None, label=None):
    if a <= 0: return
    with P.layer(a):
        P.rect(cx - w / 2, y - 14, cx + w / 2, y + 14, L.CARD, 1, radius=14)
        P.rect(cx - w / 2, y - 14, cx - w / 2 + w * clamp(frac), y + 14, col or L.RED, 1, radius=14)
        P.rect(cx - w / 2, y - 14, cx + w / 2, y + 14, L.DIM, 1, stroke=3, radius=14)
        if label:
            P.text(label, cx - w / 2 - 20, y + 12, 32, L.GRAY, 1, face=C.FONT_SEMI, align="right")


def slots(P, cx, cy, s, gv, gh, a=1.0, hl_h=0.0, hl_v=0.0, bounce=0.0):
    """Rayos X del celular: una pesa para el eje largo (vertical) y otra para el corto (horizontal)."""
    if a <= 0: return
    with P.layer(a):
        L_ = 110 * s; th = 34 * s; m = 26 * s
        P.rect(cx - th / 2, cy - L_, cx + th / 2, cy + L_, L.CARD, 0.9, radius=8 * s)
        P.rect(cx - th / 2, cy - L_, cx + th / 2, cy + L_, lerp_c(L.DIM, L.RED, hl_v), 1, stroke=3 * s, radius=8 * s)
        P.rect(cx - L_, cy - th / 2, cx + L_, cy + th / 2, L.CARD, 0.9, radius=8 * s)
        P.rect(cx - L_, cy - th / 2, cx + L_, cy + th / 2, lerp_c(L.DIM, L.RED, hl_h), 1, stroke=3 * s, radius=8 * s)
        yv = cy + (gv + bounce) * (L_ - m - 6 * s)
        xh = cx + gh * (L_ - m - 6 * s)
        P.rect(cx - m * 0.55, yv - m * 0.55, cx + m * 0.55, yv + m * 0.55, lerp_c(L.FG, L.RED, hl_v), 1, radius=5 * s)
        P.rect(xh - m * 0.55, cy - m * 0.55, xh + m * 0.55, cy + m * 0.55, lerp_c(L.FG, L.RED, hl_h), 1, radius=5 * s)


def ground(P, y, a=1.0, x0=200, x1=880):
    if a <= 0: return
    with P.layer(a):
        P.line(x0, y, x1, y, L.FG, 1, w=5)
        for x in range(int(x0) + 10, int(x1), 34):
            P.line(x, y + 6, x - 22, y + 30, L.GRAY, 0.6, w=3)


# =============================================================== escenas
def hook_scene(P, t):
    """Celular que gira; la imagen se acomoda; luego el suelo y la pregunta. También es el cuadro final (empalme)."""
    c = CUE
    a = 1 - prog(t, c["chip"] - 0.2, c["chip"] + 0.3, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        r = 90 * prog(t, c["giras"] - 0.05, c["giras"] + 0.9, in_out_cubic)
        # la imagen «se resiste» un instante y luego se endereza (como el celular real)
        follow = prog(t, c["gira"] - 0.1, c["gira"] + 0.45, out_back)
        cr = -r * follow
        back = prog(t, c["a0"] - 0.6, c["a0"] - 0.05, in_out_cubic)   # vuelve a vertical antes del zoom
        r = r * (1 - back); cr = cr * (1 - back)
        phone(P, 540, CY - 20, 300, 580, rot=r, content_rot=cr)
        # «no tiene ojos»
        ea = window(t, c["ojos"] - 0.25, c["suelo"] - 0.1, 0.25, 0.3)
        if ea > 0:
            ex, ey = 540, 470
            pth = skia.Path(); pth.moveTo(ex - 70, ey); pth.quadTo(ex, ey - 55, ex + 70, ey); pth.quadTo(ex, ey + 55, ex - 70, ey)
            stroke_path(P, pth, L.FG, ea, 6)
            P.circle(ex, ey, 20, L.FG, ea)
            P.line(ex - 80, ey + 45, ex + 80, ey - 45, L.RED, ea * prog(t, c["ojos"], c["ojos"] + 0.25), w=9)
        # suelo y flecha
        ga = prog(t, c["suelo"] - 0.3, c["suelo"] + 0.2)
        ground(P, 1225, ga)
        if ga > 0:
            P.arrow(930, 700, 930, 700 + 300 * out_cubic(ga), L.RED, ga, w=9, head=34)
            P.text("?", 930, 640 + 6 * math.sin(t * 3), 110, L.RED, ga, face=C.FONT_BLACK)


def adentro_scene(P, t):
    c = CUE
    a = window(t, c["a0"] - 0.4, c["r0"] + 0.6, 0.3, 0.5)
    if a <= 0: return
    z = prog(t, c["mueve"] - 0.7, c["mueve"] + 0.1, in_out_cubic)          # zoom al chip
    with P.layer(a):
        # el celular crece y se desvanece mientras el chip pasa al frente
        ph_s = lerp(1.0, 3.2, z)
        pa = (1 - z) * prog(t, c["a0"] - 0.4, c["a0"] - 0.1)
        if pa > 0:
            with P.transform(0, 0, ph_s, 0, 540, CY - 20):
                phone(P, 540, CY - 20, 300, 580, a=pa, content_a=1 - prog(t, c["a0"], c["chip"] + 0.2))
        # el chip: un cuadrado con patitas que se transforma en el marco del acelerómetro
        ca = prog(t, c["chip"] - 0.2, c["chip"] + 0.3)
        if ca > 0:
            half = lerp(42, 340, z)
            hy = lerp(42, 320, z)
            cy = lerp(CY - 20, CY, z)
            with P.layer(ca):
                P.rect(540 - half, cy - hy, 540 + half, cy + hy, L.CARD, 1, radius=lerp(8, 22, z))
                P.rect(540 - half, cy - hy, 540 + half, cy + hy, lerp_c(L.FG, L.DIM, z), 1, stroke=lerp(4, 3, z), radius=lerp(8, 22, z))
                pin_a = 1 - z
                for k in range(-2, 3):
                    for sg in (-1, 1):
                        P.rect(540 + sg * half, cy + k * 16 - 4, 540 + sg * (half + 14), cy + k * 16 + 4, L.GRAY, pin_a)
                ma = prog(t, c["mili"] - 0.2, c["mili"] + 0.2) * (1 - z)
                if ma > 0:
                    P.line(540 - 42, cy + 80, 540 + 42, cy + 80, L.RED, ma, w=4)
                    P.line(540 - 42, cy + 70, 540 - 42, cy + 90, L.RED, ma, w=4)
                    P.line(540 + 42, cy + 70, 540 + 42, cy + 90, L.RED, ma, w=4)
                    P.text("≈ 2 mm", 540, cy + 140, 40, L.RED, ma, face=C.FONT_BOLD)
        # la pieza que se mueve (aparece al decir «mueve» y oscila)
        ma2 = prog(t, c["mueve"] - 0.15, c["mueve"] + 0.25)
        if ma2 > 0:
            u = max(0.0, t - c["mueve"])
            wob = 16 * math.exp(-1.6 * u) * math.sin(u * 13)
            mems(P, 540, CY, 1.0, wob, ma2, frame_a=0.0)


def resortes_scene(P, t):
    c = CUE
    a = window(t, c["r0"] - 0.05, c["e0"] + 0.1, 0.15, 0.5)
    if a <= 0: return
    with P.layer(a):
        hs = pulse(t, c["resortes"] - 0.1, 0.9) + prog(t, c["estiran"] - 0.1, c["estiran"] + 0.3) * (1 - prog(t, c["d0"] - 0.2, c["d0"] + 0.3))
        g = prog(t, c["abajo"] - 0.6, c["abajo"] + 0.3)
        u = max(0.0, t - (c["abajo"] - 0.6))
        dy = G_DY * spring(u * 0.9, 9, 3.5) if g > 0 else 0.0
        uw = max(0.0, t - c["mueve"])
        dy += 16 * math.exp(-1.6 * uw) * math.sin(uw * 13)
        # en «dedos»: la pesa baja un poco más y vuelve (para ver acercarse los dedos)
        bajo = pulse(t, c["baja"] - 0.1, 1.4)
        dy = dy + 5 * bajo
        hf = prog(t, c["dedos"] - 0.15, c["dedos"] + 0.25) * (1 - prog(t, c["acercan"] + 0.4, c["acercan"] + 0.9) * 0.6)
        ch = prog(t, c["carga"] - 0.2, c["carga"] + 0.2)
        mems(P, 540, CY, 1.0, dy, 1.0, hl_spring=clamp(hs), hl_fing=hf, charge=ch)
        # flecha de gravedad (debajo de la pesa, entre los resortes no: a la derecha del marco)
        ga = prog(t, c["grav"] - 0.25, c["grav"] + 0.2) * (1 - prog(t, c["dedos"] - 0.3, c["dedos"]))
        if ga > 0:
            P.arrow(540, CY - 40 + dy, 540, CY + 70 + dy + 40 * out_cubic(ga), L.RED, ga, w=10, head=34)
            P.pill("gravedad", 540, CY - 150 + dy, 32, L.RED, ga, fill_a=0.1)
        # medidor: cuánto se movió la pesa
        ma = prog(t, c["carga"] - 0.1, c["carga"] + 0.3)
        if ma > 0:
            gauge(P, 600, 1215, 460, dy / (G_DY + 5) * prog(t, c["mide"] - 0.6, c["mide"] + 0.2), ma, label="señal")
            P.circle(830 + 22, 1215, 10 + 10 * pulse(t, c["mide"], 0.6), L.RED, pulse(t, c["mide"], 0.6))


def ejes_scene(P, t):
    c = CUE
    a = window(t, c["e0"] - 0.3, c["p0"] + 0.02, 0.45, 0.3)
    if a <= 0: return
    with P.layer(a):
        ap = prog(t, c["e0"] - 0.3, c["e0"] + 0.3, out_cubic)
        sc = lerp(1.6, 1.0, ap)
        th = 90 * prog(t, c["inclinas"] - 0.1, c["otra"] + 0.2, in_out_cubic)   # inclinación
        rad = math.radians(th)
        gv, gh = math.cos(rad), -math.sin(rad)         # componentes de la gravedad en los ejes del celular
        hl_h = prog(t, c["otra"] - 0.1, c["otra"] + 0.3) * (1 - prog(t, c["gira"] + 0.4, c["gira"] + 0.9))
        snap = prog(t, c["gira"] - 0.1, c["gira"] + 0.45, out_back)
        xr = 1 - 0.55 * snap                          # los rayos X se apagan cuando gira la imagen
        cont = 0.25 + 0.75 * snap

        def xray(P2, x, y, s):
            slots(P2, x, y + 20 * s, s * 1.15, 0.9 * gv, 0.9 * gh, xr, hl_h=hl_h)

        with P.transform(0, 0, sc, 0, 540, CY - 20):
            phone(P, 540, CY - 20, 300, 580, rot=-th, content_rot=th * snap, content_a=cont, xray=xray)
        # tres direcciones: flechas de ejes
        ta = window(t, c["tres"] - 0.2, c["inclinas"] + 0.2, 0.3, 0.4)
        if ta > 0:
            for k, (dx, dy, lab) in enumerate(((0, -1, ""), (1, 0, ""), (0, 0, ""))):
                ak = ta * prog(t, c["tres"] - 0.1 + 0.18 * k, c["tres"] + 0.2 + 0.18 * k)
                if k < 2:
                    P.arrow(540, CY - 20, 540 + dx * 270, CY - 20 + dy * 380, L.RED, ak, w=7, head=30)
                else:
                    P.circle(540, CY - 20, 26, L.RED, ak, stroke=6)
                    P.circle(540, CY - 20, 8, L.RED, ak)
        # gravedad: siempre hacia abajo
        ga = prog(t, c["grav"] - 0.2, c["grav"] + 0.2)
        if ga > 0:
            P.arrow(900, 880, 900, 1100, L.RED, ga, w=9, head=32)
            P.text("g", 940, 1010, 44, L.RED, ga, face=C.FONT_BOLD, align="left")


def pasos_scene(P, t):
    c = CUE
    a = window(t, c["p0"] - 0.3, c["k0"] + 0.1, 0.3, 0.35)
    if a <= 0: return
    t0 = c["caminar"] - 0.1
    T_STEP = 0.5
    with P.layer(a):
        def bounce_at(tt):
            if tt < t0: return 0.0
            ph = ((tt - t0) / T_STEP) % 1.0
            return 0.55 * math.exp(-5 * ph) * math.sin(ph * 2 * math.pi * 1.5) * prog(tt, t0, t0 + 0.2)

        b = bounce_at(t)
        ap = prog(t, c["p0"], c["p0"] + 0.6, in_out_cubic)
        # el celular pasa de horizontal (escena anterior) a vertical y se achica hacia arriba
        rr = -90 * (1 - ap)
        cy = lerp(CY - 20, 700, ap); sc = lerp(1.0, 0.62, ap)

        def xray(P2, x, y, s):
            th_ = math.radians(-rr)
            slots(P2, x, y + 20 * s, s * 1.15, 0.9 * math.cos(th_), -0.9 * math.sin(th_), lerp(0.45, 1.0, ap), hl_v=clamp(abs(b) * 3), bounce=b * 0.6)

        with P.transform(0, 0, sc, 0, 540, cy):
            phone(P, 540, cy, 300, 580, rot=rr, content_rot=-rr, content_a=lerp(1.0, 0.25, ap), xray=xray)
        # onda de la señal (se dibuja de izquierda a derecha)
        wa = prog(t, c["caminar"] - 0.2, c["caminar"] + 0.2)
        if wa > 0:
            x0, x1, yb = 140, 940, 1110
            span = 4.0
            pth = skia.Path()
            n = 160
            for i in range(n + 1):
                x = lerp(x0, x1, i / n)
                tt = t - span + span * i / n
                y = yb - 120 * bounce_at(tt)
                if i == 0: pth.moveTo(x, y)
                else: pth.lineTo(x, y)
            with P.layer(wa):
                P.line(x0, yb, x1, yb, L.DIM, 1, w=2)
                stroke_path(P, pth, L.FG, 1, 5)
                P.circle(x1, yb - 120 * b, 9, L.RED, 1)
        # contador de pasos
        na = prog(t, c["contar"] - 0.2, c["contar"] + 0.2)
        if na > 0:
            n_steps = int(max(0.0, t - t0) / T_STEP) + (1 if t >= t0 else 0)
            P.text(str(n_steps), 830, 720, 120, L.RED, na, face=C.FONT_BLACK)
            P.text("pasos", 830, 780, 36, L.GRAY, na, face=C.FONT_SEMI)
        # huellas que aparecen con cada paso
        for k in range(8):
            tk = t0 + k * T_STEP
            fa = prog(t, tk, tk + 0.15) * (1 - prog(t, tk + 2.0, tk + 2.6)) * wa
            if fa > 0:
                x = 180 + k * 90
                y = 1215 + (14 if k % 2 else -14)
                with P.transform(0, 0, 1.0, 0, x, y):
                    P.rect(x - 15, y - 26, x + 15, y + 14, L.GRAY, fa * 0.8, radius=14)
                    P.circle(x, y + 22, 10, L.GRAY, fa * 0.8)


def caida_scene(P, t):
    c = CUE
    a = window(t, c["k0"] - 0.25, c["ci0"] + 0.2, 0.3, 0.4)
    if a <= 0: return
    with P.layer(a):
        fall = prog(t, c["cae2"] - 0.1, c["cero"] + 0.2, lambda u: u * u)
        free = prog(t, c["cae2"] - 0.05, c["flota"] + 0.3, in_out_cubic)
        y = lerp(lerp(700, 800, prog(t, c["k0"] - 0.2, c["k0"] + 0.4, in_out_cubic)), 1500, fall)
        rot = 200 * fall + 6 * math.sin(t * 2) * (1 - fall)
        sc = lerp(0.62, 0.8, prog(t, c["k0"] - 0.2, c["k0"] + 0.3))
        hl = prog(t, c["flota"] - 0.2, c["flota"] + 0.2)
        g_local = 0.9 * (1 - free)
        # en el marco del celular girado, la pesa «cae» hacia el suelo real, luego flota
        rr = math.radians(-rot)

        def xray(P2, x, yy, s):
            slots(P2, x, yy + 20 * s, s * 1.15, g_local * math.cos(rr), -g_local * math.sin(rr), 1.0, hl_v=hl)

        with P.transform(0, 0, sc, 0, 540, y):
            phone(P, 540, y, 300, 580, a=1 - prog(fall, 0.35, 0.6), rot=rot, content_a=0.25, xray=xray, glow=hl * (1 - fall))
        # medidor que se vacía y el cero
        ma = prog(t, c["k0"] - 0.1, c["k0"] + 0.3)
        gauge(P, 600, 520, 460, 1 - free, ma, label="señal")
        za = prog(t, c["cero"] - 0.1, c["cero"] + 0.3)
        if za > 0:
            with P.transform(0, 0, 0.6 + 0.4 * out_back(za), 0, 540, 900):
                P.text("0", 540, 960, 230, L.RED, clamp(za * 2), face=C.FONT_BLACK)


def cierre_scene(P, t):
    c = CUE
    a = prog(t, c["ci0"] - 0.3, c["ci0"] + 0.3, in_out_cubic)
    if a <= 0: return
    end = c["end"]
    loop = prog(t, end - 1.3, end - 0.4, in_out_cubic)
    with P.layer(a):
        g = prog(t, c["cae"] - 0.3, c["cae"] + 0.4)
        u = max(0.0, t - (c["cae"] - 0.3))
        dy = G_DY * spring(u * 0.9, 9, 3.5) if g > 0 else 0.0
        hs = prog(t, c["res"] - 0.1, c["res"] + 0.3)
        ma = 1 - loop
        mems(P, 540, CY, 1.0, dy, ma, hl_spring=hs)
        if g > 0:
            P.arrow(540, CY - 40 + dy, 540, CY + 70 + dy + 40 * out_cubic(g), L.RED, g * ma, w=10, head=34)
        # pregunta inicial: suelo
        qa = prog(t, c["ci0"] - 0.1, c["ci0"] + 0.3) * ma
        ground(P, 1225, qa)
    # empalme con el cuadro 0: el celular vertical del gancho
    if loop > 0:
        with P.transform(0, 0, lerp(1.3, 1.0, loop), 0, 540, CY - 20):
            phone(P, 540, CY - 20, 300, 580, a=loop)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["giras"] = T("hook", "Giras"); c["gira"] = T("hook", "gira", which=1); c["ojos"] = T("hook", "ojos"); c["suelo"] = T("hook", "suelo")
    c["a0"] = T("adentro"); c["chip"] = T("adentro", "chip"); c["mili"] = T("adentro", "milímetros"); c["mueve"] = T("adentro", "mueve")
    c["r0"] = T("resortes"); c["resortes"] = T("resortes", "resortes"); c["grav"] = T("resortes", "gravedad")
    c["abajo"] = T("resortes", "abajo"); c["estiran"] = T("resortes", "estiran")
    c["d0"] = T("dedos"); c["dedos"] = T("dedos", "dedos"); c["baja"] = T("dedos", "baja"); c["acercan"] = T("dedos", "acercan")
    c["carga"] = T("dedos", "carga"); c["mide"] = T("dedos", "mide")
    c["e0"] = T("ejes"); c["tres"] = T("ejes", "tres"); c["inclinas"] = T("ejes", "inclinas"); c["egrav"] = T("ejes", "gravedad")
    c["otra"] = T("ejes", "otra"); c["gira_e"] = T("ejes", "gira")
    c["p0"] = T("pasos"); c["caminar"] = T("pasos", "caminar"); c["contar"] = T("pasos", "contar")
    c["k0"] = T("caida"); c["cae2"] = T("caida", "cae", which=1); c["flota"] = T("caida", "flota"); c["cero"] = T("caida", "cero")
    c["ci0"] = T("cierre"); c["cae"] = T("cierre", "cae"); c["res"] = T("cierre", "resortes")
    c["end"] = tl.duration
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["mueve"] - 0.2, 1.3) + 0.5 * pulse(t, c["gira"] - 0.2, 1.3) + 0.6 * pulse(t, c["cero"] - 0.2, 1.4)
    L.background(P, t, glow=glow)
    with P.transform(0, 45):
        hook_scene(P, t)
        adentro_scene(P, t)
        resortes_scene(P, t)
        _ejes_proxy(P, t)
        pasos_scene(P, t)
        caida_scene(P, t)
        cierre_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def _ejes_proxy(P, t):
    # en la escena de ejes la flecha de gravedad aparece con la palabra «gravedad» de ese bloque
    saved = CUE["grav"]; CUE["grav"] = CUE["egrav"]
    sg = CUE["gira"]; CUE["gira"] = CUE["gira_e"]
    try:
        ejes_scene(P, t)
    finally:
        CUE["grav"] = saved; CUE["gira"] = sg


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    P.text("¿CÓMO SABE", 540, 520, 96, L.FG, 1, face=C.FONT_BLACK)
    P.text("TU CELULAR DÓNDE", 540, 625, 84, L.FG, 1, face=C.FONT_BLACK)
    P.text("ESTÁ EL SUELO?", 540, 735, 96, L.RED, 1, face=C.FONT_BLACK)
    phone(P, 420, 1010, 170, 330, rot=-35, content_rot=35)
    P.arrow(720, 860, 720, 1120, L.RED, 1, w=10, head=36)
    ground(P, 1200, 1.0, 240, 840)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (c["giras"], "whoosh", 0.35), (c["gira"], "pop", 0.4), (c["ojos"], "pop_low", 0.35),
            (c["suelo"], "thump", 0.45),
            (c["a0"] - 0.3, "whoosh", 0.35), (c["chip"], "tick", 0.35), (c["mili"], "tick", 0.35), (c["mueve"], "ding", 0.5),
            (c["resortes"], "pop", 0.35), (c["abajo"] - 0.3, "whoosh_down", 0.35), (c["estiran"], "tick", 0.35),
            (c["dedos"], "pop", 0.35), (c["acercan"], "tick", 0.35), (c["carga"], "riser", 0.3), (c["mide"], "ding", 0.45),
            (c["e0"] - 0.3, "whoosh", 0.35), (c["tres"], "tick", 0.35), (c["inclinas"], "whoosh", 0.3), (c["gira_e"], "ding", 0.55),
            (c["p0"] - 0.3, "whoosh", 0.3), (c["contar"], "pop", 0.4),
            (c["k0"] - 0.2, "whoosh", 0.3), (c["cae2"], "whoosh_down", 0.4), (c["cero"], "thump", 0.55),
            (c["ci0"] - 0.3, "whoosh", 0.35), (c["cae"], "whoosh_down", 0.3), (c["res"], "ding", 0.45)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["mueve"], "pulse": (c["e0"], c["ci0"]), "quiet": [(c["k0"], c["cero"] + 0.1)]}
