"""Escenas — «¿Cómo adivina tu teclado la palabra que viene?»

Teclado (hook) → fila de interruptores (palabras como símbolos) → frases con hueco (contexto) →
mapa de palabras que empieza al azar y se ordena con el entrenamiento real (suspenso → revelación)
→ embedding (16 números reales de «café») → vuelta al teclado (empalme).
Sin títulos ni banners. Las respuestas no se revelan antes que la voz (colores de categoría
solo después de «se ordenan»).
"""
from __future__ import annotations
import math
import numpy as np
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint, vignette, vband
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic, smooth

TL = None; EP = {}; CHUNKS = []; CUE = {}; D = {}
AMBER = (1.0, 0.72, 0.3); GREEN = (0.24, 0.96, 0.65)
CATCOL = {"bebida": C.CYAN, "animal": C.VIOLET, "comida": AMBER, "lugar": GREEN}
CATNAME = {"bebida": "bebidas", "animal": "animales", "comida": "comidas", "lugar": "lugares"}


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


# =============================================================== teclado
def phone(P, t, a, s, typed, sugg, sugg_a, cy=930):
    if a <= 0: return
    W_, H_ = 560, 900; cx = 540
    with P.layer(a):
        with P.transform(0, 0, s, cx=cx, cy=cy):
            x0, y0, x1, y1 = cx - W_ / 2, cy - H_ / 2, cx + W_ / 2, cy + H_ / 2
            P.rect(x0 - 6, y0 + 12, x1 + 6, y1 + 28, (0, 0, 0), 0.6, radius=62, blur=26)
            P.rect(x0, y0, x1, y1, (0.07, 0.08, 0.11), 1, radius=60)
            P.rect(x0, y0, x1, y1, C.WHITE, 0.14, stroke=2, radius=60)
            P.rect(x0 + 16, y0 + 16, x1 - 16, y1 - 16, (0.10, 0.12, 0.18), 1, radius=46)
            # campo de texto
            P.rect(x0 + 40, y0 + 330, x1 - 40, y0 + 420, (0.16, 0.18, 0.25), 1, radius=44)
            tw = P.text(typed, x0 + 76, y0 + 388, 40, C.WHITE, 1, face=C.FONT_MED, align="left")
            if (t * 2) % 2 < 1.2:
                P.line(x0 + 82 + tw, y0 + 350, x0 + 82 + tw, y0 + 402, C.CYAN, 1, w=4)
            # barra de sugerencias
            sy = y0 + 500
            P.rect(x0 + 24, sy - 40, x1 - 24, sy + 40, (0.13, 0.15, 0.21), 1, radius=14)
            for k in range(3):
                xs = x0 + 24 + (k + 0.5) * (W_ - 48) / 3
                if k: P.line(x0 + 24 + k * (W_ - 48) / 3, sy - 24, x0 + 24 + k * (W_ - 48) / 3, sy + 24, C.WHITE, 0.15, w=2)
                ak = sugg_a[k] if k < len(sugg_a) else 0
                if ak > 0 and k < len(sugg):
                    with P.transform(0, (1 - out_back(ak)) * 20, 1, cx=xs, cy=sy):
                        P.text(sugg[k], xs, sy + 13, 36, C.CYAN, ak, face=C.FONT_BOLD)
            # teclas
            rows = ["qwertyuiop", "asdfghjklñ", "zxcvbnm"]
            for r, row in enumerate(rows):
                n = len(row); kw = (W_ - 60) / 10
                ox = cx - n * kw / 2
                for k, ch in enumerate(row):
                    kx, ky = ox + k * kw, y0 + 580 + r * 74
                    P.rect(kx + 4, ky, kx + kw - 4, ky + 62, (0.2, 0.22, 0.3), 1, radius=10)
                    P.text(ch, kx + kw / 2, ky + 42, 28, C.WHITE, 0.85, face=C.FONT_MED)
            P.rect(cx - 150, y0 + 806, cx + 150, y0 + 864, (0.2, 0.22, 0.3), 1, radius=10)


def teclado(P, t):
    c = CUE
    a = 1 - prog(t, c["sim0"] - 0.2, c["sim0"] + 0.4)
    a2 = prog(t, c["cie0"] - 0.2, c["cie0"] + 0.5)
    sugg = ["café", "té", "mate"]
    if a > 0:
        typed = "Me tomé un"[:max(0, min(10, int(t * 30) + 2))]
        sa = [prog(t, c["s_cafe"] + k * 0.3 - 0.1, c["s_cafe"] + k * 0.3 + 0.25) for k in range(3)]
        s = lerp(1.0, 0.8, prog(t, c["sim0"] - 0.2, c["sim0"] + 0.4))
        phone(P, t, a, s, typed, sugg, sa)
        aq = window(t, c["como"] - 0.1, c["sim0"], 0.3, 0.3)
        if aq > 0:
            P.text("?", 900, 520, 170, C.CYAN, out_back(prog(t, c["como"] - 0.1, c["como"] + 0.3)) * aq, face=C.FONT_BLACK, glow=0.7)
    if a2 > 0:
        sa = [prog(t, c["barrio"] + k * 0.25 - 0.2, c["barrio"] + k * 0.25 + 0.2) for k in range(3)]
        phone(P, t, a2, 1.0, "Me tomé un", sugg, sa)


