"""Escenas — «¿Por qué la IA te da la razón… aunque no la tengas?» (stheq.ia, motion graphics).

Hilo visual: un chat dentro de un celular.
Gancho: «¿Cuánto es 7 × 8?» → «56» ✓ → «¿Estás segura? Creo que es 54.» → «Tienes razón: es 54.» ✗ → «?» →
el ícono de la IA sale del chat y crece: entrenamiento. Dos respuestas salen de la IA, una persona elige la que
le gusta (✓), la elegida suelta un punto que llena la barra «puntos» y las perillas de la IA se mueven, una y
otra vez → la trampa: «¡Tienes razón!» contra «En realidad, no.»; la persona sonríe y gana la que halaga, aunque
la otra sea la correcta → cuadrícula de 100 preguntas que se pinta hasta 98 (Anthropic, 2023) → una
actualización recibe pulgares que caen, el medidor «complaciente» se va al rojo y la actualización se retira
(OpenAI, 2025) → «adulación», rodeada de burbujas que halagan → vuelve el chat: se borra «Creo que es 54», se
pide el cómo y llega 56 ✓ → se reconstruye el chat del gancho, un pulgar rojo sobre «Tienes razón» y el chat
vuelve al cuadro 0 (empalme).
"""
from __future__ import annotations
import math
import numpy as np
import skia
from PIL import Image
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.draw import paint
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic
from reelforge import marca as L

TL = None; EP = {}; CHUNKS = []; CUE = {}
_IMG = {}

PH = (250, 470, 830, 1280)          # marco del celular
AV_X = 300                          # ícono de la IA en el chat
BX0, BX1 = 336, 802                 # bordes de las burbujas (IA a la izquierda, persona a la derecha)
FS = 42


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


# =============================================================== piezas
def cross(P, x, y, s, a, col=None):
    if a <= 0: return
    P.line(x - 26 * s, y - 26 * s, x + 26 * s, y + 26 * s, col or L.RED, a, w=11 * s)
    P.line(x + 26 * s, y - 26 * s, x - 26 * s, y + 26 * s, col or L.RED, a, w=11 * s)


def check(P, x, y, s, a, col=None):
    if a <= 0: return
    pth = skia.Path(); pth.moveTo(x - 30 * s, y); pth.lineTo(x - 8 * s, y + 24 * s); pth.lineTo(x + 34 * s, y - 26 * s)
    P.c.drawPath(pth, paint(col or L.RED, a, 12 * s))


def sparkle(P, x, y, r, rgb, a):
    pth = skia.Path(); pth.moveTo(x, y - r)
    for k in range(4):
        ang0 = -math.pi / 2 + k * math.pi / 2
        ang1 = ang0 + math.pi / 4
        ang2 = ang0 + math.pi / 2
        P_in = (x + 0.28 * r * math.cos(ang1), y + 0.28 * r * math.sin(ang1))
        P_out = (x + r * math.cos(ang2), y + r * math.sin(ang2))
        pth.quadTo(*P_in, *P_out)
    pth.close()
    P.c.drawPath(pth, paint(rgb, a))


def avatar(P, x, y, r, a, ring=None):
    if a <= 0: return
    P.circle(x, y, r, L.CARD, a)
    P.circle(x, y, r, ring or L.FG, a, stroke=max(3, r * 0.09))
    sparkle(P, x, y, r * 0.6, L.FG, a)


def thumb(P, x, y, s, rgb, a):
    """Pulgar arriba estilizado centrado en (x, y)."""
    if a <= 0: return
    P.rect(x - 62 * s, y - 8 * s, x - 34 * s, y + 66 * s, rgb, a, radius=8 * s)            # puño de la manga
    P.rect(x - 26 * s, y - 14 * s, x + 50 * s, y + 66 * s, rgb, a, radius=16 * s)          # mano
    P.line(x - 10 * s, y - 6 * s, x + 6 * s, y - 64 * s, rgb, a, w=30 * s)                 # dedo pulgar
    for k in range(3):
        yy = y + (10 + 18 * k) * s
        P.line(x + 8 * s, yy, x + 46 * s, yy, L.BG, a * 0.6, w=3 * s)


