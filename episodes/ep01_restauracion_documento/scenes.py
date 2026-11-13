"""Escenas del Episodio 1 (v2) — una sola toma continua.

Toda la historia ocurre dentro del documento real: la cámara (centro, zoom y altura en
pantalla) viaja con interpolación geométrica del zoom y easing; los conceptos se dibujan
como capas sobre los píxeles verdaderos (incluido el punto con ruido que se corrige).
Los cambios de foco usan profundidad de campo (desenfoque) en vez de cortes.
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import (image, NEAREST, LINEAR, CUBIC, draw_blurred, vignette, vband,
                            spring, paint, font)
from reelforge.ease import (clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back,
                            in_out_cubic, out_quint, smooth, in_cubic)

TL = None
D = {}
EP = {}
CHUNKS = []
KEYS = []          # fotogramas clave de cámara
CUE = {}           # tiempos de cada evento

PAPER255 = np.array([int(v * 255) for v in C.PAPER], np.uint8)
INK255 = np.array([int(v * 255) for v in C.INK], np.uint8)

PX, PY = 16, 28            # el punto con ruido protagonista (columna, fila)
STROKE = (19, 23, 22, 35)  # trazo vecino de la «I»: x0, x1 (excl.), y0, y1
SY_DEFAULT = 860


def doc_rgba(b):
    rgb = np.where(b[..., None] == 1, INK255, PAPER255)
    return np.dstack([rgb, np.full(b.shape, 255, np.uint8)])


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def fmt(v, dec=0):
    return f"{v:.{dec}f}".replace(".", ",")


# =============================================================== cámara
def state(cx, cy, z, sy=SY_DEFAULT):
    return (cx, cy, z, sy)


def cam_interp(a, b, u):
    z = a[2] * (b[2] / a[2]) ** u
    if abs(math.log(b[2] / a[2])) > 0.05:      # el punto objetivo se mueve recto en pantalla
        w = (1 / z - 1 / a[2]) / (1 / b[2] - 1 / a[2])
    else:
        w = u
    return (lerp(a[0], b[0], w), lerp(a[1], b[1], w), z, lerp(a[3], b[3], u))


def cam(t):
    k = 0
    while k + 1 < len(KEYS) and KEYS[k + 1][0] <= t:
        k += 1
    if k + 1 >= len(KEYS):
        s = KEYS[-1][1]
    else:
        (t0, a), (t1, b) = KEYS[k], KEYS[k + 1]
        s = cam_interp(a, b, in_out_cubic((t - t0) / (t1 - t0))) if a != b else a
    # respiración sutil para que nunca quede estático
    br = 1 + 0.010 * math.sin(t * 0.55)
    return (s[0] + 0.15 * math.sin(t * 0.37) / max(1, s[2] / 20), s[1], s[2] * br, s[3])


def to_screen(cs, x, y):
    cx, cy, z, sy = cs
    return (x - cx) * z + C.W / 2, (y - cy) * z + sy


# =============================================================== documento
def doc_layers(t):
    """Qué imagen se ve y con qué máscara: (base, [(clave, clip)])."""
    t_simple, t_asi = CUE["wipe0"], CUE["wipe1"]
    t_rw0, t_rw1 = CUE["rewind0"], CUE["rewind1"]
    h, w = D["orig"].shape
    if t < CUE["iter0"]:
        if t < t_simple:
            return "obs", []
        if t < t_rw0:
            u = in_out_cubic((t - t_simple) / (t_asi - t_simple))
            return "obs", [("lab", ("rect", -8, -8, lerp(-8, w + 8, u), h + 8))]
        if t < t_rw1:
            u = 1 - in_cubic((t - t_rw0) / (t_rw1 - t_rw0))
            return "obs", [("lab", ("rect", -8, -8, lerp(-8, w + 8, u), h + 8))]
        return "obs", []
    # pasadas: ondas circulares desde el punto protagonista
    lv = D["levels"]
    for k in range(len(lv) - 1, 0, -1):
        tk = CUE["iter0"] + CUE["iter_dt"] * (k - 1)
        if t >= tk:
            u = out_cubic((t - tk) / 0.9)
            r = lerp(0, 560, u)
            if u >= 1:
                return f"h{lv[k]}", []
            return f"h{lv[k - 1]}", [(f"h{lv[k]}", ("circle", PX + 0.5, PY + 0.5, r))]
    return "h0", []


def draw_image(P, key, z, a=1.0):
    h, w = D["orig"].shape
    im = image(key, D["rgba"][key])
    na = prog(z, 7, 13, smooth)        # filtro bicúbico al alejarse, píxeles nítidos al acercarse
    p = skia.Paint(); p.setAlphaf(a)
    if na < 1:
        P.c.drawImageRect(im, skia.Rect(0, 0, w, h), CUBIC, p)
    if na > 0:
        p2 = skia.Paint(); p2.setAlphaf(a * na)
        P.c.drawImageRect(im, skia.Rect(0, 0, w, h), NEAREST, p2)


def visible(cs):
    cx, cy, z, sy = cs
    h, w = D["orig"].shape
    x0 = max(0, int(cx - C.W / 2 / z) - 1); x1 = min(w, int(cx + C.W / 2 / z) + 2)
    y0 = max(0, int(cy - sy / z) - 1); y1 = min(h, int(cy + (C.H - sy) / z) + 2)
    return x0, x1, y0, y1


def draw_world(P, t, cs):
    cx, cy, z, sy = cs
    h, w = D["orig"].shape
    cv = P.c
    cv.save()
    cv.translate(C.W / 2, sy); cv.scale(z, z); cv.translate(-cx, -cy)
    # tarjeta de papel con sombra
    P.rect(-4, 2, w + 4, h + 14, (0, 0, 0), 0.6, radius=6, blur=26 / z)
    P.rect(-7, -7, w + 7, h + 7, C.PAPER, 1, radius=6)
    base, extra = doc_layers(t)
    draw_image(P, base, z)
    for key, clip in extra:
        cv.save()
        if clip[0] == "rect":
            cv.clipRect(skia.Rect(*clip[1:]), doAntiAlias=True)
        else:
            pth = skia.Path(); pth.addCircle(clip[1], clip[2], clip[3]); cv.clipPath(pth, doAntiAlias=True)
        P.rect(-7, -7, w + 7, h + 7, C.PAPER, 1, radius=6)
        draw_image(P, key, z)
        cv.restore()
        if clip[0] == "rect" and 0 < clip[3] < w + 8:
            P.line(clip[3], -20, clip[3], h + 20, C.CYAN, 1, w=5 / z, glow=True)
        if clip[0] == "circle" and 0 < clip[3] < 559:
            fade = 1 - clip[3] / 560
            cv.drawCircle(clip[1], clip[2], clip[3], paint(C.CYAN, 0.9 * fade, stroke=4 / z))
    # retícula de píxeles al acercarse
    ga = prog(z, 14, 26)
    if ga > 0:
        x0, x1, y0, y1 = visible(cs)
        lp = paint(C.BG, 0.22 * ga, stroke=1.4 / z, cap="butt")
        for x in range(x0, x1 + 1):
            cv.drawLine(x, max(0, y0), x, min(h, y1), lp)
        for y in range(y0, y1 + 1):
            cv.drawLine(max(0, x0), y, min(w, x1), y, lp)
    world_overlays(P, t, cs)
    cv.restore()


def sq(P, x, y, rgb, a, z, wpx=5, inset=0.06, fill=False):
    if a <= 0: return
    if fill:
        P.rect(x + inset, y + inset, x + 1 - inset, y + 1 - inset, rgb, a)
    else:
        P.rect(x + inset, y + inset, x + 1 - inset, y + 1 - inset, rgb, a, stroke=wpx / z)


def world_overlays(P, t, cs):
    cx, cy, z, sy = cs
    orig, obs = D["orig"], D["obs"]
    x0, x1, y0, y1 = visible(cs)
    # --- problema: puntos invertidos
    a_rev = prog(t, CUE["rev"], CUE["rev"] + 0.3) * (1 - prog(t, CUE["one"] - 0.6, CUE["one"]))
    if a_rev > 0 and z > 6:
        a_ip = prog(t, CUE["ink2pap"], CUE["ink2pap"] + 0.35)
        a_pi = prog(t, CUE["pap2ink"], CUE["pap2ink"] + 0.35)
        pr = pulse(t, CUE["rev"], 0.6)
        for y in range(y0, y1):
            for x in range(x0, x1):
                if orig[y, x] != obs[y, x]:
                    ink_lost = orig[y, x] == 1
                    col = lerp_c(C.WHITE, C.PINK if ink_lost else C.VIOLET, a_ip if ink_lost else a_pi)
                    sq(P, x, y, col, a_rev, z, wpx=4 + 3 * pr)
    # --- curiosidad / intuición: el punto protagonista
    a_one = prog(t, CUE["one"], CUE["one"] + 0.4) * (1 - prog(t, CUE["net0"] - 0.4, CUE["net0"]))
    if a_one > 0:
        man = pulse(t, CUE["mancha"], 0.7) + pulse(t, CUE["mancha"] + 0.6, 0.7)
        col = lerp_c(C.CYAN, C.PINK, prog(t, CUE["mancha"], CUE["mancha"] + 0.3))
        g = 0.12 * man
        P.rect(PX - 0.12 - g, PY - 0.12 - g, PX + 1.12 + g, PY + 1.12 + g, col, a_one, stroke=7 / z)
    # vecinos (8) en onda
    a_nb = prog(t, CUE["around"], CUE["around"] + 0.3) * (1 - prog(t, CUE["net0"] - 0.4, CUE["net0"]))
    if a_nb > 0:
        ring = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
        for k, (dx, dy) in enumerate(ring):
            ak = a_nb * prog(t, CUE["around"] + 0.07 * k, CUE["around"] + 0.07 * k + 0.3)
            sq(P, PX + dx, PY + dy, C.VIOLET, ak, z, wpx=5)
    # trazo de tinta
    a_tr = prog(t, CUE["trazos"], CUE["trazos"] + 0.4) * (1 - prog(t, CUE["analog"], CUE["analog"] + 0.4))
    if a_tr > 0:
        sx0, sx1, sy0, sy1 = STROKE
        for y in range(sy0, sy1):
            for x in range(sx0, sx1):
                if obs[y, x]:
                    d = abs(y - PY)
                    sq(P, x, y, C.CYAN, a_tr * 0.45 * prog(t, CUE["trazos"] + 0.03 * d, CUE["trazos"] + 0.03 * d + 0.3),
                       z, fill=True, inset=0.0)
        P.rect(sx0 - 0.1, sy0 - 0.1, sx1 + 0.1, sy1 + 0.1, C.CYAN, a_tr, stroke=5 / z, radius=0.3)
    # --- red de Markov
    a_net = prog(t, CUE["net0"], CUE["net0"] + 0.3) * (1 - prog(t, CUE["iter0"] - 0.2, CUE["iter0"] + 0.6))
    if a_net > 0:
        tr = CUE["red"]
        lw = 4.5 / z
        # aristas a los 4 vecinos del protagonista
        for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            fr = prog(t, CUE["net0"], CUE["net0"] + 0.5)
            P.line(PX + .5, PY + .5, PX + .5 + dx * fr, PY + .5 + dy * fr, C.VIOLET, a_net, w=lw * 1.6, glow=True)
        # malla completa en onda
        for y in range(y0, y1):
            for x in range(x0, x1):
                d = abs(x - PX) + abs(y - PY)
                u = prog(t, tr + 0.05 * d, tr + 0.05 * d + 0.35)
                if u <= 0: continue
                if x + 1 < x1:
                    P.line(x + .5, y + .5, x + .5 + u, y + .5, C.VIOLET, a_net * 0.8, w=lw)
                if y + 1 < y1:
                    P.line(x + .5, y + .5, x + .5, y + .5 + u, C.VIOLET, a_net * 0.8, w=lw)
        for y in range(y0, y1):
            for x in range(x0, x1):
                d = abs(x - PX) + abs(y - PY)
                u = out_back(prog(t, tr + 0.05 * d, tr + 0.05 * d + 0.35))
                if u <= 0 and not (x == PX and y == PY): continue
                rr = 0.11 * (u if not (x == PX and y == PY) else 1.6)
                P.circle(x + .5, y + .5, rr, C.WHITE if not obs[y, x] else C.VIOLET, a_net)
                P.circle(x + .5, y + .5, rr, C.VIOLET, a_net, stroke=2.5 / z)
        # flechas que aparecen y se disuelven en aristas simétricas
        ta, tn = CUE["arrows"], CUE["nadie"]
        aa = prog(t, ta, ta + 0.3) * (1 - prog(t, tn, tn + 0.6))
        if aa > 0:
            pairs = [((0, 0), (1, 0)), ((0, 0), (0, -1)), ((-1, 0), (0, 0)), ((0, 1), (0, 0)),
                     ((1, 0), (2, 0)), ((1, -1), (1, 0))]
            for k, ((ax, ay), (bx, by)) in enumerate(pairs):
                xa, ya = PX + ax + .5, PY + ay + .5
                xb, yb = PX + bx + .5, PY + by + .5
                ang = math.atan2(yb - ya, xb - xa)
                hl = 0.32 * aa
                xe, ye = xb - 0.2 * math.cos(ang), yb - 0.2 * math.sin(ang)
                pth = skia.Path(); pth.moveTo(xe, ye)
                for s_ in (1, -1):
                    pth.lineTo(xe - hl * math.cos(ang + s_ * 0.5), ye - hl * math.sin(ang + s_ * 0.5))
                pth.close()
                P.c.drawPath(pth, paint(lerp_c(C.WHITE, C.PINK, prog(t, tn - 0.1, tn + 0.2)), aa))


# =============================================================== capas de pantalla
def spotlight(P, t, cs):
    """Oscurece todo menos un círculo alrededor del protagonista."""
    r_big = 1500
    r = r_big
    if t >= CUE["one"]:
        r = lerp(r_big, 125, prog(t, CUE["one"], CUE["one"] + 0.9, in_out_cubic))
    if t >= CUE["around"]:
        r = lerp(125, 430, prog(t, CUE["around"], CUE["around"] + 1.2, in_out_cubic))
    if t >= CUE["trazos"] - 0.4:
        r = lerp(430, r_big, prog(t, CUE["trazos"] - 0.4, CUE["trazos"] + 0.8, in_out_cubic))
    if r >= r_big - 1: return
    x, y = to_screen(cs, PX + .5, PY + .5)
    pth = skia.Path(); pth.setFillType(skia.PathFillType.kEvenOdd)
    pth.addRect(skia.Rect(0, 0, C.W, C.H)); pth.addCircle(x, y, r)
    P.c.drawPath(pth, paint(C.BG, 0.86))
    P.c.drawCircle(x, y, r, paint(C.CYAN, 0.35, stroke=3))


def question(P, t, cs):
    a = prog(t, CUE["bien"], CUE["bien"] + 0.35) * (1 - prog(t, CUE["around"], CUE["around"] + 0.4))
    if a <= 0: return
    x, y = to_screen(cs, PX + .5, PY + .5)
    bob = 10 * math.sin(t * 5)
    shake = 9 * math.sin(t * 60) * pulse(t, CUE["imposible"], 0.5)
    P.text("?", x + shake, y - 175 + bob, 150, C.CYAN, out_back(a), face=C.FONT_BLACK, glow=0.8)
    P.pill("¿tinta?", x - 230, y + 10, 34, C.WHITE, a * prog(t, CUE["bien"] + 0.2, CUE["bien"] + 0.5), fill_a=0.08)
    P.pill("¿mancha?", x + 230, y + 10, 34, C.PINK, a * prog(t, CUE["mal"], CUE["mal"] + 0.3), fill_a=0.08)


def labels_world(P, t, cs):
    # problema
    a = prog(t, CUE["ink2pap"], CUE["ink2pap"] + 0.3) * (1 - prog(t, CUE["one"] - 0.6, CUE["one"]))
    P.pill("tinta → papel", 300, 400, 36, C.PINK, a)
    a = prog(t, CUE["pap2ink"], CUE["pap2ink"] + 0.3) * (1 - prog(t, CUE["one"] - 0.6, CUE["one"]))
    P.pill("papel → tinta", 780, 400, 36, C.VIOLET, a)
    # mancha / trazo
    x, y = to_screen(cs, PX + .5, PY + .5)
    a = window(t, CUE["mancha"], CUE["trazos"] + 0.2, 0.3, 0.3)
    P.pill("¿mancha aislada?", x, y - 300, 36, C.PINK, out_back(prog(t, CUE["mancha"], CUE["mancha"] + 0.35)) * a)
    sx, sy_ = to_screen(cs, (STROKE[0] + STROKE[1]) / 2, STROKE[2])
    a = window(t, CUE["trazos"] + 0.2, CUE["analog"] + 0.2, 0.3, 0.3)
    P.pill("trazo de tinta", sx, sy_ - 60, 36, C.CYAN, out_back(prog(t, CUE["trazos"] + 0.2, CUE["trazos"] + 0.55)) * a)
    # red de Markov
    a = window(t, CUE["markov"] - 0.1, CUE["bal0"] + 0.2, 0.35, 0.4)
    if a > 0:
        s = out_back(prog(t, CUE["markov"] - 0.1, CUE["markov"] + 0.35))
        with P.transform(0, 0, 0.85 + 0.15 * s, cx=540, cy=400):
            P.rect(170, 330, 910, 470, C.BG, 0.88 * a, radius=26)
            P.rect(170, 330, 910, 470, C.VIOLET, 0.8 * a, stroke=3, radius=26)
            P.text("RED DE MARKOV", 540, 400, 62, C.WHITE, a, face=C.FONT_BLACK, glow=0.4)
            P.text("cada punto conectado con sus vecinos", 540, 448, 30, C.GRAY, a, face=C.FONT_MED)


# ---------- analogía: la palabra que no escuchaste bien
def analogy(P, t):
    t0, t1 = CUE["analog"], CUE["net0"]
    a = window(t, t0, t1, 0.4, 0.35)
    if a <= 0: return
    cy = 820
    s = 0.9 + 0.1 * out_back(prog(t, t0, t0 + 0.5))
    with P.layer(a):
        with P.transform(0, 0, s, cx=540, cy=cy):
            P.rect(110, cy - 170, 970, cy + 150, C.BG2, 0.95, radius=40)
            P.rect(110, cy - 170, 970, cy + 150, C.WHITE, 0.25, stroke=3, radius=40)
            pth = skia.Path(); pth.moveTo(250, cy + 148); pth.lineTo(220, cy + 230); pth.lineTo(330, cy + 148); pth.close()
            P.c.drawPath(pth, paint(C.BG2, 0.95))
            P.text("«vamos a la pl_ya»", 540, cy - 95, 32, C.GRAY, 1, face=C.FONT_MED)
            f = font(96, C.FONT_BOLD)
            parts = ["pl", "a", "ya"]
            ws = [f.measureText(p_) for p_ in parts]
            x = 540 - sum(ws) / 2
            yb = cy + 45
            t_lado = CUE["lado"]
            hi = prog(t, t_lado - 0.2, t_lado + 0.2)
            fix = prog(t, t_lado + 0.35, t_lado + 0.8)
            for k, (p_, wk) in enumerate(zip(parts, ws)):
                if k == 1:
                    # mancha de ruido que se convierte en la letra correcta
                    rng = np.random.default_rng(int(t * 12))
                    for _ in range(26):
                        rx = x + rng.random() * wk; ry = yb - 70 + rng.random() * 75
                        P.rect(rx, ry, rx + 12, ry + 12, C.PINK, (1 - fix) * 0.9)
                    with P.transform(0, 0, 0.6 + 0.4 * out_back(fix), cx=x + wk / 2, cy=yb - 30):
                        P.c.drawString(p_, x, yb, f, paint(C.CYAN, fix))
                        if fix > 0:
                            P.c.drawString(p_, x, yb, f, paint(C.CYAN, 0.5 * fix, blur=14))
                else:
                    col = lerp_c(C.WHITE, C.VIOLET, hi)
                    P.c.drawString(p_, x, yb, f, paint(col, 1))
                    P.line(x + 6, yb + 22, x + wk - 6, yb + 22, C.VIOLET, hi, w=6)
                x += wk


# ---------- la balanza
BAL_PIV = (540, 690)
BEAM = 360
HANG = 240


def bal_angle(t):
    alpha, beta = D["alpha"], D["beta"]
    tl_ = CUE["negro"]
    left = alpha * spring(max(0, t - (tl_ + 0.35)) * 1.3)
    right = 0.0
    for k in range(4):
        tk = CUE["blanco"] + 0.22 * k + 0.35
        right += beta * spring(max(0, t - tk) * 1.3)
    k_deg = 3.6
    return math.radians(max(-17, min(17, k_deg * (right - left))))


def pan_pos(t, side):
    th = bal_angle(t)
    px, py = BAL_PIV
    ex, ey = px + side * BEAM * math.cos(th), py + side * BEAM * math.sin(th)
    return ex, ey + HANG


def balanza(P, t, cs):
    t0, t1 = CUE["bal0"], CUE["it_beat"]
    a = window(t, t0, t1 + 0.35, 0.5, 0.45)
    if a <= 0: return
    px, py = BAL_PIV
    th = bal_angle(t)
    grow = out_back(prog(t, t0, t0 + 0.6))
    with P.layer(a):
        with P.transform(0, 0, 0.9 + 0.1 * grow, cx=px, cy=py + 150):
            # poste y base
            P.line(px, py, px, py + 420, C.GRAY, 1, w=8)
            P.rect(px - 120, py + 410, px + 120, py + 432, C.GRAY, 1, radius=10)
            # viga
            ex1, ey1 = px - BEAM * math.cos(th), py - BEAM * math.sin(th)
            ex2, ey2 = px + BEAM * math.cos(th), py + BEAM * math.sin(th)
            P.line(ex1, ey1, ex2, ey2, C.WHITE, 1, w=10)
            P.glow_circle(px, py, 16, C.WHITE, 1, spread=1.6)
            heavy = prog(t, CUE["pesan"], CUE["pesan"] + 0.4)
            for side, col, lab in ((-1, C.CYAN, "ESCÁNER"), (1, C.VIOLET, "VECINOS")):
                ex, ey = (ex1, ey1) if side < 0 else (ex2, ey2)
                bx, by = ex, ey + HANG
                P.line(ex, ey, bx - 95, by, C.GRAY, 0.8, w=3)
                P.line(ex, ey, bx + 95, by, C.GRAY, 0.8, w=3)
                glow = heavy if side > 0 else 0
                if glow > 0:
                    P.rect(bx - 130, by - 10, bx + 130, by + 40, col, 0.35 * glow, radius=20, blur=22)
                P.rect(bx - 135, by, bx + 135, by + 20, col, 1, radius=10)
                P.text(lab, bx, by + 74, 38, col, 1, face=C.FONT_BOLD, tracking=2)
            # perillas α y β
            ak = prog(t, CUE["perillas"], CUE["perillas"] + 0.5)
            if ak > 0:
                for side, col, sym, cap in ((-1, C.CYAN, "α", "confianza en el escáner"),
                                            (1, C.VIOLET, "β", "confianza en los vecinos")):
                    kx, ky = px + side * BEAM, py + 395
                    s_ = out_back(prog(t, CUE["perillas"] + (0 if side < 0 else 0.25),
                                       CUE["perillas"] + (0.45 if side < 0 else 0.7)))
                    if s_ <= 0: continue
                    with P.transform(0, 0, s_, cx=kx, cy=ky):
                        P.circle(kx, ky, 58, C.BG2, ak)
                        P.circle(kx, ky, 58, col, ak, stroke=5)
                        rot = -2.2 + 1.6 * smooth(prog(t, CUE["perillas"] + 0.5, CUE["perillas"] + 1.4)) \
                            + 0.15 * math.sin(t * 2.5)
                        P.line(kx, ky, kx + 40 * math.cos(rot), ky + 40 * math.sin(rot), col, ak, w=7)
                        P.text(sym, kx + side * 105, ky + 20, 64, col, ak, face=C.FONT_BOLD)
                    P.text(cap, kx, ky + 108, 30, C.WHITE, ak * s_, face=C.FONT_MED)
    # objetos que vuelan desde la imagen
    z = cs[2]
    sx, sy_ = to_screen(cam(CUE["bal0"]), PX + .5, PY + .5)
    size0 = cam(CUE["bal0"])[2]
    # el punto juzgado sube sobre el pivote
    uj = out_cubic(prog(t, t0 + 0.1, t0 + 0.9))
    jx, jy = lerp(sx, px, uj), lerp(sy_, py - 230, uj)
    js = lerp(size0, 120, uj)
    flip = prog(t, CUE["corrige"], CUE["corrige"] + 0.3)
    col = lerp_c(C.INK, C.PAPER, flip)
    with P.layer(a):
        P.rect(jx - js / 2, jy - js / 2, jx + js / 2, jy + js / 2, col, 1, radius=8)
        P.rect(jx - js / 2, jy - js / 2, jx + js / 2, jy + js / 2, C.PINK if flip < .5 else C.CYAN, 1, stroke=5, radius=8)
        if flip > 0:
            ring = out_cubic(clamp((t - CUE["corrige"]) / 0.8))
            P.rect(jx - js / 2 - 90 * ring, jy - js / 2 - 90 * ring, jx + js / 2 + 90 * ring, jy + js / 2 + 90 * ring,
                   C.CYAN, 1 - ring, stroke=6, radius=8 + 40 * ring)
            P.pill("papel ✓", jx + 190, jy, 36, C.CYAN, out_back(prog(t, CUE["corrige"] + 0.2, CUE["corrige"] + 0.5)))
        else:
            P.text("?", jx, jy + 30, 80, C.WHITE, prog(t, t0 + 0.6, t0 + 1.0) * (1 - flip), face=C.FONT_BLACK)
        # voz del escáner: copia del punto (negro) al plato izquierdo
        un = out_cubic(prog(t, CUE["negro"], CUE["negro"] + 0.45))
        if un > 0:
            lx, ly = pan_pos(t, -1)
            x_, y_ = lerp(jx, lx, un), lerp(jy, ly - 40, un) - 120 * math.sin(math.pi * un)
            P.rect(x_ - 36, y_ - 36, x_ + 36, y_ + 36, C.INK, 1, radius=6)
            P.rect(x_ - 36, y_ - 36, x_ + 36, y_ + 36, C.CYAN, 1, stroke=4, radius=6)
            P.text("0,87", x_, y_ - 54, 30, C.CYAN, un, face=C.FONT_BOLD)
        # voces de los vecinos: cuatro cuadros blancos al plato derecho
        nbs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        slots = [(-58, -40), (0, -40), (58, -40), (0, -100)]
        for k, (dx, dy) in enumerate(nbs):
            tk = CUE["blanco"] + 0.22 * k
            uk = out_cubic(prog(t, tk, tk + 0.45))
            sx0, sy0 = to_screen(cam(CUE["bal0"]), PX + dx + .5, PY + dy + .5)
            if uk <= 0:
                # aún en la imagen: se insinúan con un borde
                ah = prog(t, t0 + 0.2, t0 + 0.6)
                P.rect(sx0 - size0 / 2, sy0 - size0 / 2, sx0 + size0 / 2, sy0 + size0 / 2, C.VIOLET, ah, stroke=4)
                continue
            rx, ry = pan_pos(t, 1)
            tx, ty = rx + slots[k][0], ry + slots[k][1]
            x_, y_ = lerp(sx0, tx, uk), lerp(sy0, ty, uk) - 140 * math.sin(math.pi * uk)
            s_ = lerp(size0, 52, uk)
            P.rect(x_ - s_ / 2, y_ - s_ / 2, x_ + s_ / 2, y_ + s_ / 2, C.PAPER, 1, radius=6)
            P.rect(x_ - s_ / 2, y_ - s_ / 2, x_ + s_ / 2, y_ + s_ / 2, C.VIOLET, 1, stroke=4, radius=6)
        nb_in = sum(1 for k in range(4) if t > CUE["blanco"] + 0.22 * k + 0.45)
        if nb_in:
            rx, ry = pan_pos(t, 1)
            P.text(f"{nb_in} × 1,2 = {fmt(1.2 * nb_in, 1)}", rx, ry - 215, 34, C.VIOLET, 1, face=C.FONT_BOLD)
        ak = prog(t, CUE["perillas"] + 1.0, CUE["perillas"] + 1.5)
        P.text("valores de la clase:  α ≈ 0,87   ·   β = 1,2", 540, 1265, 30, C.GRAY, ak, face=C.FONT_MED)


# ---------- HUD de pasadas
def hud_iter(P, t):
    a = window(t, CUE["iter0"] - 0.2, CUE["res0"] + 0.3, 0.4, 0.4)
    if a <= 0: return
    lv = D["levels"]
    k = 0
    for j in range(1, len(lv)):
        if t >= CUE["iter0"] + CUE["iter_dt"] * (j - 1) + 0.45: k = j
    it = lv[k]
    err = D["err_iter"][it] * 100
    P.pill(f"pasada {it}", 330, 400, 40, C.WHITE, a, fill_a=0.08)
    P.pill(f"puntos mal: {fmt(err, 1)}%", 740, 400, 40, C.CYAN if it else C.PINK, a)
    P.text("misma regla, aplicada a todos los puntos a la vez", 540, 1265, 30, C.GRAY,
           a * prog(t, CUE["iter0"] + 0.5, CUE["iter0"] + 1.0), face=C.FONT_MED)


# ---------- resultados
def results(P, t, cs):
    t0, t1 = CUE["res0"], CUE["end0"]
    a = window(t, t0 + 0.3, t1 + 0.2, 0.5, 0.5)
    if a <= 0: return
    # deslizador antes / después sobre el documento
    h, w = D["orig"].shape
    us = prog(t, t0 + 0.4, t0 + 1.4, in_out_cubic)
    xs_img = lerp(w, w * 0.5, us) + w * 0.18 * math.sin((t - t0) * 1.3) * prog(t, t0 + 1.4, t0 + 2.4)
    x_s, y_top = to_screen(cs, xs_img, -8)
    _, y_bot = to_screen(cs, xs_img, h + 8)
    xl, _ = to_screen(cs, -8, 0)
    with P.layer(a * us):
        # mitad izquierda: escaneo con ruido (se dibuja encima de la restaurada)
        P.c.save(); P.c.clipRect(skia.Rect(0, y_top, x_s, y_bot))
        cx, cy, z, sy = cs
        P.c.translate(C.W / 2, sy); P.c.scale(z, z); P.c.translate(-cx, -cy)
        P.rect(-7, -7, w + 7, h + 7, C.PAPER, 1, radius=6)
        draw_image(P, "obs", z)
        P.c.restore()
        P.line(x_s, y_top - 30, x_s, y_bot + 30, C.CYAN, 1, w=6, glow=True)
        P.glow_circle(x_s, (y_top + y_bot) / 2, 18, C.CYAN, 1)
        P.text("antes", xl + 20, y_bot + 52, 32, C.PINK, 1, face=C.FONT_BOLD, align="left")
        xr, _ = to_screen(cs, w + 8, 0)
        P.text("después", xr - 20, y_bot + 52, 32, C.CYAN, 1, face=C.FONT_BOLD, align="right")
    # tarjeta 1: resultado de la clase
    t42, t94 = CUE["r42"], CUE["r94"]
    a1 = prog(t, t42 - 0.4, t42) * a
    if a1 > 0:
        y = 985
        P.rect(90, y - 70, 990, y + 150, C.BG2, 0.9 * a1, radius=28)
        P.text("LECTOR AUTOMÁTICO · RESULTADO DE LA CLASE", 130, y - 22, 28, C.GRAY, a1, face=C.FONT_BOLD, align="left")
        u = prog(t, t94 - 0.15, t94 + 0.7, out_quint)
        v = lerp(42, 94, u)
        col = lerp_c(C.PINK, C.CYAN, u)
        P.text(f"{fmt(v)}%", 950, y + 62, 96, col, a1, face=C.FONT_BLACK, align="right", glow=0.5 * u)
        P.text("del texto entendido", 130, y + 50, 32, C.WHITE, a1, face=C.FONT_MED, align="left")
        P.rect(130, y + 82, 950, y + 96, C.DIM, a1, radius=7)
        P.rect(130, y + 82, 130 + 820 * v / 100, y + 96, col, a1, radius=7)
        P.text("puntos equivocados: 15% → 2,5%", 130, y + 132, 26, C.GRAY, a1 * prog(t, t94 + 0.4, t94 + 0.9),
               face=C.FONT_MED, align="left")
    # tarjeta 2: recreación propia
    tr, t91 = CUE["recre"], CUE["r91"]
    a2 = prog(t, tr - 0.2, tr + 0.3) * a
    if a2 > 0:
        y = 1215
        s = out_back(prog(t, tr - 0.2, tr + 0.3))
        with P.transform(0, 0, 0.9 + 0.1 * s, cx=540, cy=y):
            P.rect(90, y - 62, 990, y + 62, C.BG2, 0.9 * a2, radius=28)
            P.rect(90, y - 62, 990, y + 62, C.CYAN, 0.5 * a2, stroke=2, radius=28)
            P.text("MI RECREACIÓN EN PYTHON", 130, y - 14, 28, C.CYAN, a2, face=C.FONT_BOLD, align="left")
            P.text("otra tipografía y otro ruido", 130, y + 30, 26, C.GRAY, a2, face=C.FONT_MED, align="left")
            u = prog(t, t91 - 0.2, t91 + 0.6, out_quint)
            o0, o1 = D["res"]["ocr_acc_observed"] * 100, D["res"]["ocr_acc_restored"] * 100
            v = lerp(o0, o1, u)
            txt = f"{fmt(o0)}% → {fmt(v)}%" if u > 0 else f"{fmt(o0)}%"
            P.text(txt, 950, y + 22, 64, C.CYAN if u > 0 else C.PINK, a2, face=C.FONT_BLACK, align="right")


# ---------- cierre: aplicaciones y adelanto
def tile_card(P, cx, cy, a):
    P.rect(cx - 150, cy - 150, cx + 150, cy + 150, (0, 0, 0), 0.5 * a, radius=26, blur=22)
    P.rect(cx - 150, cy - 150, cx + 150, cy + 150, C.BG2, a, radius=26)
    P.rect(cx - 150, cy - 150, cx + 150, cy + 150, C.WHITE, 0.15 * a, stroke=2, radius=26)


def label_map(P, cx, cy, noisy, clean, u, cols, a, size=260):
    n = noisy.shape[0]
    s = size / n
    x0, y0 = cx - size / 2, cy - size / 2
    wave = u * (n * 1.5)
    for r in range(n):
        for c in range(n):
            lab = clean[r, c] if (r + c) * 0.75 < wave else noisy[r, c]
            P.rect(x0 + c * s, y0 + r * s, x0 + (c + 1) * s + 0.6, y0 + (r + 1) * s + 0.6, cols[lab], a)


def closing(P, t, cs):
    t0 = CUE["end0"]
    tf = CUE["flechas"]
    a_tiles = prog(t, t0 + 0.5, t0 + 1.0) * (1 - prog(t, tf - 0.3, tf + 0.2))
    tiles = [(540, 720, CUE["tumores"], "Resonancias", D["mri"], [(0.16, 0.19, 0.27), (0.62, 0.66, 0.74), C.PINK]),
             (860, 720, CUE["bosques"], "Satélites", D["sat"], [C.GREEN, (0.85, 0.75, 0.3), (0.2, 0.45, 0.9), C.GRAY])]
    if a_tiles > 0:
        P.text("Documentos", 220, 940, 32, C.WHITE, a_tiles, face=C.FONT_SEMI)
        for (cx, cy, ts, lab, (noisy, clean), cols) in tiles:
            ak = prog(t, ts - 0.3, ts + 0.2) * a_tiles
            if ak <= 0: continue
            s = out_back(prog(t, ts - 0.3, ts + 0.3))
            with P.transform(0, 0, 0.8 + 0.2 * s, cx=cx, cy=cy):
                tile_card(P, cx, cy, ak)
                label_map(P, cx, cy, noisy, clean, prog(t, ts + 0.3, ts + 1.6, in_out_cubic), cols, ak)
            P.text(lab, cx, 940, 32, C.WHITE, ak, face=C.FONT_SEMI)
        P.text("la misma idea: escuchar a los vecinos", 540, 1050, 30, C.GRAY,
               a_tiles * prog(t, CUE["bosques"] + 0.5, CUE["bosques"] + 1.0), face=C.FONT_MED)
    # adelanto del próximo episodio
    ad = prog(t, tf - 0.2, tf + 0.4)
    if ad > 0:
        pos = {"A": (380, 600), "B": (700, 600), "C": (700, 920), "D": (380, 920)}
        edges = [("A", "B"), ("A", "D"), ("C", "B"), ("C", "D")]
        for k, (u_, v_) in enumerate(edges):
            fr = prog(t, tf + 0.1 + 0.15 * k, tf + 0.5 + 0.15 * k)
            P.arrow(*pos[u_], *pos[v_], C.WHITE, ad, w=6, head=26, frac=fr, gap=62)
        for nm, (x, y) in pos.items():
            P.node(x, y, 56, a=ad, label=nm, label_size=48, fill=C.BG2)
        aq = prog(t, tf + 0.5, tf + 0.9)
        P.text("?", 540, 815, 170, C.PINK, out_back(aq) * ad, face=C.FONT_BLACK, glow=0.6)
        P.pill(EP["next"].upper(), 540, 1130, 38, C.CYAN, prog(t, CUE["proximo"], CUE["proximo"] + 0.4))


def closing_world_alpha(t):
    return 1 - prog(t, CUE["flechas"] - 0.3, CUE["flechas"] + 0.2)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, D, EP, CHUNKS, KEYS, CUE
    TL, D, EP = tl, data, episode
    hist = D["hist"]
    D["levels"] = [0, 1, 2, 3, 5, 8, 30]
    D["rgba"] = {"obs": doc_rgba(D["obs"]), "lab": doc_rgba(D["lab"]), "orig": doc_rgba(D["orig"])}
    for k in D["levels"]:
        D["rgba"][f"h{k}"] = doc_rgba(hist[k])
    D["mri"], D["sat"] = mini_maps()

    c = {}
    c["ocr"] = T("hook", "Una"); c["ocr1"] = T("hook", "tampoco", end=True)
    c["wipe0"] = T("hook", "simple"); c["wipe1"] = T("hook", "así", end=True) + 0.15
    c["rewind1"] = T("problema") + 0.15; c["rewind0"] = c["rewind1"] - 0.5
    c["scan"] = T("problema", "escanearlo")
    c["rev"] = T("problema", "revés")
    c["ink2pap"] = T("problema", "tinta"); c["pap2ink"] = T("problema", "papel", 1)
    c["one"] = T("curiosidad", "un"); c["bien"] = T("curiosidad", "bien"); c["mal"] = T("curiosidad", "mal")
    c["imposible"] = T("curiosidad", "imposible")
    c["around"] = T("intuicion", "alrededor"); c["mancha"] = T("intuicion", "mancha")
    c["trazos"] = T("intuicion", "trazos"); c["analog"] = T("intuicion", "Como")
    c["lado"] = T("intuicion", "lado")
    c["net0"] = T("descubrimiento", "vecinos"); c["red"] = T("descubrimiento", "red")
    c["arrows"] = T("descubrimiento", "flechas"); c["nadie"] = T("descubrimiento", "nadie")
    c["markov"] = T("descubrimiento", "Markov")
    c["bal0"] = T("balanza"); c["negro"] = T("balanza", "negro"); c["blanco"] = T("balanza", "blanco")
    c["pesan"] = T("balanza", "pesan"); c["corrige"] = T("balanza", "corrige")
    c["perillas"] = T("balanza", "perillas")
    c["it_beat"] = T("iterar"); c["iter0"] = T("iterar", "todos"); c["iter_dt"] = 0.7
    c["res0"] = T("resultado"); c["r42"] = T("resultado", "42%"); c["r94"] = T("resultado", "94")
    c["recre"] = T("resultado", "recreación"); c["r91"] = T("resultado", "91%")
    c["end0"] = T("cierre"); c["tumores"] = T("cierre", "tumores"); c["bosques"] = T("cierre", "bosques")
    c["flechas"] = T("cierre", "flechas"); c["proximo"] = T("cierre", "próximo")
    CUE = c

    h, w = D["orig"].shape
    Z0 = 960 / w
    FULL = state(w / 2, h / 2, Z0)
    HOOK0 = state(w / 2, h / 2, Z0 * 1.18, 920)
    PROB = state(PX + 4.5, PY + .5, 24)
    ONE = state(PX + .5, PY + .5, 150)
    AROUND = state(PX + .5, PY + .5, 66)
    STRK = state(PX + 3.5, PY + .5, 58)
    NET = state(PX + 1.5, PY + .5, 46)
    RES = state(w / 2, h / 2, Z0 * 0.92, 590)
    zt = Z0 * 0.27
    TILE = state(w / 2 + 320 / zt, h / 2, zt, 720)
    KEYS = [
        (0.0, HOOK0), (2.6, FULL),
        (c["scan"] - 0.15, FULL), (c["rev"] + 0.9, PROB),
        (c["one"] - 0.5, PROB), (c["one"] + 1.3, ONE),
        (c["around"], ONE), (c["around"] + 1.3, AROUND),
        (c["trazos"] - 0.5, AROUND), (c["trazos"] + 0.6, STRK),
        (c["net0"] - 0.6, STRK), (c["net0"] + 0.8, NET),
        (c["iter0"], NET), (c["iter0"] + 3.2, FULL),
        (c["res0"], FULL), (c["res0"] + 1.0, RES),
        (c["end0"], RES), (c["end0"] + 1.1, TILE),
        (tl.duration + 1, TILE),
    ]
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def mini_maps():
    """Mapas de etiquetas con ruido y su versión suavizada (votación de vecinos)."""
    rng = np.random.default_rng(5)
    n = 26
    yy, xx = np.mgrid[0:n, 0:n]
    head = ((xx - 12.5) ** 2 + (yy - 12.5) ** 2) < 11.5 ** 2
    tumor = ((xx - 15) ** 2 / 16 + (yy - 10) ** 2 / 10) < 1
    mri = np.where(tumor, 2, np.where(head, 1, 0))
    from scipy.ndimage import gaussian_filter
    f = np.stack([gaussian_filter(rng.standard_normal((n, n)), 3) for _ in range(4)])
    sat = f.argmax(0)

    def noisy_clean(lab, k, p=0.2):
        nz = lab.copy()
        m = rng.random(lab.shape) < p
        nz[m] = rng.integers(0, k, m.sum())
        cur = nz.copy()
        for _ in range(6):       # cada celda adopta la etiqueta mayoritaria entre ella y sus 4 vecinos
            votes = np.zeros((k,) + lab.shape)
            for c in range(k):
                e = (cur == c).astype(float)
                P_ = np.pad(e, 1)
                votes[c] = 0.9 * (nz == c) + P_[:-2, 1:-1] + P_[2:, 1:-1] + P_[1:-1, :-2] + P_[1:-1, 2:]
            cur = votes.argmax(0)
        return nz, cur
    return noisy_clean(mri, 3), noisy_clean(sat, 4)


def draw_frame(P, t):
    P.background(t, accent=0.4 * prog(t, CUE["res0"], CUE["res0"] + 1))
    cs = cam(t)
    # profundidad de campo: la imagen se desenfoca cuando la idea sale de ella
    blur = 0.0
    blur = max(blur, 16 * window(t, CUE["analog"] - 0.1, CUE["net0"], 0.5, 0.5))
    blur = max(blur, 16 * window(t, CUE["bal0"], CUE["it_beat"] + 0.4, 0.6, 0.6))
    blur = max(blur, 16 * prog(t, CUE["flechas"] - 0.3, CUE["flechas"] + 0.3))
    dim = 0.5 * blur / 16
    wa = closing_world_alpha(t) * (1 - 0.0)
    draw_blurred(P, lambda q: draw_world(q, t, cs), blur, alpha=wa)
    if dim > 0:
        P.rect(0, 0, C.W, C.H, C.BG, dim)
    spotlight(P, t, cs)
    question(P, t, cs)
    labels_world(P, t, cs)
    analogy(P, t)
    balanza(P, t, cs)
    hud_iter(P, t)
    results(P, t, cs)
    closing(P, t, cs)
    # titular del hook (visible desde el primer cuadro)
    ah = 1 - prog(t, CUE["wipe0"] - 0.4, CUE["wipe0"])
    if ah > 0:
        s_ = 0.92 + 0.08 * out_back(prog(t, 0, 0.45))
        with P.transform(0, 0, s_, cx=540, cy=470):
            P.text("¿PUEDES", 540, 430, 112, C.WHITE, ah, face=C.FONT_BLACK)
            P.text("LEER ESTO?", 540, 545, 112, C.CYAN, ah, face=C.FONT_BLACK, glow=0.6)
    # chips del hook (fallo / éxito del lector)
    _, yb = to_screen(cs, 0, D["orig"].shape[0] + 8)
    a = window(t, CUE["ocr"], CUE["wipe0"] + 0.4, 0.3, 0.3)
    if a > 0:
        # barrido rosado del lector que falla
        _, yt = to_screen(cs, 0, -8)
        u = prog(t, CUE["ocr"], CUE["ocr1"], in_out_cubic)
        if u < 1:
            yy = lerp(yt, yb, u)
            P.line(40, yy, 1040, yy, C.PINK, a, w=5, glow=True)
        P.pill("LECTOR AUTOMÁTICO:  SIN TEXTO ÚTIL", 540, yb + 90, 34, C.PINK, a * out_back(prog(t, CUE["ocr1"] - 0.2, CUE["ocr1"] + 0.2)))
    a = window(t, CUE["wipe1"] - 0.2, CUE["rewind0"] + 0.1, 0.3, 0.25)
    P.pill("LEGIBLE OTRA VEZ", 540, yb + 90, 34, C.CYAN, a * out_back(prog(t, CUE["wipe1"] - 0.2, CUE["wipe1"] + 0.2)))
    # acabado cinematográfico y capa de interfaz
    vignette(P, 0.5)
    vband(P, 0, 330, 0.85, 0.0)
    vband(P, 1240, C.H, 0.0, 0.9)
    P.circle(C.SAFE_LEFT + 10, 262, 8, C.CYAN, 1)
    P.text(EP["tag"], C.SAFE_LEFT + 34, 273, 28, C.WHITE, 0.85, face=C.FONT_BOLD, align="left", tracking=2)
    SUB.draw(P, CHUNKS, t)
    P.rect(0, C.H - 8, C.W * t / TL.duration, C.H, C.CYAN, 0.8)


def draw_cover(P, t=3.0):
    """Portada 9:16: documento mitad ruido / mitad restaurado + titular."""
    h, w = D["orig"].shape
    P.background(t, accent=0.6)
    P.text("¿PUEDES", 540, 450, 120, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("LEER ESTO?", 540, 580, 120, C.CYAN, 1, face=C.FONT_BLACK, glow=0.7)
    cs = state(w / 2, h / 2, 960 / w, 900)
    P.c.save(); P.c.translate(540, 900); P.c.scale(cs[2], cs[2]); P.c.translate(-w / 2, -h / 2)
    P.rect(-4, 2, w + 4, h + 14, (0, 0, 0), 0.6, radius=6, blur=12)
    P.rect(-7, -7, w + 7, h + 7, C.PAPER, 1, radius=6)
    draw_image(P, "lab", cs[2])
    P.c.clipRect(skia.Rect(-8, -8, w / 2, h + 8))
    P.rect(-7, -7, w / 2, h + 7, C.PAPER, 1)
    draw_image(P, "obs", cs[2])
    P.c.restore()
    P.line(540, 640, 540, 1160, C.CYAN, 1, w=6, glow=True)
    P.pill("15% DE RUIDO", 300, 1230, 34, C.PINK)
    P.pill("RESTAURADO", 780, 1230, 34, C.CYAN)
    P.text("Cómo los píxeles vecinos rescatan un texto", 540, 1340, 40, C.WHITE, 1, face=C.FONT_BOLD)
    P.text(C.BRAND, 540, 1420, 34, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "thump", 1.0), (0.0, "swell", 0.5)]
    cues += [(c["ocr"] + 0.25 * k, "tick", 0.5) for k in range(int((c["ocr1"] - c["ocr"]) / 0.25))]
    cues += [(c["ocr1"], "pop_low", 0.7), (c["wipe0"] - 0.3, "riser", 0.6), (c["wipe1"] - 0.1, "ding", 0.8),
             (c["rewind0"], "rewind", 0.9), (c["scan"], "whoosh", 0.7),
             (c["ink2pap"], "pop", 0.5), (c["pap2ink"], "pop_low", 0.5),
             (c["one"] - 0.1, "whoosh", 0.6), (c["imposible"], "pop_low", 0.5),
             (c["around"], "whoosh_down", 0.5), (c["mancha"], "pop", 0.5), (c["trazos"], "pop", 0.5),
             (c["analog"], "whoosh", 0.5), (c["lado"] + 0.4, "ding", 0.5),
             (c["net0"], "pop", 0.5), (c["red"], "riser", 0.4), (c["nadie"], "pop_low", 0.5),
             (c["markov"], "swell", 0.8),
             (c["bal0"], "whoosh", 0.6), (c["negro"] + 0.4, "thump", 0.5),
             (c["corrige"], "ding", 0.8), (c["perillas"], "pop", 0.5), (c["perillas"] + 0.25, "pop", 0.5),
             (c["iter0"], "whoosh_down", 0.6),
             (c["res0"], "whoosh", 0.6), (c["r94"], "ding", 0.8), (c["r91"], "ding", 0.6),
             (c["end0"] + 0.2, "whoosh_down", 0.6), (c["tumores"], "pop", 0.5), (c["bosques"], "pop", 0.5),
             (c["flechas"] - 0.3, "riser", 0.6)]
    cues += [(c["blanco"] + 0.22 * k + 0.4, "pop", 0.45) for k in range(4)]
    cues += [(c["iter0"] + c["iter_dt"] * k, "tick", 0.7) for k in range(len(D["levels"]) - 1)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["net0"], "pulse": (c["res0"], c["end0"] + 2),
            "quiet": [(c["one"] - 0.5, c["around"])]}
