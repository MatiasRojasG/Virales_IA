"""Escenas — «¿Por qué tu cargador es tan chico?» (stheq.ia, motion graphics).

Hilo visual: dos cargadores de 30 W (grande y chico) → el enchufe entrega una onda enorme (220 V) que
el cargador baja a una línea casi plana (5–20 V) → un interruptor que prende y apaga cada vez más
rápido (onda cuadrada) → el transformador se achica a medida que sube la frecuencia → chip de silicio
que se calienta vs chip de GaN que no → el cargador grande se encoge hasta el chico (empalme con el
inicio). Sin fotos: todo se dibuja. Las respuestas aparecen cuando la voz las dice.
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
BIG = (330, 400)      # cargador de silicio (w, h)
SMALL = (190, 230)    # cargador de GaN


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
def charger(P, cx, cy, w, h, a=1.0, label=None, la=0.0, ring=0.0, outline=False):
    """Cargador de pared visto de frente: cuerpo redondeado, patas arriba y puerto USB-C abajo."""
    if a <= 0 or w < 4: return
    r = 0.2 * min(w, h)
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    with P.layer(a):
        pw, ph = max(4, w * 0.065), h * 0.2
        for sx in (-0.2, 0.2):
            P.rect(cx + sx * w - pw / 2, y0 - ph, cx + sx * w + pw / 2, y0 + 6, L.GRAY, 1, radius=pw / 2)
        if outline:
            P.rect(x0, y0, x1, y1, L.GRAY, 0.9, stroke=4, radius=r)
        else:
            P.rect(x0 + 8, y0 + 22, x1 + 8, y1 + 30, (0, 0, 0), 0.55, radius=r, blur=24)
            P.rect(x0, y0, x1, y1, L.FG, 1, radius=r)
            P.rect(x0 + w * 0.62, y0, x1, y1, L.GRAY, 0.18, radius=r)          # sombreado lateral
            P.rect(x0 + w * 0.08, y0 + h * 0.05, x0 + w * 0.3, y0 + h * 0.4, L.WHITE, 0.35, radius=r * 0.6, blur=8)
            pw2, ph2 = w * 0.28, max(6, h * 0.05)
            P.rect(cx - pw2 / 2, y1 - h * 0.14 - ph2, cx + pw2 / 2, y1 - h * 0.14, L.BG, 0.85, radius=ph2 / 2)
        if label and la > 0:
            with P.transform(0, (1 - out_back(la)) * 16, 1, cx=cx, cy=cy):
                P.text(label, cx, cy + h * 0.06, h * 0.16, L.BG if not outline else L.FG, la, face=C.FONT_BLACK)
        if ring > 0:
            P.rect(x0 - 16, y0 - 16 - ph * 0, x1 + 16, y1 + 16, L.RED, 0.95 * ring, stroke=6, radius=r + 14)
            P.rect(x0 - 16, y0 - 16, x1 + 16, y1 + 16, L.RED, 0.3 * ring, stroke=18, radius=r + 14, blur=12)


def socket(P, x, y, s=1.0, a=1.0):
    if a <= 0: return
    with P.layer(a):
        P.rect(x - 95 * s, y - 95 * s, x + 95 * s, y + 95 * s, L.CARD, 1, radius=30 * s)
        P.rect(x - 95 * s, y - 95 * s, x + 95 * s, y + 95 * s, L.FG, 0.8, stroke=4, radius=30 * s)
        P.circle(x, y, 58 * s, L.LINE, 1)
        for dx in (-24, 24):
            P.circle(x + dx * s, y, 11 * s, L.BG, 1)


def phone(P, x, y, s=1.0, a=1.0, fill=0.0):
    if a <= 0: return
    w, h = 130 * s, 250 * s
    with P.layer(a):
        P.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, L.FG, 1, stroke=5, radius=24 * s)
        P.rect(x - w / 2 + 10, y - h / 2 + 10, x + w / 2 - 10, y + h / 2 - 10, L.CARD, 1, radius=16 * s)
        bw, bh = 50 * s, 90 * s
        P.rect(x - bw / 2, y - bh / 2, x + bw / 2, y + bh / 2, L.FG, 0.9, stroke=3.5, radius=6)
        P.rect(x - 10 * s, y - bh / 2 - 9 * s, x + 10 * s, y - bh / 2, L.FG, 0.9, radius=3)
        f = clamp(fill)
        if f > 0:
            P.rect(x - bw / 2 + 7, y + bh / 2 - 7 - (bh - 14) * f, x + bw / 2 - 7, y + bh / 2 - 7, L.FG, 0.95, radius=3)


def wave(P, x0, x1, y, amp, cycles, phase, rgb, a=1.0, w=6, square=False):
    if a <= 0 or x1 <= x0: return
    pth = skia.Path(); n = max(40, int((x1 - x0) / 3))
    for k in range(n + 1):
        u = k / n; ang = 2 * math.pi * (cycles * u) - phase
        v = math.sin(ang)
        if square: v = 1.0 if v >= 0 else -1.0
        xx, yy = x0 + (x1 - x0) * u, y - amp * v
        (pth.moveTo if k == 0 else pth.lineTo)(xx, yy)
    P.c.drawPath(pth, paint(rgb, a * 0.25, stroke=w * 3, blur=8))
    P.c.drawPath(pth, paint(rgb, a, stroke=w))


def transformer(P, cx, cy, s, a=1.0, t=0.0):
    """Núcleo en «E» con dos bobinas (vista frontal simplificada)."""
    if a <= 0 or s <= 0.02: return
    W_, H_ = 360 * s, 260 * s
    x0, y0, x1, y1 = cx - W_ / 2, cy - H_ / 2, cx + W_ / 2, cy + H_ / 2
    leg = 46 * s
    with P.layer(a):
        P.rect(x0, y0, x1, y1, L.GRAY, 1, stroke=leg, radius=10 * s)
        P.rect(cx - leg / 2, y0, cx + leg / 2, y1, L.GRAY, 1)
        for side in (-1, 1):
            bx = cx + side * W_ * 0.25
            for k in range(7):
                yy = y0 + H_ * (0.18 + 0.64 * k / 6)
                P.rect(bx - 62 * s, yy - 9 * s, bx + 62 * s, yy + 9 * s, L.FG, 0.95, radius=9 * s)


def chip(P, cx, cy, s, a=1.0, label="", heat=0.0, t=0.0, cool=0.0):
    if a <= 0: return
    w = 210 * s
    with P.layer(a):
        if heat > 0:
            P.circle(cx, cy, w * 0.95, L.RED, 0.35 * heat, blur=60)
        for k in range(5):
            o = (k - 2) * w * 0.17
            for sx in (-1, 1):
                P.rect(cx + sx * w / 2 - (14 if sx > 0 else -14) * s * 0 - (0 if sx > 0 else 24 * s), cy + o - 7 * s,
                       cx + sx * w / 2 + (24 * s if sx > 0 else 0), cy + o + 7 * s, L.GRAY, 1, radius=3)
        body = lerp_c(L.CARD, lerp_c(L.RED, L.BG, 0.35), heat)
        P.rect(cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2, body, 1, radius=18 * s)
        P.rect(cx - w / 2, cy - w / 2, cx + w / 2, cy + w / 2, lerp_c(L.FG, L.RED, heat), 0.9, stroke=4, radius=18 * s)
        P.text(label, cx, cy + 22 * s, 64 * s, L.FG, 1, face=C.FONT_BLACK)
        # ondas de calor
        if heat > 0.05:
            for k in range(3):
                xx = cx + (k - 1) * w * 0.3
                pth = skia.Path()
                for j in range(13):
                    u = j / 12; yy = cy - w * 0.62 - u * 150 * s
                    x_ = xx + math.sin(u * 7 + t * 6 + k) * 12 * s
                    (pth.moveTo if j == 0 else pth.lineTo)(x_, yy)
                P.c.drawPath(pth, paint(L.RED, 0.7 * heat * (0.6 + 0.4 * math.sin(t * 4 + k)), stroke=5))


def sparks(P, cx, cy, t, t0, rate, a=1.0, seed=1):
    """Partículas de energía perdida (calor) que salen del chip."""
    if a <= 0 or t < t0: return
    rng = np.random.default_rng(seed)
    n = int(rate * 6)
    for k in range(n):
        ph = rng.uniform(0, 1); ang = rng.uniform(0, 2 * math.pi); sp = rng.uniform(90, 170)
        life = 0.9
        u = ((t - t0) * rate / n + ph) % 1.0
        if (t - t0) < ph * life: continue
        d = 120 + sp * u * 1.2
        P.circle(cx + math.cos(ang) * d, cy + math.sin(ang) * d, 5 * (1 - u) + 1, L.RED, a * (1 - u) * 0.9)


# =============================================================== escenas
def hook(P, t):
    c = CUE
    a = 1 - prog(t, c["e0"] - 0.35, c["e0"] + 0.25, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        s1 = out_back(prog(t, 0.0, 0.55, lambda x: x)); s2 = out_back(prog(t, 0.25, 0.8, lambda x: x))
        la = prog(t, c["w30"] - 0.1, c["w30"] + 0.35, lambda x: x)
        charger(P, 330, 900, BIG[0] * s1, BIG[1] * s1, 1, "30 W", la)
        charger(P, 770, 960, SMALL[0] * s2, SMALL[1] * s2, 1, "30 W", la)
        P.text("=", 560, 935, 90, L.GRAY, la, face=C.FONT_BLACK)
        # medida de alturas
        m = prog(t, c["chico"] - 0.2, c["chico"] + 0.5)
        if m > 0:
            for (x, cy, h) in ((330 - BIG[0] / 2 - 46, 900, BIG[1]), (770 + SMALL[0] / 2 + 46, 960, SMALL[1])):
                hh = h * m
                P.line(x, cy - hh / 2, x, cy + hh / 2, L.RED, 1, w=5)
                for yy in (cy - hh / 2, cy + hh / 2):
                    P.line(x - 16, yy, x + 16, yy, L.RED, 1, w=5)
        q = prog(t, c["como"] - 0.1, c["como"] + 0.4, lambda x: x)
        if q > 0:
            P.text("?", 560, 640 + 12 * math.sin(t * 3), 150, L.RED, out_back(q), face=C.FONT_BLACK)


def enchufe(P, t):
    c = CUE
    a = window(t, c["e0"] - 0.25, c["c0"] + 0.2, 0.5, 0.45)
    if a <= 0: return
    with P.layer(a):
        socket(P, 160, 900, 1.0, prog(t, c["e0"] - 0.2, c["e0"] + 0.3))
        charger(P, 540, 910, 150, 182, prog(t, c["e0"], c["e0"] + 0.4))
        phone(P, 905, 905, 1.0, prog(t, c["e0"] + 0.15, c["e0"] + 0.55), fill=prog(t, c["nec"] + 0.3, c["baj"] + 0.8, smooth))
        A = 120 * prog(t, c["v220"] - 0.2, c["v220"] + 0.5)
        wave(P, 262, 452, 900, A, 2.2, t * 7, L.RED, a=1, w=6)
        P.text("220 V", 357, 700, 64, L.RED, prog(t, c["v220"], c["v220"] + 0.3), face=C.FONT_BLACK)
        lo = prog(t, c["nec"] - 0.1, c["nec"] + 0.4)
        wave(P, 628, 830, 905, 10 * lo, 3, t * 7, L.FG, a=lo, w=6)
        P.text("5–20 V", 729, 790, 50, L.FG, lo, face=C.FONT_BLACK)
        g = pulse(t, c["baj"] - 0.1, 0.9)
        if g > 0:
            P.rect(540 - 95, 910 - 115, 540 + 95, 910 + 115, L.FG, 0.6 * g, stroke=5, radius=40)
            P.arrow(540, 690, 540, 770, L.FG, g, w=7, head=24)


def chip_scene(P, t):
    c = CUE
    a = window(t, c["c0"] - 0.2, c["tr0"] + 0.2, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        # frecuencia visual: sube de 1 a ~14 ciclos por segundo (la real es mucho mayor)
        f = 1.0 + 13 * prog(t, c["miles"] - 0.3, c["k65"], smooth)
        # integra la fase de forma aproximada para que no salte
        ph = 2 * math.pi * (t - c["c0"]) * (1.0 + 13 * prog(t, c["miles"] - 0.3, c["k65"], smooth) * 0.5)
        on = math.sin(ph) >= 0
        # interruptor
        cx, cy = 540, 720
        P.circle(cx - 150, cy, 18, L.FG, 1); P.circle(cx + 150, cy, 18, L.FG, 1)
        P.line(cx - 330, cy, cx - 150, cy, L.FG, 1, w=6); P.line(cx + 150, cy, cx + 330, cy, L.FG, 1, w=6)
        ang = 0 if on else -0.5
        P.line(cx - 150, cy, cx - 150 + 300 * math.cos(ang), cy + 300 * math.sin(ang), L.RED if on else L.GRAY, 1, w=10)
        if on:
            P.circle(cx + 150, cy, 34, L.RED, 0.35, blur=14)
        # onda cuadrada
        wa = prog(t, c["prende"] - 0.2, c["prende"] + 0.4)
        wave(P, 110, 970, 960, 70, 1.5 + 6 * (f - 1) / 13, t * f * 2, L.FG, a=wa, w=5, square=True)
        P.text("prendido", 110, 865, 28, L.GRAY, wa, face=C.FONT_BOLD, align="left")
        P.text("apagado", 110, 1065, 28, L.GRAY, wa, face=C.FONT_BOLD, align="left")
        k = prog(t, c["k65"] - 0.1, c["k65"] + 0.4, lambda x: x)
        if k > 0:
            with P.transform(0, 0, 0.8 + 0.2 * out_back(k), cx=540, cy=1190):
                P.text("65.000 / s", 540, 1210, 104, L.RED, clamp(k * 1.5), face=C.FONT_BLACK)


def truco(P, t):
    c = CUE
    a = window(t, c["tr0"] - 0.2, c["g0"] + 0.2, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        u = prog(t, c["rap"] - 0.1, c["trafo"] + 0.6, in_out_cubic)
        s = lerp(1.0, 0.52, u)
        charger(P, 540, 830, 540 * s, 600 * s, prog(t, c["tr0"] - 0.1, c["tr0"] + 0.4), outline=True)
        transformer(P, 540, 830, s, prog(t, c["tr0"], c["tr0"] + 0.5), t)
        lab = prog(t, c["trafo"] - 0.1, c["trafo"] + 0.35, lambda x: x)
        if lab > 0:
            P.pill("transformador", 540, 830 + 330 * s + 40, 40, L.RED, out_back(lab), face=C.FONT_BOLD)
        # control de velocidad
        sa = prog(t, c["rap"] - 0.3, c["rap"] + 0.2)
        P.line(220, 1215, 860, 1215, L.LINE, sa, w=10)
        P.line(220, 1215, lerp(220, 860, u), 1215, L.RED, sa, w=10)
        P.circle(lerp(220, 860, u), 1215, 22, L.FG, sa)
        P.text("lento", 220, 1170, 30, L.GRAY, sa, face=C.FONT_BOLD)
        P.text("rápido", 860, 1170, 30, L.FG, sa, face=C.FONT_BOLD)


def gan(P, t):
    c = CUE
    a = window(t, c["g0"] - 0.2, c["ci0"] + 0.2, 0.45, 0.45)
    if a <= 0: return
    with P.layer(a):
        sa = prog(t, c["sil"] - 0.3, c["sil"] + 0.3); ga = prog(t, c["nit"] - 0.3, c["nit"] + 0.3)
        heat = prog(t, c["cal"] - 0.3, c["cal"] + 0.6)
        chip(P, 300, 860, 1.0, sa, "Si", heat, t)
        chip(P, 780, 860, 1.0, ga, "GaN", 0.0, t)
        P.text("silicio", 300, 1060, 34, L.GRAY, sa, face=C.FONT_BOLD)
        P.text("nitruro de galio", 780, 1060, 34, L.FG, ga, face=C.FONT_BOLD)
        sparks(P, 300, 860, t, c["cal"] - 0.2, 14, a=sa, seed=3)
        sparks(P, 780, 860, t, c["pierde"], 2, a=ga, seed=5)
        k = prog(t, c["k500"] - 0.1, c["k500"] + 0.4, lambda x: x)
        if k > 0:
            with P.transform(0, 0, 0.8 + 0.2 * out_back(k), cx=780, cy=1180):
                P.text("500.000 / s", 780, 1190, 72, L.RED, clamp(k * 1.5), face=C.FONT_BLACK)
            P.text("65.000 / s", 300, 1190, 46, L.GRAY, clamp(k * 1.5), face=C.FONT_BOLD)


def cierre(P, t):
    c = CUE
    a = prog(t, c["ci0"] - 0.2, c["ci0"] + 0.3)
    if a <= 0: return
    with P.layer(a):
        # transformador antes/después
        pa = prog(t, c["ci0"], c["ci0"] + 0.4) * (1 - prog(t, c["nuevo"] - 0.4, c["nuevo"] + 0.1))
        if pa > 0:
            sh = prog(t, c["pct"] - 0.3, c["pct"] + 0.6, in_out_cubic)
            transformer(P, 540, 820, lerp(0.9, 0.9 * math.sqrt(0.4), sh), pa, t)
            P.text("hasta −60 %", 540, 1160, 96, L.RED, pa * prog(t, c["pct"], c["pct"] + 0.3), face=C.FONT_BLACK)
        # el cargador grande se encoge hasta el chico
        ca = prog(t, c["nuevo"] - 0.35, c["nuevo"] + 0.1)
        if ca > 0:
            u = prog(t, c["nuevo"] - 0.1, c["mano"] + 0.2, in_out_cubic)
            w = lerp(BIG[0], SMALL[0], u); h = lerp(BIG[1], SMALL[1], u)
            ghost = prog(t, c["mano"] - 0.2, c["mano"] + 0.3)
            charger(P, 330, 900, BIG[0], BIG[1], 0.8 * ghost, outline=True)
            charger(P, lerp(540, 770, ghost), lerp(900, 960, ghost), w, h, ca, "30 W", 1.0,
                    ring=prog(t, c["mano"], c["mano"] + 0.35))


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["w30"] = T("hook", "30"); c["chico"] = T("hook", "chico"); c["como"] = T("hook", "cómo")
    c["e0"] = T("enchufe"); c["v220"] = T("enchufe", "220"); c["nec"] = T("enchufe", "necesita")
    c["baj"] = T("enchufe", "bajarlos")
    c["c0"] = T("chip"); c["prende"] = T("chip", "prende"); c["miles"] = T("chip", "miles"); c["k65"] = T("chip", "65.000")
    c["tr0"] = T("truco"); c["rap"] = T("truco", "rápido"); c["pieza"] = T("truco", "pieza")
    c["trafo"] = T("truco", "transformador")
    c["g0"] = T("gan"); c["sil"] = T("gan", "silicio"); c["cal"] = T("gan", "calienta"); c["nit"] = T("gan", "nitruro")
    c["pierde"] = T("gan", "pierde"); c["k500"] = T("gan", "500.000")
    c["ci0"] = T("cierre"); c["pct"] = T("cierre", "60"); c["nuevo"] = T("cierre", "nuevo"); c["mano"] = T("cierre", "mano")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["k65"] - 0.2, 1.2) + 0.6 * pulse(t, c["k500"] - 0.2, 1.4) + 0.6 * prog(t, c["mano"] - 0.2, c["mano"] + 0.5)
    L.background(P, t, glow=glow)
    hook(P, t)
    enchufe(P, t)
    chip_scene(P, t)
    truco(P, t)
    gan(P, t)
    cierre(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    charger(P, 330, 980, BIG[0], BIG[1], 1, "30 W", 1)
    charger(P, 770, 1040, SMALL[0], SMALL[1], 1, "30 W", 1, ring=1)
    P.text("=", 560, 1015, 90, L.GRAY, 1, face=C.FONT_BLACK)
    P.text("MISMO PODER.", 540, 560, 100, L.FG, 1, face=C.FONT_BLACK)
    P.text("¿POR QUÉ ES", 540, 670, 100, L.RED, 1, face=C.FONT_BLACK)
    P.text("TAN CHICO?", 540, 780, 100, L.RED, 1, face=C.FONT_BLACK)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.35), (0.1, "pop", 0.4), (0.35, "pop", 0.4), (c["w30"], "ding", 0.45),
            (c["chico"], "tick", 0.6), (c["como"], "pop_low", 0.5),
            (c["e0"] - 0.25, "whoosh", 0.45), (c["v220"], "thump", 0.55), (c["nec"], "pop", 0.4), (c["baj"], "whoosh_down", 0.4),
            (c["c0"] - 0.2, "whoosh", 0.4)]
    n = 24
    for k in range(n):
        cues.append((lerp(c["prende"], c["k65"] - 0.1, (k / n) ** 0.7), "tick", 0.16))
    cues += [(c["k65"], "ding", 0.6), (c["tr0"] - 0.2, "whoosh", 0.4), (c["trafo"], "pop", 0.5),
             (c["g0"] - 0.2, "whoosh", 0.4), (c["cal"], "riser", 0.3), (c["nit"], "swell", 0.4), (c["k500"], "ding", 0.65),
             (c["ci0"] - 0.2, "whoosh_down", 0.4), (c["pct"], "thump", 0.55), (c["mano"], "ding", 0.6)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["tr0"], "pulse": (c["g0"], c["ci0"]), "quiet": [(c["como"] - 0.2, c["e0"] + 0.2)]}