def bubble(P, lines, side, top, a, rise=0.0, hl=0.0, size=FS, strike=0.0, dim=0.0):
    """Burbuja de chat. side 'u' (persona, derecha, blanca) o 'ia' (izquierda, gris, con ícono)."""
    if a <= 0: return None
    if isinstance(lines, str): lines = [lines]
    pad_x, pad_y, lh = 32, 24, size * 1.28
    w = max(P.text_width(s, size, C.FONT_SEMI) for s in lines) + 2 * pad_x
    h = len(lines) * lh + 2 * pad_y - (lh - size * 1.05)
    y0 = top + 26 * (1 - rise)
    if side == "u":
        x0, x1 = BX1 - w, BX1
        fill, txt = L.FG, L.BG
    else:
        x0, x1 = BX0, BX0 + w
        fill, txt = lerp_c(L.CARD, L.hx("#2A2A2A"), 1.0), L.FG
    s = 0.92 + 0.08 * rise
    cx, cy = (x0 + x1) / 2, y0 + h / 2
    with P.layer(a * (1 - 0.6 * dim)):
        with P.transform(0, 0, s, cx=cx, cy=cy):
            P.rect(x0, y0, x1, y0 + h, fill, 1, radius=30)
            if hl > 0:
                P.rect(x0 - 4, y0 - 4, x1 + 4, y0 + h + 4, L.RED, hl, stroke=5, radius=34)
            for i, s_ in enumerate(lines):
                P.text(s_, x0 + pad_x, y0 + pad_y + size * 0.82 + i * lh, size, txt, 1, face=C.FONT_SEMI, align="left")
            if strike > 0:
                P.line(x0 + 18, cy, x0 + 18 + (w - 36) * strike, cy, L.RED, 1, w=7)
            if side == "ia":
                avatar(P, AV_X, y0 + h - 26, 26, 1)
    return (x0, y0, x1, y0 + h)


def phone(P, a):
    if a <= 0: return
    x0, y0, x1, y1 = PH
    P.rect(x0, y0, x1, y1, L.hx("#111111"), a, radius=64)
    P.rect(x0, y0, x1, y1, L.DIM, a, stroke=5, radius=64)
    P.rect(540 - 60, y0 + 18, 540 + 60, y0 + 40, L.BG, a, radius=11)


def ap(t, t0, d=0.32):
    """Aparición de una burbuja: (alpha, rise)."""
    u = prog(t, t0 - 0.05, t0 + d, out_cubic)
    return u, u


# =============================================================== chat del gancho (y del cierre)
M1 = "¿Cuánto es 7 × 8?"
M3 = ["¿Estás segura?", "Creo que es 54."]
M4 = "Tienes razón: es 54."
TOPS = (520, 642, 764, 948)


def hook_chat(P, t, a, show, hl4=0.0, x4=0.0, ok2=0.0, q=0.0, thumb_a=0.0):
    """show: alphas (a1..a4) y rises para cada burbuja."""
    if a <= 0: return
    with P.layer(a):
        phone(P, 1)
        (a1, r1), (a2, r2), (a3, r3), (a4, r4) = show
        bubble(P, M1, "u", TOPS[0], a1, r1)
        b2 = bubble(P, "56", "ia", TOPS[1], a2, r2)
        if b2 and ok2 > 0:
            check(P, b2[2] + 50, (b2[1] + b2[3]) / 2, 0.9, ok2 * a2, col=L.FG)
        bubble(P, M3, "u", TOPS[2], a3, r3)
        b4 = bubble(P, M4, "ia", TOPS[3], a4, r4, hl=hl4)
        if b4 and x4 > 0:
            cross(P, b4[2] + 52, (b4[1] + b4[3]) / 2, 0.95, x4 * a4)
        if q > 0:
            P.text("?", 540, 1205 + 6 * math.sin(t * 3), 150, L.RED, q, face=C.FONT_BLACK)
        if thumb_a > 0:
            s = 1.25 * out_back(clamp(thumb_a))
            thumb(P, 640, 1150, s, L.RED, clamp(thumb_a))


