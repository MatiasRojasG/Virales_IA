"""Escenas — «La foto nocturna». Una sola toma continua:
celular → foto → muro (gotas de luz) → un punto → sus vecinos → promedio (borra el letrero)
→ resortes (fila real del letrero) → combinaciones → pasadas → de vuelta al celular → documento.
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

TL = None; D = {}; EP = {}; CHUNKS = []; KEYS = []; CUE = {}

PW, PH = 360, 640                 # foto (px)
WX, WY = 204, 572                 # punto protagonista sobre el muro (7 gotas; vecinos ≈ 1)
ROW, RX0, RX1 = 438, 108, 141     # fila del letrero para los resortes
PHOTONS = 12


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def fmt(v, dec=0):
    s = f"{v:,.{dec}f}".replace(",", "§").replace(".", ",").replace("§", ".")
    return s


def rgba(a):
    a8 = (np.clip(a, 0, 1) * 255).astype(np.uint8)
    return np.dstack([a8, np.full(a.shape[:2], 255, np.uint8)])


# =============================================================== cámara (igual que v2)
def state(cx, cy, z, sy=960):
    return (cx, cy, z, sy)


def cam_interp(a, b, u):
    z = a[2] * (b[2] / a[2]) ** u
    w = (1 / z - 1 / a[2]) / (1 / b[2] - 1 / a[2]) if abs(math.log(b[2] / a[2])) > 0.05 else u
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
    br = 1 + 0.010 * math.sin(t * 0.55)
    return (s[0], s[1], s[2] * br, s[3])


def to_screen(cs, x, y):
    cx, cy, z, sy = cs
    return (x - cx) * z + C.W / 2, (y - cy) * z + sy


def visible(cs):
    cx, cy, z, sy = cs
    x0 = max(0, int(cx - C.W / 2 / z) - 1); x1 = min(PW, int(cx + C.W / 2 / z) + 2)
    y0 = max(0, int(cy - sy / z) - 1); y1 = min(PH, int(cy + (C.H - sy) / z) + 2)
    return x0, x1, y0, y1


# =============================================================== qué foto se ve
def photo_layers(t):
    """(base, [(clave, clip)]) en coordenadas de la foto."""
    c = CUE
    if t >= c["loop0"]:                       # empalme con el primer cuadro
        return "noisy", []
    if t < c["reveal0"]:
        return "noisy", []
    if t < c["rw0"]:
        u = in_out_cubic((t - c["reveal0"]) / 0.9)
        return "noisy", [("good", ("rect", -1, -1, PW + 1, lerp(-1, PH + 1, u)))]
    if t < c["rw1"]:
        u = 1 - in_cubic((t - c["rw0"]) / (c["rw1"] - c["rw0"]))
        return "noisy", [("good", ("rect", -1, -1, PW + 1, lerp(-1, PH + 1, u)))]
    if t < c["avg0"]:
        return "noisy", []
    if t < c["calc0"]:      # promedio: onda circular desde el punto del muro
        u = clamp((t - c["avg0"]) / 2.4)      # crece lento al principio: acompaña al zoom de salida
        if u >= 1: return "blur", []
        return "noisy", [("blur", ("circle", WX + .5, WY + .5, 0.6 + 760 * u ** 3))]
    if t < c["it0"]:
        return "noisy", []
    lv = D["levels"]
    for k in range(len(lv) - 1, 0, -1):
        tk = c["it0"] + c["it_dt"] * (k - 1)
        if t >= tk:
            u = out_cubic((t - tk) / 0.8)
            if u >= 1: return f"it{lv[k]}", []
            return (f"it{lv[k - 1]}" if lv[k - 1] else "noisy"), [(f"it{lv[k]}", ("circle", PW / 2, PH / 2, lerp(0, 760, u)))]
    return "noisy", []


HD_MAP = {"noisy": "noisy", "good": "good", "blur": "blur", "clean": "clean", "it20": "good"}


def draw_img(P, key, z, a=1.0):
    """Foto entera → versión HD real (1080×1920); al acercarse → versión de píxeles grandes."""
    im = image(key, D["rgba"][key])
    hk = HD_MAP.get(key, key if key.startswith("it") else None)
    hd_a = 1 - prog(z, 4.5, 7.0, smooth) if hk and hk in D.get("hd", {}) else 0.0
    na = prog(z, 7, 13, smooth)
    p = skia.Paint(); p.setAlphaf(a)
    if hd_a > 0:
        ph = skia.Paint(); ph.setAlphaf(a)
        P.c.drawImageRect(image("hd_" + hk, D["hd"][hk]), skia.Rect(0, 0, PW, PH), CUBIC, ph)
        if hd_a >= 0.999: return
        p.setAlphaf(a * (1 - hd_a))
    if na < 1: P.c.drawImageRect(im, skia.Rect(0, 0, PW, PH), CUBIC, p)
    if na > 0:
        p2 = skia.Paint(); p2.setAlphaf(a * na)
        P.c.drawImageRect(im, skia.Rect(0, 0, PW, PH), NEAREST, p2)


def phone_body(P, a=1.0):
    """Celular dibujado en coordenadas de la foto (se mueve con la cámara)."""
    P.rect(-26, -64, PW + 26, PH + 118, (0, 0, 0), 0.55 * a, radius=46, blur=18)
    P.rect(-22, -60, PW + 22, PH + 112, (0.07, 0.08, 0.11), a, radius=44)
    P.rect(-22, -60, PW + 22, PH + 112, C.WHITE, 0.12 * a, stroke=1.5, radius=44)
    P.rect(PW / 2 - 40, -44, PW / 2 + 40, -30, (0, 0, 0), a, radius=7)


def phone_ui(P, t, a=1.0):
    c = CUE
    press = pulse(t, c["flash"] - 0.18, 0.4)
    r = 30 * (1 - 0.18 * press)
    P.circle(PW / 2, PH + 56, 36, C.WHITE, a, stroke=4)
    P.circle(PW / 2, PH + 56, r, C.WHITE, a)
    P.text("NOCHE", PW / 2, PH + 22, 11, C.CYAN, a * 0.9, face=C.FONT_BOLD, tracking=2)
    P.rect(28, PH + 42, 58, PH + 72, (0.3, 0.3, 0.35), a, radius=6)


def draw_world(P, t, cs):
    cx, cy, z, sy = cs
    cv = P.c
    cv.save(); cv.translate(C.W / 2, sy); cv.scale(z, z); cv.translate(-cx, -cy)
    pa = D["phone_a"](t)
    if pa > 0:
        phone_body(P, pa)
        phone_ui(P, t, pa)
    base, extra = photo_layers(t)
    draw_img(P, base, z)
    for key, clip in extra:
        cv.save()
        if clip[0] == "rect":
            cv.clipRect(skia.Rect(*clip[1:]), doAntiAlias=True)
        else:
            pth = skia.Path(); pth.addCircle(clip[1], clip[2], clip[3]); cv.clipPath(pth, doAntiAlias=True)
        draw_img(P, key, z)
        cv.restore()
        if clip[0] == "rect" and 0 < clip[4] < PH:
            P.line(-1, clip[4], PW + 1, clip[4], C.CYAN, 1, w=4 / z, glow=True)
        if clip[0] == "circle" and clip[3] < 759:
            cv.drawCircle(clip[1], clip[2], clip[3], paint(C.CYAN, 0.8 * (1 - clip[3] / 760), stroke=3 / z))
    # destello del obturador
    fl = pulse(t, CUE["flash"] - 0.05, 0.35)
    if fl > 0: P.rect(0, 0, PW, PH, C.WHITE, 0.9 * fl)
    # retícula al acercarse
    ga = prog(z, 30, 60)
    if ga > 0:
        x0, x1, y0, y1 = visible(cs)
        lp = paint(C.BG, 0.35 * ga, stroke=1.6 / z, cap="butt")
        for x in range(x0, x1 + 1): cv.drawLine(x, y0, x, y1, lp)
        for y in range(y0, y1 + 1): cv.drawLine(x0, y, x1, y, lp)
    overlays(P, t, cs)
    cv.restore()


# =============================================================== capas sobre la foto
def overlays(P, t, cs):
    c = CUE
    z = cs[2]
    noisy = D["noisy"]
    # --- gotas de luz (fotones) llenando cada punto del muro
    a_ph = window(t, c["gotas"] - 0.3, c["moteado"] + 0.6, 0.3, 0.5)
    if a_ph > 0:
        rng = np.random.default_rng(4)
        for yy in range(WY - 4, WY + 5):
            for xx in range(WX - 3, WX + 4):
                n = D["counts"][yy, xx]
                arr = np.sort(c["gotas"] + rng.random(max(n, 1)) * 2.6)[:n]
                landed = int((arr <= t).sum())
                # oscuro hasta que llegan las gotas
                P.rect(xx, yy, xx + 1, yy + 1, (0.02, 0.02, 0.03), a_ph * (1 - landed / max(n, 1)) * 0.95)
                for k, ta in enumerate(arr):
                    if ta - 0.5 < t < ta:
                        u = (t - (ta - 0.5)) / 0.5
                        px = xx + 0.2 + 0.6 * ((k * 0.37) % 1)
                        P.circle(px, lerp(yy - 1.6, yy + 0.5, in_cubic(u)), 0.07, (1, 0.9, 0.6), a_ph)
                if z > 60:
                    P.text(str(landed), xx + 0.5, yy + 0.66, 0.42, C.WHITE if noisy[yy, xx].mean() < 0.45 else C.INK,
                           a_ph * prog(t, c["gotas"], c["gotas"] + 0.3), face=C.FONT_BOLD)
    # --- el punto protagonista y sus vecinos
    a_one = window(t, c["solo"], c["avg0"] + 0.3, 0.35, 0.35)
    if a_one > 0:
        P.rect(WX - 0.1, WY - 0.1, WX + 1.1, WY + 1.1, C.CYAN, a_one, stroke=6 / z)
    a_nb = window(t, c["lado"], c["avg0"] + 0.3, 0.3, 0.35)
    if a_nb > 0:
        for k, (dx, dy) in enumerate([(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]):
            ak = a_nb * prog(t, c["lado"] + 0.06 * k, c["lado"] + 0.06 * k + 0.3)
            P.rect(WX + dx + 0.06, WY + dy + 0.06, WX + dx + 0.94, WY + dy + 0.94, C.VIOLET, ak, stroke=5 / z)
            P.line(WX + .5, WY + .5, WX + dx + .5, WY + dy + .5, C.VIOLET, ak * 0.7, w=3 / z)
    # el punto adopta el promedio de su vecindario
    ua = prog(t, c["corr"], c["corr"] + 0.8, in_out_cubic)
    if ua > 0 and t < c["avg0"] + 0.4:
        col = lerp_c(tuple(noisy[WY, WX]), tuple(D["avg9"]), ua)
        P.rect(WX, WY, WX + 1, WY + 1, col, window(t, c["corr"], c["avg0"] + 0.4, 0.2, 0.3))
    # --- letrero ilegible
    # (se marca en pantalla)
    # --- red: retícula simbólica en la revelación
    a_net = window(t, c["markov"] - 0.2, c["markov"] + 2.8, 0.4, 0.6)
    if a_net > 0:
        step = 24
        for gy in range(step // 2, PH, step):
            for gx in range(step // 2, PW, step):
                d = math.hypot(gx - PW / 2, gy - PH / 2) / 400
                u = prog(t, c["markov"] - 0.2 + d, c["markov"] + 0.2 + d)
                if u <= 0: continue
                if gx + step < PW: P.line(gx, gy, gx + step * u, gy, C.VIOLET, a_net * 0.7, w=1.6)
                if gy + step < PH: P.line(gx, gy, gx, gy + step * u, C.VIOLET, a_net * 0.7, w=1.6)
                P.circle(gx, gy, 2.6 * u, C.WHITE, a_net)


# =============================================================== capas de pantalla
def spotlight(P, t, cs):
    c = CUE
    r_big = 1500
    r = r_big
    if t >= c["solo"] - 0.2:
        r = lerp(r_big, 120, prog(t, c["solo"] - 0.2, c["solo"] + 0.8, in_out_cubic))
    if t >= c["lado"] - 0.2:
        r = lerp(120, 430, prog(t, c["lado"] - 0.2, c["lado"] + 0.8, in_out_cubic))
    if t >= c["avg0"] - 0.3:
        r = lerp(430, r_big, prog(t, c["avg0"] - 0.3, c["avg0"] + 0.8, in_out_cubic))
    if r >= r_big - 1: return
    x, y = to_screen(cs, WX + .5, WY + .5)
    pth = skia.Path(); pth.setFillType(skia.PathFillType.kEvenOdd)
    pth.addRect(skia.Rect(0, 0, C.W, C.H)); pth.addCircle(x, y, r)
    P.c.drawPath(pth, paint(C.BG, 0.86))
    P.c.drawCircle(x, y, r, paint(C.CYAN, 0.35, stroke=3))


def headline(P, t, line1, line2, col2, a, s=1.0):
    """Rótulo breve sobre la imagen (no es un título): qué estamos viendo."""
    if a <= 0: return
    txt = {"TU CÁMARA VIO": "lo que vio la cámara", "TU CELULAR TE MOSTRÓ": "lo que te mostró el celular"}.get(line1, line1)
    with P.transform(0, 0, s, cx=540, cy=330):
        P.pill(txt, 540, 330, 40, col2, a)


def screen_labels(P, t, cs):
    c = CUE
    # hook: titular presente desde el cuadro 0 (sin fundido de entrada)
    a1 = 1 - prog(t, c["reveal0"] - 0.15, c["reveal0"] + 0.05)
    headline(P, t, "TU CÁMARA VIO", "ESTO", C.PINK, a1, 1.0 + 0.12 * (1 - out_back(prog(t, 0, 0.35))))
    a2 = window(t, c["reveal0"], c["novio"] - 0.1, 0.15, 0.3)
    headline(P, t, "TU CELULAR TE MOSTRÓ", "ESTO", C.CYAN, a2, 0.9 + 0.1 * out_back(prog(t, c["reveal0"], c["reveal0"] + 0.35)))
    aq = window(t, c["novio"] - 0.2, c["luz0"] + 0.4, 0.3, 0.3)
    if aq > 0:
        P.text("?", 540, 520, 210, C.CYAN, out_back(prog(t, c["novio"] - 0.2, c["novio"] + 0.3)) * aq,
               face=C.FONT_BLACK, glow=0.8)
    # empalme final: el mismo titular que abre el video
    al = prog(t, c["loop0"], c["loop0"] + 0.25)
    headline(P, t, "TU CÁMARA VIO", "ESTO", C.PINK, al)
    # gotas
    a = window(t, c["gotas"], c["moteado"] + 0.3, 0.3, 0.3)
    P.pill("cada número = gotas de luz que llegaron", 540, 360, 32, C.WHITE, a, fill_a=0.08)
    a = window(t, c["moteado"], c["dif0"] + 0.4, 0.3, 0.3)
    P.pill("el muro real es parejo", 540, 360, 34, C.WHITE, a, fill_a=0.08)
    # un punto
    x, y = to_screen(cs, WX + .5, WY + .5)
    a = window(t, c["verdad"] - 0.2, c["lado"] + 0.2, 0.3, 0.3)
    if a > 0:
        P.text("?", x, y - 170 + 8 * math.sin(t * 5), 140, C.CYAN, out_back(prog(t, c["verdad"] - 0.2, c["verdad"] + 0.3)) * a,
               face=C.FONT_BLACK, glow=0.8)
        P.pill("¿brillo real?", x - 230, y + 10, 32, C.WHITE, a, fill_a=0.08)
        P.pill("¿ruido?", x + 210, y + 10, 32, C.PINK, a * prog(t, c["ruido"], c["ruido"] + 0.3))
    a = window(t, c["corr"], c["avg0"] + 0.2, 0.3, 0.3)
    if a > 0:
        n0 = D["counts"][WY, WX]
        v = lerp(n0, D["avg9_count"], prog(t, c["corr"], c["corr"] + 0.8, in_out_cubic))
        P.pill(f"{n0} gotas  →  promedio del vecindario: {fmt(v, 1)}", 540, 1270, 30, C.VIOLET, a)
    # letrero ilegible
    a = window(t, c["bordes"], c["b0"] + 0.4, 0.3, 0.4)
    P.pill("ILEGIBLE", 540, 1180, 40, C.PINK, out_back(prog(t, c["ilegible"] - 0.2, c["ilegible"] + 0.3)) * a)
    P.text("el muro quedó limpio... y los bordes también se fueron", 540, 360, 30, C.GRAY,
           window(t, c["bordes"] - 0.2, c["b0"] + 0.3, 0.3, 0.3), face=C.FONT_MED)


def zigzag(P, x0, y0, x1, y1, rgb, a, w=3, coils=6, amp=12):
    L = math.hypot(x1 - x0, y1 - y0)
    if L < 1: return
    ux, uy = (x1 - x0) / L, (y1 - y0) / L
    nx, ny = -uy, ux
    pth = skia.Path(); pth.moveTo(x0, y0)
    n = coils * 2
    for k in range(1, n):
        s = k / n
        off = amp * (1 if k % 2 else -1)
        pth.lineTo(x0 + ux * L * s + nx * off, y0 + uy * L * s + ny * off)
    pth.lineTo(x1, y1)
    P.c.drawPath(pth, paint(rgb, a, stroke=w))


# ---------- resortes sobre la fila real del letrero
CH_X0, CH_X1 = 120, 960
CH_Y0, CH_Y1 = 1160, 640     # brillo 0 abajo, 1 arriba


def chain_y(v):
    return lerp(CH_Y0, CH_Y1, v)


def chain_state(t):
    """Posiciones de las cuentas y pesos de los resortes entre vecinos en el tiempo t."""
    c = CUE
    A, B = D["chainA"], D["chainB"]
    if t < c["sp_flat"]:
        return A[0], np.ones(len(A[0]) - 1)
    if t < c["suelta"]:
        k = int(clamp((t - c["sp_flat"]) / 2.4) * (len(A) - 1))
        return A[k], np.ones(len(A[0]) - 1)
    u = clamp((t - c["suelta"]) / 2.6)
    k = int(out_cubic(u) * (len(B) - 1))
    x = B[k]
    wgt = 1 / (1 + ((x[1:] - x[:-1]) / D["delta"]) ** 2)
    return x, wgt


def chain_energy(x, wgt_robust):
    y = D["row_y"]; b = D["chain_beta"]; dl = D["delta"]
    d = x[1:] - x[:-1]
    return float(((x - y) ** 2).sum() + b * (dl ** 2 * np.log1p((d / dl) ** 2)).sum())


def resortes(P, t, cs):
    c = CUE
    a = window(t, c["sp0"], c["calc0"] + 0.3, 0.6, 0.5)
    if a <= 0: return
    y = D["row_y"]
    n = len(y)
    xs = np.linspace(CH_X0, CH_X1, n)
    rise = out_cubic(prog(t, c["sp0"], c["sp0"] + 1.0))
    x, wgt = chain_state(t)
    with P.layer(a):
        # ejes
        P.line(CH_X0 - 40, CH_Y0 + 40, CH_X1 + 40, CH_Y0 + 40, C.DIM, 1, w=3)
        P.text("brillo", CH_X0 - 50, CH_Y1 - 30, 28, C.GRAY, 1, face=C.FONT_MED, align="left")
        P.text("una fila de puntos del letrero →", CH_X1 + 40, CH_Y0 + 92, 28, C.GRAY, 1, face=C.FONT_MED, align="right")
        al = prog(t, c["sp0"] + 0.3, c["sp0"] + 0.8)
        P.rich([("■ ", C.CYAN), ("lo que vio la cámara     ", C.GRAY), ("● ", C.WHITE), ("punto corregido", C.GRAY)],
               540, CH_Y1 - 70, 30, al, face=C.FONT_MED)
        # de dónde salen: fila resaltada en la foto
        sx0, sy_ = to_screen(cs, RX0, ROW + .5); sx1, _ = to_screen(cs, RX1 + 1, ROW + .5)
        P.rect(sx0, sy_ - 8, sx1, sy_ + 8, C.CYAN, 0.6 * (1 - rise))
        a_cam = prog(t, c["sp0"] + 0.5, c["sp0"] + 1.0)
        a_vec = prog(t, c["sp0"] + 0.7, c["sp0"] + 1.2)
        for i in range(n):
            bx = lerp(lerp(sx0, sx1, i / (n - 1)), xs[i], rise)
            by = lerp(sy_, chain_y(x[i]), rise)
            gy = chain_y(y[i])
            # marcador: lo que vio la cámara
            if a_cam > 0:
                P.rect(xs[i] - 7, gy - 7, xs[i] + 7, gy + 7, C.CYAN, a_cam * rise, stroke=2.5)
                if abs(by - gy) > 4:
                    zigzag(P, bx, by, xs[i], gy, C.CYAN, a_cam * 0.8, w=2.4, coils=4, amp=6)
        # resortes entre vecinos
        if a_vec > 0:
            for i in range(n - 1):
                x0_, y0_ = xs[i], chain_y(x[i]); x1_, y1_ = xs[i + 1], chain_y(x[i + 1])
                wv = wgt[i]
                if wv > 0.35:
                    zigzag(P, x0_, y0_, x1_, y1_, C.VIOLET, a_vec * (0.4 + 0.6 * wv), w=2 + 2 * wv,
                           coils=3, amp=7 * wv + 2)
                else:   # resorte suelto: dos extremos colgando
                    sl = prog(t, c["suelta"], c["suelta"] + 0.4)
                    mx, my = (x0_ + x1_) / 2, (y0_ + y1_) / 2
                    P.line(x0_, y0_, lerp(mx, x0_ + 8, sl), lerp(my, y0_ + 40, sl), C.PINK, a_vec * 0.9, w=2.5)
                    P.line(x1_, y1_, lerp(mx, x1_ - 8, sl), lerp(my, y1_ + 40, sl), C.PINK, a_vec * 0.9, w=2.5)
        for i in range(n):
            bx = lerp(lerp(sx0, sx1, i / (n - 1)), xs[i], rise)
            by = lerp(sy_, chain_y(x[i]), rise)
            col = D["row_rgb"][i]
            P.circle(bx, by, 13, tuple(col), 1)
            P.circle(bx, by, 13, C.WHITE, 0.9, stroke=2.5)
        # medidor de tensión y probabilidad
        at = prog(t, c["tension"] - 0.3, c["tension"] + 0.2)
        if at > 0:
            E = chain_energy(x, None)
            e0, e1 = D["E_max"], D["E_min"]
            fr = clamp((E - e1) / (e0 - e1))
            P.text("tensión total", 130, 420, 30, C.WHITE, at, face=C.FONT_SEMI, align="left")
            P.rect(130, 440, 510, 462, C.DIM, at, radius=11)
            P.rect(130, 440, 130 + 380 * fr, 462, C.PINK, at, radius=11)
            ap = prog(t, c["probable"] - 0.3, c["probable"] + 0.2) * at
            if ap > 0:
                pr = math.exp(-(E - e1) / max(1e-6, (e0 - e1) / 4))
                P.text("qué tan probable es esta foto", 570, 420, 30, C.WHITE, ap, face=C.FONT_SEMI, align="left")
                P.rect(570, 440, 950, 462, C.DIM, ap, radius=11)
                P.rect(570, 440, 570 + 380 * pr, 462, C.CYAN, ap, radius=11)


# ---------- combinaciones
def combinaciones(P, t):
    c = CUE
    a = window(t, c["calc0"] + 0.2, c["it0"] + 0.2, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        # un punto: cientos de brillos posibles
        ab = prog(t, c["brillos"] - 0.2, c["brillos"] + 0.4)
        if ab > 0:
            x0, y0 = 160, 520
            for k in range(32):
                v = k / 31
                P.rect(x0 + k * 24, y0, x0 + k * 24 + 22, y0 + 80, (v, v, v), ab * prog(t, c["brillos"] + 0.02 * k, c["brillos"] + 0.02 * k + 0.2))
            P.text("1 punto  →  256 brillos posibles", 540, y0 - 30, 36, C.WHITE, ab, face=C.FONT_BOLD)
        am = prog(t, c["millones"] - 0.2, c["millones"] + 0.3)
        if am > 0:
            n = int(12_000_000 * out_quint(prog(t, c["millones"], c["millones"] + 1.0)))
            P.text(f"{fmt(n)} puntos", 540, 720, 64, C.CYAN, am, face=C.FONT_BLACK)
            P.text("256 × 256 × 256 × …  (12 millones de veces)", 540, 790, 32, C.GRAY, am, face=C.FONT_MED)
        aa = prog(t, c["atomos"] - 0.4, c["atomos"] + 0.2)
        if aa > 0:
            # cifra de fotos posibles vs átomos
            P.rect(110, 870, 970, 1120, C.BG2, 0.92 * aa, radius=28)
            P.text("fotos posibles", 150, 935, 32, C.WHITE, aa, face=C.FONT_SEMI, align="left")
            P.text("un 1 seguido de 28.898.880 ceros", 930, 935, 32, C.PINK, aa, face=C.FONT_BOLD, align="right")
            P.rect(150, 958, 930, 976, C.PINK, aa, radius=9)
            P.text("átomos del universo", 150, 1040, 32, C.WHITE, aa, face=C.FONT_SEMI, align="left")
            P.text("un 1 seguido de 80 ceros", 930, 1040, 32, C.CYAN, aa, face=C.FONT_BOLD, align="right")
            # en escala de "cantidad de ceros", los átomos ni se ven
            P.rect(150, 1063, 150 + max(3, 780 * 80 / 28_898_880), 1081, C.CYAN, aa, radius=4)


def hud_iter(P, t):
    c = CUE
    a = window(t, c["it0"] - 0.2, c["markov"] - 0.2, 0.4, 0.4)
    if a <= 0: return
    lv = D["levels"]; k = 0
    for j in range(1, len(lv)):
        if t >= c["it0"] + c["it_dt"] * (j - 1) + 0.4: k = j
    P.pill(f"pasada {lv[k]}", 540, 330, 40, C.WHITE, a, fill_a=0.08)


# ---------- una sola bolita: cada resorte por separado
BX, BXL, BXR = 540, 290, 790


def arrow_v(P, x, y0, y1, rgb, a, w=7, head=22):
    if a <= 0 or abs(y1 - y0) < 6: return
    P.arrow(x, y0, x, y1, rgb, a, w=w, head=min(head, abs(y1 - y0) * 0.8))


def bolita(P, t):
    c = CUE
    a = window(t, c["b0"], c["sp0"] + 0.2, 0.5, 0.5)
    if a <= 0: return
    yc, n1, n2, beta = D["b_cam"], D["b_n1"], D["b_n2"], D["chain_beta"]
    xeq = (yc + beta * (n1 + n2)) / (1 + 2 * beta)
    # posición de la bolita
    v = yc
    # 1) arrastre y regreso (resorte de la cámara)
    td = c["b_aleja"]
    if td - 0.3 <= t < c["b_vec"]:
        drag = -0.30 * smooth(prog(t, td - 0.3, td + 0.25))
        if t > td + 0.55:
            drag = -0.30 * (1 - spring(t - (td + 0.55)) )
        v = yc + drag
    # 2) los vecinos la acercan hasta el equilibrio
    if t >= c["b_acerca"]:
        u = spring((t - c["b_acerca"]) * 0.9, freq=6, damp=4)
        v = lerp(yc, xeq, u)
    with P.layer(a):
        # eje de brillo
        P.arrow(150, chain_y(0) + 30, 150, chain_y(1) - 30, C.GRAY, 1, w=4, head=20)
        P.text("más brillante", 175, chain_y(1) - 10, 28, C.GRAY, 1, face=C.FONT_MED, align="left")
        P.text("más oscuro", 175, chain_y(0) + 20, 28, C.GRAY, 1, face=C.FONT_MED, align="left")
        by = chain_y(v)
        # resorte a la cámara
        ac = prog(t, c["b_cam_t"] - 0.2, c["b_cam_t"] + 0.3)
        if ac > 0:
            gy = chain_y(yc)
            P.rect(BX - 22, gy - 22, BX + 22, gy + 22, C.CYAN, ac, stroke=4, radius=4)
            P.text("lo que midió la cámara", BX + 50, gy + 10, 30, C.CYAN, ac, face=C.FONT_SEMI, align="left")
            if abs(by - gy) > 6:
                zigzag(P, BX, by, BX, gy, C.CYAN, ac, w=4, coils=5, amp=16)
                # fuerza del resorte de la cámara (hacia el marcador)
                arrow_v(P, BX - 70, by, by + (gy - by) * 0.75, C.CYAN, ac)
        # vecinos
        av = prog(t, c["b_vec"] - 0.2, c["b_vec"] + 0.4)
        if av > 0:
            for xn, vn in ((BXL, n1), (BXR, n2)):
                ny = chain_y(vn)
                zigzag(P, BX, by, xn, ny, C.VIOLET, av, w=4, coils=5, amp=14)
                P.circle(xn, ny, 34, (0.35, 0.33, 0.36), av)
                P.circle(xn, ny, 34, C.VIOLET, av, stroke=4)
                P.text("vecino", xn, ny + 76, 30, C.VIOLET, av, face=C.FONT_SEMI)
            if t >= c["b_acerca"] - 0.2:
                pull = (by - chain_y((n1 + n2) / 2))
                arrow_v(P, BX + 70, by, by - pull * 0.6, C.VIOLET, av)
        # la bolita
        col = lerp_c((0.85, 0.82, 0.78), (0.35, 0.33, 0.36), clamp((yc - v) / max(1e-3, yc - xeq)))
        P.circle(BX, by, 40, col, 1)
        P.circle(BX, by, 40, C.WHITE, 1, stroke=4)
        P.text("un punto", BX, by - 60, 30, C.WHITE, prog(t, c["b0"], c["b0"] + 0.4) * (1 - prog(t, c["b_cam_t"], c["b_cam_t"] + 0.3)),
               face=C.FONT_SEMI)
        # equilibrio
        ae = prog(t, c["b_eq"] - 0.2, c["b_eq"] + 0.3)
        P.pill("fuerzas equilibradas", 540, 420, 38, C.WHITE, out_back(ae), fill_a=0.08)


# ---------- la idea completa: fórmula ↔ resortes
EQ = {}


def eqs():
    if not EQ:
        from reelforge.mathtex import Equation
        EQ["E"] = Equation([r"E(x)", "=", (r"\sum_i (x_i - y_i)^2", C.CYAN), "+",
                            (r"\beta \sum_{i \sim j} \rho(x_i - x_j)", C.VIOLET)])
        EQ["P"] = Equation([r"P(x \mid y)", r"\propto", (r"e^{-E(x)}", C.WHITE)])
        EQ["F"] = Equation([r"=", (r"\prod_i \phi_i(x_i, y_i)", C.CYAN), (r"\prod_{i \sim j} \psi_{ij}(x_i, x_j)", C.VIOLET)])
    return EQ


def formula(P, t):
    c = CUE
    a = window(t, c["f_form"] - 0.2, c["u0"] + 0.2, 0.5, 0.5)
    if a <= 0: return
    E = eqs()
    with P.layer(a):
        size = min(78, 950 / (E["E"].width / 100))
        pp = [prog(t, c["f_form"] - 0.1, c["f_form"] + 0.4, lambda v: v)] * 2 \
            + [prog(t, c["f_obs"] - 0.6, c["f_obs"], lambda v: v)] \
            + [prog(t, c["f_dif"] - 0.6, c["f_dif"], lambda v: v)] * 2
        gc = pulse(t, c["f_obs"] - 0.3, 1.2); gv = pulse(t, c["f_dif"] - 0.3, 1.2)
        E["E"].draw(P, 540, 640, size=size, part_prog=pp, glow={2: gc, 4: gv})
        # cada término con su resorte
        for i, col, lab, tt in ((2, C.CYAN, "resorte a la cámara", c["f_obs"]), (4, C.VIOLET, "resortes entre vecinos", c["f_dif"])):
            al = prog(t, tt - 0.4, tt + 0.1)
            if al <= 0: continue
            x, y = E["E"].part_center(i, 540, 640, size)
            zigzag(P, x - 60, y + 95, x + 60, y + 95, col, al, w=4, coils=5, amp=12)
            P.circle(x - 60, y + 95, 10, col, al); P.circle(x + 60, y + 95, 10, C.WHITE, al)
            P.text(lab, x, y + 150, 30, col, al, face=C.FONT_SEMI)
            P.text("datos" if i == 2 else "suavidad", x, y + 186, 26, C.GRAY, al, face=C.FONT_MED)
        ae = prog(t, c["f_en"] - 0.3, c["f_en"] + 0.2)
        P.text("energía = tensión total de todos los resortes", 540, 520, 32, C.WHITE, ae, face=C.FONT_SEMI)
        ap = prog(t, c["f_prob"] - 0.6, c["f_prob"])
        E["P"].draw(P, 540, 960, size=82, reveal=ap)
        P.text("menos energía  →  foto más probable", 540, 1060, 32, C.CYAN, prog(t, c["f_prob"], c["f_prob"] + 0.4), face=C.FONT_SEMI)
        af = prog(t, c["f_prob"] + 0.8, c["f_prob"] + 1.4)
        if af > 0:
            E["F"].draw(P, 540, 1140, size=54, reveal=af)
            P.text("en la clase: factores φ (datos) y ψ (vecinos), multiplicados", 540, 1268, 26, C.GRAY, af, face=C.FONT_MED)


# ---------- dónde más se usa
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
        for col in range(n):
            lab = clean[r, col] if (r + col) * 0.75 < wave else noisy[r, col]
            P.rect(x0 + col * s, y0 + r * s, x0 + (col + 1) * s + 0.6, y0 + (r + 1) * s + 0.6, cols[lab], a)


def usos(P, t):
    c = CUE
    a = window(t, c["u0"] - 0.1, c["cierre0"] + 0.3, 0.5, 0.5)
    if a <= 0: return
    tiles = [(540, 560, c["u_doc"], "Documentos escaneados", "doc"),
             (540, 900, c["u_tum"], "Resonancias", "mri"),
             (540, 1240, c["u_sat"], "Satélites", "sat")]
    with P.layer(a):
        for k, (cx, cy, ts, lab, kind) in enumerate(tiles):
            ak = prog(t, ts - 0.3, ts + 0.2)
            if ak <= 0: continue
            s_ = 0.85 + 0.15 * out_back(prog(t, ts - 0.3, ts + 0.3))
            u = prog(t, ts + 0.2, ts + 1.6, in_out_cubic)
            xc = 330
            with P.transform(0, 0, s_, cx=xc, cy=cy):
                if kind == "doc":
                    w_, h_ = 300, 300 * D["doc_noisy"].shape[0] / D["doc_noisy"].shape[1]
                    P.rect(xc - 160, cy - h_ / 2 - 12, xc + 160, cy + h_ / 2 + 12, C.PAPER, ak, radius=14)
                    im_n = image("docn", D["doc_noisy"]); im_c = image("docc", D["doc_clean"])
                    pp = skia.Paint(); pp.setAlphaf(ak)
                    P.c.drawImageRect(im_n, skia.Rect(xc - 150, cy - h_ / 2, xc + 150, cy + h_ / 2), CUBIC, pp)
                    P.c.save(); P.c.clipRect(skia.Rect(xc - 150, cy - h_ / 2, xc - 150 + 300 * u, cy + h_ / 2))
                    P.c.drawImageRect(im_c, skia.Rect(xc - 150, cy - h_ / 2, xc + 150, cy + h_ / 2), CUBIC, pp)
                    P.c.restore()
                else:
                    noisy, clean = D[kind]
                    cols = ([(0.16, 0.19, 0.27), (0.62, 0.66, 0.74), C.PINK] if kind == "mri"
                            else [C.GREEN, (0.85, 0.75, 0.3), (0.2, 0.45, 0.9), C.GRAY])
                    tile_card(P, xc, cy, ak)
                    label_map(P, xc, cy, noisy, clean, u, cols, ak)
            P.text(lab, 540, cy - 10, 40, C.WHITE, ak, face=C.FONT_BOLD, align="left")
            sub = {"doc": "puntos: tinta o papel", "mri": "puntos: tejido sano o lesión",
                   "sat": "puntos: bosque, cultivo, ciudad o agua"}[kind]
            P.text(sub, 540, cy + 36, 28, C.GRAY, ak, face=C.FONT_MED, align="left")
        P.text("Ilustración simplificada: los celulares reales combinan", 540, 330, 26, C.GRAY,
               prog(t, c["u0"] + 0.5, c["u0"] + 1.0), face=C.FONT_MED)
        P.text("varias tomas y redes neuronales, con esta misma idea de fondo.", 540, 362, 26, C.GRAY,
               prog(t, c["u0"] + 0.5, c["u0"] + 1.0), face=C.FONT_MED)


def cierre(P, t, cs):
    c = CUE
    # deslizador antes / después en el celular mientras se responde la pregunta inicial
    us = window(t, c["cierre0"] + 0.6, c["vec_end"] + 0.2, 0.6, 0.4)
    if us > 0:
        xsl = PW * (0.5 + 0.32 * math.sin((t - c["cierre0"]) * 1.4))
        x_s, y_t = to_screen(cs, xsl, 0); _, y_b = to_screen(cs, xsl, PH)
        xl, _ = to_screen(cs, 0, 0)
        cx, cy, z, sy = cs
        with P.layer(us):
            P.c.save(); P.c.clipRect(skia.Rect(xl, y_t, x_s, y_b))
            P.c.translate(C.W / 2, sy); P.c.scale(z, z); P.c.translate(-cx, -cy)
            draw_img(P, "noisy", z)
            P.c.restore()
            P.line(x_s, y_t, x_s, y_b, C.CYAN, 1, w=5, glow=True)
            P.glow_circle(x_s, (y_t + y_b) / 2, 16, C.CYAN, 1)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, D, EP, CHUNKS, KEYS, CUE
    TL, D, EP = tl, data, episode
    D["levels"] = [0, 1, 2, 3, 4, 6, 9, 13, 20]
    D["rgba"] = {k: rgba(D[k]) for k in ("noisy", "good", "blur", "clean")}
    D["rgba"]["dark"] = rgba(D["clean"] * 0.25)
    for k in D["levels"][1:]:
        D["rgba"][f"it{k}"] = rgba(D[f"it{k}"])
    noisy = D["noisy"]
    D["counts"] = D["counts"].astype(int)          # fotones contados por cada punto (simulación)
    patch = noisy[WY - 1:WY + 2, WX - 1:WX + 2]
    D["avg9"] = patch.reshape(-1, 3).mean(0)
    D["avg9_count"] = float(D["counts"][WY - 1:WY + 2, WX - 1:WX + 2].mean())
    # cadena 1D: fila real del letrero
    y = noisy[ROW, RX0:RX1 + 1].mean(1).astype(np.float64)
    D["row_y"] = y; D["row_rgb"] = noisy[ROW, RX0:RX1 + 1]
    D["delta"] = 0.10; D["chain_beta"] = 4.0
    xa = y.copy(); A = [xa.copy()]
    for _ in range(60):                         # todos los resortes iguales (solo promediar)
        P_ = np.pad(xa, 1, mode="edge")
        xa = (y + 4.0 * (P_[:-2] + P_[2:])) / (1 + 8.0); A.append(xa.copy())
    xb = xa.copy(); B = [xb.copy()]
    for _ in range(80):                         # resortes que se sueltan (robusto)
        P_ = np.pad(xb, 1, mode="edge")
        wl = 1 / (1 + ((xb - P_[:-2]) / 0.10) ** 2); wr = 1 / (1 + ((xb - P_[2:]) / 0.10) ** 2)
        xb = (y + 4.0 * (wl * P_[:-2] + wr * P_[2:])) / (1 + 4.0 * (wl + wr)); B.append(xb.copy())
    D["chainA"], D["chainB"] = A, B
    es = [chain_energy(v, None) for v in A + B]
    D["E_max"], D["E_min"] = max(es), min(es)

    # bolita: el punto protagonista (8 gotas) y sus vecinos izquierdo/derecho, en brillo
    lum = lambda p: float(np.dot(p, [0.299, 0.587, 0.114]))
    D["b_cam"] = lum(noisy[WY, WX])
    nbm = (sum(lum(noisy[WY + dy, WX + dx]) for dy in (-1, 0, 1) for dx in (-1, 0, 1)) - D["b_cam"]) / 8
    D["b_n1"] = D["b_n2"] = nbm           # el vecindario promedio (ver "promedio del vecindario")
    D["mri"], D["sat"] = mini_maps()

    c = {}
    c["flash"] = -10.0                         # sin destello: el video abre ya dentro de la foto
    c["esto2"] = T("hook", "esto", 1); c["reveal0"] = c["esto2"] - 0.25
    c["novio"] = T("hook", "vio", 1); c["rw1"] = T("luz") + 0.1; c["rw0"] = c["rw1"] - 0.5
    c["luz0"] = T("luz"); c["gotas"] = T("luz", "gotas"); c["moteado"] = T("luz", "moteado")
    c["dif0"] = T("dificil"); c["solo"] = T("dificil", "solo"); c["verdad"] = T("dificil", "verdad")
    c["ruido"] = T("dificil", "ruido")
    c["lado"] = T("vecinos", "lado"); c["corr"] = T("vecinos", "corregirse")
    c["avg0"] = T("vecinos", "vecinos", end=True) + 0.1
    c["bordes"] = T("exceso", "bordes"); c["ilegible"] = T("exceso", "ilegible")
    c["b0"] = T("bolita"); c["b_cam_t"] = T("bolita", "midió"); c["b_aleja"] = T("bolita", "aleja")
    c["b_vec"] = T("bolita", "vecinos"); c["b_acerca"] = T("bolita", "acercan"); c["b_eq"] = T("bolita", "equilibran")
    c["sp0"] = T("resortes"); c["sp_flat"] = T("resortes", "igual")
    c["suelta"] = T("resortes", "suelta"); c["tension"] = c["probable"] = 1e9   # se dice recién en «formula»
    c["calc0"] = T("calculo"); c["brillos"] = c["millones"] = c["atomos"] = 1e9   # (cuenta de átomos retirada)
    c["it0"] = T("calculo", "acomoda"); c["it_dt"] = 0.5
    c["markov"] = T("formula", "Markov"); c["f_form"] = T("formula", "tensión")
    c["f_obs"] = c["f_form"] + 0.5; c["f_dif"] = c["f_form"] + 1.1
    c["f_en"] = T("formula", "energía"); c["f_prob"] = T("formula", "probable")
    c["u0"] = T("usos"); c["u_doc"] = T("usos", "documentos"); c["u_tum"] = T("usos", "tumores")
    c["u_sat"] = T("usos", "bosques")
    c["cierre0"] = T("cierre"); c["vec_end"] = T("cierre", "vecinos", end=True)
    c["loop0"] = c["vec_end"] + 0.35
    CUE = c

    # visibilidad del celular: al preguntar y al responder
    D["phone_a"] = lambda t: clamp(window(t, c["novio"] - 0.5, c["gotas"] - 0.3, 0.6, 0.8)
                                   + window(t, c["cierre0"], c["vec_end"] + 0.1, 0.8, 0.4))

    HOOKS = state(PW / 2, PH / 2, 3.0, 810)      # foto entera en HD; subida para que letrero y vitrina queden sobre los subtítulos
    PHONE = state(PW / 2, PH / 2 + 25, 1.25, 840)
    PHOTO = state(PW / 2, PH / 2, 3.0, 810)
    WALL = state(WX + .5, WY + .5, 115, 900)
    WALL_OUT = state(WX + .5, WY + .5, 40, 900)
    ONE = state(WX + .5, WY + .5, 170, 900)
    NB = state(WX + .5, WY + .5, 120, 900)
    SIGN = state(180, 437, 4.6, 820)
    SIGN_DOF = state(180, 437, 5.2, 820)
    REV = state(PW / 2, PH / 2 + 25, 1.2, 870)
    KEYS = [
        (0.0, HOOKS), (c["novio"] - 0.5, HOOKS), (c["novio"] + 0.8, PHONE),
        (c["luz0"] + 0.3, PHONE), (c["gotas"] - 0.1, WALL),
        (c["moteado"] - 0.3, WALL), (c["moteado"] + 0.9, WALL_OUT),
        (c["solo"] - 0.4, WALL_OUT), (c["solo"] + 0.8, ONE),
        (c["lado"] - 0.3, ONE), (c["lado"] + 0.8, NB),
        (c["avg0"] - 0.3, NB), (c["avg0"] + 2.2, PHOTO),
        (c["bordes"] - 0.2, PHOTO), (c["ilegible"] + 0.2, SIGN),
        (c["b0"], SIGN), (c["b0"] + 1.2, SIGN_DOF),
        (c["calc0"], SIGN_DOF), (c["it0"] - 0.6, PHOTO),
        (c["cierre0"], PHOTO), (c["cierre0"] + 1.0, REV),
        (c["vec_end"] - 0.7, REV), (c["loop0"], HOOKS),
        (tl.duration + 1, HOOKS),
    ]
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    P.background(t, accent=0.3 * prog(t, c["markov"], c["markov"] + 1))
    cs = cam(t)
    blur = 0.0
    blur = max(blur, 18 * window(t, c["b0"] + 0.2, c["it0"] - 0.3, 0.8, 0.6))
    blur = max(blur, 18 * window(t, c["f_form"] - 0.3, c["cierre0"] + 0.4, 0.7, 0.7))
    draw_blurred(P, lambda q: draw_world(q, t, cs), blur)
    dim = 0.72 * blur / 18
    if dim > 0: P.rect(0, 0, C.W, C.H, C.BG, dim)
    spotlight(P, t, cs)
    screen_labels(P, t, cs)
    bolita(P, t)
    resortes(P, t, cs)
    combinaciones(P, t)
    hud_iter(P, t)
    a_mk = window(t, c["markov"] - 0.1, c["f_form"], 0.3, 0.3)
    P.pill("RED DE MARKOV", 540, 360, 44, C.VIOLET, out_back(prog(t, c["markov"] - 0.1, c["markov"] + 0.3)) * a_mk)
    formula(P, t)
    usos(P, t)
    cierre(P, t, cs)
    vignette(P, 0.45)
    vband(P, 0, 330, 0.85, 0.0)
    vband(P, 1230, C.H, 0.0, 0.9)
    if EP.get("tag"):
        P.circle(C.SAFE_LEFT + 10, 262, 8, C.CYAN, 1)
        P.text(EP["tag"], C.SAFE_LEFT + 34, 273, 28, C.WHITE, 0.85, face=C.FONT_BOLD, align="left", tracking=2)
    SUB.draw(P, CHUNKS, t)
    P.rect(0, C.H - 8, C.W * t / TL.duration, C.H, C.CYAN, 0.8)


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
        for _ in range(6):
            votes = np.zeros((k,) + lab.shape)
            for cc in range(k):
                e = (cur == cc).astype(float)
                P_ = np.pad(e, 1)
                votes[cc] = 0.9 * (nz == cc) + P_[:-2, 1:-1] + P_[2:, 1:-1] + P_[1:-1, :-2] + P_[1:-1, 2:]
            cur = votes.argmax(0)
        return nz, cur
    return noisy_clean(mri, 3), noisy_clean(sat, 4)


def draw_cover(P, t=3.0):
    P.background(t, accent=0.6)
    P.text("¿CÓMO LIMPIA", 540, 360, 96, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("TU CELULAR", 540, 465, 96, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("UNA FOTO DE NOCHE?", 540, 570, 84, C.CYAN, 1, face=C.FONT_BLACK, glow=0.6)
    z = 1.05; sy = 1130
    cs = state(PW / 2, PH / 2, z, sy)
    cv = P.c
    cv.save(); cv.translate(540, sy); cv.scale(z, z); cv.translate(-PW / 2, -PH / 2)
    phone_body(P, 1)
    draw_img(P, "good", z)
    cv.clipRect(skia.Rect(0, 0, PW / 2, PH))
    draw_img(P, "noisy", z)
    cv.restore()
    P.line(540, sy - PH * z / 2, 540, sy + PH * z / 2, C.CYAN, 1, w=6, glow=True)
    P.pill("SENSOR", 400, sy + PH * z / 2 + 120, 30, C.PINK)
    P.pill("RESULTADO", 680, sy + PH * z / 2 + 120, 30, C.CYAN)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "thump", 0.9), (0.0, "swell", 0.5),
            (c["reveal0"] - 0.3, "riser", 0.5), (c["reveal0"] + 0.6, "ding", 0.8),
            (c["novio"] - 0.4, "whoosh", 0.5), (c["rw0"], "rewind", 0.9), (c["gotas"] - 0.2, "whoosh", 0.6),
            (c["solo"] - 0.3, "whoosh", 0.5), (c["ruido"], "pop_low", 0.5),
            (c["lado"], "pop", 0.5), (c["corr"], "pop", 0.5), (c["avg0"], "whoosh_down", 0.5),
            (c["ilegible"], "pop_low", 0.7), (c["b0"], "whoosh", 0.5), (c["b_cam_t"], "pop", 0.5),
            (c["b_aleja"] + 0.55, "pop_low", 0.5), (c["b_vec"], "pop", 0.5), (c["b_eq"], "ding", 0.5),
            (c["sp0"], "whoosh", 0.4), (c["suelta"], "pop_low", 0.7), (c["suelta"] + 0.15, "pop", 0.5),
            (c["probable"], "ding", 0.6), (c["millones"], "riser", 0.4), (c["atomos"], "thump", 0.6),
            (c["it0"] - 0.4, "whoosh_down", 0.5), (c["markov"], "swell", 0.8),
            (c["f_form"] - 0.3, "whoosh", 0.5), (c["f_obs"] - 0.3, "pop", 0.5), (c["f_dif"] - 0.3, "pop", 0.5),
            (c["f_prob"], "ding", 0.6), (c["u0"], "whoosh", 0.5), (c["u_doc"], "pop", 0.5),
            (c["u_tum"], "pop", 0.5), (c["u_sat"], "pop", 0.5), (c["cierre0"], "swell", 0.7),
            (c["vec_end"] - 0.3, "ding", 0.8), (c["loop0"], "rewind", 0.6)]
    rng = np.random.default_rng(2)
    for tt in np.sort(c["gotas"] + rng.random(18) * 2.6):
        cues.append((float(tt), "tick", 0.25))
    cues += [(c["it0"] + c["it_dt"] * k, "tick", 0.6) for k in range(len(D["levels"]) - 1)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["b0"], "pulse": (c["it0"], c["u0"]),
            "quiet": [(c["dif0"] - 0.3, c["lado"])]}
