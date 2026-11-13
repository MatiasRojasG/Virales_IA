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


# =============================================================== la neurona
def neurona(P, t):
    c = CUE
    a = window(t, c["neu0"] - 0.1, c["cap0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    g = D["gray128"]
    with P.layer(a):
        # cara arriba con ventana que recorre (al detectar bordes)
        S = 380; fx0, fy0 = 540 - S / 2, 560
        img(P, "gray128", fx0, fy0, fx0 + S, fy0 + S, 1)
        # mapa de bordes que se pinta a medida que la ventana recorre
        tb = c["bordes"]
        scan = prog(t, tb - 0.3, tb + 2.2, lambda v: v)
        # ventana en (r, c) del recorrido
        if t < tb - 0.3:
            wr, wc = 56, 40          # junto al borde del ojo
        else:
            k = int(scan * 32 * 32)
            wr, wc = (k // 32) * 4, (k % 32) * 4
        cell = S / 128
        P.rect(fx0 + wc * cell, fy0 + wr * cell, fx0 + (wc + 12) * cell, fy0 + (wr + 12) * cell, C.CYAN, 1, stroke=4, radius=4)
        # tres pasos: puntos × pesos → suma → se enciende
        ab = prog(t, c["peso"] - 0.4, c["peso"] + 0.2)
        if ab > 0:
            yb = 1040
            # parche de 3x3 (promedio de bloques de la ventana)
            patch = np.array([[g[wr + i * 4:wr + i * 4 + 4, wc + j * 4:wc + j * 4 + 4].mean() for j in range(3)] for i in range(3)])
            Wt = np.array([[-1, 0, 1]] * 3, float)
            cs = 56
            px0 = 120
            for i in range(3):
                for j in range(3):
                    v = patch[i, j]
                    P.rect(px0 + j * cs, yb + i * cs, px0 + (j + 1) * cs - 4, yb + (i + 1) * cs - 4, (v, v, v), ab, radius=6)
            P.text("puntos", px0 + 1.5 * cs, yb - 18, 26, C.WHITE, ab, face=C.FONT_SEMI)
            P.text("×", px0 + 3 * cs + 30, yb + 1.6 * cs, 50, C.WHITE, ab, face=C.FONT_BOLD)
            wx0 = px0 + 3 * cs + 70
            for i in range(3):
                for j in range(3):
                    w = Wt[i, j]
                    col = C.CYAN if w > 0 else (C.VIOLET if w < 0 else C.DIM)
                    P.rect(wx0 + j * cs, yb + i * cs, wx0 + (j + 1) * cs - 4, yb + (i + 1) * cs - 4, col, ab * (0.9 if w else 0.5), radius=6)
                    P.text(f"{int(w):+d}" if w else "0", wx0 + j * cs + cs / 2 - 2, yb + i * cs + cs / 2 + 8, 22, C.WHITE, ab, face=C.FONT_BOLD)
            P.text("pesos", wx0 + 1.5 * cs, yb - 18, 26, C.WHITE, ab, face=C.FONT_SEMI)
            asum = prog(t, c["suma"] - 0.3, c["suma"] + 0.2)
            val = float((patch * Wt).sum())
            P.text("→", wx0 + 3 * cs + 34, yb + 1.6 * cs, 50, C.WHITE, asum, face=C.FONT_BOLD)
            P.text("suma", wx0 + 3 * cs + 120, yb - 18, 26, C.WHITE, asum, face=C.FONT_SEMI)
            P.text(f"{val:+.2f}".replace(".", ","), wx0 + 3 * cs + 120, yb + 1.6 * cs + 12, 34, C.WHITE, asum, face=C.FONT_BOLD)
            aen = prog(t, c["enciende"] - 0.3, c["enciende"] + 0.2)
            on = clamp(abs(val) / 0.6)
            nx, ny = 940, yb + 1.5 * cs
            P.text("→", 860, yb + 1.6 * cs, 50, C.WHITE, aen, face=C.FONT_BOLD)
            P.circle(nx, ny, 46, C.BG2, aen)
            if on > 0.05:
                P.glow_circle(nx, ny, 46, C.CYAN, aen * on, spread=1.8)
            P.circle(nx, ny, 46, C.CYAN, aen, stroke=4)
            P.text("neurona", nx, ny + 84, 26, C.CYAN, aen, face=C.FONT_SEMI)
        # mapa de bordes resultante (a la derecha de la cara no hay espacio: se superpone)
        if t > tb - 0.3:
            ae = prog(t, tb - 0.3, tb)
            P.c.save()
            rows_done = scan * 128
            P.c.clipRect(skia.Rect(fx0, fy0, fx0 + S, fy0 + S * clamp(rows_done / 128 + 4 / 128)))
            img(P, "edge_v", fx0, fy0, fx0 + S, fy0 + S, ae)
            P.c.restore()
            P.text("dónde se encendió la neurona: bordes", 540, fy0 + S + 40, 28, C.CYAN, ae, face=C.FONT_SEMI)


# =============================================================== capas
def capas(P, t):
    c = CUE
    a = window(t, c["cap0"] - 0.1, c["apr0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    with P.layer(a):
        rows = [("imagen", 600), ("bordes", 790), ("partes", 980), ("huella", 1165)]
        # imagen
        img(P, "gray128", 540 - 70, 600 - 70, 540 + 70, 600 + 70, 1)
        a1 = prog(t, c["cap0"] + 0.2, c["cap0"] + 0.8)
        xs1 = [240, 440, 640, 840]
        for k, key in enumerate(["edge_v", "edge_h", "edge_d1", "edge_d2"]):
            x = xs1[k]
            P.line(540, 670, x, 730, C.VIOLET, a1 * 0.6, w=2)
            img(P, key, x - 60, 730, x + 60, 850, a1)
            P.rect(x - 60, 730, x + 60, 850, C.CYAN, a1 * 0.6, stroke=2, radius=4)
        a2 = prog(t, c["partes"] - 0.3, c["partes"] + 0.4)
        xs2 = [300, 540, 780]
        crops = [(0.25, 0.33, 0.45, 0.53), (0.40, 0.42, 0.60, 0.62), (0.32, 0.68, 0.68, 0.86)]
        for k, (u0, v0, u1, v1) in enumerate(crops):
            x = xs2[k]
            for x1_ in xs1:
                P.line(x1_, 852, x, 918, C.VIOLET, a2 * 0.35, w=1.6)
            img(P, "base", x - 65, 920, x + 65, 1050, a2, src=(u0 * 256, v0 * 256, u1 * 256, v1 * 256))
            P.rect(x - 65, 920, x + 65, 1050, C.CYAN, a2 * 0.6, stroke=2, radius=4)
        P.text("ojo", 300, 1080, 26, C.GRAY, a2, face=C.FONT_MED); P.text("nariz", 540, 1080, 26, C.GRAY, a2, face=C.FONT_MED)
        P.text("boca", 780, 1080, 26, C.GRAY, a2, face=C.FONT_MED)
        a3 = prog(t, c["huella"] - 0.3, c["huella"] + 0.4)
        if a3 > 0:
            e = D["emb_base"]; e = e / (e.max() + 1e-9)
            n = len(e); bw = 22
            hx0 = 540 - n * bw / 2
            for x in xs2:
                P.line(x, 1052, 540, 1120, C.VIOLET, a3 * 0.35, w=1.6)
            for k in range(n):
                h = 70 * e[k] * prog(t, c["huella"] + 0.02 * k, c["huella"] + 0.02 * k + 0.3)
                P.rect(hx0 + k * bw + 2, 1200 - h, hx0 + (k + 1) * bw - 2, 1200, C.CYAN, a3, radius=3)
            P.text("huella: 32 números que resumen tu rostro", 540, 1240, 28, C.CYAN, a3, face=C.FONT_SEMI)
        labs = [("bordes", 790, a1), ("partes", 985, a2)]
        for lab, y, al in labs:
            P.text(lab, 70, y, 28, C.WHITE, al, face=C.FONT_BOLD, align="left")
        ap = prog(t, c["profundo"] - 0.3, c["profundo"] + 0.3)
        P.pill("APRENDIZAJE PROFUNDO", 540, 560 - 40, 36, C.VIOLET, out_back(ap))


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
    c["neu0"] = T("neurona"); c["peso"] = T("neurona", "peso"); c["suma"] = T("neurona", "suma")
    c["enciende"] = T("neurona", "enciende"); c["bordes"] = T("neurona", "bordes")
    c["cap0"] = T("capas"); c["partes"] = T("capas", "partes"); c["huella"] = T("capas", "huella")
    c["profundo"] = T("capas", "profundo")
    c["apr0"] = T("aprender"); c["miles"] = T("aprender", "miles"); c["error"] = T("aprender", "error")
    c["reduce"] = T("aprender", "reduce"); c["cerro"] = T("aprender", "cerro")
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
            (c["neu0"], "whoosh", 0.5), (c["enciende"], "ding", 0.5), (c["bordes"], "riser", 0.4),
            (c["cap0"], "whoosh", 0.5), (c["partes"], "pop", 0.5), (c["huella"], "pop", 0.5), (c["profundo"], "swell", 0.7),
            (c["apr0"], "whoosh", 0.5), (c["cerro"], "whoosh_down", 0.4),
            (c["res0"], "whoosh", 0.5), (c["ordenan"], "riser", 0.5), (c["nueva"] + 0.2, "ding", 0.8),
            (c["cie0"], "whoosh_down", 0.5), (c["cie0"] + 0.7, "ding", 0.7), (c["mirar"], "swell", 0.5)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["neu0"], "pulse": (c["apr0"], c["cie0"]),
            "quiet": [(c["dif0"], c["reg0"])]}
