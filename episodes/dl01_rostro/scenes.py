"""Escenas — «¿Cómo sabe tu celular que eres tú?»

La misma cara recorre todo el video: celular → píxeles → números → comparación →
reglas que se rompen → una neurona que detecta bordes → capas (bordes → partes → huella) →
entrenamiento real (curva de error) → huellas que se ordenan por persona → celular.
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint, font, vignette, vband, spring, image, NEAREST, LINEAR, CUBIC
from reelforge.ease import (clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back,
                            in_out_cubic, out_quint, smooth, in_cubic)

TL = None; EP = {}; CHUNKS = []; CUE = {}; D = {}
AMBER = (1.0, 0.72, 0.3); GREEN = (0.24, 0.96, 0.65); BLUE = (0.35, 0.55, 1.0)
PCOL = [C.CYAN, C.VIOLET, C.PINK, AMBER, GREEN, BLUE, C.WHITE, (0.55, 0.6, 0.7)]


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def rgba(a):
    if a.ndim == 2: a = np.dstack([a, a, a])
    a8 = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return np.dstack([a8, np.full(a.shape[:2], 255, np.uint8)])


def img(P, key, x0, y0, x1, y1, a=1.0, nearest=False, src=None):
    im = image(key, D["rgba"][key])
    p = skia.Paint(); p.setAlphaf(clamp(a))
    if src is None:
        P.c.drawImageRect(im, skia.Rect(x0, y0, x1, y1), NEAREST if nearest else CUBIC, p)
    else:
        P.c.drawImageRect(im, skia.Rect(*src), skia.Rect(x0, y0, x1, y1), NEAREST if nearest else CUBIC, p)


def rounded_img(P, key, x0, y0, x1, y1, r=24, a=1.0, nearest=False):
    P.c.save()
    rr = skia.RRect.MakeRectXY(skia.Rect(x0, y0, x1, y1), r, r)
    P.c.clipRRect(rr, doAntiAlias=True)
    img(P, key, x0, y0, x1, y1, a, nearest)
    P.c.restore()


def headline(P, a, s=1.0, l1="¿CÓMO SABE", l2="QUE ERES TÚ?", col=C.CYAN):
    if a <= 0: return
    with P.transform(0, 0, s, cx=540, cy=420):
        P.text(l1, 540, 390, 88, C.WHITE, a, face=C.FONT_BLACK)
        P.text(l2, 540, 488, 96, col, a, face=C.FONT_BLACK, glow=0.5)


# =============================================================== celular
def phone(P, t, a, key, s=1.0, cy=1000, unlock=0.0, scan=None):
    if a <= 0: return
    W_, H_ = 500, 860
    cx = 540
    with P.layer(a):
        with P.transform(0, 0, s, cx=cx, cy=cy):
            x0, y0, x1, y1 = cx - W_ / 2, cy - H_ / 2, cx + W_ / 2, cy + H_ / 2
            P.rect(x0 - 6, y0 + 12, x1 + 6, y1 + 28, (0, 0, 0), 0.6, radius=62, blur=26)
            P.rect(x0, y0, x1, y1, (0.07, 0.08, 0.11), 1, radius=60)
            P.rect(x0, y0, x1, y1, C.WHITE, 0.14, stroke=2, radius=60)
            sx0, sy0, sx1, sy1 = x0 + 16, y0 + 16, x1 - 16, y1 - 16
            P.rect(sx0, sy0, sx1, sy1, (0.10, 0.12, 0.18), 1, radius=46)
            # vista de cámara frontal: la cara
            fs = 400
            fx0, fy0 = cx - fs / 2, cy - fs / 2 + 30
            rounded_img(P, key, fx0, fy0, fx0 + fs, fy0 + fs, r=200)
            # esquinas de escaneo
            col = lerp_c(C.WHITE, C.CYAN, unlock)
            L = 46; m = 12
            for (qx, qy, sx_, sy_) in ((fx0 - m, fy0 - m, 1, 1), (fx0 + fs + m, fy0 - m, -1, 1),
                                       (fx0 - m, fy0 + fs + m, 1, -1), (fx0 + fs + m, fy0 + fs + m, -1, -1)):
                P.line(qx, qy, qx + sx_ * L, qy, col, 1, w=6); P.line(qx, qy, qx, qy + sy_ * L, col, 1, w=6)
            if scan is not None and 0 < scan < 1:
                yy = fy0 + fs * scan
                P.line(fx0, yy, fx0 + fs, yy, C.CYAN, 0.9, w=4, glow=True)
            # candado
            lx, ly = cx, y0 + 110
            open_ = out_back(unlock)
            P.rect(lx - 26, ly - 4, lx + 26, ly + 34, col, 1, radius=7)
            P.c.save(); P.c.translate(lx + 13 * open_, ly - 14 * open_)
            P.c.drawArc(skia.Rect(-17, -24, 17, 10), 180, 180, False, paint(col, 1, stroke=6))
            P.line(-17, -7, -17, 2, col, 1, w=6); P.line(17, -7, 17, 2 + 10 * (1 - open_), col, 1, w=6)
            P.c.restore()
            P.text("Desbloqueado" if unlock > 0.5 else "Mirando...", cx, y1 - 90, 34,
                   C.CYAN if unlock > 0.5 else C.GRAY, 1, face=C.FONT_BOLD)


# =============================================================== píxeles y números
def pixeles(P, t):
    c = CUE
    a = window(t, c["px0"] - 0.1, c["dif0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    S = 760; x0, y0 = 540 - S / 2, 560
    u = prog(t, c["px0"], c["px0"] + 1.0, in_out_cubic)          # color → píxeles grises
    with P.layer(a):
        img(P, "base", x0, y0, x0 + S, y0 + S, 1 - u)
        img(P, "base32", x0, y0, x0 + S, y0 + S, u, nearest=True)
        g = prog(t, c["px0"] + 0.6, c["px0"] + 1.2)
        if g > 0:
            cell = S / 32
            for k in range(33):
                P.line(x0 + k * cell, y0, x0 + k * cell, y0 + S, C.BG, 0.5 * g, w=1.2, cap="butt")
                P.line(x0, y0 + k * cell, x0 + S, y0 + k * cell, C.BG, 0.5 * g, w=1.2, cap="butt")
        # números: lupa sobre el ojo
        an = prog(t, c["numeros"] - 0.2, c["numeros"] + 0.4)
        if an > 0:
            g32 = D["base32"]
            r0, c0 = 11, 8
            cell = S / 32
            lx0, ly0 = x0 + c0 * cell, y0 + r0 * cell
            P.rect(lx0 - 4, ly0 - 4, lx0 + 6 * cell + 4, ly0 + 6 * cell + 4, C.CYAN, an, stroke=4, radius=6)
            # panel ampliado
            px0, py0, pc = 150, 1050, 130
            for i in range(6):
                for j in range(6):
                    v = g32[r0 + i, c0 + j]
                    xx, yy = px0 + j * pc, py0 + i * 0
            Z = 6; zc = 78
            zx0, zy0 = 540 - Z * zc / 2, 690
            P.rect(zx0 - 10, zy0 - 10, zx0 + Z * zc + 10, zy0 + Z * zc + 10, C.BG, 0.92 * an, radius=16)
            for i in range(Z):
                for j in range(Z):
                    v = float(g32[r0 + i, c0 + j])
                    P.rect(zx0 + j * zc + 2, zy0 + i * zc + 2, zx0 + (j + 1) * zc - 2, zy0 + (i + 1) * zc - 2, (v, v, v), an, radius=6)
                    P.text(str(int(v * 255)), zx0 + j * zc + zc / 2, zy0 + i * zc + zc / 2 + 10, 26,
                           C.INK if v > 0.5 else C.WHITE, an * prog(t, c["numeros"] + 0.1 * (i + j) / 3, c["numeros"] + 0.3 + 0.1 * (i + j) / 3),
                           face=C.FONT_BOLD)
            P.text("0 = negro  ·  255 = blanco", 540, zy0 + Z * zc + 50, 28, C.GRAY, an, face=C.FONT_MED)


def comparar(P, t):
    c = CUE
    a = window(t, c["dif0"] - 0.1, c["reg0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    R = D["res"]
    with P.layer(a):
        S = 300
        # arriba: tú (antes); abajo: tú (nuevo look) y otra persona
        pos = {"base32": (540, 700), "new32": (290, 1060), "other32": (790, 1060)}
        labels = {"base32": ("tú", C.CYAN), "new32": ("tú, otro look", C.CYAN), "other32": ("otra persona", C.PINK)}
        for k, (cx, cy) in pos.items():
            ak = prog(t, c["dif0"] + (0 if k == "base32" else 0.5), c["dif0"] + (0.4 if k == "base32" else 0.9))
            img(P, k, cx - S / 2, cy - S / 2, cx + S / 2, cy + S / 2, ak, nearest=True)
            P.rect(cx - S / 2, cy - S / 2, cx + S / 2, cy + S / 2, labels[k][1], ak * 0.8, stroke=3, radius=4)
            P.text(labels[k][0], cx, cy - S / 2 - 18, 32, labels[k][1], ak, face=C.FONT_BOLD)
        # mapas de cambio: puntos que cambiaron
        ach = prog(t, c["todos"] - 0.3, c["todos"] + 0.5)
        for k, frac, key in (("new32", R["changed_frac_self"], "chg_self"), ("other32", R["changed_frac_other"], "chg_other")):
            cx, cy = pos[k]
            if ach > 0:
                img(P, key, cx - S / 2, cy - S / 2, cx + S / 2, cy + S / 2, 0.75 * ach, nearest=True)
                P.text(f"cambió el {int(round(frac * 100))} % de los puntos", cx, cy + S / 2 + 40, 28,
                       C.WHITE, ach * (1 - prog(t, c["otra"] - 0.3, c["otra"])), face=C.FONT_SEMI)
        # veredicto
        av = prog(t, c["otra"] - 0.2, c["otra"] + 0.4)
        if av > 0:
            P.line(540, 860, 790, 900, C.PINK, av, w=5, frac=av)
            P.rect(160, 1270 - 40, 920, 1270 + 18, C.BG, 0.9 * av, radius=26)
            P.text("comparando números: «se parece más» a otra persona", 540, 1260, 28, C.PINK, av, face=C.FONT_BOLD)


def reglas(P, t):
    c = CUE
    a = window(t, c["reg0"] - 0.1, c["neu0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    S = 600; x0, y0 = 540 - S / 2, 580
    rompe = prog(t, c["rompen"] - 0.6, c["rompen"])
    with P.layer(a):
        img(P, "base", x0, y0, x0 + S, y0 + S, 1 - rompe)
        img(P, "new", x0, y0, x0 + S, y0 + S, rompe)
        # medidas a mano (coordenadas normalizadas de la persona 0)
        meas = [((0.35, 0.43), (0.65, 0.43), "distancia entre ojos", c["ojos"]),
                ((0.50, 0.44), (0.50, 0.56), "largo de nariz", c["nariz"]),
                ((0.36, 0.77), (0.64, 0.77), "ancho de boca", c["boca"])]
        for k, ((ax, ay), (bx, by), lab, tt) in enumerate(meas):
            am = prog(t, tt - 0.2, tt + 0.3)
            if am <= 0: continue
            jit = 14 * rompe * math.sin(t * 13 + k * 2)
            col = lerp_c(C.CYAN, C.PINK, rompe)
            X = lambda u: x0 + u * S; Y = lambda v: y0 + v * S
            P.line(X(ax), Y(ay) + jit, X(bx), Y(by) - jit, col, am, w=5, frac=am)
            P.circle(X(ax), Y(ay) + jit, 8, col, am); P.circle(X(bx), Y(by) - jit, 8, col, am)
            P.text(lab, 540, 1240 + k * 0, 0, col, 0)
        lab_y = [1225, 1265, 1305]
        P.text("regla: medir ojos, nariz y boca", 540, 1236, 32, C.CYAN, prog(t, c["ojos"], c["ojos"] + 0.4) * (1 - rompe), face=C.FONT_SEMI)
        if rompe > 0:
            P.text("✗", 860, 700, 120, C.PINK, out_back(rompe), face=C.FONT_BLACK, glow=0.5)
            P.text("sombras · lentes · ángulos", 540, 1236, 32, C.PINK, rompe, face=C.FONT_SEMI)


# =============================================================== la neurona, paso a paso
EDGE_RC, FLAT_RC = (48, 42), (70, 70)          # pedacitos reales de la cara (fila, columna en 128×128)
WTS = np.array([[-1, 0, 1]] * 3, float)


def patch_at(rc):
    g = D["gray128"]; r, c_ = rc
    return np.round(np.array([[g[r + i * 4:r + i * 4 + 4, c_ + j * 4:c_ + j * 4 + 4].mean() for j in range(3)]
                              for i in range(3)]), 1)


def fmt1(v):
    return f"{v:.1f}".replace(".", ",").replace("-", "−")


def grid3(P, x0, y0, vals, a, cs=68, kind="luz", hi_cols=None):
    for i in range(3):
        for j in range(3):
            v = vals[i, j]
            X0, Y0 = x0 + j * cs, y0 + i * cs
            if kind == "luz":
                col = (v, v, v); tc = C.INK if v > 0.5 else C.WHITE; txt = fmt1(v)
            elif kind == "peso":
                col = C.CYAN if v > 0 else (C.VIOLET if v < 0 else C.DIM); tc = C.WHITE
                txt = f"{int(v):+d}" if v else "0"
            else:
                col = C.CYAN if v > 0.05 else (C.VIOLET if v < -0.05 else C.DIM); tc = C.WHITE; txt = fmt1(v)
            P.rect(X0 + 3, Y0 + 3, X0 + cs - 3, Y0 + cs - 3, col, a * (0.95 if kind == "luz" else 0.85), radius=8)
            if hi_cols and j in hi_cols:
                P.rect(X0 + 1, Y0 + 1, X0 + cs - 1, Y0 + cs - 1, C.WHITE, a * hi_cols[j], stroke=4, radius=9)
            P.text(txt, X0 + cs / 2, Y0 + cs / 2 + 9, 24 if cs >= 60 else 16, tc, a, face=C.FONT_BOLD)


def neurona(P, t):
    c = CUE
    a = window(t, c["neu0"] - 0.1, c["b0"] + 0.5, 0.5, 0.5)
    if a <= 0: return
    # ¿pedacito del borde o de la mejilla?
    mv = prog(t, c["s_par"] - 0.3, c["s_par"] + 0.4, in_out_cubic)
    pe, pf = patch_at(EDGE_RC), patch_at(FLAT_RC)
    vals = pe * (1 - mv) + pf * mv
    rc = (lerp(EDGE_RC[0], FLAT_RC[0], mv), lerp(EDGE_RC[1], FLAT_RC[1], mv))
    with P.layer(a):
        # la cara y la ventana: QUÉ ENTRA
        S = 330; fx0, fy0 = 540 - S / 2, 545
        img(P, "gray128", fx0, fy0, fx0 + S, fy0 + S, 1)
        cell = S / 128
        aw = prog(t, c["n_pedacito"] - 0.3, c["n_pedacito"] + 0.2)
        wx0, wy0 = fx0 + rc[1] * cell, fy0 + rc[0] * cell
        P.rect(wx0, wy0, wx0 + 12 * cell, wy0 + 12 * cell, C.CYAN, aw, stroke=4, radius=3)
        y0 = 960; cs = 78
        xs = [40, 330, 620]
        # puntos (luz)
        al = prog(t, c["n_luz"] - 0.4, c["n_luz"] + 0.2)
        if al > 0:
            P.line(wx0 + 6 * cell, wy0 + 12 * cell, xs[0] + 1.5 * cs, y0 - 50, C.CYAN, al * 0.7, w=3)
            P.text("ENTRA: luz", xs[0] + 1.5 * cs, y0 - 22, 26, C.WHITE, al, face=C.FONT_BOLD)
            grid3(P, xs[0], y0, vals, al, cs, "luz")
        # pesos
        ap = prog(t, c["p_peso"] - 0.3, c["p_peso"] + 0.3)
        if ap > 0:
            P.text("×", xs[1] - 38, y0 + 1.6 * cs, 50, C.WHITE, ap, face=C.FONT_BOLD)
            hp = pulse(t, c["p_pos"], 1.4); hn = pulse(t, c["p_neg"], 1.4)
            grid3(P, xs[1], y0, WTS, ap, cs, "peso", hi_cols={2: hp, 0: hn})
            P.text("pesos", xs[1] + 1.5 * cs, y0 - 22, 26, C.WHITE, ap, face=C.FONT_BOLD)
            P.text("+ quiere luz", xs[1] + 1.5 * cs, y0 + 3 * cs + 34, 24, C.CYAN, prog(t, c["p_pos"] - 0.2, c["p_pos"] + 0.3), face=C.FONT_SEMI)
            P.text("− quiere oscuridad", xs[1] + 1.5 * cs, y0 + 3 * cs + 64, 24, C.VIOLET, prog(t, c["p_neg"] - 0.2, c["p_neg"] + 0.3), face=C.FONT_SEMI)
        # productos y suma
        am = prog(t, c["s_mult"] - 0.2, c["s_mult"] + 0.4)
        if am > 0:
            P.text("=", xs[2] - 38, y0 + 1.6 * cs, 50, C.WHITE, am, face=C.FONT_BOLD)
            grid3(P, xs[2], y0, vals * WTS, am, cs, "prod")
            P.text("cada punto × su peso", xs[2] + 1.5 * cs, y0 - 22, 24, C.WHITE, am, face=C.FONT_BOLD)
        asum = prog(t, c["s_suma"] - 0.2, c["s_suma"] + 0.3)
        total = float((vals * WTS).sum())
        if asum > 0:
            P.text("suma:", xs[2] - 10, y0 + 3 * cs + 52, 30, C.WHITE, asum, face=C.FONT_SEMI, align="left")
            P.text(fmt1(total if total > 0.04 or total < -0.04 else 0.0), xs[2] + 3 * cs, y0 + 3 * cs + 52, 40, C.WHITE, asum,
                   face=C.FONT_BLACK, align="right")
        # la neurona: QUÉ SALE
        an = prog(t, c["s_solo"] - 0.3, c["s_solo"] + 0.2)
        if an > 0:
            nx, ny = 540, 920 - 0
            nx, ny = 990, y0 + 1.5 * cs
            P.arrow(xs[2] + 3 * cs + 6, ny, nx - 50, ny, C.WHITE, an, w=4, head=16)
            on = clamp(total / 1.2) * prog(t, c["s_enc"] - 0.3, c["s_enc"] + 0.2)
            P.circle(nx, ny, 44, C.BG2, an)
            if on > 0.05: P.glow_circle(nx, ny, 44, C.CYAN, an * on, spread=1.9)
            P.circle(nx, ny, 44, C.CYAN, an, stroke=4)
            P.text("SALE:", nx, ny + 80, 24, C.WHITE, an, face=C.FONT_BOLD)
            P.text("1 número", nx, ny + 108, 24, C.WHITE, an, face=C.FONT_BOLD)
            st = "encendida" if on > 0.5 else "apagada"
            P.text(st, nx, ny - 66, 26, C.CYAN if on > 0.5 else C.GRAY, an * prog(t, c["s_enc"] - 0.3, c["s_enc"] + 0.2), face=C.FONT_BOLD)


def barrido(P, t):
    c = CUE
    a = window(t, c["b0"] - 0.2, c["cap0"] + 0.4, 0.5, 0.4)
    if a <= 0: return
    with P.layer(a):
        S = 560; fx0, fy0 = 540 - S / 2, 600
        img(P, "gray128", fx0, fy0, fx0 + S, fy0 + S, 1)
        # los pesos de esta neurona como recordatorio
        grid3(P, 70, 610, WTS, prog(t, c["b0"], c["b0"] + 0.4), 40, "peso")
        P.text("busca:", 130, 790, 24, C.WHITE, prog(t, c["b_borde"] - 0.2, c["b_borde"] + 0.3), face=C.FONT_SEMI)
        P.text("oscuro → claro", 130, 820, 24, C.CYAN, prog(t, c["b_borde"] - 0.2, c["b_borde"] + 0.3), face=C.FONT_BOLD)
        scan = prog(t, c["b_pasamos"] - 0.2, c["b_pasamos"] + 2.4, lambda v: v)
        cell = S / 128
        if scan > 0:
            k = int(scan * 32 * 32)
            wr, wc = (k // 32) * 4, (k % 32) * 4
            P.c.save()
            P.c.clipRect(skia.Rect(fx0, fy0, fx0 + S, fy0 + S * clamp((wr + 4) / 128)))
            img(P, "edge_v", fx0, fy0, fx0 + S, fy0 + S, 1)
            P.c.restore()
            if scan < 1:
                P.rect(fx0 + wc * cell, fy0 + wr * cell, fx0 + (wc + 12) * cell, fy0 + (wr + 12) * cell, C.CYAN, 1, stroke=4, radius=3)
            P.text("donde se encendió la neurona", 540, fy0 + S + 40, 28, C.CYAN, prog(t, c["b_pasamos"] + 0.5, c["b_pasamos"] + 1.0),
                   face=C.FONT_SEMI)


# =============================================================== capas: lo que sale de una entra a la siguiente
def capas(P, t):
    c = CUE
    a = window(t, c["cap0"] - 0.1, c["apr0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    rowy = [600, 790, 990, 1170]
    hl = [pulse(t, c["c_luz"] + k * 0.75, 0.9) for k in range(4)]      # "de luz, a bordes, a partes, a huella"
    with P.layer(a):
        # fila 0: imagen
        img(P, "gray128", 540 - 65, rowy[0] - 65, 540 + 65, rowy[0] + 65, 1)
        P.text("imagen", 70, rowy[0] - 6, 26, C.WHITE, 1, face=C.FONT_BOLD, align="left")
        P.text("(luz)", 70, rowy[0] + 24, 24, C.GRAY, 1, face=C.FONT_MED, align="left")
        if hl[0] > 0: P.rect(540 - 72, rowy[0] - 72, 540 + 72, rowy[0] + 72, C.CYAN, hl[0], stroke=4, radius=6)
        # fila 1: capa 1 = 4 neuronas, cada una con sus pesos, y sus 4 mapas de salida
        a1 = prog(t, c["cap0"] + 0.1, c["cap0"] + 0.7)
        xs1 = [300, 460, 620, 780]
        pats = [np.array([[-1, 0, 1]] * 3), np.array([[-1] * 3, [0] * 3, [1] * 3]),
                np.array([[0, 1, 1], [-1, 0, 1], [-1, -1, 0]]), np.array([[1, 1, 0], [1, 0, -1], [0, -1, -1]])]
        maps1 = ["edge_v", "edge_h", "edge_d1", "edge_d2"]
        out1 = prog(t, c["c_mapas"] - 0.3, c["c_mapas"] + 0.4)
        for k, x in enumerate(xs1):
            if a1 <= 0: break
            P.line(540, rowy[0] + 66, x, rowy[1] - 62, C.VIOLET, a1 * 0.55, w=2)
            # la neurona (con su patrón de pesos) se transforma en su mapa de salida
            grid3(P, x - 30, rowy[1] - 30, pats[k], a1 * (1 - out1), 20, "peso")
            img(P, maps1[k], x - 60, rowy[1] - 60, x + 60, rowy[1] + 60, a1 * out1)
            P.rect(x - 60, rowy[1] - 60, x + 60, rowy[1] + 60, C.CYAN, a1 * (0.5 + hl[1]), stroke=2 + 3 * hl[1], radius=4)
        P.text("capa 1", 70, rowy[1] - 6, 26, C.WHITE, a1, face=C.FONT_BOLD, align="left")
        P.text("sale: bordes", 70, rowy[1] + 24, 24, C.CYAN, a1 * out1, face=C.FONT_SEMI, align="left")
        # fila 2: los mapas ENTRAN a la capa 2 → mapas de partes
        a2 = prog(t, c["c_entran"] - 0.2, c["c_entran"] + 0.5)
        xs2 = [380, 540, 700]
        flow = prog(t, c["c_entran"] - 0.2, c["c_entran"] + 1.2, lambda v: v)
        for x in xs2:
            for x1 in xs1:
                P.line(x1, rowy[1] + 62, x, rowy[2] - 62, C.VIOLET, a2 * 0.35, w=1.6)
                if 0 < flow < 1:          # pulsos que viajan de una capa a la otra
                    u = (flow * 1.4 - (x1 - 300) / 1600) % 1
                    P.circle(lerp(x1, x, u), lerp(rowy[1] + 62, rowy[2] - 62, u), 5, C.CYAN, a2)
        ap = prog(t, c["c_partes"] - 0.2, c["c_partes"] + 0.5)
        for k, (x, lab) in enumerate(zip(xs2, ["ojo", "nariz", "boca"])):
            if a2 <= 0: break
            P.circle(x, rowy[2], 26, C.BG2, a2 * (1 - ap)); P.circle(x, rowy[2], 26, C.VIOLET, a2 * (1 - ap), stroke=3)
            img(P, f"part_{k}", x - 60, rowy[2] - 60, x + 60, rowy[2] + 60, a2 * ap)
            P.rect(x - 60, rowy[2] - 60, x + 60, rowy[2] + 60, C.CYAN, a2 * (0.5 + hl[2]), stroke=2 + 3 * hl[2], radius=4)
            P.text(lab, x, rowy[2] + 88, 24, C.GRAY, ap, face=C.FONT_MED)
        P.text("capa 2", 70, rowy[2] - 6, 26, C.WHITE, a2, face=C.FONT_BOLD, align="left")
        P.text("sale: partes", 70, rowy[2] + 24, 24, C.CYAN, a2 * ap, face=C.FONT_SEMI, align="left")
        # fila 3: huella (salida real de la red entrenada para tu foto)
        a3 = prog(t, c["c_huella"] - 0.3, c["c_huella"] + 0.4)
        if a3 > 0:
            e = D["emb_base"]; e = e / (e.max() + 1e-9)
            n = len(e); bw = 19
            hx0 = 590 - n * bw / 2
            for x in xs2:
                P.line(x, rowy[2] + 62, 590, rowy[3] - 70, C.VIOLET, a3 * 0.35, w=1.6)
            for k in range(n):
                h = 80 * e[k] * prog(t, c["c_huella"] + 0.02 * k, c["c_huella"] + 0.02 * k + 0.3)
                P.rect(hx0 + k * bw + 2, rowy[3] + 40 - h, hx0 + (k + 1) * bw - 2, rowy[3] + 40, C.CYAN, a3, radius=3)
            if hl[3] > 0: P.rect(hx0 - 10, rowy[3] - 50, hx0 + n * bw + 10, rowy[3] + 50, C.CYAN, hl[3], stroke=4, radius=8)
            P.text("capa 3", 70, rowy[3] - 6, 26, C.WHITE, a3, face=C.FONT_BOLD, align="left")
            P.text("sale: huella", 70, rowy[3] + 24, 24, C.CYAN, a3, face=C.FONT_SEMI, align="left")
        ap = prog(t, c["profundo"] - 0.3, c["profundo"] + 0.3)
        P.pill("APRENDIZAJE PROFUNDO", 540, 505, 36, C.VIOLET, out_back(ap))
        P.text("ilustración de lo que suelen aprender las capas", 540, 1265, 22, C.GRAY, a, face=C.FONT_MED)


# =============================================================== aprender de los errores
def aprender(P, t):
    c = CUE
    a = window(t, c["apr0"] - 0.1, c["res0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    sl = D["step_losses"]
    with P.layer(a):
        # flujo de fotos de entrenamiento + adivinanza
        af = prog(t, c["miles"] - 0.3, c["miles"] + 0.3)
        if af > 0:
            k = int((t - c["miles"]) * 5) if t > c["miles"] else 0
            sample = D["samples"][k % len(D["samples"])]
            img(P, sample, 120, 600, 340, 820, af)
            right = (k % 3 != 0) or t > c["reduce"] + 1.0
            P.text("¿persona?", 230, 860, 28, C.WHITE, af, face=C.FONT_SEMI)
            P.text("✓" if right else "✗", 230, 930, 60, C.CYAN if right else C.PINK, af, face=C.FONT_BLACK)
        # curva real de error
        ac = prog(t, c["error"] - 0.3, c["error"] + 0.3)
        if ac > 0:
            gx0, gx1, gy0, gy1 = 420, 980, 600, 900
            P.text("error de la red (entrenamiento real)", 700, 580, 26, C.WHITE, ac, face=C.FONT_SEMI)
            P.line(gx0, gy1, gx1, gy1, C.DIM, ac, w=3); P.line(gx0, gy0, gx0, gy1, C.DIM, ac, w=3)
            n = 400
            frac = prog(t, c["error"], c["cerro"] + 1.5, lambda v: v)
            m = min(n, max(2, int(n * frac)))
            ys = np.convolve(sl[:n], np.ones(5) / 5, mode="same")
            emax = ys[:20].max()
            pth = skia.Path()
            for i in range(m):
                x = lerp(gx0, gx1, i / (n - 1)); y = lerp(gy1, gy0, min(1, ys[i] / emax))
                pth.moveTo(x, y) if i == 0 else pth.lineTo(x, y)
            P.c.drawPath(pth, paint(C.PINK, ac, stroke=4))
            P.text("pasos de ajuste →", gx1, gy1 + 36, 24, C.GRAY, ac, face=C.FONT_MED, align="right")
        # el cerro a ciegas: descenso de gradiente
        ah = prog(t, c["cerro"] - 0.4, c["cerro"] + 0.2)
        if ah > 0:
            hx0, hx1, hy = 140, 940, 1210
            f = lambda u: 0.35 + 0.65 * (u - 0.72) ** 2 / 0.52 + 0.05 * math.sin(u * 9)
            pth = skia.Path()
            for i in range(101):
                u = i / 100; x = lerp(hx0, hx1, u); y = hy - 260 * (1 - f(u)) * 0 - 240 * (f(u))
                y = hy - 240 * f(u) + 0
                pth.moveTo(x, y) if i == 0 else pth.lineTo(x, y)
            P.c.drawPath(pth, paint(C.VIOLET, ah, stroke=5))
            # pelota que baja por pasos (derivada numérica)
            u = 0.06; steps = int(clamp((t - c["cerro"]) / 2.6) * 22)
            for _ in range(steps):
                d = (f(u + 1e-3) - f(u - 1e-3)) / 2e-3
                u = clamp(u - 0.035 * d / max(0.4, abs(d)) * min(1, abs(d)), 0, 1)
            bx, by = lerp(hx0, hx1, u), hy - 240 * f(u)
            P.glow_circle(bx, by - 18, 16, C.CYAN, ah)
            P.text("pesos", 540, hy + 40, 26, C.GRAY, ah, face=C.FONT_MED)
            P.text("error", hx0 - 10, hy - 250, 26, C.GRAY, ah, face=C.FONT_MED, align="left")


# =============================================================== resultado: huellas ordenadas
def resultado(P, t):
    c = CUE
    a = window(t, c["res0"] - 0.1, c["cie0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    Pp, Pe, Y = D["Ppix"], D["Pemb"], D["Yte"]
    u = prog(t, c["ordenan"] - 0.4, c["ordenan"] + 1.4, in_out_cubic)
    box = (150, 600, 930, 1180)
    with P.layer(a):
        P.rect(box[0] - 30, box[1] - 30, box[2] + 30, box[3] + 30, C.BG2, 0.85, radius=30)
        P.text("cada punto = una foto", 540, 570, 28, C.GRAY, 1, face=C.FONT_MED)
        lab = "ordenadas por píxeles" if u < 0.5 else "ordenadas por huella"
        P.text(lab, 540, 1240, 30, C.WHITE, 1, face=C.FONT_SEMI)
        n = len(Y)
        for i in range(n + 1):
            p = lerp(Pp[i], Pe[i], u) if u < 1 else Pe[i]
            x = lerp(box[0], box[2], (p[0] + 1) / 2); y = lerp(box[1], box[3], (p[1] + 1) / 2)
            if i < n:
                P.circle(x, y, 9, PCOL[Y[i]], 0.85)
            else:
                an = prog(t, c["nueva"] - 0.3, c["nueva"] + 0.3)
                if an > 0:
                    P.glow_circle(x, y, 16, C.WHITE, an)
                    P.circle(x, y, 26 + 10 * pulse(t, c["nueva"] + 0.2, 0.8), C.CYAN, an, stroke=4)
                    img(P, "new", x + 30, y - 120, x + 150, y, an)
                    P.text("tu foto nueva ✓", x + 90, y + 40, 28, C.CYAN, an, face=C.FONT_BOLD)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D
    TL, EP, D = tl, episode, data
    D["rgba"] = {}
    for k in ("base", "new", "other"):
        D["rgba"][k] = rgba(D[k])
    for k in ("base32", "new32", "other32"):
        D["rgba"][k] = rgba(D[k])
    base32 = D["base32"]
    for k, key in (("new32", "chg_self"), ("other32", "chg_other")):
        ch = np.abs(D[k] - base32) > 0.05
        m = np.zeros(base32.shape + (4,), np.uint8)
        m[ch] = [255, 77, 141, 200]
        D["rgba"][key] = m
    g = D["base"].mean(2)
    from PIL import Image
    g128 = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).resize((128, 128), Image.LANCZOS)).astype(np.float32) / 255
    D["gray128"] = g128; D["rgba"]["gray128"] = rgba(g128)
    from scipy.ndimage import convolve
    ks = {"edge_v": [[-1, 0, 1]] * 3, "edge_h": [[-1, -1, -1], [0, 0, 0], [1, 1, 1]],
          "edge_d1": [[0, 1, 1], [-1, 0, 1], [-1, -1, 0]], "edge_d2": [[1, 1, 0], [1, 0, -1], [0, -1, -1]]}
    for key, k in ks.items():
        e = np.abs(convolve(g128, np.array(k, float)))
        e = np.clip(e / (np.percentile(e, 99) + 1e-6), 0, 1)
        col = np.dstack([e * 0.0, e * 0.85, e * 1.0])
        D["rgba"][key] = rgba(col)
    D["emb_base"] = D["emb3"][0]
    yy, xx = np.mgrid[0:64, 0:64] / 64
    blobs = [[(0.35, 0.43), (0.65, 0.43)], [(0.49, 0.51)], [(0.5, 0.77)]]
    g64 = np.asarray(Image.fromarray((g128 * 255).astype(np.uint8)).resize((64, 64))).astype(np.float32) / 255
    for k, bl in enumerate(blobs):
        m = sum(np.exp(-((xx - bx) ** 2 + (yy - by) ** 2) / (2 * 0.05 ** 2)) for bx, by in bl)
        m = np.clip(m, 0, 1)
        col = np.dstack([g64 * 0.18, g64 * 0.18 + m * 0.85, g64 * 0.22 + m])
        D["rgba"][f"part_{k}"] = rgba(np.clip(col, 0, 1))
    # fotos de entrenamiento (muestras) para el flujo
    import experiment as X
    rng = np.random.default_rng(9)
    D["samples"] = []
    for k in range(24):
        pid = int(rng.integers(0, 8))
        im = X.render(pid, size=128, color=True, **X.sample_variation(rng))
        key = f"s{k}"; D["rgba"][key] = rgba(im); D["samples"].append(key)

    c = {}
    c["pelo"] = T("hook", "pelo"); c["desbloq"] = T("hook", "desbloquea"); c["tu"] = T("hook", "tú")
    c["px0"] = T("pixeles"); c["numeros"] = T("pixeles", "números")
    c["dif0"] = T("dificil"); c["todos"] = T("dificil", "todos"); c["otra"] = T("dificil", "otra")
    c["reg0"] = T("reglas"); c["ojos"] = T("reglas", "ojos"); c["nariz"] = T("reglas", "nariz"); c["boca"] = T("reglas", "boca")
    c["rompen"] = T("reglas", "rompen")
    c["neu0"] = T("neurona"); c["n_entra"] = T("neurona", "entra"); c["n_pedacito"] = T("neurona", "pedacito")
    c["n_luz"] = T("neurona", "luz")
    c["p0"] = T("pesos"); c["p_peso"] = T("pesos", "peso"); c["p_pos"] = T("pesos", "positivo"); c["p_neg"] = T("pesos", "Negativo")
    c["s_mult"] = T("suma", "Multiplica"); c["s_suma"] = T("suma", "suma"); c["s_solo"] = T("suma", "solo")
    c["s_enc"] = T("suma", "enciende"); c["s_par"] = T("suma", "pareja")
    c["b0"] = T("barrido"); c["b_borde"] = T("barrido", "borde"); c["b_pasamos"] = T("barrido", "pasamos")
    c["cap0"] = T("capas"); c["c_mapas"] = T("capas", "mapas"); c["c_entran"] = T("capas", "entran")
    c["c_partes"] = T("capas", "partes"); c["c_huella"] = T("capas", "huella"); c["c_luz"] = T("capas", "luz")
    c["profundo"] = T("capas", "profundo")
    c["apr0"] = T("aprender"); c["miles"] = T("aprender", "miles"); c["error"] = T("aprender", "error")
    c["reduce"] = T("aprender", "reducirlo"); c["cerro"] = T("aprender", "cerro")
    c["res0"] = T("resultado"); c["ordenan"] = T("resultado", "ordenan"); c["nueva"] = T("resultado", "nueva")
    c["cie0"] = T("cierre"); c["mirar"] = T("cierre", "mirar")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    P.background(t, accent=0.25 * window(t, c["res0"], c["cie0"], 0.5, 0.5))
    # celular: inicio y cierre
    a_ph = (1 - prog(t, c["px0"] - 0.3, c["px0"] + 0.4)) + prog(t, c["cie0"] - 0.2, c["cie0"] + 0.5)
    key = "base" if t < c["pelo"] + 0.1 else "new"
    u1 = prog(t, 0.6, 1.4) * (1 - prog(t, c["pelo"], c["pelo"] + 0.2))
    u2 = prog(t, c["desbloq"] - 0.2, c["desbloq"] + 0.4)
    unlock = u1 if t < c["pelo"] + 0.2 else u2
    if t > c["cie0"] - 0.3: unlock = prog(t, c["cie0"] + 0.4, c["cie0"] + 1.0)
    scan = prog(t, 0.05, 0.9) if t < 1 else (prog(t, c["pelo"] + 0.2, c["desbloq"] - 0.1) if t < c["desbloq"] + 0.5 else None)
    s_ph = lerp(1.0, 1.6, prog(t, c["px0"] - 0.3, c["px0"] + 0.4, in_cubic)) if t < c["cie0"] - 0.3 else \
        lerp(0.9, 1.0, out_cubic(prog(t, c["cie0"] - 0.2, c["cie0"] + 0.6)))
    phone(P, t, clamp(a_ph), key, s_ph, unlock=unlock, scan=scan)
    headline(P, clamp(1 - prog(t, c["px0"] - 0.5, c["px0"] - 0.1) + prog(t, c["cie0"], c["cie0"] + 0.4)),
             1.0 + 0.1 * (1 - out_back(prog(t, 0, 0.35))))
    pixeles(P, t)
    comparar(P, t)
    reglas(P, t)
    neurona(P, t)
    barrido(P, t)
    capas(P, t)
    aprender(P, t)
    resultado(P, t)
    ad = window(t, c["dif0"], c["cie0"], 0.4, 0.4)
    P.text("Simulación propia con rostros sintéticos · los sistemas reales usan sensores y redes de cada fabricante",
           540, 1300, 21, C.GRAY, ad * 0.9, face=C.FONT_MED)
    vignette(P, 0.45)
    vband(P, 1240, C.H, 0.0, 0.85)
    P.circle(C.SAFE_LEFT + 10, 262, 8, C.CYAN, 1)
    P.text(EP["tag"], C.SAFE_LEFT + 34, 273, 26, C.WHITE, 0.85, face=C.FONT_BOLD, align="left", tracking=2)
    SUB.draw(P, CHUNKS, t)
    P.rect(0, C.H - 8, C.W * t / TL.duration, C.H, C.CYAN, 0.8)


def draw_cover(P, t=0.0):
    P.background(1.0, accent=0.6)
    phone(P, 3.0, 1.0, "new", 0.95, cy=1040, unlock=1.0)
    P.text("¿CÓMO SABE TU CELULAR", 540, 380, 74, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("QUE ERES TÚ?", 540, 480, 96, C.CYAN, 1, face=C.FONT_BLACK, glow=0.5)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.5), (0.05, "riser", 0.3), (1.2, "ding", 0.6), (c["desbloq"] + 0.1, "ding", 0.8),
            (c["px0"] - 0.3, "whoosh", 0.6), (c["numeros"], "pop", 0.5), (c["dif0"], "whoosh", 0.5),
            (c["todos"], "pop_low", 0.6), (c["otra"], "thump", 0.6), (c["reg0"], "whoosh", 0.5),
            (c["ojos"], "pop", 0.4), (c["nariz"], "pop", 0.4), (c["boca"], "pop", 0.4), (c["rompen"], "pop_low", 0.7),
            (c["neu0"], "whoosh", 0.5), (c["n_luz"], "pop", 0.4), (c["p_peso"], "pop", 0.4), (c["s_mult"], "pop", 0.4),
            (c["s_suma"], "pop", 0.5), (c["s_enc"], "ding", 0.6), (c["s_par"], "pop_low", 0.5),
            (c["b0"], "whoosh", 0.5), (c["b_pasamos"], "riser", 0.4),
            (c["cap0"], "whoosh", 0.5), (c["c_mapas"], "pop", 0.5), (c["c_entran"], "whoosh_down", 0.4),
            (c["c_partes"], "pop", 0.5), (c["c_huella"], "pop", 0.5), (c["profundo"], "swell", 0.7),
            (c["apr0"], "whoosh", 0.5), (c["cerro"], "whoosh_down", 0.4),
            (c["res0"], "whoosh", 0.5), (c["ordenan"], "riser", 0.5), (c["nueva"] + 0.2, "ding", 0.8),
            (c["cie0"], "whoosh_down", 0.5), (c["cie0"] + 0.7, "ding", 0.7), (c["mirar"], "swell", 0.5)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["neu0"], "pulse": (c["apr0"], c["cie0"]),
            "quiet": [(c["dif0"], c["reg0"])]}