# =============================================================== palabras como símbolos (interruptores)
WORDS_ROW = ["café", "té", "perro", "pan", "playa", "mate", "gato", "queso"]


def simbolos(P, t):
    c = CUE
    a = window(t, c["sim0"] - 0.1, c["int0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    with P.layer(a):
        # «café» como simple símbolo, antes de volverse interruptor
        ab = window(t, c["sim0"] - 0.1, c["interruptor"] + 0.2, 0.4, 0.4)
        if ab > 0:
            P.text("café", 540, 860, 150, C.WHITE, ab, face=C.FONT_BLACK)
            P.text("para el computador: un símbolo, sin significado", 540, 960, 30, C.GRAY,
                   ab * prog(t, c["sim0"] + 0.6, c["sim0"] + 1.2), face=C.FONT_MED)
        n = 22; sw = 40; x0 = 540 - n * sw / 2
        rows = [("café", 0, 640), ("té", 1, 800), ("perro", 2, 960)]
        for k, (w, on, y) in enumerate(rows):
            ak = prog(t, c["interruptor"] - 0.4 + 0.25 * k, c["interruptor"] + 0.25 * k)
            if ak <= 0: continue
            P.text(w, x0 - 20, y + 12, 34, C.WHITE, ak, face=C.FONT_BOLD, align="right")
            for j in range(n):
                lit = j == on
                P.rect(x0 + j * sw + 4, y - 22, x0 + (j + 1) * sw - 4, y + 22, C.CYAN if lit else (0.18, 0.2, 0.28), ak, radius=8)
                if lit: P.rect(x0 + j * sw, y - 26, x0 + (j + 1) * sw, y + 26, C.CYAN, 0.35 * ak, blur=10, radius=8)
            P.text("…", x0 + n * sw + 30, y + 12, 34, C.GRAY, ak, face=C.FONT_BOLD)
        P.text("una fila de interruptores: uno por cada palabra del idioma", 540, 1080, 26, C.GRAY,
               prog(t, c["interruptor"] + 0.3, c["interruptor"] + 0.8), face=C.FONT_MED)
        # misma distancia
        ad = prog(t, c["distintos"] - 0.3, c["distintos"] + 0.3)
        if ad > 0:
            P.c.drawArc(skia.Rect(x0 - 220, 640, x0 - 120, 800), 90, 180, False, paint(C.PINK, ad, stroke=5))
            P.text("tan distintos", x0 - 250, 735, 0, C.PINK, 0)
        ap = prog(t, c["perro"] - 0.3, c["perro"] + 0.3)
        if ap > 0:
            P.c.drawArc(skia.Rect(x0 - 260, 640, x0 - 100, 960), 90, 180, False, paint(C.PINK, ap, stroke=5))
            P.rect(240, 1150, 840, 1225, C.BG, 0.9 * ap, radius=36)
            P.rich([("café↔té", C.WHITE), ("  =  ", C.PINK), ("café↔perro", C.WHITE)], 540, 1202, 40, ap, face=C.FONT_BOLD)
        # conflicto: no puede adivinar
        aq = window(t, c["adivinar"] - 0.3, c["int0"] + 0.2, 0.3, 0.3)
        if aq > 0:
            P.text("?", 540, 520, 150, C.PINK, out_back(aq), face=C.FONT_BLACK, glow=0.6)


# =============================================================== el contexto
SENTS = [["me", "tomé", "un", "_", "caliente"], ["pedí", "un", "_", "en", "la", "cafetería"], ["un", "_", "caliente", "por", "favor"]]
HIL = {"tomé", "pedí", "caliente"}


def contexto(P, t):
    c = CUE
    a = window(t, c["int0"] - 0.1, c["jue0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    from reelforge.draw import font
    f = font(46, C.FONT_BOLD)
    with P.layer(a):
        for k, s in enumerate(SENTS):
            y = 640 + k * 150
            ak = prog(t, c["rodeados"] - 0.4 + 0.3 * k, c["rodeados"] + 0.3 * k)
            if ak <= 0: continue
            ws = [f.measureText(w if w != "_" else "chocolate") + 24 for w in s]
            x = 540 - sum(ws) / 2
            fill = ["café", "té"][int((t - c["rodeados"]) / 1.1 + k) % 2]
            for w, wd in zip(s, ws):
                if w == "_":
                    P.rect(x + 4, y - 44, x + wd - 4, y + 18, C.CYAN, 0.18 * ak, radius=12)
                    P.rect(x + 4, y - 44, x + wd - 4, y + 18, C.CYAN, 0.8 * ak, stroke=3, radius=12)
                    P.text(fill, x + wd / 2, y, 44, C.CYAN, ak, face=C.FONT_BOLD)
                else:
                    hi = prog(t, c["tome"] - 0.2, c["tome"] + 0.3) if w in HIL else 0
                    P.text(w, x + wd / 2, y, 44, lerp_c(C.WHITE, C.VIOLET, hi), ak, face=C.FONT_BOLD)
                    if hi > 0: P.line(x + 14, y + 16, x + wd - 14, y + 16, C.VIOLET, hi * ak, w=5)
                x += wd
        ad = prog(t, c["dime"] - 0.3, c["dime"] + 0.4)
        if ad > 0:
            P.rect(170, 1110, 910, 1230, C.BG2, 0.9 * ad, radius=30)
            P.text("«Dime con quién andas...", 540, 1158, 36, C.WHITE, ad, face=C.FONT_SEMI)
            P.text("y te diré quién eres»", 540, 1208, 36, C.WHITE, prog(t, c["dire"] - 0.2, c["dire"] + 0.3), face=C.FONT_SEMI)


# =============================================================== puentes visuales (sin pantallas vacías)
def piensa(P, t):
    c = CUE
    a = window(t, c["int0"] - 0.1, c["rodeados"] + 0.3, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        bob = 8 * math.sin(t * 2.2)
        P.text("café", 330, 900 + bob, 96, C.CYAN, 1, face=C.FONT_BLACK, glow=0.4)
        P.text("té", 750, 900 - bob, 96, C.CYAN, 1, face=C.FONT_BLACK, glow=0.4)
        P.text("?", 540, 890, 110, C.WHITE, out_back(prog(t, c["int0"] + 0.2, c["int0"] + 0.6)), face=C.FONT_BLACK)
        P.text("tú sabes que se parecen", 540, 1040, 32, C.GRAY, prog(t, c["int0"] + 0.4, c["int0"] + 0.9), face=C.FONT_MED)


def juego_intro(P, t):
    c = CUE
    a = window(t, c["jue0"] - 0.1, c["lugar"] + 0.5, 0.4, 0.4)
    if a <= 0: return
    sents = D["sents"]
    with P.layer(a):
        # miles de frases que pasan
        af = 1 - prog(t, c["juego"] - 0.1, c["juego"] + 0.5)
        if af > 0:
            off = (t - c["jue0"]) * 140
            for k in range(14):
                y = 560 + ((k * 52 + off) % 728)
                al = af * (1 - abs(y - 924) / 380)
                P.text(sents[(k + int(off // 728) * 14) % len(sents)], 540, y, 32, C.WHITE, max(0, al) * 0.85, face=C.FONT_MED)
            n = int(6000 * prog(t, c["jue0"] + 0.3, c["juego"], out_cubic))
            P.text(f"{n:,} frases".replace(",", "."), 540, 520, 36, C.CYAN, af, face=C.FONT_BOLD)
        # el juego: adivinar la siguiente
        ag = prog(t, c["juego"] - 0.1, c["juego"] + 0.4) * (1 - prog(t, c["lugar"] - 0.1, c["lugar"] + 0.4))
        if ag > 0:
            P.rect(110, 760, 970, 1060, C.BG2, 0.95 * ag, radius=30)
            P.text("el  perro  come", 470, 890, 52, C.VIOLET, ag, face=C.FONT_BOLD)
            P.rect(700, 836, 930, 910, C.CYAN, 0.18 * ag + 0.1 * pulse(t % 1.0, 0, 1.0), radius=14)
            P.rect(700, 836, 930, 910, C.CYAN, ag, stroke=3, radius=14)
            ad = prog(t, c["adivinar"] - 0.2, c["adivinar"] + 0.3)
            guesses = ["parque", "té", "pan", "queso", "pollo"]
            if ad > 0:
                k = int((t - c["adivinar"]) * 2.5) % len(guesses)
                P.text(guesses[k], 815, 890, 44, C.CYAN, ad * ag, face=C.FONT_BOLD)
                P.text("✗" if guesses[k] in ("parque", "té") else "✓", 815, 990, 54,
                       C.PINK if guesses[k] in ("parque", "té") else GREEN, ad * ag, face=C.FONT_BLACK)
            P.text("palabras anteriores", 470, 960, 26, C.GRAY, ag, face=C.FONT_MED)


# =============================================================== el mapa de palabras (entrenamiento real)
BOX = (130, 600, 950, 1220)


def map_pos(t):
    """Interpola entre instantáneas reales del entrenamiento según el guion."""
    c = CUE
    keys = D["snap_keys"]
    # al azar hasta «se equivoca»; luego pasos tempranos; en la revelación, el resto (lento)
    if t < c["mueve"]:
        return D["snaps"][keys[0]], 0
    if t < c["rev0"]:
        u = prog(t, c["mueve"], c["rev0"], lambda v: v) * 0.35
    else:
        u = 0.35 + 0.65 * prog(t, c["rev0"], c["ordenan"] + 0.4, in_out_cubic)
    fk = u * (len(keys) - 1)
    k0 = int(min(len(keys) - 2, fk)); w = fk - k0
    A, B = D["snaps"][keys[k0]], D["snaps"][keys[k0 + 1]]
    return A + (B - A) * smooth(w), u


def mapa(P, t):
    c = CUE
    a = window(t, c["lugar"] - 0.2, c["vec0"] + 0.4, 0.5, 0.5)
    if a <= 0: return
    pos, u = map_pos(t)
    foc, cats = D["focus"], D["cats"]
    colors_on = prog(t, c["ordenan"] + 0.2, c["ordenan"] + 0.9)
    pos = pos + D["ring"] * prog(t, c["ordenan"] - 0.3, c["ordenan"] + 0.6, in_out_cubic)
    shrink = prog(t, c["nom0"] - 0.2, c["nom0"] + 0.6, in_out_cubic) * (1 - prog(t, c["cie0"] - 0.4, c["cie0"]))
    with P.layer(a):
        with P.layer(1 - 0.8 * shrink):
            P.rect(BOX[0] - 20, BOX[1] - 20, BOX[2] + 20, BOX[3] + 20, C.BG2, 0.85, radius=28)
            # barrios (solo después de la revelación)
            for cat in CATCOL:
                ac = prog(t, c["cat_" + cat] - 0.2, c["cat_" + cat] + 0.4)
                if ac <= 0: continue
                pts = np.array([pos[i] for i in range(len(foc)) if cats[i] == cat])
                cx_, cy_ = pts.mean(0)
                X, Y = lerp(BOX[0], BOX[2], (cx_ + 1.15) / 2.3), lerp(BOX[3], BOX[1], (cy_ + 1.15) / 2.3)
                r = 30 + np.abs(pts - pts.mean(0)).max() * 400 / 2.3
                P.circle(X, Y, r + 30, CATCOL[cat], 0.12 * ac)
                P.circle(X, Y, r + 30, CATCOL[cat], 0.7 * ac, stroke=3)
                P.text(CATNAME[cat], X, Y - r - 44, 32, CATCOL[cat], ac, face=C.FONT_BOLD)
            for i, w in enumerate(foc):
                x = lerp(BOX[0], BOX[2], (pos[i][0] + 1.15) / 2.3)
                y = lerp(BOX[3], BOX[1], (pos[i][1] + 1.15) / 2.3)
                col = lerp_c(C.WHITE, CATCOL[cats[i]], colors_on)
                ai = prog(t, c["lugar"] + 0.03 * i, c["lugar"] + 0.03 * i + 0.3)
                P.circle(x, y, 10, col, ai)
                P.text(w, x, y - 18, 26, col, ai * 0.95, face=C.FONT_SEMI)
        # el juego en una línea
        ag = window(t, c["lugar"], c["rev0"], 0.3, 0.4)
        P.text("cada palabra, un lugar (al azar)", 540, 540, 30, C.WHITE, ag, face=C.FONT_SEMI)
        ae = window(t, c["mueve"], c["rev0"], 0.3, 0.3)
        if ae > 0:
            P.text("✗  falló → los lugares se corrigen un poco", 540, 1290, 26, C.PINK, ae, face=C.FONT_SEMI)
        an = window(t, c["animal"] - 0.2, c["nom0"], 0.3, 0.3)
        P.text("nadie le dijo qué era un animal", 540, 1290, 26, C.VIOLET, an, face=C.FONT_SEMI)


def embedding(P, t):
    c = CUE
    a = window(t, c["nom0"] - 0.1, c["vec0"] + 0.4, 0.5, 0.4)
    if a <= 0: return
    v = np.array(D["vec_cafe"]); v = v / np.abs(v).max()
    with P.layer(a):
        P.rect(80, 960, 1000, 1280, C.BG, 0.85 * a, radius=30)
        P.pill("EMBEDDING", 540, 1035, 44, C.CYAN, out_back(prog(t, c["emb"] - 0.2, c["emb"] + 0.3)))
        P.text("el lugar de «café»: 16 números aprendidos", 540, 1105, 28, C.WHITE, a, face=C.FONT_SEMI)
        bw = 40; x0 = 540 - 16 * bw / 2
        for k, val in enumerate(v):
            h = 70 * val * prog(t, c["emb"] + 0.03 * k, c["emb"] + 0.03 * k + 0.3)
            P.rect(x0 + k * bw + 4, 1190 - max(h, 0), x0 + (k + 1) * bw - 4, 1190 - min(h, 0), C.CYAN if val > 0 else C.VIOLET, a, radius=4)
        P.text("(el mapa los muestra aplanados en 2)", 540, 1300, 24, C.GRAY, a, face=C.FONT_MED)


# =============================================================== materia: vector, tabla, lectura y predicción
def cells(P, vals, x0, y, cw=40, ch=40, a=1.0, vmax=3.0, labels=False, size=16):
    for k, v in enumerate(vals):
        u = clamp(abs(v) / vmax)
        col = lerp_c((0.16, 0.18, 0.25), C.CYAN if v >= 0 else C.VIOLET, 0.25 + 0.75 * u)
        P.rect(x0 + k * cw + 2, y, x0 + (k + 1) * cw - 2, y + ch, col, a, radius=5)
        if labels:
            P.text(f"{v:.1f}".replace(".", ",").replace("-", "−"), x0 + k * cw + cw / 2, y + ch / 2 + 6, size, C.WHITE, a, face=C.FONT_BOLD)


def vector_scene(P, t):
    c = CUE
    a = window(t, c["vec0"] - 0.1, c["tab0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    with P.layer(a):
        # mapa de la ciudad: (este, norte)
        am = window(t, c["vec0"] + 0.3, c["dieciseis"] + 0.2, 0.4, 0.4)
        if am > 0:
            gx0, gy0, s_ = 220, 1120, 110
            with P.layer(am):
                for k in range(6):
                    P.line(gx0 + k * s_, gy0, gx0 + k * s_, gy0 - 5 * s_, C.WHITE, 0.12, w=6)
                    P.line(gx0, gy0 - k * s_, gx0 + 5 * s_, gy0 - k * s_, C.WHITE, 0.12, w=6)
                hx, hy = gx0 + 3 * s_, gy0 - 2 * s_
                P.circle(gx0, gy0, 10, C.WHITE, 1)
                ue = prog(t, c["este"] - 0.2, c["este"] + 0.6, in_out_cubic)
                if ue > 0:
                    P.arrow(gx0, gy0 + 40, gx0 + 3 * s_ * ue, gy0 + 40, C.CYAN, 1, w=6, head=20)
                    P.text("3 al este", gx0 + 1.5 * s_, gy0 + 90, 30, C.CYAN, ue, face=C.FONT_BOLD)
                un = prog(t, c["norte"] - 0.2, c["norte"] + 0.6, in_out_cubic)
                if un > 0:
                    P.arrow(gx0 - 40, gy0, gx0 - 40, gy0 - 2 * s_ * un, C.VIOLET, 1, w=6, head=20)
                    P.text("2 al norte", gx0 - 60, gy0 - s_, 30, C.VIOLET, un, face=C.FONT_BOLD, align="right")
                # casa
                P.rect(hx - 34, hy - 20, hx + 34, hy + 34, C.WHITE, 1, radius=4)
                pth = skia.Path(); pth.moveTo(hx - 46, hy - 16); pth.lineTo(hx, hy - 58); pth.lineTo(hx + 46, hy - 16); pth.close()
                P.c.drawPath(pth, paint(C.WHITE, 1))
                av = prog(t, c["vector"] - 0.3, c["vector"] + 0.3)
                P.text("tu casa = (3, 2)", 540, 540, 52, C.WHITE, prog(t, c["norte"] + 0.6, c["norte"] + 1.0), face=C.FONT_BLACK)
                P.pill("VECTOR: una lista de números que dice dónde está algo", 540, 610, 28, C.CYAN, out_back(av))
        # los 16 números reales de «café»
        a16 = prog(t, c["dieciseis"] - 0.4, c["dieciseis"] + 0.3)
        if a16 > 0:
            v = np.array(D["rows"]["café"])
            jit = prog(t, c["ajusta"] - 0.2, c["ajusta"] + 2.2, out_cubic) if t > c["ajusta"] - 0.2 else 1.0
            rng = np.random.default_rng(int(t * 6))
            if 0 < jit < 1:
                v = v * jit + rng.normal(0, 1.2, 16) * (1 - jit)
            P.text("café =", 540, 640, 44, C.CYAN, a16, face=C.FONT_BLACK)
            for row in range(2):
                cells(P, v[row * 8:(row + 1) * 8], 540 - 4 * 110, 700 + row * 130, cw=110, ch=96, a=a16, vmax=3.2,
                      labels=True, size=30)
            P.text("16 números = un lugar en un mapa de 16 direcciones", 540, 990, 28, C.WHITE, a16, face=C.FONT_SEMI)
            P.text("nadie elige estos números: los ajusta el juego", 540, 1040, 28, C.GRAY,
                   prog(t, c["ajusta"] - 0.2, c["ajusta"] + 0.3), face=C.FONT_MED)
            ap = prog(t, c["aplana"] - 0.3, c["aplana"] + 0.4)
            if ap > 0:
                P.arrow(540, 1080, 540, 1150, C.WHITE, ap, w=5, head=18)
                P.text("aplanado a 2 → un punto en el mapa", 540, 1200, 30, C.CYAN, ap, face=C.FONT_BOLD)


TABLE_WORDS = ["café", "té", "mate", "perro", "gato", "pan", "queso", "parque"]


def tabla_scene(P, t):
    c = CUE
    a = window(t, c["tab0"] - 0.1, c["leer0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    cw, ch = 40, 52
    x0, y0 = 300, 640
    with P.layer(a):
        P.text("tabla de embeddings", 540, 590, 32, C.WHITE, 1, face=C.FONT_BOLD)
        out = prog(t, c["saca"] - 0.1, c["saca"] + 0.9, in_out_cubic)
        for r, w in enumerate(TABLE_WORDS):
            ar = prog(t, c["tab0"] + 0.06 * r, c["tab0"] + 0.06 * r + 0.3)
            y = y0 + r * (ch + 8)
            if w == "café" and out > 0:
                y = lerp(y, 1150, out)
            P.text(w, x0 - 16, y + ch / 2 + 10, 28, C.CYAN if (w == "café" and out > 0) else C.WHITE, ar, face=C.FONT_SEMI, align="right")
            cells(P, D["rows"][w], x0, y, cw=cw, ch=ch, a=ar)
            if w == "café" and out > 0.3:
                P.rect(x0 - 6, y - 6, x0 + 16 * cw + 6, y + ch + 6, C.CYAN, out, stroke=3, radius=8)
        # columna de interruptores (one-hot): solo «café» encendido
        ai = prog(t, c["interr"] - 0.3, c["interr"] + 0.3)
        if ai > 0:
            P.text("interruptor", 100, y0 - 20, 22, C.GRAY, ai, face=C.FONT_MED)
            for r, w in enumerate(TABLE_WORDS):
                y = y0 + r * (ch + 8)
                lit = w == "café"
                P.rect(76, y + 6, 124, y + ch - 6, C.CYAN if lit else (0.18, 0.2, 0.28), ai, radius=8)
                if lit: P.rect(70, y, 130, y + ch, C.CYAN, 0.35 * ai, blur=10, radius=8)
        if out > 0.5:
            P.text("el interruptor de «café» elige su fila", 540, 1250, 28, C.CYAN, out, face=C.FONT_SEMI)


def leer_scene(P, t):
    c = CUE
    a = window(t, c["leer0"] - 0.1, c["pred0"] + 0.3, 0.5, 0.4)
    if a <= 0: return
    ox, oy, L = 300, 1000, 520
    s_te, s_pe = D["sim_cafe_te"], D["sim_cafe_perro"]
    base = math.radians(28)
    ang = {"café": base, "té": base + math.acos(clamp(s_te, -1, 1)), "perro": base + math.acos(clamp(s_pe, -1, 1))}
    cols = {"café": C.CYAN, "té": C.CYAN, "perro": C.VIOLET}
    with P.layer(a):
        # «¿cómo se lee?»: el vector de café, número por número… (se tacha)
        ar = window(t, c["leer0"], c["comparando"] + 0.2, 0.4, 0.4)
        if ar > 0:
            v = np.array(D["rows"]["café"])
            P.text("café =", 540, 760, 40, C.CYAN, ar, face=C.FONT_BLACK)
            for row in range(2):
                cells(P, v[row * 8:(row + 1) * 8], 540 - 4 * 100, 800 + row * 110, cw=100, ch=86, a=ar, vmax=3.2,
                      labels=True, size=28)
            ax = prog(t, c["numero"] - 0.1, c["numero"] + 0.4)
            if ax > 0:
                P.line(130, 820, 130 + 820 * ax, 990, C.PINK, ar, w=7)
                P.text("¿número por número? no", 540, 1070, 32, C.PINK, ar * ax, face=C.FONT_BOLD)
        aa = prog(t, c["comparando"] - 0.3, c["comparando"] + 0.4)
        P.circle(ox, oy, 8, C.WHITE, aa)
        for k, w in enumerate(["café", "té", "perro"]):
            ak = prog(t, c["comparando"] - 0.2 + 0.3 * k, c["comparando"] + 0.3 * k + 0.3)
            if ak <= 0: continue
            th = ang[w]
            P.arrow(ox, oy, ox + L * math.cos(th) * ak, oy - L * math.sin(th) * ak, cols[w], ak, w=6, head=24)
            P.text(w, ox + (L + 40) * math.cos(th), oy - (L + 40) * math.sin(th) + 10, 34, cols[w], ak, face=C.FONT_BOLD)
        al = prog(t, c["lado"] - 0.3, c["lado"] + 0.4)
        if al > 0:
            P.c.drawArc(skia.Rect(ox - 220, oy - 220, ox + 220, oy + 220), -math.degrees(ang["perro"]),
                        math.degrees(ang["perro"] - ang["café"]), False, paint(C.VIOLET, al, stroke=4))
            P.text("apuntan a lados distintos", 680, 640, 26, C.VIOLET, al, face=C.FONT_SEMI)
            P.text("casi el mismo lado", 860, 900, 26, C.CYAN, al, face=C.FONT_SEMI)
        # escala de 0 a 1
        asc = prog(t, c["escala"] - 0.3, c["escala"] + 0.3)
        if asc > 0:
            x0, x1, y = 140, 940, 1150
            P.line(x0, y, x1, y, C.DIM, asc, w=8)
            P.text("0", x0, y + 44, 26, C.GRAY, asc, face=C.FONT_MED); P.text("1", x1, y + 44, 26, C.GRAY, asc, face=C.FONT_MED)
            P.text("parecido", 540, y - 40, 26, C.GRAY, asc, face=C.FONT_MED)
            for w, s_, tt, col in (("café–té", s_te, c["casi"], C.CYAN), ("café–perro", s_pe, c["cero"], C.VIOLET)):
                am = prog(t, tt - 0.3, tt + 0.4)
                if am <= 0: continue
                x = lerp(x0, x1, clamp(s_)) * am + x0 * (1 - am)
                P.glow_circle(x, y, 14, col, am)
                P.text(f"{w}: {s_:.3f}".replace(".", ",") if s_ > 0.99 else f"{w}: {s_:.2f}".replace(".", ","), x, y + 50 if col == C.CYAN else y + 90, 28, col, am, face=C.FONT_BOLD)


def prediccion_scene(P, t):
    c = CUE
    a = window(t, c["pred0"] - 0.1, c["cie0"] + 0.2, 0.5, 0.4)
    if a <= 0: return
    cw, ch = 34, 34
    x0 = 540 - 8 * cw
    with P.layer(a):
        for k, w in enumerate(["me", "tomé", "un"]):
            ak = prog(t, c["junta"] - 0.2 + 0.25 * k, c["junta"] + 0.25 * k + 0.3)
            y = 560 + k * 46
            P.text(f"«{w}»", x0 - 14, y + 26, 26, C.WHITE, ak, face=C.FONT_SEMI, align="right")
            cells(P, D["rows"][w], x0, y, cw=cw, ch=ch, a=ak)
        aj = prog(t, c["junta"] + 0.9, c["junta"] + 1.4)
        if aj > 0:
            P.text("juntos (promedio)", x0 - 14, 728 + 24, 24, C.CYAN, aj, face=C.FONT_BOLD, align="right")
            cells(P, D["ctx_avg"], x0, 728, cw=cw, ch=ch, a=aj)
            P.rect(x0 - 4, 724, x0 + 16 * cw + 4, 766, C.CYAN, aj, stroke=3, radius=6)
        # parecido con cada palabra → probabilidad
        ac = prog(t, c["cada"] - 0.3, c["cada"] + 0.3)
        cand = ["mate", "té", "café", "perro", "pan", "parque"]
        sc, pr = D["kb_scores"], D["kb_probs"]
        smax = max(sc.values())
        topr = prog(t, c["probab"] - 0.2, c["probab"] + 0.8, in_out_cubic)
        for k, w in enumerate(cand):
            y = 830 + k * 62
            ak = ac * prog(t, c["cada"] + 0.1 * k, c["cada"] + 0.1 * k + 0.3)
            if ak <= 0: continue
            P.text(w, 250, y + 28, 32, C.CYAN if pr[w] > 0.05 else C.WHITE, ak, face=C.FONT_BOLD, align="right")
            v_sc = clamp(max(sc[w], 0) / smax); v_pr = clamp(pr[w] / 0.25)
            v = lerp(v_sc, v_pr, topr)
            P.rect(280, y + 4, 280 + 560 * max(v, 0.005), y + 40, C.CYAN if pr[w] > 0.05 else C.DIM, ak, radius=10)
            lab = f"puntaje {sc[w]:.1f}".replace(".", ",").replace("-", "−") if topr < 0.5 else f"{pr[w] * 100:.0f} %"
            P.text(lab, 860, y + 32, 28, C.WHITE, ak, face=C.FONT_SEMI, align="left")
        P.text("el resto se reparte entre otras bebidas (chocolate, jugo)", 540, 1225, 24, C.GRAY, topr, face=C.FONT_MED)
        P.text("(el modelo usa un segundo vector por palabra para esta comparación)", 540, 1262, 21, C.GRAY, ac, face=C.FONT_MED)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE, D
    TL, EP, D = tl, episode, dict(data)
    keys = sorted(D["snaps"].keys(), key=float)
    D["snap_keys"] = keys
    # cada instantánea a su propia escala (el estado inicial es diminuto, pero su desorden es real)
    sn = {}
    for k, v in D["snaps"].items():
        v = np.array(v); v = v - v.mean(0); sn[k] = v / (np.abs(v).max(0) + 1e-9)
    D["snaps"] = sn
    # anillo de legibilidad: dentro de un barrio, las palabras quedan casi encima unas de otras
    cats = D["cats"]; ring = np.zeros((len(cats), 2))
    for cat in set(cats):
        ids = [i for i, x in enumerate(cats) if x == cat]
        for j, i in enumerate(ids):
            ang = 2 * math.pi * j / len(ids)
            ring[i] = (0.17 * math.cos(ang), 0.2 * math.sin(ang))
    D["ring"] = ring
    c = {}
    c["s_cafe"] = T("hook", "café"); c["como"] = T("hook", "Cómo")
    c["sim0"] = T("simbolos"); c["interruptor"] = T("simbolos", "interruptor"); c["distintos"] = T("simbolos", "distintos")
    c["perro"] = T("simbolos", "perro"); c["adivinar"] = T("conflicto", "adivinar")
    c["int0"] = T("intuicion"); c["rodeados"] = T("intuicion", "rodeados"); c["tome"] = T("intuicion", "tomé")
    c["dime"] = T("intuicion", "Dime"); c["dire"] = T("intuicion", "diré")
    import experiment as X
    D["sents"] = [" ".join(w) for w in X.corpus(80, seed=3)]
    c["adivinar"] = T("juego", "adivinar")
    c["jue0"] = T("juego"); c["juego"] = T("juego", "juego"); c["lugar"] = T("juego", "lugar"); c["mueve"] = T("juego", "mueve")
    c["rev0"] = T("revelacion"); c["ordenan"] = T("revelacion", "ordenan")
    c["cat_bebida"] = T("revelacion", "bebidas"); c["cat_animal"] = T("revelacion", "animales")
    c["cat_comida"] = T("revelacion", "comidas"); c["cat_lugar"] = T("revelacion", "lugares")
    c["animal"] = T("revelacion", "animal")
    c["nom0"] = T("nombre"); c["emb"] = T("nombre", "embedding")
    c["vec0"] = T("vector"); c["este"] = T("vector", "este"); c["norte"] = T("vector", "norte")
    c["vector"] = T("vector", "vector"); c["dieciseis"] = T("vector", "dieciséis"); c["ajusta"] = T("vector", "ajusta")
    c["aplana"] = T("vector", "aplana")
    c["tab0"] = T("tabla"); c["interr"] = T("tabla", "interruptor"); c["saca"] = T("tabla", "saca")
    c["leer0"] = T("leer"); c["comparando"] = T("leer", "comparándolo"); c["numero"] = T("leer", "número"); c["lado"] = T("leer", "lado")
    c["escala"] = T("leer", "escala"); c["casi"] = T("leer", "casi"); c["cero"] = T("leer", "cero", 1)
    c["pred0"] = T("prediccion"); c["junta"] = T("prediccion", "junta"); c["cada"] = T("prediccion", "cada")
    c["probab"] = T("prediccion", "probabilidad"); c["sug"] = T("prediccion", "sugerencias")
    c["cie0"] = T("cierre"); c["barrio"] = c["cie0"] + 0.2; c["anda"] = T("cierre", "anda")
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    P.background(t, accent=0.25 * window(t, c["ordenan"], c["nom0"], 0.6, 0.6))
    teclado(P, t)
    simbolos(P, t)
    contexto(P, t)
    piensa(P, t)
    juego_intro(P, t)
    mapa(P, t)
    embedding(P, t)
    vector_scene(P, t)
    tabla_scene(P, t)
    leer_scene(P, t)
    prediccion_scene(P, t)
    ad = window(t, c["jue0"], c["vec0"], 0.4, 0.4) + window(t, c["pred0"], c["cie0"], 0.4, 0.4)
    P.text("Modelo propio con frases de ejemplo · los teclados reales usan modelos mucho más grandes", 540, 1330, 21,
           C.GRAY, ad * 0.9, face=C.FONT_MED)
    vignette(P, 0.45)
    vband(P, 1250, C.H, 0.0, 0.85)
    SUB.draw(P, CHUNKS, t)


def draw_cover(P, t=0.0):
    P.background(1.0, accent=0.6)
    phone(P, 3.0, 1.0, 0.9, "Me tomé un", ["café", "té", "mate"], [1, 1, 1], cy=1060)
    P.text("¿CÓMO ADIVINA", 540, 400, 92, C.WHITE, 1, face=C.FONT_BLACK)
    P.text("TU TECLADO?", 540, 505, 92, C.CYAN, 1, face=C.FONT_BLACK, glow=0.5)
    P.text(C.BRAND, 540, 1830, 32, C.VIOLET, 1, face=C.FONT_BOLD, tracking=4)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.4)] + [(0.05 + k / 30, "tick", 0.35) for k in range(0, 9, 2)]
    cues += [(c["s_cafe"] + 0.3 * k, "pop", 0.5) for k in range(3)]
    cues += [(c["como"], "riser", 0.4), (c["sim0"] - 0.2, "whoosh", 0.5), (c["interruptor"], "pop", 0.5),
             (c["perro"], "pop_low", 0.6), (c["adivinar"], "thump", 0.5), (c["int0"], "whoosh", 0.5),
             (c["rodeados"], "pop", 0.4), (c["dime"], "swell", 0.5), (c["jue0"], "whoosh", 0.5),
             (c["lugar"], "riser", 0.3), (c["mueve"], "pop_low", 0.4), (c["rev0"], "riser", 0.6),
             (c["ordenan"], "ding", 0.8), (c["cat_bebida"], "pop", 0.5), (c["cat_animal"], "pop", 0.5),
             (c["cat_comida"], "pop", 0.5), (c["cat_lugar"], "pop", 0.5), (c["emb"], "swell", 0.6),
             (c["vec0"], "whoosh", 0.5), (c["vector"], "pop", 0.5), (c["dieciseis"], "riser", 0.4),
             (c["tab0"], "whoosh", 0.5), (c["saca"], "pop", 0.6), (c["leer0"], "whoosh", 0.5),
             (c["casi"], "ding", 0.5), (c["cero"], "pop_low", 0.5), (c["pred0"], "whoosh", 0.5),
             (c["probab"], "riser", 0.4), (c["sug"], "ding", 0.7),
             (c["cie0"] - 0.2, "whoosh_down", 0.5), (c["barrio"], "pop", 0.5), (c["anda"], "ding", 0.7)]
    return cues


def music_kw(tl):
    c = CUE
    return {"arp_from": c["jue0"], "pulse": (c["pred0"], c["cie0"]), "quiet": [(c["rev0"] - 0.2, c["ordenan"])]}