def hook_scene(P, t):
    c = CUE
    a = 1 - prog(t, c["ap0"] - 0.35, c["ap0"] + 0.05, in_out_cubic)
    if a <= 0: return
    show = [(1.0, 1.0), ap(t, c["responde"]), ap(t, c["estas"]), ap(t, c["razon"])]
    ok2 = prog(t, c["bien"], c["bien"] + 0.25)
    x4 = prog(t, c["no"] - 0.05, c["no"] + 0.2)
    q = prog(t, c["porque"] - 0.15, c["porque"] + 0.25)
    with P.transform(0, 0, 1 - 0.08 * (1 - a), cx=540, cy=880):
        hook_chat(P, t, a, show, hl4=x4, x4=x4, ok2=ok2, q=q)


# =============================================================== entrenamiento (aprende → trampa)
AVC = (540, 585)
CARD_L, CARD_R = (350, 840), (730, 840)
CW, CH = 330, 200
HEAD = (540, 1085)
BAR = (330, 800, 1252)


def card(P, cx, cy, a, sel=0.0, dim=0.0, text=None, seed=0, label=None, la=0.0):
    if a <= 0: return
    x0, y0, x1, y1 = cx - CW / 2, cy - CH / 2, cx + CW / 2, cy + CH / 2
    with P.layer(a * (1 - 0.65 * dim)):
        P.rect(x0, y0, x1, y1, L.hx("#262626"), 1, radius=26)
        P.rect(x0, y0, x1, y1, lerp_c(L.DIM, L.RED, sel), 1, stroke=4 + 3 * sel, radius=26)
        if text:
            P.text(text, cx, cy + 14, 38, L.FG, 1, face=C.FONT_BOLD)
        else:
            rnd = np.random.default_rng(seed)
            for k in range(3):
                w = (0.55 + 0.4 * rnd.random()) * (CW - 70)
                P.line(x0 + 35, y0 + 58 + k * 42, x0 + 35 + w, y0 + 58 + k * 42, L.GRAY, 1, w=12)
    if sel > 0:
        check(P, x1 - 18, y0 - 6, 0.9, sel * a)
    if la > 0 and label:
        P.pill(label, cx, y0 - 44, 30, L.FG, la * a, fill_a=0.08)


def sliders(P, a, phase):
    if a <= 0: return
    for k in range(3):
        y = AVC[1] - 46 + 46 * k
        P.line(660, y, 830, y, L.DIM, a, w=6)
        u = 0.5 + 0.38 * math.sin(phase * (1.3 + 0.4 * k) + k * 1.7)
        P.circle(lerp(668, 822, u), y, 13, L.FG, a)
    for k in range(3):
        y = AVC[1] - 46 + 46 * k
        P.line(250, y, 420, y, L.DIM, a, w=6)
        u = 0.5 + 0.38 * math.sin(phase * (1.1 + 0.5 * k) + k * 2.3 + 1)
        P.circle(lerp(258, 412, u), y, 13, L.FG, a)


