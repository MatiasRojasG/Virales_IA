"""Escenas — «¿Cómo sabe caer un personaje de GTA?» (stheq.ia, motion graphics).

Hilo visual: un monigote articulado dibujado por código. Gancho: una flecha roja lo empuja; un «fantasma» gris cae
como muñeco y el monigote blanco estira los brazos y da un paso → caída grabada: una tira de cuadros y tres
monigotes que repiten la misma caída al mismo tiempo → muñeco de trapo: cae sin control (simulación de péndulo) →
Oxford: una red de neuronas encima del cuerpo que se enciende → idea: músculos rojos y un «cerebro» en la cabeza;
lo empujan, aparece en el suelo el punto donde debe pisar (punto de captura) y el pie aterriza ahí → «Euphoria» y
«GTA IV · 2008» → tres monigotes con empujones distintos: tres reacciones distintas → barras 55.000 vs 600.000
(×10) → cierre: otro empujón, la tira de cuadros grabados se tacha, el punto aparece y el monigote recupera el
equilibrio; la flecha vuelve a entrar (empalme con el gancho).
El movimiento sale de simulaciones propias (fisica.py). Sin fotos ni imágenes del juego.
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
import fisica as F

TL = None; EP = {}; CHUNKS = []; CUE = {}
_IMG = {}
SIM = {}

S = 230.0          # px por metro
GY = 1185          # suelo


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


# =============================================================== monigote
def ik(hx, hy, fx, fy, l1, l2, bend=1):
    """Rodilla/codo de un brazo de dos segmentos (coordenadas en metros, y hacia arriba)."""
    dx, dy = fx - hx, fy - hy
    d = max(1e-4, min(math.hypot(dx, dy), l1 + l2 - 1e-4))
    a = (l1 * l1 - l2 * l2 + d * d) / (2 * d)
    h = math.sqrt(max(0.0, l1 * l1 - a * a))
    ux, uy = dx / d, dy / d
    mx, my = hx + ux * a, hy + uy * a
    return mx - uy * h * bend, my + ux * h * bend


def pose_control(sim, ts, ox=0.0):
    """Pose (en metros) a partir de la simulación con control."""
    x = F.sample(sim, "x", ts) + ox; v = F.sample(sim, "v", ts); p = F.sample(sim, "p", ts) + ox
    fl = F.sample(sim, "fl", ts) + ox; fr = F.sample(sim, "fr", ts) + ox
    ll = F.sample(sim, "ll", ts); lr = F.sample(sim, "lr", ts)
    leg = 0.92
    hy = min(0.9, min(math.sqrt(max(0.0, leg ** 2 - (x - f) ** 2)) for f in (fl, fr)) - 0.015)
    hy = max(0.62, hy)
    lean = math.atan(0.55 * (x - p) + 0.12 * v)
    k = clamp(abs(v) / 0.9)
    wob = math.sin(ts * 9.0) * 0.35 * k
    arm_r = lerp(0.18, 2.0, k) + wob          # ángulo del brazo desde abajo (adelante +)
    arm_l = lerp(-0.18, -1.6, k) - wob * 0.7
    return dict(hip=(x, hy), lean=lean, feet=((fl, ll), (fr, lr)), arms=(arm_l, arm_r), elbow=0.5 * k + 0.15,
                head=lean * 0.5)


def pose_stand(ox=0.0):
    return dict(hip=(ox, 0.9), lean=0.0, feet=((ox - 0.12, 0.0), (ox + 0.12, 0.0)), arms=(-0.16, 0.16),
                elbow=0.15, head=0.0)


def pose_trapo(sim, ts, ox=0.0, canned=False):
    """Cuerpo sin control: pivota sobre los pies; rodillas y brazos sueltos."""
    th = F.sample(sim, "th", ts); om = F.sample(sim, "om", ts)
    if canned:   # caída «grabada»: misma curva, en 8 cuadros clave rígidos
        th = math.floor(th / (math.pi / 2) * 8) / 8 * (math.pi / 2)
        om = 0.0
    u = th / (math.pi / 2)
    leg = 0.9 - 0.22 * u
    hx = ox + leg * math.sin(th * 0.85); hy = max(0.12, leg * math.cos(th * 0.85))
    lean = th * 1.12
    flop = -om * 0.25
    arm = -lean + 0.25 + flop          # cuelgan hacia el suelo
    return dict(hip=(hx, hy), lean=lean, feet=((ox - 0.1, 0.0), (ox + 0.08, 0.0)), arms=(arm - 0.3, arm + 0.2),
                elbow=0.1, head=lean * 0.25 + flop * 0.6, limp=True)


def figure(P, pose, cx, a=1.0, col=None, w=15, muscles=0.0, brain=0.0, t=0.0, scale=1.0, gy=GY):
    if a <= 0: return
    col = col or L.FG
    s = S * scale
    X = lambda x: cx + (x) * s
    Y = lambda y: gy - y * s
    hx, hy = pose["hip"]; ln = pose["lean"]
    sx, sy = hx + 0.55 * math.sin(ln), hy + 0.55 * math.cos(ln)            # hombros
    nx, ny = sx + 0.1 * math.sin(ln + pose["head"]), sy + 0.1 * math.cos(ln + pose["head"])
    hdx, hdy = nx + 0.13 * math.sin(ln + pose["head"]), ny + 0.13 * math.cos(ln + pose["head"])
    segs = []
    # piernas
    knees = []
    for (fx, fl) in pose["feet"]:
        kx, ky = ik(hx, hy, fx, fl, 0.47, 0.47, bend=-1 if pose.get("limp") else -1)
        segs += [((hx, hy), (kx, ky)), ((kx, ky), (fx, fl))]
        knees.append((kx, ky, fx, fl))
    # brazos
    hands = []
    for k, ang in enumerate(pose["arms"]):
        ga = ln + math.pi + ang              # ángulo global (0 = arriba)
        ex, ey = sx + 0.29 * math.sin(ga), sy + 0.29 * math.cos(ga)
        ga2 = ga + (pose["elbow"] if k == 1 else -pose["elbow"])
        wx, wy = ex + 0.27 * math.sin(ga2), ey + 0.27 * math.cos(ga2)
        segs += [((sx, sy), (ex, ey)), ((ex, ey), (wx, wy))]
        hands.append((ex, ey, wx, wy))
    segs.append(((hx, hy), (sx, sy)))
    with P.layer(a):
        for (a0, a1) in segs:
            P.line(X(a0[0]), Y(a0[1]), X(a1[0]), Y(a1[1]), col, 1, w=w * scale)
        P.line(X(sx), Y(sy), X(nx), Y(ny), col, 1, w=w * scale)
        P.circle(X(hdx), Y(hdy), 0.12 * s, col, 1)
        for (kx, ky, fx, fl) in knees:   # pies
            P.line(X(fx - 0.02), Y(fl), X(fx + 0.09), Y(fl), col, 1, w=w * scale)
        if muscles > 0:      # músculos: haces rojos sobre muslos, pantorrillas, brazos y espalda
            for (a0, a1) in segs[:-1] + [segs[-1]]:
                mx0 = lerp(a0[0], a1[0], 0.18); my0 = lerp(a0[1], a1[1], 0.18)
                mx1 = lerp(a0[0], a1[0], 0.82); my1 = lerp(a0[1], a1[1], 0.82)
                P.line(X(mx0), Y(my0), X(mx1), Y(my1), L.RED, 0.8 * muscles, w=w * 0.55 * scale)
        if brain > 0:
            bx, by = X(hdx), Y(hdy)
            P.circle(bx, by, 0.065 * s, L.RED, brain)
            P.circle(bx, by, 0.065 * s * (1.6 + 0.5 * math.sin(t * 6)), L.RED, 0.35 * brain, blur=8)
            # «nervios»: del cerebro por la espalda hasta las piernas
            pth = [(hdx, hdy), (nx, ny), (sx, sy), (hx, hy)]
            ph = (t * 1.6) % 1.0
            for k in range(3):
                q0 = pth[k]; q1 = pth[k + 1]
                P.line(X(q0[0]), Y(q0[1]), X(q1[0]), Y(q1[1]), L.RED, 0.9 * brain, w=4 * scale)
            for (kx, ky, fx, fl) in knees:
                P.line(X(hx), Y(hy), X(kx), Y(ky), L.RED, 0.9 * brain, w=4 * scale)
                P.line(X(kx), Y(ky), X(fx), Y(fl), L.RED, 0.9 * brain, w=4 * scale)
                P.circle(X(lerp(hx, fx, ph)), Y(lerp(hy, fl, ph)) - 0 * ky, 7 * scale, L.RED, brain)
    return dict(head=(X(hdx), Y(hdy)), hip=(X(hx), Y(hy)))


def ground(P, a=1.0, x0=90, x1=990, gy=GY):
    if a <= 0: return
    P.line(x0, gy + 4, x1, gy + 4, L.DIM, a, w=5)


def push_arrow(P, x_tip, y, a, k=1.0):
    if a <= 0: return
    P.arrow(x_tip - 210 * k, y, x_tip, y, L.RED, a, w=16, head=40)


def warp(t, t0, t1, s1):
    """Tiempo real → tiempo de simulación: t0→0 y t1→s1 (cámara lenta), luego velocidad normal."""
    if t <= t0: return 0.0
    if t <= t1: return (t - t0) / (t1 - t0) * s1
    return s1 + (t - t1)


def capture_marker(P, x_px, a, t):
    if a <= 0: return
    P.circle(x_px, GY + 4, 22, L.RED, a)
    P.circle(x_px, GY + 4, 22 + 26 * ((t * 1.4) % 1.0), L.RED, a * (1 - (t * 1.4) % 1.0), stroke=4)


def film_strip(P, cx, cy, sim, a, n=6, w=118, h=150, crossed=0.0):
    """Tira de película con cuadros de la caída grabada."""
    if a <= 0: return
    x0 = cx - n * w / 2
    with P.layer(a):
        P.rect(x0 - 14, cy - h / 2 - 26, x0 + n * w + 14, cy + h / 2 + 26, L.CARD, 1, radius=12)
        for k in range(n + 1):
            for yy in (cy - h / 2 - 14, cy + h / 2 + 14):
                P.rect(x0 + k * w - 30, yy - 6, x0 + k * w - 14, yy + 6, L.BG, 1, radius=3)
        for k in range(n):
            fx = x0 + k * w + w / 2
            P.rect(fx - w / 2 + 6, cy - h / 2, fx + w / 2 - 6, cy + h / 2, L.BG, 1, radius=6)
            ts = k / (n - 1) * 0.95
            figure(P, pose_trapo(sim, ts, canned=True), fx - 22, 1, col=L.GRAY, w=15, scale=0.26, gy=cy + h / 2 - 12)
        if crossed > 0:
            P.line(x0 - 20, cy + h / 2 + 30, lerp(x0 - 20, x0 + n * w + 20, crossed), lerp(cy + h / 2 + 30, cy - h / 2 - 30, crossed),
                   L.RED, 1, w=12)


# =============================================================== escenas
def hook_scene(P, t):
    c = CUE
    a = 1 - prog(t, c["g0"] - 0.35, c["g0"] + 0.1, in_out_cubic)
    if a <= 0: return
    cx = 470
    with P.layer(a):
        ground(P, 1)
        tp = c["hit"]
        ts = warp(t, tp, c["paso"] + 0.15, 0.37)
        # fantasma: así caería sin control
        ga = window(t, c["caer"] - 0.2, c["estira"] + 0.6, 0.3, 0.6)
        if ga > 0:
            gts = warp(t, c["caer"] - 0.3, c["muneco"] + 0.5, 0.95)
            figure(P, pose_trapo(SIM["trapo_hook"], gts), cx - 40, ga * 0.45, col=L.GRAY)
        pose = pose_control(SIM["c10"], ts) if t >= tp else pose_stand()
        info = figure(P, pose, cx, 1)
        # flecha que empuja
        xa = lerp(cx - 260, cx - 70, prog(t, 0.0, tp, in_out_cubic)) if t < tp else lerp(cx - 70, cx - 200, prog(t, tp, tp + 0.6, out_cubic))
        push_arrow(P, xa, GY - 0.75 * S, 1 - prog(t, tp + 0.4, tp + 0.9))
        if t >= tp:
            P.circle(cx - 60, GY - 0.75 * S, 40 + 80 * prog(t, tp, tp + 0.5), L.RED, 0.5 * (1 - prog(t, tp, tp + 0.5)), stroke=5)
        q = prog(t, c["sabe"] - 0.3, c["sabe"] + 0.15)
        if q > 0:
            hx, hy = info["head"]
            P.text("?", hx + 110, hy - 60 + 6 * math.sin(t * 3), 150, L.RED, out_back(q) * clamp(q * 2), face=C.FONT_BLACK)


def grabado_scene(P, t):
    c = CUE
    a = window(t, c["g0"] - 0.3, c["tr0"] + 0.05, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        sa = prog(t, c["grababan"] - 0.3, c["grababan"] + 0.2)
        film_strip(P, 540, 600, SIM["trapo"], sa)
        ground(P, 1)
        tri = prog(t, c["siempre"] - 0.35, c["siempre"] + 0.1, in_out_cubic)
        loop = 1.25
        tl0 = c["grababan"] - 0.2
        ts = ((t - tl0) % loop) if t > tl0 else 0.0
        ts = min(ts, 0.95)
        pose = pose_trapo(SIM["trapo"], ts, canned=True)
        for k, ox in enumerate((-300, 0, 300)):
            aa = 1.0 if k == 1 else tri
            x = lerp(470, 470 + ox, tri) if k != 1 else lerp(470, 470, tri)
            figure(P, pose, x, aa, col=L.FG if k == 1 else L.GRAY, scale=lerp(1.0, 0.78, tri))
        # contador de repeticiones
        if t > tl0:
            nrep = 1 + int((t - tl0) / loop)
            P.text(f"×{nrep}", 900, 820, 70, L.RED, prog(t, tl0, tl0 + 0.3), face=C.FONT_BLACK)


def trapo_scene(P, t):
    c = CUE
    a = window(t, c["tr0"] - 0.3, c["ox0"] + 0.05, 0.4, 0.4)
    if a <= 0: return
    cx = 400
    with P.layer(a):
        ground(P, 1)
        tp = c["soltar"] + 0.15
        ts = warp(t, tp, c["muneco2"], 0.9)
        pose = pose_trapo(SIM["trapo"], ts) if t >= tp else pose_stand(0)
        hi = pulse(t, c["muneco2"] - 0.1, 1.0)
        figure(P, pose, cx, 1, col=lerp_c(L.FG, L.GRAY, prog(t, c["muneco2"] - 0.3, c["muneco2"] + 0.3)))
        xa = lerp(cx - 260, cx - 70, prog(t, c["tr0"], tp, in_out_cubic)) if t < tp else cx - 70
        push_arrow(P, xa, GY - 0.75 * S, (1 - prog(t, tp + 0.2, tp + 0.6)) * prog(t, c["tr0"], c["tr0"] + 0.3))
        if hi > 0:
            P.circle(cx + 0.95 * S, GY - 10, 60 + 60 * hi, L.FG, 0.25 * hi, stroke=4)


NET = None


def net_nodes():
    global NET
    if NET is None:
        rng = np.random.default_rng(5)
        layers = [5, 7, 7, 4]
        NET = []
        for li, n in enumerate(layers):
            for k in range(n):
                NET.append((li, 220 + li * 213 + rng.uniform(-14, 14), 520 + (k + 0.5) * (300 / n) + rng.uniform(-8, 8)))
    return NET


def oxford_scene(P, t):
    c = CUE
    a = window(t, c["ox0"] - 0.3, c["id0"] + 0.4, 0.4, 0.5)
    if a <= 0: return
    with P.layer(a):
        ground(P, 1)
        nodes = net_nodes()
        na = prog(t, c["sistema"] - 0.15, c["sistema"] + 0.5)
        nf = 1 - prog(t, c["sistema"] - 0.55, c["sistema"] - 0.15)
        on = prog(t, c["sistema"], c["mov"] + 0.4)
        if na > 0:
            for i, (li, x, y) in enumerate(nodes):
                for (lj, x2, y2) in nodes:
                    if lj == li + 1:
                        P.line(x, y, x2, y2, L.GRAY, 0.22 * na, w=2)
            for i, (li, x, y) in enumerate(nodes):
                fire = clamp(on * 4 - li) * (0.5 + 0.5 * math.sin(t * 7 + i))
                P.circle(x, y, 15, L.FG, na)
                if fire > 0: P.circle(x, y, 15, L.RED, fire * na)
        # el cuerpo bajo la red (se mueve un poco al «encenderse»)
        sway = 0.06 * math.sin((t - c["mov"]) * 3) * prog(t, c["mov"] - 0.3, c["mov"] + 0.3)
        pose = pose_stand(0); pose["lean"] = sway
        pose["arms"] = (-0.16 - 2 * sway, 0.16 + 2 * sway)
        info = figure(P, pose, 540, 1, scale=0.82)
        if na > 0:   # cables de la última capa al cuerpo
            hx, hy = info["head"]
            for (li, x, y) in nodes:
                if li == 3:
                    P.line(x, y + 12, hx, hy - 30, L.RED, 0.5 * na * on, w=3)
        pa = prog(t, c["oxford"] - 0.2, c["oxford"] + 0.25)
        if pa > 0 and nf > 0:
            P.pill("Universidad de Oxford", 540, 640, 36, L.FG, pa * nf)
        ra = prog(t, c["torsten"] - 0.2, c["torsten"] + 0.2)
        if ra > 0 and nf > 0:
            P.text("Torsten Reil", 540, 735, 58, L.FG, ra * nf, face=C.FONT_BLACK)


def idea_scene(P, t):
    c = CUE
    a = window(t, c["id0"] - 0.2, c["n0"] + 0.4, 0.4, 0.5)
    if a <= 0: return
    cx = 420
    with P.layer(a):
        ground(P, 1)
        tp = c["empujan"] + 0.15
        land = 0.36
        ts = warp(t, tp, c["pie"] + 0.1, land)
        sim = SIM["c10"]
        pose = pose_control(sim, ts) if t >= tp else pose_stand()
        mus = prog(t, c["musculos"] - 0.2, c["musculos"] + 0.4)
        br = prog(t, c["cerebro"] - 0.2, c["cerebro"] + 0.3)
        fade = 1 - prog(t, c["n0"] - 0.1, c["n0"] + 0.4)
        figure(P, pose, cx, 1, muscles=mus * fade, brain=br * fade, t=t)
        xa = lerp(cx - 260, cx - 70, prog(t, c["empujan"] - 0.5, tp, in_out_cubic)) if t < tp else lerp(cx - 70, cx - 200, prog(t, tp, tp + 0.6))
        push_arrow(P, xa, GY - 0.75 * S, prog(t, c["empujan"] - 0.5, c["empujan"] - 0.2) * (1 - prog(t, tp + 0.3, tp + 0.7)))
        # el «cálculo»: punto de captura y trayectoria del pie
        ca = prog(t, c["calcula"] - 0.15, c["calcula"] + 0.2) * (1 - prog(t, c["pie"] + 0.6, c["n0"]))
        if ca > 0:
            tgt = F.sample(sim, "tgt", max(ts, 0.2))
            x_t = cx + tgt * S
            capture_marker(P, x_t, ca, t)
            hip = pose["hip"]
            x0, y0 = cx + hip[0] * S, GY - hip[1] * S
            pe = skia.DashPathEffect.Make([16, 12], 0)
            pnt = paint(L.RED, 0.8 * ca, stroke=4); pnt.setPathEffect(pe)
            pth = skia.Path(); pth.moveTo(x0, y0); pth.quadTo((x0 + x_t) / 2 + 40, y0 + 40, x_t, GY - 10)
            P.c.drawPath(pth, pnt)


def nombre_scene(P, t):
    c = CUE
    a = window(t, c["n0"] - 0.1, c["g60"] + 0.05, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        ea = prog(t, c["euphoria"] - 0.2, c["euphoria"] + 0.25)
        up = prog(t, c["por"] - 0.4, c["por"] + 0.2, in_out_cubic)
        if ea > 0:
            with P.transform(0, 0, 0.85 + 0.15 * out_back(ea), cx=540, cy=lerp(700, 560, up)):
                P.text("EUPHORIA", 540, lerp(720, 580, up), lerp(120, 80, up), L.FG, ea, face=C.FONT_BLACK, tracking=6)
        ga = prog(t, c["gta"] - 0.2, c["gta"] + 0.2) * (1 - up)
        if ga > 0:
            P.line(200, 900, 880, 900, L.DIM, ga, w=6)
            for k, yr in enumerate(range(2008, 2027, 3)):
                xx = lerp(200, 880, (yr - 2008) / 18)
                P.circle(xx, 900, 7, L.GRAY, ga)
            P.circle(200, 900, 20, L.RED, ga)
            P.text("GTA IV", 200, 980, 50, L.FG, ga, face=C.FONT_BLACK)
            ya = prog(t, c["y2008"] - 0.2, c["y2008"] + 0.2)
            P.text("2008", 200, 845, 44, L.RED, ya * ga, face=C.FONT_BLACK)
            P.text("2026", 880, 845, 36, L.GRAY, ya * ga, face=C.FONT_SEMI)
            P.line(220, 900, lerp(220, 870, prog(t, c["y2008"], c["y2008"] + 1.0, in_out_cubic)), 900, L.RED, ga, w=6)
        # tres empujones distintos
        if up > 0:
            ground(P, up)
            tp = c["caidas"] - 0.45
            for k, (key, ox) in enumerate((("c055", 210), ("c10", 480), ("c14", 750))):
                ts = warp(t, tp + 0.12 * k, tp + 0.12 * k + 0.01, 0.01)
                pose = pose_control(SIM[key], ts) if t >= tp + 0.12 * k else pose_stand()
                figure(P, pose, ox - 60, up, scale=0.72, w=16)
                tk = tp + 0.12 * k
                xa = lerp(ox - 60 - 150, ox - 60 - 45, prog(t, tk - 0.4, tk, in_out_cubic))
                push_arrow(P, xa, GY - 0.75 * S * 0.72, up * (1 - prog(t, tk + 0.15, tk + 0.4)), k=0.5)


def gta6_scene(P, t):
    c = CUE
    a = window(t, c["g60"] - 0.3, c["c0"] + 0.05, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        base = 1130; top = 640
        g = prog(t, c["n600"] - 0.3, c["anim"] + 0.4, in_out_cubic)
        v5 = 55_000 * prog(t, c["g60"], c["g60"] + 0.8, out_cubic)
        v6 = 55_000 + (600_000 - 55_000) * g
        for (x, val, lab, col) in ((340, v5, "GTA V", L.GRAY), (740, v6, "GTA VI", L.FG)):
            hh = (base - top) * val / 600_000
            P.rect(x - 110, base - max(hh, 6), x + 110, base, col if lab == "GTA V" else lerp_c(L.FG, L.RED, prog(t, c["diez"] - 0.2, c["diez"] + 0.3)), 1, radius=10)
            P.text(lab, x, base + 64, 48, L.FG, 1, face=C.FONT_BLACK)
            P.text(f"{int(round(val, -3)):,}".replace(",", "."), x, base - max(hh, 6) - 30, 54, L.FG, 1, face=C.FONT_BLACK)
        P.text("animaciones de peatones", 540, 1280, 34, L.GRAY, prog(t, c["peatones"] - 0.2, c["peatones"] + 0.3), face=C.FONT_SEMI)
        xa = prog(t, c["diez"] - 0.2, c["diez"] + 0.25)
        if xa > 0:
            with P.transform(0, 0, 0.7 + 0.3 * out_back(xa), cx=420, cy=760):
                P.text("×10", 420, 790, 120, L.RED, xa, face=C.FONT_BLACK)


def cierre_scene(P, t):
    c = CUE
    a = prog(t, c["c0"] - 0.3, c["c0"] + 0.2, in_out_cubic)
    if a <= 0: return
    cx = 420
    with P.layer(a):
        ground(P, 1)
        tp = c["empujon"] + 0.1
        ts = warp(t, tp, c["calcula2"] + 0.35, 0.36)
        sim = SIM["c10"]
        pose = pose_control(sim, ts) if t >= tp else pose_stand()
        figure(P, pose, cx, 1, brain=prog(t, c["calcula2"] - 0.2, c["calcula2"] + 0.2) * (1 - prog(t, c["end"] - 1.4, c["end"] - 0.6)), t=t)
        xa = lerp(cx - 260, cx - 70, prog(t, c["c0"], tp, in_out_cubic)) if t < tp else lerp(cx - 70, cx - 200, prog(t, tp, tp + 0.6))
        push_arrow(P, xa, GY - 0.75 * S, prog(t, c["c0"], c["c0"] + 0.3) * (1 - prog(t, tp + 0.3, tp + 0.7)))
        # «no recuerda»: tira de película que se tacha
        fa = window(t, c["recuerda"] - 0.3, c["calcula2"] + 0.4, 0.3, 0.4)
        film_strip(P, 540, 600, SIM["trapo"], fa, crossed=prog(t, c["recuerda"] + 0.2, c["recuerda"] + 0.7, in_out_cubic))
        ca = prog(t, c["calcula2"] - 0.1, c["calcula2"] + 0.2) * (1 - prog(t, c["end"] - 1.6, c["end"] - 0.9))
        if ca > 0:
            capture_marker(P, cx + F.sample(sim, "tgt", max(ts, 0.2)) * S, ca, t)
        # empalme: la flecha vuelve a entrar al final
        la = prog(t, c["end"] - 1.0, c["end"] - 0.1, in_out_cubic)
        if la > 0:
            hx = cx + pose["hip"][0] * S
            push_arrow(P, lerp(hx - 330, hx - 180, la), GY - 0.75 * S, la)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, SIM
    TL, EP = tl, episode
    c = {}
    c["hit"] = T("hook", "Empujas") + 0.45; c["caer"] = T("hook", "caer"); c["muneco"] = T("hook", "muñeco")
    c["estira"] = T("hook", "estira"); c["paso"] = T("hook", "paso"); c["sabe"] = T("hook", "sabe")
    c["g0"] = T("grabado"); c["grababan"] = T("grabado", "grababan"); c["siempre"] = T("grabado", "siempre")
    c["tr0"] = T("trapo"); c["soltar"] = T("trapo", "soltar"); c["muneco2"] = T("trapo", "muñeco")
    c["ox0"] = T("oxford"); c["oxford"] = T("oxford", "Oxford"); c["torsten"] = T("oxford", "Torsten")
    c["sistema"] = T("oxford", "sistema"); c["mov"] = T("oxford", "movimiento")
    c["id0"] = T("idea"); c["musculos"] = T("idea", "músculos"); c["cerebro"] = T("idea", "cerebro")
    c["empujan"] = T("idea", "empujan"); c["calcula"] = T("idea", "calcula"); c["pie"] = T("idea", "pie")
    c["n0"] = T("nombre"); c["euphoria"] = T("nombre", "Euphoria"); c["gta"] = T("nombre", "GTA")
    c["y2008"] = T("nombre", "2008"); c["por"] = T("nombre", "Por"); c["caidas"] = T("nombre", "caídas")
    c["g60"] = T("gta6"); c["peatones"] = T("gta6", "peatones"); c["n600"] = T("gta6", "600.000")
    c["anim"] = T("gta6", "animaciones"); c["diez"] = T("gta6", "diez")
    c["c0"] = T("cierre"); c["empujon"] = T("cierre", "empujón"); c["recuerda"] = T("cierre", "recuerda")
    c["calcula2"] = T("cierre", "calcula"); c["caerse"] = T("cierre", "caerse")
    c["end"] = tl.duration
    CUE = c
    SIM = {"c10": F.sim_control(1.0, T=12), "c055": F.sim_control(0.55, T=6), "c14": F.sim_control(1.4, T=6),
           "trapo": F.sim_trapo(0.5, T=6), "trapo_hook": F.sim_trapo(0.8, T=8)}
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["calcula"] - 0.2, 1.3) + 0.5 * pulse(t, c["euphoria"] - 0.2, 1.3) + 0.4 * pulse(t, c["diez"] - 0.2, 1.3)
    L.background(P, t, glow=glow)
    hook_scene(P, t)
    grabado_scene(P, t)
    trapo_scene(P, t)
    oxford_scene(P, t)
    idea_scene(P, t)
    nombre_scene(P, t)
    gta6_scene(P, t)
    cierre_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    P.text("¿CÓMO SABE", 540, 560, 96, L.FG, 1, face=C.FONT_BLACK)
    P.text("NO CAERSE?", 540, 670, 104, L.RED, 1, face=C.FONT_BLACK)
    ground(P, 1)
    sim = SIM["c10"]
    figure(P, pose_trapo(SIM["trapo_hook"], 0.55), 330, 0.45, col=L.GRAY)
    figure(P, pose_control(sim, 0.24), 520, 1, brain=1.0, t=0.4)
    capture_marker(P, 520 + F.sample(sim, "tgt", 0.24) * S, 1, 0.1)
    push_arrow(P, 470, GY - 0.75 * S, 1)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (c["hit"], "thump", 0.55), (c["paso"], "tick", 0.35), (c["sabe"], "pop", 0.45),
            (c["g0"] - 0.3, "whoosh", 0.4), (c["grababan"], "rewind", 0.35), (c["siempre"], "pop", 0.35),
            (c["tr0"] - 0.3, "whoosh", 0.35), (c["soltar"] + 0.15, "thump", 0.45), (c["muneco2"], "pop_low", 0.5),
            (c["ox0"] - 0.3, "whoosh", 0.35), (c["sistema"], "riser", 0.3), (c["musculos"], "tick", 0.35),
            (c["cerebro"], "ding", 0.4), (c["empujan"] + 0.15, "thump", 0.5), (c["calcula"], "pop", 0.45),
            (c["pie"], "tick", 0.4), (c["euphoria"], "ding", 0.55), (c["gta"], "tick", 0.35),
            (c["caidas"] - 0.45, "thump", 0.4), (c["g60"] - 0.3, "whoosh", 0.4), (c["n600"], "riser", 0.3),
            (c["diez"], "ding", 0.55), (c["c0"] - 0.3, "whoosh", 0.35), (c["empujon"] + 0.1, "thump", 0.45),
            (c["recuerda"] + 0.2, "pop_low", 0.4), (c["calcula2"], "pop", 0.45), (c["caerse"], "ding", 0.45)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["id0"], "pulse": (c["n0"], c["c0"]), "quiet": [(c["sabe"] - 0.1, c["g0"] + 0.2)]}
