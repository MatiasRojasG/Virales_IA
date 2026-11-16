"""Escenas — «El robot que se cayó una y otra vez».

Todo ocurre en un solo escenario: suelo, plataforma y un robot que salta siguiendo las
trayectorias REALES de la simulación (experiment.py). Las estelas de cada intento cambian de
rosado (mucho error) a cyan (poco error); dos perillas muestran fuerza y ángulo; una curva
registra el error. Al final, las dos perillas se multiplican en una red de miles.
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
AMBER = (1.0, 0.72, 0.3)
X0, Y0, S = 150, 1180, 118                       # mundo (m) → pantalla
PX0, PX1, PY = 5.5, 6.7, 2.0
SUCCESS = 20                                     # primer aterrizaje real (intento 21)
ZOOM, RS = 1.15, 1.3                             # el escenario ocupa el ancho de la pantalla; robot grande


def label(P, txt, col, a):
    """Contador de intentos, fuera del escenario escalado (queda en la parte alta)."""
    P.c.save(); P.c.resetMatrix()
    P.pill(txt, 540, 470, 40, col, a, fill_a=0.08)
    P.c.restore()


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def W(x, y):
    return X0 + x * S, Y0 - y * S


def err_col(l):
    u = clamp(math.log10(max(l, 1e-3) + 1e-9) / -2.0 + 0.62)       # 17 → rosado, 0.01 → cyan
    return lerp_c(C.PINK, AMBER, clamp(u * 2)) if u < 0.5 else lerp_c(AMBER, C.CYAN, clamp(u * 2 - 1))


# =============================================================== el robot
def robot(P, x, y, s=1.0, a=1.0, rot=0.0, squash=0.0, col=C.CYAN, eyes=1.0):
    if a <= 0: return
    with P.transform(0, 0, 1, rot=rot, cx=x, cy=y - 40 * s):
        sx, sy = s * (1 + 0.25 * squash), s * (1 - 0.25 * squash)
        P.c.save(); P.c.translate(x, y); P.c.scale(sx, sy)
        P.rect(-14, -12, -6, 0, col, a, radius=4); P.rect(6, -12, 14, 0, col, a, radius=4)        # patas
        P.rect(-38, -82, 38, -12, col, a, radius=26)                                               # cuerpo
        P.rect(-28, -70, 28, -36, C.BG, a, radius=14)                                              # visor
        P.circle(-12, -53, 6 * eyes + 0.5, C.CYAN if col != C.CYAN else C.WHITE, a)
        P.circle(12, -53, 6 * eyes + 0.5, C.CYAN if col != C.CYAN else C.WHITE, a)
        P.line(0, -82, 0, -100, col, a, w=4); P.circle(0, -104, 6, AMBER, a)                        # antena
        P.c.restore()


# =============================================================== intentos
def schedule():
    c = CUE
    sch = [(0, c["cae"] - 1.0, 1.0), (1, c["otra1"] - 1.0, 1.0), (2, c["otra2"] - 1.0, 1.0)]
    t0, t1 = c["rep0"] + 0.1, c["logra_hasta"] - 0.3
    ks = list(range(3, SUCCESS))
    dt = (t1 - t0) / len(ks)
    sch += [(k, t0 + i * dt, dt * 0.9) for i, k in enumerate(ks)]
    sch.append((SUCCESS, c["logra"] - 1.5, 1.5))
    return sch


def pos_on(att, u):
    pts = att["pts"]; f = u * (len(pts) - 1); i = int(min(len(pts) - 2, f)); w = f - i
    return lerp(pts[i][0], pts[i + 1][0], w), lerp(pts[i][1], pts[i + 1][1], w)


def escena(P, t):
    c = CUE
    A = D["attempts"]
    a = 1 - window(t, c["red0"] + 0.2, c["cie0"] - 0.1, 0.6, 0.5) * 0.97
    lab_a = 1 - window(t, c["red0"] - 0.2, c["cie0"] + 10, 0.3, 0.3)
    with P.layer(a), P.transform(0, 0, ZOOM, cx=483, cy=Y0):
        # suelo y plataforma
        P.line(40, Y0 + 2, 1040, Y0 + 2, C.DIM, 1, w=6)
        x0, y0 = W(PX0, PY); x1, _ = W(PX1, PY)
        P.rect(x0, y0, x1, Y0, (0.13, 0.15, 0.22), 1, radius=6)
        P.rect(x0 - 6, y0 - 8, x1 + 6, y0 + 10, C.WHITE, 1, radius=6)
        done = [(k, ts, d) for (k, ts, d) in D["sch"] if t >= ts + d]
        # estelas de intentos terminados (las más antiguas, más tenues)
        for j, (k, ts, d) in enumerate(done):
            age = len(done) - j
            al = 0.85 if age == 1 else max(0.12, 0.6 - 0.05 * age)
            pts = [W(*q) for q in A[k]["pts"]]
            col = err_col(A[k]["loss"])
            pth = skia.Path(); pth.moveTo(*pts[0])
            for q in pts[1:]: pth.lineTo(*q)
            P.c.drawPath(pth, paint(col, al * (1 - prog(t, c["red0"], c["red0"] + 0.5) * 0.7), stroke=4))
        # robot: intento actual o reposo
        cur = next(((k, ts, d) for (k, ts, d) in D["sch"] if ts <= t < ts + d), None)
        if cur:
            k, ts, d = cur; u = (t - ts) / d
            x, y = pos_on(A[k], u)
            sx, sy = W(x, y)
            # trayectoria que se va dibujando
            pts = [W(*q) for q in A[k]["pts"]]; n = max(2, int(u * len(pts)))
            pth = skia.Path(); pth.moveTo(*pts[0])
            for q in pts[1:n]: pth.lineTo(*q)
            P.c.drawPath(pth, paint(err_col(A[k]["loss"]), 0.95, stroke=5))
            robot(P, sx, sy, RS, 1, rot=-20 * math.sin(u * math.pi))
            label(P, f"intento {k + 1}", C.WHITE, lab_a)
        else:
            last = [x for x in D["sch"] if x[1] + x[2] <= t]
            if not last or t < D["sch"][0][1]:
                robot(P, *W(0, 0), RS, 1, squash=0.15 * math.sin(t * 4) ** 2)          # espera, respirando
            else:
                k, ts, d = last[-1]; dt = t - (ts + d)
                ex, ey = A[k]["pts"][-1]; sx, sy = W(ex, ey)
                if A[k]["res"] == "plataforma":
                    sq = math.exp(-dt * 6) * math.cos(dt * 18) * 0.6
                    flip = 0.0
                    if t > c["simul"] - 1.2:                                                 # pirueta final
                        uf = in_out_cubic(prog(t, c["simul"] - 1.2, c["simul"] - 0.2))
                        flip = 360 * uf
                    robot(P, sx, sy - 160 * math.sin(math.pi * clamp((flip / 360))), RS, 1, rot=flip, squash=sq)
                    confeti(P, t, ts + d, sx, sy)
                else:
                    # cae y queda tumbado un momento; luego vuelve al inicio
                    tum = out_cubic(clamp(dt / 0.35))
                    fade = 1 - prog(dt, 0.9, 1.3)
                    robot(P, sx, sy, RS, fade, rot=-90 * tum, col=lerp_c(C.CYAN, C.PINK, tum), eyes=1 - 0.8 * tum)
                    if dt > 0.9:
                        robot(P, *W(0, 0), RS, prog(dt, 0.9, 1.3))
                    if dt < 0.6 and k <= 2:
                        P.text("¡pum!", sx, sy - 120, 46, C.PINK, 1 - prog(dt, 0.3, 0.6), face=C.FONT_BLACK)
                if k == SUCCESS or (A[k]["res"] != "plataforma"):
                    label(P, f"intento {k + 1}", C.CYAN if A[k]["res"] == "plataforma" else C.WHITE, lab_a)
        # pista: cuánto le faltó y hacia dónde
        ap = window(t, c["pista_w"] - 0.2, c["per0"] + 0.4, 0.4, 0.4)
        if ap > 0:
            ex, ey = A[2]["pts"][-1]; sx, sy = W(ex, ey); tx, ty = W((PX0 + PX1) / 2, PY)
            P.arrow(sx, sy - 20, tx, ty - 20, AMBER, ap, w=6, head=26)
            dist = math.hypot((PX0 + PX1) / 2 - ex, PY - ey)
            P.pill(f"le faltaron {dist:.1f} m".replace(".", ","), (sx + tx) / 2, (sy + ty) / 2 - 90, 30, AMBER, ap)
        # pregunta del inicio
        aq = window(t, c["preg0"] + 0.4, c["pista0"] + 0.2, 0.3, 0.3)
        if aq > 0:
            x, y = W(0, 0)
            P.text("?", x + 40, y - 190 + 8 * math.sin(t * 5), 110, C.CYAN, out_back(aq), face=C.FONT_BLACK, glow=0.6)


def confeti(P, t, t0, x, y):
    dt = t - t0
    if dt < 0 or dt > 2.2: return
    rng = np.random.default_rng(4)
    for k in range(40):
        ang = rng.uniform(-math.pi, 0); v = rng.uniform(250, 650)
        px = x + math.cos(ang) * v * dt; py = y + math.sin(ang) * v * dt + 500 * dt * dt
        col = [C.CYAN, C.VIOLET, AMBER, C.WHITE][k % 4]
        P.rect(px - 7, py - 4, px + 7, py + 4, col, 1 - dt / 2.2, radius=2)


# =============================================================== perillas y curva de error
def dial(P, x, y, frac, label, col, a, r=62):
    P.circle(x, y, r, C.BG2, a); P.circle(x, y, r, col, a, stroke=6)
    ang = -math.pi * 1.25 + clamp(frac) * math.pi * 1.5
    P.line(x, y, x + (r - 14) * math.cos(ang), y + (r - 14) * math.sin(ang), C.WHITE, a, w=8)
    P.text(label, x, y + r + 40, 30, col, a, face=C.FONT_BOLD)


def current_attempt(t):
    k = 0
    for (kk, ts, d) in D["sch"]:
        if t >= ts: k = kk
    return k


def panel(P, t):
    c = CUE
    a = prog(t, c["per0"] - 0.2, c["per0"] + 0.4) * (1 - prog(t, c["red0"] - 0.2, c["red0"] + 0.4))
    if a <= 0: return
    A = D["attempts"]; k = current_attempt(t)
    # antes de «poquito» muestra el intento 3; en «poquito» gira al ajuste siguiente
    if t < c["poquito"]: k = 2
    elif t < D["sch"][3][1]: k = 3 if t > c["poquito"] + 0.2 else 2
    v, ang = A[k]["v"], A[k]["ang"]
    hi = pulse(t, c["fuerza"], 0.8), pulse(t, c["angulo"], 0.8)
    with P.layer(a):
        dial(P, 190, 640, (v - 4) / 6, "fuerza", lerp_c(C.VIOLET, C.CYAN, hi[0]), 1)
        dial(P, 390, 640, ang / 1.2, "ángulo", lerp_c(C.VIOLET, C.CYAN, hi[1]), 1)
        # curva de error
        ae = prog(t, c["rep0"] - 0.2, c["rep0"] + 0.3)
        if ae > 0:
            gx0, gx1, gy0, gy1 = 560, 1000, 580, 740
            P.line(gx0, gy1, gx1, gy1, C.DIM, ae, w=3); P.line(gx0, gy0, gx0, gy1, C.DIM, ae, w=3)
            P.text("error", gx0 + 8, gy0 - 14, 26, C.WHITE, ae, face=C.FONT_SEMI, align="left")
            Ls = [A[j]["loss"] for j in range(min(k, SUCCESS) + 1)]
            pts = [(lerp(gx0, gx1, j / SUCCESS), lerp(gy1, gy0, math.sqrt(l / A[0]["loss"]))) for j, l in enumerate(Ls)]
            for (p1, q1), (p2, q2) in zip(pts, pts[1:]): P.line(p1, q1, p2, q2, C.CYAN, ae, w=5)
            if pts: P.glow_circle(*pts[-1], 9, err_col(Ls[-1]), ae)
            ab = prog(t, c["baja"] - 0.2, c["baja"] + 0.3)
            if ab > 0: P.arrow(gx1 - 30, gy0 + 10, gx1 - 30, gy1 - 20, C.CYAN, ab, w=5, head=18)


# =============================================================== red neuronal: de 2 perillas a millones
def red(P, t):
    c = CUE
    a = window(t, c["red0"] - 0.1, c["cie0"], 0.5, 0.5)
    if a <= 0: return
    with P.layer(a):
        g = prog(t, c["millones"] - 0.4, c["millones"] + 1.4, in_out_cubic)
        n = int(lerp(4, 22, g))                                   # perillas por lado de la grilla
        if g <= 0:
            # dos perillas al centro → se convierten en una red pequeña
            u = prog(t, c["red0"], c["red0"] + 0.8, in_out_cubic)
            layers = [3, 5, 5, 2]
            pos = [[(lerp(330, 750, li / 3), 860 + (j - (m - 1) / 2) * 110) for j in range(m)] for li, m in enumerate(layers)]
            for li in range(3):
                for (xa, ya) in pos[li]:
                    for (xb, yb) in pos[li + 1]:
                        P.line(xa, ya, xb, yb, C.VIOLET, 0.35 * u, w=2)
            for li, col in enumerate(pos):
                for (x, y) in col:
                    fr = 0.5 + 0.4 * math.sin(t * 2 + x * 0.01 + y * 0.02)
                    P.circle(x, y, 30 * u, C.BG2, 1); P.circle(x, y, 30 * u, C.CYAN, u, stroke=4)
                    ang = -math.pi * 1.25 + fr * math.pi * 1.5
                    P.line(x, y, x + 20 * u * math.cos(ang), y + 20 * u * math.sin(ang), C.WHITE, u, w=4)
            P.text("cada conexión = una perilla", 540, 560, 34, C.WHITE, prog(t, c["red0"] + 0.6, c["red0"] + 1.0), face=C.FONT_SEMI)
        else:
            cell = 800 / n
            for i in range(n):
                for j in range(n):
                    x = 140 + (j + 0.5) * cell; y = 520 + (i + 0.5) * cell
                    fr = 0.5 + 0.45 * math.sin(t * 3 + i * 0.7 + j * 1.3)
                    r = cell * 0.38
                    col = C.CYAN if (i + j) % 7 else C.VIOLET
                    P.circle(x, y, r, col, 0.9, stroke=max(1.5, r * 0.16))
                    ang = -math.pi * 1.25 + fr * math.pi * 1.5
                    P.line(x, y, x + r * 0.75 * math.cos(ang), y + r * 0.75 * math.sin(ang), C.WHITE, 0.9, w=max(1.5, r * 0.14))
            P.pill("millones de perillas", 540, 1290 - 30, 40, C.CYAN, prog(t, c["millones"], c["millones"] + 0.4))


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D
    TL, EP, D = tl, episode, data
    c = {}
    c["cae"] = T("hook", "cae"); c["otra1"] = T("hook", "Otra"); c["otra2"] = T("hook", "otra", 1)
    c["preg0"] = T("pregunta"); c["aprende"] = T("pregunta", "aprende")
    c["pista0"] = T("pista"); c["pista_w"] = T("pista", "pista")
    c["per0"] = T("perillas"); c["fuerza"] = T("perillas", "fuerza"); c["angulo"] = T("perillas", "ángulo")
    c["poquito"] = T("perillas", "poquito")
    c["rep0"] = T("repetir"); c["baja"] = T("repetir", "baja")
    c["logra_hasta"] = T("logra", "veintiuno"); c["logra"] = T("logra", "logra")
    c["red0"] = T("redes"); c["millones"] = T("redes", "millones")
    c["cie0"] = T("cierre"); c["simul"] = T("cierre", "simulación")
    CUE = c
    D["sch"] = schedule()
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    P.background(t, accent=0.35 * window(t, c["logra"] - 0.2, c["red0"], 0.3, 0.6))
    escena(P, t)
    panel(P, t)
    red(P, t)
    vignette(P, 0.45)
    vband(P, 1250, C.H, 0.0, 0.85)
    SUB.draw(P, CHUNKS, t)


def draw_cover(P, t=0.0):
    P.background(1.0, accent=0.6)
    A = D["attempts"]
    for k in (0, 4, 9, 14, SUCCESS):
        pts = [W(*q) for q in A[k]["pts"]]
        pth = skia.Path(); pth.moveTo(*pts[0])
        for q in pts[1:]: pth.lineTo(*q)
        P.c.drawPath(pth, paint(err_col(A[k]["loss"]), 0.9, stroke=6))
    P.line(40, Y0 + 2, 1040, Y0 + 2, C.DIM, 1, w=6)
    x0, y0 = W(PX0, PY); x1, _ = W(PX1, PY)
    P.rect(x0, y0, x1, Y0, (0.13, 0.15, 0.22), 1, radius=6); P.rect(x0 - 6, y0 - 8, x1 + 6, y0 + 10, C.WHITE, 1, radius=6)
    robot(P, *W(*A[SUCCESS]["pts"][-1]), 1.0)
    P.text("SE CAYÓ 20 VECES", 540, 420, 92, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("Y APRENDIÓ SOLO", 540, 525, 92, C.CYAN, 1, face=C.FONT_BLACK, glow=0.5)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.4)]
    for (k, ts, d) in D["sch"]:
        res = D["attempts"][k]["res"]
        big = k <= 2 or k == SUCCESS
        cues.append((ts, "whoosh", 0.5 if big else 0.18))
        if res == "plataforma" and k == SUCCESS:
            cues += [(ts + d, "thump", 0.7), (ts + d + 0.05, "ding", 0.9)]
        elif res != "plataforma":
            cues.append((ts + d, "pop_low", 0.7 if big else 0.25))
    cues += [(c["aprende"], "riser", 0.35), (c["pista_w"], "pop", 0.5), (c["fuerza"], "tick", 0.6),
             (c["angulo"], "tick", 0.6), (c["poquito"], "pop", 0.5), (c["baja"], "pop", 0.5),
             (c["red0"], "whoosh", 0.6), (c["millones"], "riser", 0.5), (c["cie0"], "whoosh_down", 0.5),
             (c["simul"] - 1.2, "whoosh", 0.4), (c["simul"] - 0.2, "ding", 0.6)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["per0"], "pulse": (c["rep0"], c["red0"]), "quiet": [(c["logra_hasta"] - 0.3, c["logra"])]}