def train_scene(P, t):
    c = CUE
    a = prog(t, c["ap0"] - 0.25, c["ap0"] + 0.3) * (1 - prog(t, c["d0"] - 0.35, c["d0"] + 0.05, in_out_cubic))
    if a <= 0: return
    with P.layer(a):
        # ícono de la IA: viene desde el chat (burbuja «Tienes razón») y crece
        mv = prog(t, c["ap0"] - 0.35, c["ap0"] + 0.45, in_out_cubic)
        ax, ay = lerp(AV_X, AVC[0], mv), lerp(TOPS[3] + 74, AVC[1], mv)
        avatar(P, ax, ay, lerp(26, 70, mv), 1, ring=lerp_c(L.FG, L.RED, pulse(t, c["aprendio"] - 0.1, 0.7)))
        # perillas internas (se ajusta)
        sa = prog(t, c["ajusta"] - 0.2, c["ajusta"] + 0.3)
        ph = 3.2 * max(0.0, t - c["ajusta"]) * (1 - prog(t, c["tr0"], c["tr0"] + 0.6) * 0.0)
        sliders(P, sa * (1 - 0.6 * prog(t, c["tr0"] - 0.2, c["tr0"] + 0.3)), ph)

        # tarjetas: salen desde la IA
        ca = prog(t, c["dos"] - 0.1, c["dos"] + 0.45, out_cubic)
        trap = prog(t, c["tr_razon"] - 0.6, c["tr_razon"] - 0.15)      # cambian al texto de la trampa
        # ciclos de entrenamiento («una y otra vez»)
        cyc_t0 = c["otra"] - 0.2
        period = 1.05
        ncyc = 0 if t < cyc_t0 else min(2, int((t - cyc_t0) / period) + 1)
        k_cyc = (t - cyc_t0) / period if t >= cyc_t0 else -1
        # selección
        selR = prog(t, c["mas"] - 0.05, c["mas"] + 0.25)
        if 0 <= k_cyc < 2:
            u = k_cyc % 1.0
            right = int(k_cyc) % 2 == 1
            s_ = prog(u, 0.25, 0.45)
            selL_c, selR_c = (0.0, s_) if right else (s_, 0.0)
        else:
            selL_c, selR_c = None, None
        selR_eff = selR if selR_c is None else selR_c
        selL_eff = 0.0 if selL_c is None else selL_c
        if t >= cyc_t0 + 2 * period:
            selR_eff = selL_eff = 0.0
        # trampa: gana la que halaga (izquierda)
        tr_sel = prog(t, c["tr_razon"], c["tr_razon"] + 0.3)
        if trap > 0:
            selL_eff = max(selL_eff * (1 - trap), tr_sel); selR_eff = selR_eff * (1 - trap)
        corr = prog(t, c["correcta"] - 0.1, c["correcta"] + 0.25)
        for side, (cx, cy) in (("L", CARD_L), ("R", CARD_R)):
            x = lerp(AVC[0], cx, ca); y = lerp(AVC[1], cy, ca)
            seed = (0 if side == "L" else 1) + 2 * ncyc
            sel = selL_eff if side == "L" else selR_eff
            dim = (selR_eff if side == "L" else selL_eff) * 0.7
            if side == "R": dim = max(dim, 0.5 * corr)
            # cambio de contenido en cada ciclo (pequeño parpadeo de escala)
            flick = 1.0
            if 0 <= k_cyc < 2:
                flick = 1 - 0.12 * window(k_cyc % 1.0, 0.0, 0.18, 0.05, 0.1)
            with P.transform(0, 0, lerp(0.3, 1.0, ca) * flick, cx=x, cy=y):
                with P.layer(1 - trap):
                    card(P, x, y, ca, sel=sel, dim=dim, seed=seed)
                if trap > 0:
                    txt = "¡Tienes razón!" if side == "L" else "En realidad, no."
                    card(P, x, y, trap * ca, sel=sel, dim=dim, text=txt,
                         label="correcta" if side == "R" else None, la=corr)
        # persona que elige
        ha = prog(t, c["persona"] - 0.2, c["persona"] + 0.3)
        smile = prog(t, c["tr_razon"], c["tr_razon"] + 0.4)
        if ha > 0:
            with P.transform(0, 18 * (1 - ha), 1.0):
                L.head(P, HEAD[0], HEAD[1], 0.40, a=ha, smile=0.2 + 0.8 * smile)
        # barra de puntos
        ba = prog(t, c["puntos"] - 0.3, c["puntos"] + 0.1)
        if ba > 0:
            x0, x1, y = BAR
            fill = 0.12
            fill += 0.18 * prog(t, c["puntos"] + 0.35, c["puntos"] + 0.7)
            for k in range(2):
                t_hit = cyc_t0 + k * period + 0.85
                fill += 0.15 * prog(t, t_hit - 0.1, t_hit + 0.2)
            fill += 0.2 * prog(t, c["tr_razon"] + 0.6, c["tr_razon"] + 0.95)
            P.text("puntos", x0 - 14, y + 10, 28, L.GRAY, ba, face=C.FONT_BOLD, align="right")
            P.rect(x0, y - 13, x1, y + 13, L.CARD, ba, radius=13)
            P.rect(x0, y - 13, x0 + (x1 - x0) * clamp(fill), y + 13, L.RED, ba, radius=13)
            # puntos que vuelan desde la tarjeta elegida a la barra
            flights = [(c["puntos"], CARD_R)]
            for k in range(2):
                flights.append((cyc_t0 + k * period + 0.45, CARD_R if k % 2 == 1 else CARD_L))
            flights.append((c["tr_razon"] + 0.25, CARD_L))
            for t_f, (fx, fy) in flights:
                u = prog(t, t_f, t_f + 0.55, in_out_cubic)
                if 0 < u < 1:
                    tx = x0 + (x1 - x0) * clamp(fill)
                    px = lerp(fx, tx, u); py = lerp(fy + CH / 2, y, u) - 120 * math.sin(math.pi * u)
                    P.circle(px, py, 15, L.RED, 1)
        # pregunta: ¿dónde está la trampa?
        qa = window(t, c["tr0"] - 0.1, c["tr_razon"] - 0.2, 0.25, 0.3)
        if qa > 0:
            P.text("?", AVC[0] + 115, AVC[1] + 30 + 5 * math.sin(t * 3), 110, L.RED, qa, face=C.FONT_BLACK)


