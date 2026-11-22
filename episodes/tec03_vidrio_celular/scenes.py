"""Escenas — «¿Por qué no se rompe la pantalla?» (stheq.ia, motion graphics).

Hilo visual: un martillo golpea la pantalla de un celular y no pasa nada; una ventana, en cambio, se hace
trizas → corte del vidrio con grietas diminutas en su superficie: al doblarse, la cara estirada abre una
grieta → el mismo corte se llena de átomos de sodio y entra en un baño de sal fundida (≈ 400 °C): los
átomos de sodio de la superficie salen y entran átomos de potasio, más grandes → triángulo de pool cuyas
bolas se cambian por pelotas de tenis: no caben y quedan apretadas → la superficie del vidrio queda
comprimida y la grieta no logra abrirse → una caída mala igual lo puede romper → el martillo vuelve a
golpear el celular, que aguanta (empalme con el inicio).
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

PH_X, PH_Y = 540, 890          # celular
PIV = (990, 1255)              # pivote del martillo
HAM_LEN = 560
X0, X1, YT, YB = 140, 940, 780, 960   # corte del vidrio
NOTCH = [235, 370, 540, 705, 845]
COLS = 14; ROWS = 5


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
def phone(P, x, y, s=1.0, a=1.0, glow=0.0, crack=0.0, rot=0.0, crack_at=(0.0, 0.0), squeeze=0.0):
    """Celular de frente. crack: 0..1 (líneas rojas desde crack_at, relativo al centro, en unidades sin escala)."""
    if a <= 0: return
    with P.layer(a), P.transform(0, 0, s, rot, cx=x, cy=y):
        if glow > 0:
            P.rect(x - 170, y - 310, x + 170, y + 310, L.FG, 0.22 * glow, radius=50, blur=40)
        P.rect(x - 150, y - 290, x + 150, y + 290, L.BG, 1, radius=40)
        P.rect(x - 150, y - 290, x + 150, y + 290, L.FG, 1, stroke=8, radius=40)
        P.rect(x - 128, y - 262, x + 128, y + 262, L.CARD, 1, radius=26)
        P.rect(x - 40, y - 250, x + 40, y - 236, L.DIM, 1, radius=6)
        # reflejo del vidrio
        P.line(x - 90, y - 120, x + 20, y - 230, L.FG, 0.10, w=18)
        P.line(x - 60, y - 40, x + 70, y - 170, L.FG, 0.06, w=10)
        if crack > 0:
            cx, cy = x + crack_at[0], y + crack_at[1]
            rng = np.random.default_rng(7)
            for k in range(9):
                ang = -math.pi * 0.95 + k * 0.23 + rng.uniform(-0.08, 0.08)
                ln = rng.uniform(150, 330) * crack
                px, py = cx, cy
                for j in range(4):
                    seg = ln / 4
                    a2 = ang + rng.uniform(-0.35, 0.35)
                    nx, ny = px + math.cos(a2) * seg, py + math.sin(a2) * seg
                    nx = clamp(nx, x - 126, x + 126); ny = clamp(ny, y - 260, y + 260)
                    P.line(px, py, nx, ny, L.RED, 1, w=4)
                    px, py = nx, ny
        if squeeze > 0:
            for yy in (y - 160, y, y + 160):
                P.arrow(x - 280, yy, x - 172, yy, L.RED, squeeze, w=8, head=26)
                P.arrow(x + 280, yy, x + 172, yy, L.RED, squeeze, w=8, head=26)


def hammer(P, ang, a=1.0, pivot=PIV):
    """Martillo que gira (grados, horario) alrededor de la punta del mango."""
    if a <= 0: return
    px, py = pivot
    with P.layer(a), P.transform(0, 0, 1.0, ang, cx=px, cy=py):
        P.line(px, py, px, py - HAM_LEN + 30, L.BROWN, 1, w=26)
        P.line(px - 6, py - 40, px - 6, py - HAM_LEN + 60, L.hx("#8A6446"), 0.6, w=6)
        hy = py - HAM_LEN
        P.rect(px - 95, hy - 48, px + 95, hy + 48, L.GRAY, 1, radius=12)
        P.rect(px - 95, hy - 48, px + 95, hy + 48, L.FG, 0.7, stroke=4, radius=12)
        P.rect(px - 95, hy - 48, px - 70, hy + 48, L.FG, 0.85, radius=8)


def hammer_head(ang, pivot=PIV):
    th = math.radians(ang)
    return pivot[0] + math.sin(th) * HAM_LEN, pivot[1] - math.cos(th) * HAM_LEN


def swing(t, t_hit, rest=-12.0, hit=-50.0):
    """Ángulo del martillo: se levanta, baja rápido hasta t_hit, rebota y vuelve al reposo."""
    if t <= t_hit:
        a = lerp(rest, rest + 14, prog(t, t_hit - 1.3, t_hit - 0.35, in_out_cubic))
        return lerp(a, hit, prog(t, t_hit - 0.35, t_hit, in_cubic))
    if t <= t_hit + 0.25:
        return lerp(hit, hit + 8, math.sin(math.pi * 0.5 * (t - t_hit) / 0.25))
    return lerp(hit + 8, rest, prog(t, t_hit + 0.25, t_hit + 1.4, in_out_cubic))


def window_pane(P, x, y, a=1.0, shatter=0.0, t=0.0, t_sh=0.0):
    if a <= 0: return
    w, h = 150, 220
    with P.layer(a):
        P.rect(x - w, y - h, x + w, y + h, L.FG, 0.08 * (1 - 0.7 * shatter))
        if shatter <= 0:
            P.line(x - w + 40, y - 60, x - 20, y - h + 30, L.FG, 0.12, w=14)
        else:
            cx, cy = x + 10, y - 30
            rng = np.random.default_rng(3)
            for k in range(12):
                ang = k * 2 * math.pi / 12 + rng.uniform(-0.15, 0.15)
                ln = rng.uniform(120, 260) * clamp(shatter * 1.6)
                ex = clamp(cx + math.cos(ang) * ln, x - w, x + w); ey = clamp(cy + math.sin(ang) * ln, y - h, y + h)
                P.line(cx, cy, ex, ey, L.RED, 1, w=4)
            for r in (50, 105):
                P.circle(cx, cy, r * clamp(shatter * 1.6), L.RED, 0.8, stroke=3)
            # trozos que caen
            dt = max(0.0, t - t_sh - 0.15)
            for k in range(9):
                sx = x - w + 30 + k * 33 + rng.uniform(-10, 10); sy = y + rng.uniform(-80, 120)
                fy = sy + 380 * dt * dt + 60 * dt
                if fy > y + h + 120: continue
                tri = skia.Path(); sz = rng.uniform(14, 26); rr = dt * (2 + k)
                for j in range(3):
                    aa = rr + j * 2.1
                    (tri.moveTo if j == 0 else tri.lineTo)(sx + math.cos(aa) * sz, fy + math.sin(aa) * sz)
                tri.close()
                P.c.drawPath(tri, paint(L.FG, 0.55 * clamp(dt * 4) * (1 - clamp((fy - y - h) / 120))))
        P.rect(x - w, y - h, x + w, y + h, L.FG, 1, stroke=10, radius=6)
        P.line(x, y - h, x, y + h, L.FG, 1, w=8)
        P.line(x - w, y, x + w, y, L.FG, 1, w=8)


def flash(P, x, y, u, r=120):
    if 0 < u < 1:
        P.circle(x, y, r * (0.4 + 1.2 * u), L.FG, 0.8 * (1 - u), stroke=6)
        P.circle(x, y, r * 0.6, L.FG, 0.35 * (1 - u), blur=30)


# ----------------------------------------------------------------- corte del vidrio
def bend_dy(x, b):
    u = (x - 540) / 400.0
    return -b * 70 * (1 - u * u)


def slab(P, a, oy=0.0, b=0.0, notches=0.0, hl=0.0, crack_open=0.0, crack_depth=0.0, hl_surface=0.0, fill=1.0):
    """Corte transversal del vidrio, con flexión b (arco hacia arriba: la cara de arriba se estira)."""
    if a <= 0: return
    with P.layer(a):
        n = 60
        top = [(lerp(X0, X1, k / n), YT + oy + bend_dy(lerp(X0, X1, k / n), b)) for k in range(n + 1)]
        bot = [(lerp(X0, X1, k / n), YB + oy + bend_dy(lerp(X0, X1, k / n), b)) for k in range(n + 1)]
        pth = skia.Path(); pth.moveTo(*top[0])
        for p in top[1:]: pth.lineTo(*p)
        for p in bot[::-1]: pth.lineTo(*p)
        pth.close()
        P.c.drawPath(pth, paint(L.FG, 0.10 * fill))
        P.c.drawPath(pth, paint(L.FG, 1, stroke=5))
        if hl_surface > 0:
            sp = skia.Path(); sp.moveTo(*top[0])
            for p in top[1:]: sp.lineTo(*p)
            P.c.drawPath(sp, paint(L.RED, 0.45 * hl_surface, stroke=18, blur=10))
            P.c.drawPath(sp, paint(L.RED, hl_surface, stroke=6))
        # grietas diminutas
        for k, nx in enumerate(NOTCH):
            na = clamp(notches * 5 - k)
            if na <= 0: continue
            ny = YT + oy + bend_dy(nx, b)
            hw, d = 8, 18
            if k == 2:
                hw += 26 * crack_open; d += 150 * crack_depth
            P.c.drawPath(_crack_path(nx, ny, hw, d, k), paint(L.RED if (k == 2 and (hl > 0 or crack_open > 0)) else L.FG, na))
            if k == 2 and hl > 0:
                P.circle(nx, ny + 6, 46, L.RED, hl, stroke=5)


def _crack_path(x, y, hw, d, seed):
    pth = skia.Path(); pth.moveTo(x - hw, y - 1)
    steps = max(2, int(d / 22))
    pts = []
    for j in range(1, steps + 1):
        u = j / steps
        zig = (6 if j % 2 else -6) * (d > 40)
        pts.append((x + zig, y + d * u))
    left = [(x - hw * (1 - j / steps) + px - x, py) for j, (px, py) in enumerate(pts, 1)]
    right = [(x + hw * (1 - j / steps) + px - x, py) for j, (px, py) in enumerate(pts, 1)]
    for p in left: pth.lineTo(*p)
    for p in right[::-1]: pth.lineTo(*p)
    pth.lineTo(x + hw, y - 1); pth.close()
    return pth


def lattice_pos(i, j, oy=0.0, b=0.0):
    x = lerp(X0 + 32, X1 - 32, i / (COLS - 1))
    y = YT + 18 + j * 36 + oy + bend_dy(x, b)
    return x, y


def lattice(P, t, a, oy=0.0, b=0.0, out_u=0.0, in_u=0.0, comp=0.0):
    """Átomos dentro del vidrio. out_u: sodio de la superficie saliendo; in_u: potasio entrando."""
    if a <= 0: return
    with P.layer(a):
        for j in range(ROWS):
            surf = j in (0, ROWS - 1)
            sgn = -1 if j == 0 else 1
            for i in range(COLS):
                x, y = lattice_pos(i, j, oy, b)
                if not surf:
                    P.circle(x, y, 9, L.GRAY, 1); continue
                st = i / COLS * 0.45
                uo = clamp((out_u - st) / 0.55)
                if uo < 1:
                    yo = y + sgn * 150 * in_out_cubic(uo)
                    P.circle(x + 10 * math.sin(i + uo * 3), yo, 9, L.GRAY, 1 - smooth(clamp((uo - 0.6) / 0.4)))
                ui = clamp((in_u - st) / 0.55)
                if ui > 0:
                    yi = y + sgn * 190 * (1 - in_out_cubic(ui))
                    r = 15 + 1.5 * comp
                    P.circle(x, yi, r, L.RED, smooth(clamp(ui * 2.5)))
                    if comp > 0:
                        P.circle(x, yi, r + 6, L.RED, 0.25 * comp, blur=8)


def comp_arrows(P, a, oy=0.0, b=0.0, push=0.0):
    if a <= 0: return
    for j in (0, ROWS - 1):
        _, yl = lattice_pos(0, j, oy, b); _, yr = lattice_pos(COLS - 1, j, oy, b)
        d = 18 * push
        P.arrow(20 + d, yl, 118 + d, yl, L.RED, a, w=8, head=26)
        P.arrow(1060 - d, yr, 962 - d, yr, L.RED, a, w=8, head=26)


def bath(P, t, a, hot=0.0):
    if a <= 0: return
    with P.layer(a):
        x0, x1, y0, y1 = 70, 1010, 600, 1150
        P.rect(x0, y0, x1, y1, L.RED, 0.10 + 0.05 * hot, radius=24)
        pth = skia.Path()
        for k in range(61):
            x = lerp(x0 + 10, x1 - 10, k / 60)
            y = y0 + 6 * math.sin(k * 0.6 - t * 3)
            (pth.moveTo if k == 0 else pth.lineTo)(x, y)
        P.c.drawPath(pth, paint(L.RED, 0.8, stroke=5))
        P.line(x0, y0 - 30, x0, y1, L.FG, 1, w=6); P.line(x1, y0 - 30, x1, y1, L.FG, 1, w=6)
        P.line(x0, y1, x1, y1, L.FG, 1, w=6)
        for k in range(10):
            u = (t * 0.35 + k * 0.137) % 1.0
            bx = x0 + 60 + (k * 97) % (x1 - x0 - 120)
            by = lerp(y1 - 20, y0 + 20, u)
            if YT - 40 < by < YB + 40 and X0 < bx < X1: continue
            P.circle(bx + 6 * math.sin(t * 2 + k), by, 6 + 3 * (k % 3), L.RED, 0.5 * (1 - u) * hot, stroke=3)


def rack(P, t, a, grow=0.0, squeeze=0.0):
    """Triángulo de pool: bolas que se cambian por pelotas de tenis."""
    if a <= 0: return
    cx, ay = 540, 520
    with P.layer(a):
        sc = 1 + 0.06 * squeeze * (1 + 0.15 * math.sin(t * 18) * (1 - squeeze))
        with P.transform(0, 0, sc, cx=cx, cy=ay + 150):
            pts = []
            for i in range(5):
                for j in range(i + 1):
                    pts.append((cx + (j - i / 2) * 50, ay + 50 + i * 44))
            r = 22 + 6 * grow
            for k, (x, y) in enumerate(pts):
                col = lerp_c(L.GRAY, L.FG, grow)
                P.circle(x, y, r, col, 1)
                P.circle(x, y, r, L.BG, 0.8, stroke=2.5)
                if grow < 0.5:
                    P.circle(x - 5, y - 6, 7, L.FG, 0.9 * (1 - grow * 2))
                else:
                    sa = clamp(grow * 2 - 1)
                    P.c.drawArc(skia.Rect(x - r * 1.3, y - r * 0.8, x + r * 0.2, y + r * 0.8), -60, 120, False, paint(L.DIM, sa, stroke=3))
                    P.c.drawArc(skia.Rect(x - r * 0.2, y - r * 0.8, x + r * 1.3, y + r * 0.8), 120, 120, False, paint(L.DIM, sa, stroke=3))
            tri = skia.Path()
            m = 34 + 4 * grow
            tri.moveTo(cx, ay + 50 - m * 1.25)
            tri.lineTo(cx + 2 * 50 + m * 1.1, ay + 50 + 4 * 44 + m * 0.65)
            tri.lineTo(cx - 2 * 50 - m * 1.1, ay + 50 + 4 * 44 + m * 0.65)
            tri.close()
            P.c.drawPath(tri, paint(L.BROWN, 1, stroke=12))
        if squeeze > 0:
            P.arrow(cx - 250, ay + 160, cx - 165, ay + 145, L.RED, squeeze, w=8, head=24)
            P.arrow(cx + 250, ay + 160, cx + 165, ay + 145, L.RED, squeeze, w=8, head=24)
            P.arrow(cx, ay + 350, cx, ay + 282, L.RED, squeeze, w=8, head=24)


# =============================================================== escenas
def hook_scene(P, t):
    c = CUE
    a = 1 - prog(t, c["g0"] - 0.4, c["g0"] + 0.2, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        mv = prog(t, c["ventana"] - 0.45, c["ventana"] + 0.25, in_out_cubic)
        back = prog(t, c["aguanta"] - 0.6, c["aguanta"] + 0.0, in_out_cubic)
        mv = mv * (1 - back)
        x = lerp(PH_X, 300, mv); s = lerp(1.0, 0.72, mv)
        hit = c["hit1"]
        sh = math.sin((t - hit) * 60) * 10 * math.exp(-(t - hit) * 7) if t > hit else 0.0
        glow = 0.9 * pulse(t, c["aguanta"] - 0.1, 1.3)
        phone(P, x + sh, PH_Y, s, 1, glow=glow)
        ha = 1 - prog(t, c["vidrio"] - 0.2, c["vidrio"] + 0.3)
        hammer(P, swing(t, hit), ha)
        hx, hy = hammer_head(-50)
        flash(P, hx - 40, hy, clamp((t - hit) / 0.45))
        wa = prog(t, c["ventana"] - 0.3, c["ventana"] + 0.3) * (1 - back)
        sht = prog(t, c["trizas"] - 0.05, c["trizas"] + 0.35)
        window_pane(P, 790, PH_Y, wa, sht, t, c["trizas"])
        flash(P, 800, PH_Y - 30, clamp((t - c["trizas"]) / 0.4) if t > c["trizas"] else 0, 90)
        lab = prog(t, c["vidrio"] - 0.1, c["vidrio"] + 0.3) * (1 - mv * 0) * (1 - back)
        P.text("VIDRIO", x, PH_Y + 290 * s + 80, 40, L.GRAY, lab * (1 - prog(t, c["ventana"] - 0.4, c["ventana"])), face=C.FONT_BOLD, tracking=3)
        q = prog(t, c["aguanta"] - 0.05, c["aguanta"] + 0.4, lambda u: u)
        if q > 0:
            P.text("?", PH_X, 1290 + 6 * math.sin(t * 3), 120, L.RED, out_back(q) * clamp(q * 2), face=C.FONT_BLACK)


def slab_state(t):
    """Estado continuo del corte de vidrio de la escena 2 a la 5."""
    c = CUE
    s = {}
    s["a"] = window(t, c["g0"] - 0.2, c["irromp"], 0.5, 0.45)
    s["notches"] = prog(t, c["grietas"] - 0.1, c["grietas"] + 0.6, lambda u: u)
    s["hl"] = window(t, c["diminutas"] - 0.1, c["dobla"] + 0.2, 0.3, 0.3)
    bend1 = prog(t, c["dobla"] - 0.1, c["dobla"] + 0.6, in_out_cubic) * (1 - prog(t, c["b0"] - 0.6, c["b0"] + 0.2, in_out_cubic))
    bend2 = prog(t, c["abra"] - 0.2, c["abra"] + 0.5, in_out_cubic) * (1 - prog(t, c["templado"] - 0.2, c["templado"] + 0.5, in_out_cubic))
    s["b"] = 1.0 * bend1 + 0.8 * bend2
    s["stretch"] = window(t, c["estira"] - 0.1, c["b0"] - 0.3, 0.3, 0.4)
    heal = 1 - prog(t, c["b0"] - 0.5, c["b0"] + 0.1, in_out_cubic)
    s["open"] = prog(t, c["abre"] - 0.1, c["abre"] + 0.4) * heal + 0.12 * math.sin(max(0, t - c["abra"]) * 9) ** 2 * bend2
    s["depth"] = prog(t, c["avanza"] - 0.1, c["avanza"] + 0.6) * heal
    s["surface"] = window(t, c["desde"] - 0.1, c["proteger"] + 0.9, 0.3, 0.4)
    s["lat"] = prog(t, c["b0"] - 0.2, c["proteger"] + 0.2)
    s["bath"] = window(t, c["sal"] - 0.3, c["a0"] + 0.1, 0.5, 0.5)
    s["hot"] = prog(t, c["c400"] - 0.2, c["c400"] + 0.4)
    s["out"] = prog(t, c["sodio"] - 0.1, c["sodio"] + 1.6, lambda u: u)
    s["in"] = prog(t, c["potasio"] - 0.2, c["potasio"] + 1.4, lambda u: u)
    down = prog(t, c["a0"] - 0.3, c["a0"] + 0.5, in_out_cubic) * (1 - prog(t, c["eso"] - 0.2, c["eso"] + 0.5, in_out_cubic))
    s["oy"] = 270 * down
    s["comp"] = prog(t, c["comprimida"] - 0.15, c["comprimida"] + 0.4)
    s["push"] = pulse(t, c["apreton"] - 0.1, 0.9) + 0.6 * pulse(t, c["comprimida"], 0.8)
    s["notch2"] = prog(t, c["c0"] - 0.3, c["c0"] + 0.3)
    return s


def slab_scene(P, t):
    c = CUE
    s = slab_state(t)
    if s["a"] <= 0: return
    with P.layer(s["a"]):
        bath(P, t, s["bath"], s["hot"])
        if s["bath"] > 0:
            ta = prog(t, c["c400"] - 0.1, c["c400"] + 0.35, lambda u: u) * s["bath"]
            if ta > 0:
                with P.transform(0, 0, 0.85 + 0.15 * out_back(ta), cx=540, cy=560):
                    P.text("≈ 400 °C", 540, 578, 76, L.RED, clamp(ta * 1.5), face=C.FONT_BLACK)
        notches = s["notches"] * (1 - s["lat"]) + s["notch2"] * (1 if t > c["c0"] - 0.3 else 0)
        slab(P, 1, s["oy"], s["b"], notches=notches, hl=s["hl"], crack_open=s["open"],
             crack_depth=s["depth"], hl_surface=s["surface"], fill=1 - 0.5 * s["lat"])
        lattice(P, t, s["lat"], s["oy"], s["b"], s["out"], s["in"], s["comp"])
        # flechas: la cara de arriba se estira
        st = max(s["stretch"], 0.8 * prog(t, c["abra"] - 0.1, c["abra"] + 0.4) * (1 - prog(t, c["templado"] - 0.3, c["templado"] + 0.2)))
        if st > 0:
            y = YT - 120
            P.arrow(470, y, 250, y, L.FG, st, w=8, head=26); P.arrow(610, y, 830, y, L.FG, st, w=8, head=26)
            P.text("se estira", 540, y - 40, 36, L.FG, st * (1 if t < c["b0"] else 0), face=C.FONT_BOLD)
        # etiquetas de sodio y potasio
        so = window(t, c["sodio"] - 0.05, c["a0"], 0.3, 0.4)
        if so > 0:
            P.circle(330, 1235, 9, L.GRAY, so); P.text("sodio", 352, 1247, 38, L.GRAY, so, face=C.FONT_BOLD, align="left")
        po = window(t, c["potasio"] - 0.05, c["a0"], 0.3, 0.4)
        if po > 0:
            P.circle(620, 1235, 15, L.RED, po); P.text("potasio", 648, 1247, 38, L.RED, po, face=C.FONT_BOLD, align="left")
        ar = max(s["comp"] * (1 - prog(t, c["irromp"] - 0.3, c["irromp"])), 0)
        comp_arrows(P, ar, s["oy"], s["b"], s["push"])
        la = window(t, c["comprimida"] - 0.05, c["abra"] - 0.1, 0.35, 0.35)
        if la > 0:
            with P.transform(0, 0, 0.85 + 0.15 * out_back(clamp(la)), cx=540, cy=1080):
                P.text("COMPRIMIDO", 540, 1100, 64, L.RED, la, face=C.FONT_BLACK, tracking=4)
        pa = window(t, c["templado"] - 0.1, c["irromp"], 0.4, 0.3)
        if pa > 0:
            P.pill("vidrio templado químicamente", 540, 1180, 42, L.RED, out_back(clamp(pa)), face=C.FONT_BOLD)


def rack_scene(P, t):
    c = CUE
    a = window(t, c["pool"] - 0.6, c["eso"] + 0.4, 0.5, 0.6)
    if a <= 0: return
    grow = prog(t, c["tenis"] - 0.2, c["tenis"] + 0.6, in_out_cubic)
    sq = prog(t, c["caben"] - 0.1, c["caben"] + 0.5) * 0.6 + 0.4 * prog(t, c["apretadas"] - 0.1, c["apretadas"] + 0.3)
    rack(P, t, a, grow, sq * grow)


def end_scene(P, t):
    c = CUE
    a = prog(t, c["irromp"] - 0.05, c["irromp"] + 0.3)
    if a <= 0: return
    with P.layer(a):
        # caída: el celular cae inclinado y se triza en la esquina
        fall_t0, fall_hit = c["irromp"] + 0.1, c["caida"] + 0.25
        u = prog(t, fall_t0, fall_hit, in_cubic)
        swap = prog(t, c["pero"] - 0.35, c["pero"] + 0.15, in_out_cubic)
        y = lerp(700, 925, u)
        crack = prog(t, fall_hit, fall_hit + 0.35)
        sh = math.sin((t - fall_hit) * 50) * 8 * math.exp(-(t - fall_hit) * 6) if t > fall_hit else 0.0
        ga = 1 - swap
        P.line(150, 1250, 930, 1250, L.GRAY, ga * a, w=5)
        phone(P, PH_X + sh, y, 0.82, ga, rot=28, crack=crack, crack_at=(120, 255))
        if t > fall_hit:
            flash(P, PH_X + 190, 1240, clamp((t - fall_hit) / 0.4), 90)
        # el celular nuevo y el martillo (empalme con el inicio)
        if swap > 0:
            hit = c["hit2"]
            sh2 = math.sin((t - hit) * 60) * 10 * math.exp(-(t - hit) * 7) if t > hit else 0.0
            glow = 0.8 * prog(t, c["apretada"] - 0.2, c["apretada"] + 0.4)
            sq = prog(t, c["apretada"] - 0.15, c["apretada"] + 0.35)
            phone(P, PH_X + sh2, PH_Y, lerp(0.9, 1.0, swap), swap, glow=glow, squeeze=sq * (1 - 0.15 * math.sin(t * 6) ** 2))
            hammer(P, swing(t, hit), swap)
            hx, hy = hammer_head(-50)
            flash(P, hx - 40, hy, clamp((t - hit) / 0.45))


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["pantalla"] = T("hook", "pantalla"); c["vidrio"] = T("hook", "vidrio"); c["ventana"] = T("hook", "ventana")
    c["trizas"] = T("hook", "trizas"); c["aguanta"] = T("hook", "aguanta")
    c["hit1"] = T("hook", "pantalla")
    c["g0"] = T("grieta"); c["grietas"] = T("grieta", "grietas"); c["diminutas"] = T("grieta", "diminutas")
    c["dobla"] = T("grieta", "dobla"); c["estira"] = T("grieta", "estira"); c["abre"] = T("grieta", "abre")
    c["avanza"] = T("grieta", "avanza"); c["desde"] = T("grieta", "desde")
    c["b0"] = T("bano"); c["proteger"] = T("bano", "proteger"); c["sal"] = T("bano", "sal")
    c["c400"] = T("bano", "400"); c["sodio"] = T("bano", "sodio"); c["potasio"] = T("bano", "potasio")
    c["a0"] = T("aprieta"); c["pool"] = T("aprieta", "pool"); c["tenis"] = T("aprieta", "tenis")
    c["caben"] = T("aprieta", "caben"); c["apretadas"] = T("aprieta", "apretadas"); c["eso"] = T("aprieta", "eso")
    c["comprimida"] = T("aprieta", "comprimida")
    c["c0"] = T("cierre"); c["abra"] = T("cierre", "abra"); c["apreton"] = T("cierre", "apretón")
    c["templado"] = T("cierre", "templado"); c["irromp"] = T("cierre", "irrompible"); c["caida"] = T("cierre", "caída")
    c["pero"] = T("cierre", "pero"); c["golpe"] = T("cierre", "golpe"); c["apretada"] = T("cierre", "apretada")
    c["hit2"] = c["golpe"]
    c["end"] = tl.duration
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = (0.5 * pulse(t, c["potasio"] - 0.2, 1.3) + 0.5 * pulse(t, c["comprimida"] - 0.2, 1.3)
            + 0.6 * prog(t, c["apretada"] - 0.2, c["apretada"] + 0.6))
    L.background(P, t, glow=glow)
    hook_scene(P, t)
    slab_scene(P, t)
    rack_scene(P, t)
    end_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    with P.transform(0, 170):
        phone(P, PH_X, PH_Y, 0.9, 1, glow=0.6, squeeze=0.0)
        hammer(P, -50, 1, pivot=(PIV[0], PIV[1]))
        hx, hy = hammer_head(-50)
        flash(P, hx - 40, hy, 0.35)
    P.text("¿POR QUÉ", 540, 560, 104, L.FG, 1, face=C.FONT_BLACK)
    P.text("NO SE ROMPE?", 540, 676, 104, L.RED, 1, face=C.FONT_BLACK)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.35), (c["hit1"], "thump", 0.6), (c["hit1"] + 0.02, "tick", 0.4),
            (c["trizas"], "pop_low", 0.5), (c["aguanta"], "pop", 0.4),
            (c["g0"] - 0.3, "whoosh", 0.4), (c["grietas"], "tick", 0.35), (c["estira"], "whoosh_down", 0.3),
            (c["abre"], "pop_low", 0.45),
            (c["b0"] - 0.3, "whoosh", 0.4), (c["sal"], "swell", 0.3), (c["c400"], "ding", 0.45),
            (c["sodio"], "pop", 0.35), (c["potasio"] - 0.4, "riser", 0.3), (c["potasio"], "ding", 0.6),
            (c["a0"] - 0.25, "whoosh", 0.35), (c["tenis"], "pop", 0.45), (c["apretadas"], "thump", 0.4),
            (c["comprimida"], "ding", 0.6),
            (c["apreton"], "thump", 0.4), (c["templado"], "pop", 0.4), (c["caida"] + 0.25, "thump", 0.5),
            (c["pero"] - 0.3, "whoosh", 0.35), (c["hit2"], "thump", 0.6), (c["apretada"], "ding", 0.65)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["potasio"], "pulse": (c["a0"], c["c0"]), "quiet": [(c["aguanta"] - 0.2, c["g0"] + 0.2)]}
