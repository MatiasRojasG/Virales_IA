"""Escenas — «¿Cómo ve de noche un auto sin conductor?» (stheq.ia, motion graphics).

Hilo visual: una calle de noche vista desde arriba. Un auto avanza sin nadie al volante (lupa sobre el asiento
vacío) y alguien vestido de negro cruza, casi invisible → visor de cámara: casi negro, «muy poco» → el techo
lanza un pulso láser rojo que viaja hasta la persona y vuelve → regla de 30 cm por milmillonésima de segundo,
contador 0 → 200 y cota de 30 m → barrido de 360°: miles de rayos y cada rebote deja un punto (raycasting
real hecho con NumPy sobre la calle dibujada) → zoom a la persona: líneas de puntos que dibujan su forma →
«LIDAR» → vista lejana: círculo de 300 m, sol → luna sin que cambien los puntos → lidar + cámaras + radar →
vuelta a la calle: la persona rodeada de puntos, un último pulso y su eco (empalme con el inicio).
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
DARK = (0.24, 0.24, 0.25)          # ropa negra: casi invisible sobre el fondo

# ---------------------------------------------------------------- mundo (metros) y vista
K = 23.0                           # px por metro
WC = (0.0, 13.0)                   # punto del mundo en el centro de la vista
SC = (540.0, 885.0)                # centro de la vista en pantalla
PED = (0.0, 30.0)                  # la persona que cruza (cuando se detiene)
PED_R = 1.0                        # radio de choque (exagerado para que se vea)


def S(x, y, k=K, wc=WC, sc=SC):
    return sc[0] + (x - wc[0]) * k, sc[1] - (y - wc[1]) * k


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


# =============================================================== escena de la calle (geometría + raycasting)
BUILD_L = [(-20, -12, -8, 25), (-20, 35, -8, 60)]
BUILD_R = [(8, -12, 20, 25), (8, 35, 20, 60)]
PARKED = [(-3.8, 7.5), (-3.8, 14.0), (3.8, 4.5), (3.8, 18.5)]      # centros (x, y), 2 × 4,6 m
TREES = [(-6.6, 3.0), (-6.6, 20.0), (6.6, 10.0), (6.6, 22.5)]
OTHER = (6.4, 15.5)                                                  # otra persona en la vereda


def rect_segs(x0, y0, x1, y1):
    return [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))]


def scene_geometry():
    segs, circ = [], []
    for b in BUILD_L + BUILD_R:
        segs += rect_segs(*b)
    for (x, y) in PARKED:
        segs += rect_segs(x - 1.0, y - 2.3, x + 1.0, y + 2.3)
    for (x, y) in TREES:
        circ.append((x, y, 0.7, 0))
    circ.append((OTHER[0], OTHER[1], 0.55, 0))
    circ.append((PED[0], PED[1], PED_R, 1))            # 1 = la persona que cruza
    return segs, circ


def raycast(n=2160, rmax=40.0, seed=7):
    """Lanza n rayos desde el techo del auto (0, 0) y devuelve el punto de rebote más cercano de cada uno."""
    rng = np.random.default_rng(seed)
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    d = np.stack([np.sin(th), np.cos(th)], 1)                      # θ = 0: hacia adelante
    best = np.full(n, rmax); kind = np.full(n, -1)
    segs, circ = scene_geometry()
    for (p, q) in segs:
        p = np.array(p, float); q = np.array(q, float); e = q - p
        den = d[:, 0] * (-e[1]) - d[:, 1] * (-e[0])
        with np.errstate(divide="ignore", invalid="ignore"):
            tt = (p[0] * (-e[1]) - p[1] * (-e[0])) / den
            uu = (d[:, 0] * p[1] - d[:, 1] * p[0]) / den
        ok = (np.abs(den) > 1e-9) & (tt > 0.5) & (uu >= 0) & (uu <= 1) & (tt < best)
        best[ok] = tt[ok]; kind[ok] = 0
    for (cx, cy, r, kd) in circ:
        b = d[:, 0] * cx + d[:, 1] * cy
        disc = b * b - (cx * cx + cy * cy - r * r)
        ok = disc > 0
        tt = np.where(ok, b - np.sqrt(np.maximum(disc, 0)), np.inf)
        ok &= (tt > 0.5) & (tt < best)
        best[ok] = tt[ok]; kind[ok] = kd
    hit = kind >= 0
    best = best + rng.normal(0, 0.04, n)                           # pequeño ruido de medición
    pts = np.stack([d[:, 0] * best, d[:, 1] * best], 1)
    # anillos sobre el asfalto: los haces inclinados hacia abajo tocan el suelo a distancias fijas
    gp, gth = [], []
    for rr in (3.2, 4.6, 6.4, 8.9, 12.4, 17.5):
        m = int(rr * 26)
        for j in range(m):
            a = 2 * np.pi * j / m
            i = int(a / (2 * np.pi) * n) % n
            if hit[i] and best[i] < rr: continue           # tapado por algo más cerca
            gp.append((np.sin(a) * rr + rng.normal(0, 0.03), np.cos(a) * rr + rng.normal(0, 0.03))); gth.append(a)
    return th, pts, hit, kind, np.array(gp), np.array(gth)


RAYS = None


def street(P, a=1.0, lights=0.0):
    """Calle de noche desde arriba: calzada, cruce peatonal, veredas, edificios, autos estacionados y árboles."""
    if a <= 0: return
    with P.layer(a):
        x0, _ = S(-5.2, 0); x1, _ = S(5.2, 0)
        P.rect(x0, 300, x1, 1400, (0.075, 0.075, 0.08), 1)
        # línea central segmentada
        for k in range(-6, 30):
            ya, yb = k * 3.0, k * 3.0 + 1.5
            if 25.5 < ya < 34.5 or 25.5 < yb < 34.5: continue
            xa, sa = S(0, ya); _, sb = S(0, yb)
            P.line(xa, sa, xa, sb, L.DIM, 0.9, w=4)
        # calle transversal y cruce peatonal
        _, ty0 = S(0, 34.5); _, ty1 = S(0, 25.5)
        P.rect(40, ty0, 1040, ty1, (0.075, 0.075, 0.08), 1)
        for k in range(9):
            xs = -4.6 + k * 1.15
            a0, b0 = S(xs, 27.6); a1, b1 = S(xs + 0.6, 32.4)
            P.rect(a0, b1, a1, b0, L.LINE, 1)
        # veredas y edificios
        for (bx0, by0, bx1, by1) in BUILD_L + BUILD_R:
            a0, b0 = S(bx0, by0); a1, b1 = S(bx1, by1)
            P.rect(a0, b1, a1, b0, (0.11, 0.11, 0.115), 1)
            P.rect(a0, b1, a1, b0, L.LINE, 1, stroke=3)
        for (cx, cy) in PARKED:
            a0, b0 = S(cx - 1.0, cy - 2.3); a1, b1 = S(cx + 1.0, cy + 2.3)
            P.rect(a0, b1, a1, b0, (0.14, 0.14, 0.15), 1, radius=10)
            P.rect(a0 + 6, b1 + 14, a1 - 6, b1 + 34, (0.09, 0.09, 0.1), 1, radius=4)
        for (cx, cy) in TREES:
            X, Y = S(cx, cy)
            P.circle(X, Y, 0.7 * K, (0.12, 0.12, 0.125), 1)
        # faroles apagados / tenues
        if lights > 0:
            for (cx, cy) in ((-5.8, 12), (5.8, 24)):
                X, Y = S(cx, cy)
                P.circle(X, Y, 60, L.FG, 0.04 * lights, blur=30)


def person_top(P, X, Y, k, a=1.0, col=DARK, walk=0.0, outline=0.0):
    """Persona vista desde arriba (hombros + cabeza), exagerada ×3,4 para que se lea."""
    if a <= 0: return
    s = k * 3.4
    with P.layer(a):
        sw = 0.08 * s * math.sin(walk)
        P.rect(X - 0.27 * s, Y - 0.12 * s + sw, X + 0.27 * s, Y + 0.12 * s - sw, col, 1, radius=0.12 * s)
        P.circle(X, Y, 0.11 * s, lerp_c(col, (0, 0, 0), 0.3), 1)
        if outline > 0:
            P.rect(X - 0.27 * s, Y - 0.12 * s, X + 0.27 * s, Y + 0.12 * s, L.GRAY, outline, stroke=2, radius=0.12 * s)


def car_top(P, X, Y, k, a=1.0, t=0.0, spin=0.0, glow=0.0):
    """Auto visto desde arriba (mirando hacia arriba) con el lidar en el techo."""
    if a <= 0: return
    w, h = 1.95 * k, 4.8 * k
    with P.layer(a):
        P.rect(X - w / 2 - 6, Y - h / 2 + 8, X + w / 2 + 6, Y + h / 2 + 8, (0, 0, 0), 0.6, radius=18, blur=12)
        P.rect(X - w / 2, Y - h / 2, X + w / 2, Y + h / 2, L.FG, 1, radius=0.5 * k)
        P.rect(X - w / 2 + 0.2 * k, Y - h / 2 + 1.05 * k, X + w / 2 - 0.2 * k, Y - h / 2 + 1.75 * k, L.CARD, 1, radius=0.18 * k)
        P.rect(X - w / 2 + 0.25 * k, Y + h / 2 - 1.2 * k, X + w / 2 - 0.25 * k, Y + h / 2 - 0.7 * k, L.CARD, 1, radius=0.15 * k)
        for sx in (-1, 1):                                  # faros
            P.rect(X + sx * w * 0.3 - 0.22 * k, Y - h / 2 + 0.05 * k, X + sx * w * 0.3 + 0.22 * k, Y - h / 2 + 0.25 * k, L.GRAY, 1, radius=4)
        # lidar en el techo
        r = 0.42 * k
        if glow > 0:
            P.circle(X, Y, r * 2.4, L.RED, 0.35 * glow, blur=r)
        P.circle(X, Y, r, L.BG, 1); P.circle(X, Y, r, L.RED, 1, stroke=3)
        ang = spin
        P.line(X, Y, X + math.sin(ang) * r * 0.8, Y - math.cos(ang) * r * 0.8, L.RED, 1, w=3)


def seat_lens(P, X, Y, R, a, t):
    """Lupa sobre la cabina: el volante gira solo y el asiento del conductor está vacío."""
    if a <= 0: return
    with P.layer(a):
        P.circle(X, Y, R, L.BG, 0.96)
        P.c.save()
        pth = skia.Path(); pth.addCircle(X, Y, R - 4); P.c.clipPath(pth, doAntiAlias=True)
        # asiento vacío
        P.rect(X - 95, Y - 20, X + 35, Y + 125, L.CARD, 1, radius=26)
        P.rect(X - 85, Y + 95, X + 25, Y + 150, L.DIM, 1, radius=20)
        # volante
        wx, wy = X - 30, Y - 75
        P.circle(wx, wy, 58, L.FG, 1, stroke=11)
        ang = 0.6 * math.sin(t * 1.3)
        for k in range(3):
            q = ang + k * 2 * math.pi / 3 + math.pi / 2
            P.line(wx, wy, wx + math.cos(q) * 54, wy + math.sin(q) * 54, L.FG, 1, w=9)
        P.circle(wx, wy, 14, L.FG, 1)
        P.c.restore()
        P.circle(X, Y, R, L.FG, 1, stroke=5)


# --------------------------------------------------------------- persona de frente (nube de puntos)
def inside_person(x, y, stride=0.0):
    """Silueta de una persona caminando, coordenadas normalizadas (alto ≈ 2)."""
    if (x) ** 2 + (y + 0.80) ** 2 < 0.115 ** 2: return True            # cabeza
    if abs(x) < 0.05 and -0.70 < y < -0.62: return True                 # cuello
    if -0.64 < y < 0.02 and abs(x) < 0.215 - 0.03 * max(0, y + 0.3): return True   # torso
    for sgn in (-1, 1):                                                  # brazos
        sw = sgn * stride * 0.12
        cx = sgn * 0.27 + sw * (y + 0.6)
        if -0.60 < y < 0.08 and abs(x - cx) < 0.055: return True
        lx = sgn * 0.09 + sgn * stride * 0.16 * (y + 0.0)                # piernas
        if 0.0 < y < 0.96 and abs(x - lx) < 0.075: return True
    return False


def person_cloud_points(rows=22):
    pts = []
    rng = np.random.default_rng(3)
    for r in range(rows):
        y = -0.94 + r * (1.9 / (rows - 1))
        for k in range(31):
            x = -0.45 + k * 0.03
            if inside_person(x, y, stride=0.8):
                pts.append((x + rng.normal(0, 0.004), y, r))
    return np.array(pts)


PCLOUD = None
NOISE = None


def person_front_path(cx, cy, hgt, stride=0.8):
    """Silueta rellena (para el visor de la cámara)."""
    pth = skia.Path()
    s = hgt / 2
    pth.addCircle(cx, cy - 0.80 * s, 0.115 * s)
    pth.addRRect(skia.RRect.MakeRectXY(skia.Rect(cx - 0.215 * s, cy - 0.66 * s, cx + 0.215 * s, cy + 0.04 * s), 0.08 * s, 0.08 * s))
    for sgn in (-1, 1):
        x = cx + sgn * 0.27 * s
        pth.addRRect(skia.RRect.MakeRectXY(skia.Rect(x - 0.055 * s, cy - 0.60 * s, x + 0.055 * s, cy + 0.08 * s), 0.05 * s, 0.05 * s))
        lx = cx + sgn * (0.09 + stride * 0.08) * s
        pth.addRRect(skia.RRect.MakeRectXY(skia.Rect(lx - 0.075 * s, cy, lx + 0.075 * s, cy + 0.96 * s), 0.05 * s, 0.05 * s))
    return pth


def noise_img():
    global NOISE
    if NOISE is None:
        rng = np.random.default_rng(11)
        frames = []
        for f in range(6):
            v = rng.normal(16, 9, (180, 150)).clip(0, 60).astype(np.uint8)
            rgba = np.dstack([v, v, v, np.full_like(v, 255)])
            frames.append(skia.Image.fromarray(rgba, colorType=skia.kRGBA_8888_ColorType))
        NOISE = frames
    return NOISE


def brackets(P, x0, y0, x1, y1, a, rgb=None, L_=50, w=6):
    rgb = rgb or L.FG
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        P.line(x, y, x + dx * L_, y, rgb, a, w=w); P.line(x, y, x, y + dy * L_, rgb, a, w=w)


# =============================================================== estado del auto y la persona
def car_y(t):
    c = CUE
    return lerp(-4.0, 0.0, prog(t, 0.0, c["cruza"] + 0.6, out_cubic))


def ped_x(t):
    c = CUE
    return lerp(-9.0, PED[0], prog(t, c["alguien"] - 0.3, c["ve"] + 0.2, out_cubic))


def view_street(P, t, a=1.0, cy_car=0.0, px=0.0, ped_vis=0.15, spin=0.0, lidar_glow=0.0):
    """Calle + auto + persona en la vista estándar."""
    street(P, a, lights=1.0)
    X, Y = S(0, cy_car)
    car_top(P, X, Y, K, a, t, spin=spin, glow=lidar_glow)
    PX, PY = S(px, PED[1])
    person_top(P, PX, PY, K, a * 1.0, col=lerp_c(DARK, L.FG, ped_vis), walk=t * 6)
    OX, OY = S(*OTHER)
    person_top(P, OX, OY, K, a, col=lerp_c(DARK, L.FG, ped_vis * 0.8), walk=0)


def pulse_path(t, t0, t1, a_go=0.5):
    """Posición (0..1 ida, 1..2 vuelta) de un pulso entre t0 y t1."""
    u = prog(t, t0, t1)
    return 2 * u


def draw_pulse(P, t, t0, t1, a=1.0, src=(0.0, 0.0), dst=None):
    if a <= 0 or t < t0 or t > t1 + 0.4: return
    dst = dst or (PED[0], PED[1] - PED_R)
    u = 2 * prog(t, t0, t1)
    X0, Y0 = S(*src); X1, Y1 = S(*dst)
    if u <= 1:
        x, y = lerp(X0, X1, u), lerp(Y0, Y1, u)
        P.line(X0, Y0, x, y, L.RED, 0.45 * a, w=4)
        P.circle(x, y, 11, L.RED, a); P.circle(x, y, 26, L.RED, 0.4 * a, blur=10)
    else:
        v = u - 1
        x, y = lerp(X1, X0, v), lerp(Y1, Y0, v)
        P.line(X1, Y1, X0, Y0, L.RED, 0.25 * a * (1 - v), w=3)
        P.line(X1, Y1, x, y, L.FG, 0.5 * a, w=3)
        P.circle(x, y, 9, L.FG, a); P.circle(x, y, 22, L.FG, 0.3 * a, blur=10)
    hit = window(u, 0.95, 1.6, 0.05, 0.5)
    if hit > 0:
        P.circle(X1, Y1, 20 + 40 * (u - 0.95), L.RED, hit * 0.8, stroke=4)


# =============================================================== escenas
def hook_scene(P, t):
    c = CUE
    a = 1 - prog(t, c["o0"] - 0.35, c["o0"] + 0.1, in_out_cubic)
    a2 = prog(t, c["p0"] - 0.3, c["p0"] + 0.15, in_out_cubic)        # vuelve la calle tras el visor
    a = max(a, a2 * (1 - prog(t, c["n_forma"] - 0.6, c["n_forma"] + 0.2)))
    if a <= 0: return
    cy_car = car_y(t)
    px = ped_x(t)
    spin = t * 9
    glow = pulse(t, c["luz"] - 0.2, 1.2)
    with P.layer(a):
        P.c.save(); P.c.clipRect(skia.Rect(0, 330, 1080, 1330))
        street(P, 1, lights=1.0)
        # rayos y puntos del barrido (escena «nube»)
        sweep_layer(P, t)
        X, Y = S(0, cy_car)
        car_top(P, X, Y, K, 1, t, spin=spin, glow=glow)
        PX, PY = S(px, PED[1])
        lit = prog(t, c["n_punto"] - 0.2, c["n_punto"] + 0.6) * 0.0
        person_top(P, PX, PY, K, 1, col=lerp_c(DARK, L.FG, lit), walk=t * 6 if t < c["ve"] else 0)
        OX, OY = S(*OTHER)
        person_top(P, OX, OY, K, 1, col=DARK)
        # pulso de ida y vuelta
        draw_pulse(P, t, c["laser"] - 0.1, c["volver"] + 0.1)
        tiempo_overlay(P, t)
        P.c.restore()
        # lupa sobre el asiento vacío
        la = window(t, c["nadie"] - 0.3, c["alguien"] + 0.2, 0.3, 0.4)
        if la > 0:
            seat_lens(P, 800, 1010, 165, la, t)
            P.line(X + 30, Y - 20, 800 - 120, 1010 + 60, L.FG, la * 0.7, w=3)
            P.text("nadie", 800, 1230, 46, L.RED, la * prog(t, c["nadie"], c["nadie"] + 0.25), face=C.FONT_BLACK)
        # «¿?» sobre la persona
        q = window(t, c["ve"] - 0.15, c["o0"] - 0.1, 0.2, 0.2)
        if q > 0:
            PX, PY = S(px, PED[1])
            P.circle(PX, PY, 70, L.RED, 0.8 * q, stroke=4)
            P.text("?", PX + 110, PY + 30 + 5 * math.sin(t * 3), 120, L.RED, out_back(q) * q, face=C.FONT_BLACK)
        ca = window(t, c["alguien"] - 0.2, c["ve"] - 0.1, 0.3, 0.3)
        if ca > 0:
            PX, PY = S(px, PED[1])
            P.text("¿alguien?", PX - 10, PY + 95, 34, L.GRAY, ca * 0.8, face=C.FONT_SEMI)


def camera_scene(P, t):
    """Visor de cámara: de noche casi no se ve nada."""
    c = CUE
    a = window(t, c["o0"] - 0.35, c["p0"] + 0.05, 0.4, 0.35)
    if a <= 0: return
    x0, y0, x1, y1 = 165, 520, 915, 1260
    with P.layer(a):
        frames = noise_img()
        P.img(frames[int(t * 20) % len(frames)], x0, y0, x1, y1, 1, nearest=False)
        dim = prog(t, c["poco"] - 0.4, c["poco"] + 0.3)
        # la persona, apenas distinguible
        P.c.drawPath(person_front_path(540, 905, 560), paint((0.035, 0.035, 0.04), 0.85 + 0.15 * dim))
        P.rect(x0, y0, x1, y1, (0, 0, 0), 0.35 * dim)
        brackets(P, x0 + 20, y0 + 20, x1 - 20, y1 - 20, 1)
        blink = 0.5 + 0.5 * math.cos(t * 5)
        P.circle(x0 + 60, y0 + 70, 12, L.RED, blink)
        P.text("REC", x0 + 82, y0 + 82, 30, L.FG, 0.9, face=C.FONT_BOLD, align="left")
        # cámara (ícono) arriba a la derecha
        cx, cy = x1 - 95, y0 + 70
        P.rect(cx - 40, cy - 24, cx + 30, cy + 24, L.FG, 1, radius=8)
        pth = skia.Path(); pth.moveTo(cx + 30, cy - 8); pth.lineTo(cx + 56, cy - 22); pth.lineTo(cx + 56, cy + 22); pth.lineTo(cx + 30, cy + 8); pth.close()
        P.c.drawPath(pth, paint(L.FG, 1))
        ma = prog(t, c["poco"] - 0.15, c["poco"] + 0.25)
        if ma > 0:
            P.pill("muy poco", 540, 1180, 40, L.RED, ma)


def tiempo_overlay(P, t):
    """Regla de 30 cm, contador 0 → 200 y cota de 30 m (escena «tiempo»), sobre la calle."""
    c = CUE
    a = window(t, c["t0"] - 0.2, c["n0"] + 0.1, 0.3, 0.4)
    if a <= 0: return
    with P.layer(a):
        # 1) regla: 30 cm por milmillonésima de segundo (recuadro a la derecha)
        ra = window(t, c["cm"] - 0.3, c["si"] + 0.1, 0.3, 0.3)
        if ra > 0:
            bx0, bx1, by = 640, 960, 700
            P.rect(bx0 - 30, by - 110, bx1 + 30, by + 120, L.BG, 0.92 * ra, radius=24)
            P.rect(bx0 - 30, by - 110, bx1 + 30, by + 120, L.FG, 0.8 * ra, stroke=3, radius=24)
            P.line(bx0, by, bx1, by, L.FG, ra, w=6)
            for xx in (bx0, bx1):
                P.line(xx, by - 18, xx, by + 18, L.FG, ra, w=6)
            u = (prog(t, c["cm"] - 0.2, c["segundo"] + 0.4) * 2.0) % 1.0
            P.circle(lerp(bx0, bx1, u), by, 13, L.RED, ra); P.circle(lerp(bx0, bx1, u), by, 30, L.RED, 0.35 * ra, blur=10)
            P.text("30 cm", 800, by - 40, 50, L.RED, ra, face=C.FONT_BLACK)
            P.text("en 1 milmillonésima", 800, by + 62, 30, L.FG, ra * prog(t, c["milm"] - 0.3, c["milm"]), face=C.FONT_SEMI)
            P.text("de segundo", 800, by + 98, 30, L.FG, ra * prog(t, c["milm"] - 0.3, c["milm"]), face=C.FONT_SEMI)
        # 2) pulso de ida y vuelta + contador
        t0, t1 = c["si"] + 0.05, c["milms"] + 0.5
        draw_pulse(P, t, t0, t1)
        ca = window(t, c["si"] - 0.1, c["n0"] + 0.1, 0.3, 0.3)
        if ca > 0:
            n = int(round(200 * prog(t, t0, t1)))
            done = prog(t, t1 - 0.05, t1 + 0.2)
            P.rect(650, 600, 990, 830, L.BG, 0.92 * ca, radius=24)
            P.text(f"{n}", 820, 730, 110, lerp_c(L.FG, L.RED, done), ca, face=C.FONT_BLACK)
            P.text("milmillonésimas", 820, 775, 30, L.FG, ca, face=C.FONT_SEMI)
            P.text("de segundo", 820, 810, 30, L.FG, ca, face=C.FONT_SEMI)
            P.text("ida y vuelta", 820, 640, 30, L.GRAY, ca, face=C.FONT_SEMI)
        # 3) cota de 30 m
        da = window(t, c["metros"] - 0.25, c["n0"] + 0.1, 0.25, 0.4)
        if da > 0:
            xa = 395
            _, ya = S(0, 0); _, yb = S(0, PED[1])
            gr = prog(t, c["metros"] - 0.25, c["metros"] + 0.3, out_cubic)
            ym = lerp(ya, yb, gr)
            P.line(xa, ya, xa, ym, L.RED, da, w=6)
            P.line(xa - 18, ya, xa + 18, ya, L.RED, da, w=6)
            if gr > 0.95: P.line(xa - 18, yb, xa + 18, yb, L.RED, da, w=6)
            P.line(xa, ya, S(0, 0)[0] - 30, ya, L.RED, 0.4 * da, w=2)
            P.line(xa, yb, S(0, PED[1])[0] - 40, yb, L.RED, 0.4 * da, w=2)
            with P.transform(0, 0, 0.85 + 0.15 * out_back(da), cx=xa - 90, cy=(ya + yb) / 2):
                P.rect(xa - 175, (ya + yb) / 2 - 50, xa - 15, (ya + yb) / 2 + 40, L.BG, 0.9 * da, radius=18)
                P.text("30 m", xa - 95, (ya + yb) / 2 + 22, 62, L.RED, da, face=C.FONT_BLACK)


def sweep_angle(t):
    """Ángulo acumulado del barrido (rad): arranca lento en «Ahora» y acelera en «millones»."""
    c = CUE
    if t < c["n0"]: return None
    tm = c["millones"]; sp1, sp2, ramp = 1.6, 10.0, 1.2
    if t < tm: return sp1 * (t - c["n0"])
    base = sp1 * (tm - c["n0"]); u = t - tm
    if u < ramp: return base + sp1 * u + 0.5 * (sp2 - sp1) * u * u / ramp
    return base + sp1 * ramp + 0.5 * (sp2 - sp1) * ramp + sp2 * (u - ramp)


def sweep_layer(P, t):
    """Rayos del barrido y puntos de rebote acumulados."""
    c = CUE
    ang = sweep_angle(t)
    if ang is None: return
    th, pts, hit, kind, gp, gth = RAYS
    n = len(th)
    a = 1 - prog(t, c["n_forma"] - 0.6, c["n_forma"] + 0.2)
    if a <= 0: return
    turns = ang / (2 * math.pi)
    done = min(n, int(ang / (2 * math.pi) * n)) if turns < 1 else n
    # rayos del sector actual
    cur = ang % (2 * math.pi)
    nr = 36 if turns < 1.0 else 70
    for j in range(nr):
        i = int(((cur - j * 0.012) % (2 * math.pi)) / (2 * math.pi) * n) % n
        X0, Y0 = S(0, 0); X1, Y1 = S(*pts[i])
        P.line(X0, Y0, X1, Y1, L.RED, a * 0.35 * (1 - j / nr), w=2)
    # anillos del suelo
    for j in range(len(gp)):
        if turns < 1 and gth[j] > ang: continue
        X, Y = S(*gp[j])
        if 330 < Y < 1330: P.circle(X, Y, 2.4, L.GRAY, a * 0.8)
    # puntos
    hi = pulse(t, c["n_punto"] - 0.1, 1.2)
    sel = np.nonzero(hit[:done] if turns < 1 else hit)[0]
    for i in sel:
        X, Y = S(*pts[i])
        if not (330 < Y < 1330): continue
        rgb = L.RED if kind[i] == 1 else L.FG
        P.circle(X, Y, 3.6 if kind[i] != 1 else 5, rgb, a * 0.95)
    if hi > 0 and len(sel):
        i = sel[int(len(sel) * 0.62)]
        X, Y = S(*pts[i])
        P.circle(X, Y, 30, L.RED, hi, stroke=4)
        P.circle(X, Y, 8, L.RED, hi)


def cloud_scene(P, t):
    """Zoom a la persona: las filas de puntos dibujan su forma; «LIDAR»."""
    c = CUE
    a = window(t, c["n_forma"] - 0.5, c["d0"] + 0.05, 0.5, 0.45)
    if a <= 0: return
    with P.layer(a):
        cx, cy, hgt = 540, 860, 640
        zoom = 0.75 + 0.25 * prog(t, c["n_forma"] - 0.5, c["n_forma"] + 0.4, out_cubic)
        rows = PCLOUD[:, 2].max() + 1
        rev = prog(t, c["n_forma"] - 0.3, c["n_persona"] + 0.5)
        for (x, y, r) in PCLOUD:
            ra = clamp(rev * (rows + 2) - r)
            if ra <= 0: continue
            X = cx + x * hgt / 2 * zoom; Y = cy + y * hgt / 2 * zoom
            P.circle(X, Y, 4.6 * ra, L.RED, ra)
        # escaneo: una línea que baja
        if rev < 1:
            yy = cy + (-1 + 2 * rev) * hgt / 2 * zoom
            P.line(200, yy, 880, yy, L.RED, 0.35, w=3)
        la = prog(t, c["lidar"] - 0.25, c["lidar"] + 0.25)
        if la > 0:
            with P.transform(0, 0, 0.85 + 0.15 * out_back(la), cx=540, cy=1240):
                P.pill("LIDAR", 540, 1240, 54, L.FG, la, face=C.FONT_BLACK)


def dato_scene(P, t):
    """Vista lejana: el auto en el centro de un círculo de 300 m. Sol → luna; los puntos no cambian."""
    c = CUE
    a = window(t, c["d0"] - 0.35, c["e0"] + 0.05, 0.45, 0.4)
    if a <= 0: return
    with P.layer(a):
        cx, cy, R = 540, 860, 330
        grow = prog(t, c["alrededor"] - 0.4, c["auto"] + 0.4, in_out_cubic)
        rr = R * grow
        if rr > 2:
            P.circle(cx, cy, rr, L.FG, 0.05)
            P.circle(cx, cy, rr, L.FG, 0.8, stroke=3)
            for q in (0.33, 0.66):
                P.circle(cx, cy, rr * q, L.DIM, 0.7, stroke=2)
        # puntos «de ciudad» dentro del círculo (fijos)
        rng = np.random.default_rng(5)
        N = 420
        ang = rng.uniform(0, 2 * np.pi, N); rad = np.sqrt(rng.uniform(0.01, 1, N))
        for k in range(N):
            if rad[k] > grow: continue
            P.circle(cx + math.cos(ang[k]) * rad[k] * R, cy + math.sin(ang[k]) * rad[k] * R, 2.6, L.FG, 0.55)
        # barrido
        sa = t * 3.0
        P.line(cx, cy, cx + math.cos(sa) * rr, cy + math.sin(sa) * rr, L.RED, 0.6 * grow, w=3)
        # auto pequeño
        car_top(P, cx, cy, 14, 1, t, spin=t * 9)
        # 300 m
        la = prog(t, c["m300"] - 0.25, c["m300"] + 0.25)
        if la > 0:
            P.line(cx, cy, cx + R, cy, L.RED, la, w=6, frac=prog(t, c["m300"] - 0.25, c["m300"] + 0.35, out_cubic))
            with P.transform(0, 0, 0.85 + 0.15 * out_back(la), cx=cx + R * 0.55, cy=cy - 40):
                P.rect(cx + R * 0.55 - 120, cy - 105, cx + R * 0.55 + 120, cy - 20, L.BG, 0.9 * la, radius=18)
                P.text("300 m", cx + R * 0.55, cy - 40, 66, L.RED, la, face=C.FONT_BLACK)
            P.text("según Waymo", cx, cy + R + 60, 32, L.GRAY, la, face=C.FONT_SEMI)
        # día / noche
        da = prog(t, c["dia"] - 0.25, c["dia"] + 0.2)
        na = prog(t, c["noche"] - 0.25, c["noche"] + 0.2)
        if da > 0:
            L.sun(P, 900, 560, 36 * (1 - na), da * (1 - na), t)
            L.moon(P, 900, 560, 38, na)


def camera_icon(P, x, y, s, a):
    P.rect(x - 40 * s, y - 26 * s, x + 30 * s, y + 26 * s, L.FG, a, radius=8 * s)
    pth = skia.Path(); pth.moveTo(x + 30 * s, y - 9 * s); pth.lineTo(x + 58 * s, y - 24 * s); pth.lineTo(x + 58 * s, y + 24 * s); pth.lineTo(x + 30 * s, y + 9 * s); pth.close()
    P.c.drawPath(pth, paint(L.FG, a))
    P.circle(x - 5 * s, y, 13 * s, L.BG, a)


def radar_icon(P, x, y, s, a, t):
    for k in range(3):
        r = (22 + 22 * k) * s
        P.c.drawArc(skia.Rect(x - r, y - r, x + r, y + r), -135, 90, False, paint(L.FG, a, 6 * s))
    P.circle(x, y, 9 * s, L.FG, a)
    rr = (20 + 60 * ((t * 0.8) % 1)) * s
    P.c.drawArc(skia.Rect(x - rr, y - rr, x + rr, y + rr), -135, 90, False, paint(L.RED, a * (1 - (t * 0.8) % 1), 5 * s))


def lidar_icon(P, x, y, s, a, t):
    P.rect(x - 34 * s, y - 30 * s, x + 34 * s, y + 30 * s, L.FG, a, radius=14 * s)
    P.rect(x - 34 * s, y - 6 * s, x + 34 * s, y + 6 * s, L.RED, a)
    q = t * 6
    P.line(x, y, x + math.cos(q) * 70 * s, y + math.sin(q) * 22 * s, L.RED, a * 0.5, w=3)


def equipo_scene(P, t):
    c = CUE
    a = window(t, c["e0"] - 0.3, c["k0"] + 0.05, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        cx, cy = 540, 960
        car_top(P, cx, cy, 52, 1, t, spin=t * 9)
        items = [("lidar", 540, 600, c["e0"] - 0.1, lidar_icon),
                 ("cámaras", 230, 800, c["camaras"] - 0.15, None),
                 ("radar", 850, 800, c["radar"] - 0.15, radar_icon)]
        for (lab, x, y, t0, fn) in items:
            ia = prog(t, t0, t0 + 0.3)
            if ia <= 0: continue
            with P.transform(0, 0, 0.8 + 0.2 * out_back(ia), cx=x, cy=y):
                P.circle(x, y, 95, L.CARD, ia)
                P.circle(x, y, 95, L.FG, ia * 0.8, stroke=3)
                if lab == "cámaras": camera_icon(P, x, y, 1.0, ia)
                elif lab == "lidar": lidar_icon(P, x, y, 1.0, ia, t)
                else: radar_icon(P, x, y + 20, 1.0, ia, t)
                P.text(lab, x, y + 140, 40, L.FG, ia, face=C.FONT_BOLD)
            P.line(x, y + (95 if y > 700 else 95), cx, cy - 60, L.RED, 0.5 * ia, w=3, frac=prog(t, t0 + 0.1, t0 + 0.6))


def end_scene(P, t):
    """Vuelta a la calle: la persona rodeada de puntos, un último pulso y su eco (empalme con el inicio)."""
    c = CUE
    a = prog(t, c["k0"] - 0.35, c["k0"] + 0.15, in_out_cubic)
    if a <= 0: return
    th, pts, hit, kind, gp, gth = RAYS
    with P.layer(a):
        P.c.save(); P.c.clipRect(skia.Rect(0, 330, 1080, 1330))
        street(P, 1, lights=1.0)
        X, Y = S(0, 0)
        glow = pulse(t, c["lanza"] - 0.2, 1.2)
        car_top(P, X, Y, K, 1, t, spin=t * 9, glow=glow)
        fade = 1 - prog(t, c["subirias"] - 0.2, c["end"] - 0.3)
        for i in np.nonzero(hit)[0]:
            Xp, Yp = S(*pts[i])
            if not (330 < Yp < 1330): continue
            if kind[i] == 1:
                P.circle(Xp, Yp, 5, L.RED, fade)
            else:
                P.circle(Xp, Yp, 3.4, L.FG, 0.6 * fade)
        for j in range(len(gp)):
            Xp, Yp = S(*gp[j])
            if 330 < Yp < 1330: P.circle(Xp, Yp, 2.4, L.GRAY, 0.5 * fade)
        PX, PY = S(*PED)
        person_top(P, PX, PY, K, 1, col=DARK)
        OX, OY = S(*OTHER)
        person_top(P, OX, OY, K, 1, col=DARK)
        draw_pulse(P, t, c["lanza"] - 0.15, c["eco"] + 0.2)
        ea = window(t, c["eco"] - 0.1, c["subirias"], 0.1, 0.6)
        if ea > 0:
            for k in range(3):
                u = ((t - c["eco"]) * 0.9 + k / 3) % 1
                P.circle(PX, PY, 40 + 140 * u, L.RED, ea * (1 - u) * 0.8, stroke=4)
        P.c.restore()


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, RAYS, PCLOUD
    TL, EP = tl, episode
    c = {}
    c["nadie"] = T("hook", "nadie"); c["alguien"] = T("hook", "Alguien"); c["cruza"] = T("hook", "cruza")
    c["ve"] = T("hook", "ve")
    c["o0"] = T("oscuro"); c["poco"] = T("oscuro", "poco")
    c["p0"] = T("pulso"); c["luz"] = T("pulso", "luz"); c["laser"] = T("pulso", "láser"); c["volver"] = T("pulso", "volver")
    c["t0"] = T("tiempo"); c["cm"] = T("tiempo", "30"); c["milm"] = T("tiempo", "milmillonésima")
    c["segundo"] = T("tiempo", "segundo"); c["si"] = T("tiempo", "Si"); c["milms"] = T("tiempo", "milmillonésimas")
    c["metros"] = T("tiempo", "metros")
    c["n0"] = T("nube"); c["millones"] = T("nube", "millones"); c["n_punto"] = T("nube", "punto")
    c["n_forma"] = T("nube", "dibujan"); c["n_persona"] = T("nube", "persona"); c["lidar"] = T("nube", "lidar")
    c["d0"] = T("dato"); c["alrededor"] = T("dato", "alrededor"); c["auto"] = T("dato", "auto")
    c["m300"] = T("dato", "300"); c["dia"] = T("dato", "día"); c["noche"] = T("dato", "noche")
    c["e0"] = T("equipo"); c["camaras"] = T("equipo", "cámaras"); c["radar"] = T("equipo", "radar")
    c["k0"] = T("cierre"); c["lanza"] = T("cierre", "lanza"); c["eco"] = T("cierre", "eco")
    c["subirias"] = T("cierre", "subirías")
    c["end"] = tl.duration
    CUE = c
    RAYS = raycast()
    PCLOUD = person_cloud_points()
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["luz"] - 0.2, 1.3) + 0.5 * pulse(t, c["n_persona"] - 0.2, 1.3) + 0.4 * pulse(t, c["m300"] - 0.2, 1.3)
    L.background(P, t, glow=glow)
    hook_scene(P, t)
    camera_scene(P, t)
    cloud_scene(P, t)
    dato_scene(P, t)
    equipo_scene(P, t)
    end_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    P.text("¿CÓMO VE DE NOCHE", 540, 470, 80, L.FG, 1, face=C.FONT_BLACK)
    P.text("SIN CONDUCTOR?", 540, 570, 90, L.RED, 1, face=C.FONT_BLACK)
    # persona en nube de puntos + auto
    cx, cy, hgt = 540, 930, 520
    for (x, y, r) in PCLOUD:
        P.circle(cx + x * hgt / 2, cy + y * hgt / 2, 4.2, L.RED, 1)
    car_top(P, 540, 1300, 40, 1, 0.0, spin=0.6, glow=0.6)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (c["nadie"], "pop", 0.45), (c["alguien"], "whoosh", 0.25), (c["ve"], "thump", 0.5),
            (c["o0"] - 0.3, "whoosh_down", 0.35), (c["poco"], "pop_low", 0.4),
            (c["p0"] - 0.3, "whoosh", 0.35), (c["luz"], "ding", 0.45), (c["laser"], "tick", 0.4), (c["volver"], "tick", 0.35),
            (c["cm"], "pop", 0.35), (c["si"], "riser", 0.3), (c["milms"] + 0.5, "ding", 0.45), (c["metros"], "thump", 0.45),
            (c["n0"], "riser", 0.3), (c["millones"], "whoosh", 0.35), (c["n_punto"], "pop", 0.4),
            (c["n_forma"] - 0.4, "whoosh", 0.35), (c["n_persona"], "ding", 0.5), (c["lidar"], "pop", 0.45),
            (c["d0"] - 0.3, "whoosh_down", 0.35), (c["m300"], "ding", 0.5), (c["noche"], "tick", 0.35),
            (c["e0"] - 0.2, "whoosh", 0.3), (c["camaras"], "pop", 0.35), (c["radar"], "pop", 0.35),
            (c["k0"] - 0.3, "whoosh", 0.35), (c["lanza"], "tick", 0.4), (c["eco"] + 0.2, "ding", 0.45)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["p0"], "pulse": (c["n0"], c["e0"]), "quiet": [(c["ve"] - 0.1, c["o0"] + 0.3)]}