# =============================================================== dato (Anthropic 2023)
def dato_scene(P, t):
    c = CUE
    a = prog(t, c["d0"] - 0.2, c["d0"] + 0.35) * (1 - prog(t, c["o0"] - 0.35, c["o0"] + 0.05))
    if a <= 0: return
    with P.layer(a):
        P.pill("Anthropic · 2023", 540, 525, 30, L.FG, prog(t, c["anthropic"] - 0.2, c["anthropic"] + 0.2), fill_a=0.08)
        ba = prog(t, c["d_estas"] - 0.1, c["d_estas"] + 0.3)
        if ba > 0:
            P.rect(540 - 165, 568, 540 + 165, 630, L.FG, ba, radius=31)
            P.text("¿Estás seguro?", 540, 611, 34, L.BG, ba, face=C.FONT_SEMI)
        n0, s, g = 10, 42, 7
        W = n0 * s + (n0 - 1) * g
        x0, y0 = 540 - W / 2, 668
        ga = prog(t, c["d0"] + 0.2, c["anthropic"] + 0.6)
        filled = 98 * prog(t, c["perdon"] - 0.1, c["n98"] + 0.05, in_out_cubic)
        nf = int(filled)
        for i in range(100):
            col, row = i % 10, i // 10
            x = x0 + col * (s + g); y = y0 + row * (s + g)
            appear = prog(ga, i / 140, i / 140 + 0.3)
            if appear <= 0: continue
            if i < nf:
                P.rect(x, y, x + s, y + s, L.RED, appear, radius=8)
            elif i == nf and filled > 0:
                P.rect(x, y, x + s, y + s, L.RED, appear * (filled - nf), radius=8)
                P.rect(x, y, x + s, y + s, L.DIM, appear, stroke=3, radius=8)
            else:
                P.rect(x, y, x + s, y + s, L.DIM, appear, stroke=3, radius=8)
        ca = prog(t, c["perdon"] - 0.1, c["perdon"] + 0.2)
        if ca > 0:
            pop = 1 + 0.12 * pulse(t, c["n98"], 0.5)
            with P.transform(0, 0, pop, cx=540, cy=1215):
                P.text(f"{int(round(filled))} %", 540, 1262, 80, L.RED, ca, face=C.FONT_BLACK)


# =============================================================== OpenAI 2025
def openai_scene(P, t):
    c = CUE
    a = prog(t, c["o0"] - 0.2, c["o0"] + 0.35) * (1 - prog(t, c["n0"] - 0.35, c["n0"] + 0.05))
    if a <= 0: return
    with P.layer(a):
        P.pill("OpenAI · 2025", 540, 525, 30, L.FG, prog(t, c["o0"] + 0.3, c["o0"] + 0.7), fill_a=0.08)
        cx, cy = 540, 790
        boxa = prog(t, c["o0"], c["o0"] + 0.45, out_cubic)
        # retiro: la actualización retrocede (flecha circular) y se marca
        ret = prog(t, c["retiro"] - 0.05, c["retiro"] + 0.4)
        with P.transform(0, 0, 0.9 + 0.1 * boxa, cx=cx, cy=cy):
            P.rect(cx - 230, cy - 95, cx + 230, cy + 95, L.hx("#262626"), boxa, radius=28)
            P.rect(cx - 230, cy - 95, cx + 230, cy + 95, L.DIM, boxa, stroke=4, radius=28)
            avatar(P, cx - 150, cy, 44, boxa)
            P.text("actualización", cx + 45, cy + 15, 42, L.FG, boxa, face=C.FONT_BOLD)
        if ret > 0:
            r = 46; ax, ay = cx + 290, cy - 120
            P.c.drawArc(skia.Rect(ax - r, ay - r, ax + r, ay + r), -60, -270 * ret, False, paint(L.RED, ret, 8))
            ang = math.radians(-60 - 270 * ret)
            hx_, hy_ = ax + r * math.cos(ang), ay + r * math.sin(ang)
            P.circle(hx_, hy_, 10, L.RED, ret)
        # pulgares que caen dentro de la actualización
        for k in range(7):
            t_k = c["pulgares"] - 0.2 + k * 0.2
            u = prog(t, t_k, t_k + 0.7, in_out_cubic)
            if u <= 0 or u >= 1: continue
            sx = [-330, 330, -250, 250, -380, 380, 0][k]
            x = lerp(cx + sx, cx + 0.25 * sx, u)
            y = lerp(500 if k != 6 else 470, cy - 20, u)
            thumb(P, x, y, 0.55, L.FG, 1 - prog(u, 0.75, 1.0))
        # medidor «complaciente»
        ga = prog(t, c["pulgares"] - 0.2, c["pulgares"] + 0.3)
        if ga > 0:
            gx, gy, R = 540, 1160, 140
            P.c.drawArc(skia.Rect(gx - R, gy - R, gx + R, gy + R), 180, 180, False, paint(L.DIM, ga, 14))
            lvl = 0.25 + 0.35 * prog(t, c["pulgares"], c["complaciente"] - 0.2) \
                + 0.4 * prog(t, c["complaciente"] - 0.2, c["complaciente"] + 0.4, out_back)
            lvl = min(lvl, 1.04)
            P.c.drawArc(skia.Rect(gx - R, gy - R, gx + R, gy + R), 180, 180 * clamp(lvl), False,
                        paint(lerp_c(L.FG, L.RED, clamp((lvl - 0.5) * 2)), ga, 14))
            ang = math.radians(180 + 180 * lvl)
            P.line(gx, gy, gx + (R - 30) * math.cos(ang), gy + (R - 30) * math.sin(ang), L.FG, ga, w=8)
            P.circle(gx, gy, 14, L.FG, ga)
            P.text("complaciente", gx, gy + 62, 32, lerp_c(L.GRAY, L.RED, prog(t, c["complaciente"], c["complaciente"] + 0.3)),
                   ga, face=C.FONT_BOLD)
        # sello «retirada» después de la revelación
        st = prog(t, c["complaciente"] + 0.55, c["complaciente"] + 0.85, out_back)
        if st > 0:
            with P.transform(0, 0, lerp(1.5, 1.0, clamp(st)), rot=-8, cx=cx, cy=cy):
                P.rect(cx - 190, cy - 52, cx + 190, cy + 52, L.BG, 0.75 * clamp(st), radius=14)
                P.rect(cx - 190, cy - 52, cx + 190, cy + 52, L.RED, clamp(st), stroke=7, radius=14)
                P.text("RETIRADA", cx, cy + 22, 62, L.RED, clamp(st), face=C.FONT_BLACK, tracking=4)


# =============================================================== nombre: adulación
FLAT = [("¡Exacto!", 330, 660), ("¡Qué gran idea!", 700, 720), ("¡Tienes razón!", 360, 1060), ("¡Brillante!", 740, 1110)]


def nombre_scene(P, t):
    c = CUE
    a = prog(t, c["n0"] - 0.2, c["n0"] + 0.3) * (1 - prog(t, c["tip0"] - 0.35, c["tip0"] + 0.05))
    if a <= 0: return
    with P.layer(a):
        pop = out_back(prog(t, c["adulacion"] - 0.15, c["adulacion"] + 0.35))
        with P.transform(0, 0, 0.7 + 0.3 * pop, cx=540, cy=880):
            P.text("adulación", 540, 915, 120, L.RED, clamp(pop), face=C.FONT_BLACK)
        for k, (s, x, y) in enumerate(FLAT):
            u = prog(t, c["n0"] + 0.15 * k, c["n0"] + 0.15 * k + 0.4)
            fl = 8 * math.sin(t * 2 + k)
            dr = 30 * prog(t, c["quieres"] - 0.2, c["tip0"])
            yy = y + fl - dr * (1 if y < 880 else -1) * 0.5
            w = P.text_width(s, 36, C.FONT_SEMI) + 56
            P.rect(x - w / 2, yy - 36, x + w / 2, yy + 36, L.hx("#2A2A2A"), u, radius=34)
            P.text(s, x, yy + 13, 36, L.FG, u, face=C.FONT_SEMI)


# =============================================================== tip
def tip_scene(P, t):
    c = CUE
    a = prog(t, c["tip0"] - 0.2, c["tip0"] + 0.3) * (1 - prog(t, c["ci0"] - 0.35, c["ci0"] + 0.05))
    if a <= 0: return
    with P.layer(a):
        phone(P, 1)
        bubble(P, M1, "u", TOPS[0], 1.0, 1.0)
        # «Creo que es 54»: aparece, se tacha y se va
        b_in = prog(t, c["tip0"] + 0.1, c["tip0"] + 0.4)
        strike = prog(t, c["crees"] - 0.05, c["crees"] + 0.3)
        gone = prog(t, c["crees"] + 0.3, c["crees"] + 0.55)
        bubble(P, "Creo que es 54.", "u", TOPS[1], b_in * (1 - gone), b_in, strike=strike)
        # «¿Cómo llegaste?» y respuesta con el cómo
        a2, r2 = ap(t, c["pide"])
        bubble(P, "Muéstrame cómo.", "u", TOPS[1], a2 * gone, r2)
        a3, r3 = ap(t, c["muestre"] + 0.1)
        b3 = bubble(P, ["7 × 10 = 70", "70 − 14 = 56"], "ia", TOPS[2], a3, r3)
        if b3:
            check(P, b3[2] + 50, (b3[1] + b3[3]) / 2, 0.95, prog(t, c["llego"] + 0.25, c["llego"] + 0.5), col=L.FG)


# =============================================================== cierre (empalme con el cuadro 0)
def cierre_scene(P, t):
    c = CUE
    a = prog(t, c["ci0"] - 0.2, c["ci0"] + 0.3)
    if a <= 0: return
    end = c["end"]
    loop = prog(t, end - 0.9, end - 0.15, in_out_cubic)
    s0 = c["ci0"] + 0.1
    show = [(1.0, 1.0)] + [(u * (1 - loop), r) for u, r in (ap(t, s0 + 0.3 * k, 0.28) for k in range(1, 4))]
    hl = prog(t, c["c_razon"] - 0.1, c["c_razon"] + 0.3) * (1 - loop)
    th = prog(t, c["gusta"] - 0.1, c["gusta"] + 0.35) * (1 - loop)
    ok2 = prog(t, s0 + 0.5, s0 + 0.7) * (1 - loop)
    hook_chat(P, t, a, show, hl4=hl, ok2=ok2, thumb_a=th)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["responde"] = T("hook", "responde"); c["bien"] = T("hook", "bien"); c["estas"] = T("hook", "Estás")
    c["razon"] = T("hook", "razón"); c["no"] = T("hook", "no"); c["porque"] = T("hook", "Por")
    c["ap0"] = T("aprende"); c["aprendio"] = T("aprende", "aprendió"); c["dos"] = T("aprende", "dos")
    c["persona"] = T("aprende", "persona"); c["mas"] = T("aprende", "más")
    c["puntos"] = T("premio", "puntos"); c["ajusta"] = T("premio", "ajusta"); c["otra"] = T("premio", "otra")
    c["tr0"] = T("trampa"); c["tr_razon"] = T("trampa", "razón"); c["correcta"] = T("trampa", "correcta")
    c["d0"] = T("dato"); c["anthropic"] = T("dato", "Anthropic"); c["d_estas"] = T("dato", "estás")
    c["perdon"] = T("dato", "perdón"); c["n98"] = T("dato", "98")
    c["o0"] = T("openai"); c["retiro"] = T("openai", "retiró"); c["pulgares"] = T("openai", "pulgares")
    c["complaciente"] = T("openai", "complaciente")
    c["n0"] = T("nombre"); c["adulacion"] = T("nombre", "adulación"); c["quieres"] = T("nombre", "quieres")
    c["tip0"] = T("tip"); c["crees"] = T("tip", "crees"); c["como"] = T("tip", "cómo"); c["pide"] = T("tip", "pide"); c["muestre"] = T("tip", "muestre"); c["llego"] = T("tip", "llegó")
    c["ci0"] = T("cierre"); c["c_razon"] = T("cierre", "razón"); c["gusta"] = T("cierre", "gusta")
    c["end"] = tl.duration
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["no"] - 0.1, 1.2) + 0.6 * pulse(t, c["correcta"] - 0.1, 1.3) \
        + 0.6 * pulse(t, c["n98"] - 0.1, 1.4) + 0.5 * pulse(t, c["complaciente"], 1.2) + 0.5 * pulse(t, c["gusta"], 1.2)
    L.background(P, t, glow=glow)
    hook_scene(P, t)
    train_scene(P, t)
    dato_scene(P, t)
    openai_scene(P, t)
    nombre_scene(P, t)
    tip_scene(P, t)
    cierre_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    P.text("¿POR QUÉ LA IA", 540, 520, 96, L.FG, 1, face=C.FONT_BLACK)
    P.text("TE DA LA", 540, 625, 96, L.FG, 1, face=C.FONT_BLACK)
    P.text("RAZÓN?", 540, 740, 118, L.RED, 1, face=C.FONT_BLACK)
    with P.transform(-30, 250, 1.12, cx=540, cy=900):
        bubble(P, M3, "u", 640, 1.0, 1.0)
        b4 = bubble(P, M4, "ia", 830, 1.0, 1.0, hl=1.0)
        cross(P, b4[2] + 52, (b4[1] + b4[3]) / 2, 0.95, 1.0)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (c["responde"], "pop", 0.35), (c["bien"], "tick", 0.35), (c["estas"], "pop", 0.35),
            (c["razon"], "pop", 0.4), (c["no"], "pop_low", 0.5), (c["porque"], "pop", 0.35),
            (c["ap0"] - 0.3, "whoosh", 0.35), (c["dos"], "whoosh", 0.3), (c["mas"], "tick", 0.4),
            (c["puntos"] + 0.5, "ding", 0.4), (c["ajusta"], "tick", 0.3), (c["otra"] + 0.6, "tick", 0.3),
            (c["tr0"], "pop", 0.35), (c["tr_razon"], "tick", 0.4), (c["correcta"], "pop_low", 0.5),
            (c["d0"] - 0.3, "whoosh", 0.35), (c["d_estas"], "pop", 0.35), (c["perdon"], "riser", 0.3),
            (c["n98"], "ding", 0.6),
            (c["o0"] - 0.3, "whoosh", 0.35), (c["retiro"], "rewind", 0.35), (c["pulgares"], "tick", 0.35),
            (c["complaciente"], "ding", 0.5), (c["complaciente"] + 0.6, "thump", 0.5),
            (c["n0"] - 0.3, "whoosh", 0.35), (c["adulacion"], "ding", 0.55),
            (c["tip0"] - 0.3, "whoosh", 0.35), (c["crees"], "pop_low", 0.4), (c["llego"] + 0.25, "ding", 0.45),
            (c["ci0"] - 0.3, "whoosh", 0.35), (c["gusta"], "thump", 0.5)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["ap0"], "pulse": (c["d0"], c["n0"]), "quiet": [(c["porque"] - 0.1, c["ap0"] + 0.2)]}
