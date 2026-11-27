"""Escenas — «¿Cómo pasa la energía por el aire?» (stheq.ia, motion graphics).

Hilo visual: un celular sobre una base de carga.
Gancho (vista desde arriba): el celular flota sobre la base, cae, aparece el rayo de carga y luego un «?» →
corte lateral: la base y el celular como dos láminas con una bobina de cobre cada una (puntos), separadas por aire →
un cable lleva corriente de una bobina a la otra y se disuelve: aquí no hay camino de metal → bobina con un medidor:
un imán entra y sale y la aguja salta → vuelve el corte: la corriente de la base cambia de sentido (⊙/⊗), sus líneas
de campo crecen, se apagan y se invierten; un imán fantasma sube y baja al mismo ritmo → las líneas llegan a la
bobina del celular y empujan corriente hacia la batería: «inducción magnética» → el celular se corre, el campo se
escapa y la batería se llena lento; aparecen imanes y lo centran → paquetes de aviso del celular a la base, batería
llena, el campo se apaga → vuelta a la vista desde arriba, ondas que van y vienen, y el celular vuelve a flotar
(empalme con el cuadro 0).
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
COPPER = L.hx("#C98A4B")

# vista lateral (corte)
PAD_X0, PAD_X1, PAD_TOP, PAD_BOT = 290, 790, 1040, 1110
PH_X0, PH_X1, PH_TOP, PH_BOT = 240, 840, 820, 872
COIL_PAD_Y, COIL_PH_Y = 1074, 846
COIL_DX = [-175, -140, -105, -70, 70, 105, 140, 175]
CX = 540


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
def bolt(P, cx, cy, s, rgb, a):
    if a <= 0: return
    pts = [(10, -60), (-26, 6), (-2, 6), (-12, 60), (28, -10), (4, -10), (14, -60)]
    pth = skia.Path(); pth.moveTo(cx + pts[0][0] * s, cy + pts[0][1] * s)
    for x, y in pts[1:]: pth.lineTo(cx + x * s, cy + y * s)
    pth.close()
    P.c.drawPath(pth, paint(rgb, a))


def cross(P, x, y, s, a, col=None):
    if a <= 0: return
    P.line(x - 26 * s, y - 26 * s, x + 26 * s, y + 26 * s, col or L.RED, a, w=11 * s)
    P.line(x + 26 * s, y - 26 * s, x - 26 * s, y + 26 * s, col or L.RED, a, w=11 * s)


def check(P, x, y, s, a, col=None):
    if a <= 0: return
    pth = skia.Path(); pth.moveTo(x - 30 * s, y); pth.lineTo(x - 8 * s, y + 24 * s); pth.lineTo(x + 34 * s, y - 26 * s)
    P.c.drawPath(pth, paint(col or L.RED, a, 12 * s))


def top_view(P, t, a, phone_dy=0.0, phone_s=1.0, charge=0.0, bolt_a=0.0, q=0.0, rings=0.0, bolt_red=0.0):
    """Base redonda vista desde arriba con el celular encima."""
    if a <= 0: return
    with P.layer(a):
        cx, cy = 540, 900
        # anillos de campo (ondas que van y vienen)
        if rings > 0:
            for k in range(4):
                u = ((t * 0.55 + k / 4) % 1.0)
                P.circle(cx, cy, 240 + 230 * u, L.FG, rings * 0.35 * (1 - u), stroke=4)
        P.circle(cx, cy, 236, L.CARD, 1)
        P.circle(cx, cy, 236, L.DIM, 1, stroke=5)
        P.circle(cx, cy, 150, L.GRAY, 0.25 + 0.5 * charge * (0.6 + 0.4 * math.sin(t * 4)), stroke=4)
        # sombra y celular
        lift = clamp(-phone_dy / 260)
        P.rect(cx - 150, cy - 290, cx + 150, cy + 290, L.BG, 0.55 * (1 - 0.6 * lift), radius=48, blur=26 + 30 * lift)
        with P.transform(0, phone_dy, phone_s, cx=cx, cy=cy - 20):
            x0, y0, x1, y1 = cx - 160, cy - 330, cx + 160, cy + 290
            P.rect(x0, y0, x1, y1, L.BG, 1, radius=52)
            P.rect(x0, y0, x1, y1, L.FG, 1, stroke=6, radius=52)
            P.rect(x0 + 18, y0 + 18, x1 - 18, y1 - 18, L.CARD, 1, radius=38)
            P.rect(cx - 50, y0 + 34, cx + 50, y0 + 58, L.BG, 1, radius=12)
            # batería en pantalla
            if charge > 0:
                bx0, by0 = cx - 70, cy + 150
                P.rect(bx0, by0, bx0 + 140, by0 + 60, L.FG, charge, stroke=5, radius=12)
                P.rect(bx0 + 140, by0 + 18, bx0 + 152, by0 + 42, L.FG, charge, radius=4)
                fill = 0.35 + 0.15 * clamp(charge)
                P.rect(bx0 + 10, by0 + 10, bx0 + 10 + 120 * fill, by0 + 50, L.FG, charge, radius=6)
            bolt(P, cx, cy - 60, 1.9, lerp_c(L.FG, L.RED, bolt_red), bolt_a)
            if q > 0:
                P.text("?", cx, cy - 10 + 6 * math.sin(t * 3), 210, L.RED, q, face=C.FONT_BLACK)


def slab(P, x0, y0, x1, y1, a, label=None, la=0.0):
    if a <= 0: return
    P.rect(x0, y0, x1, y1, L.CARD, a, radius=16)
    P.rect(x0, y0, x1, y1, L.GRAY, a, stroke=4, radius=16)


def coil_row(P, y, dx, a, cur=0.0, glow=0.0):
    """Corte de una bobina plana: puntos de cobre; cur>0: ⊙ a la izquierda y ⊗ a la derecha (cur<0, al revés)."""
    if a <= 0: return
    for k, ox in enumerate(COIL_DX):
        x = CX + dx + ox
        if glow > 0:
            P.circle(x, y, 22, COPPER, 0.35 * glow * a, blur=10)
        P.circle(x, y, 14, COPPER, a)
        m = abs(cur)
        if m > 0.05:
            left = ox < 0
            dot = (cur > 0) == left
            if dot:
                P.circle(x, y, 4.5, L.BG, a * m)
            else:
                P.line(x - 6, y - 6, x + 6, y + 6, L.BG, a * m, w=3)
                P.line(x + 6, y - 6, x - 6, y + 6, L.BG, a * m, w=3)


def field_lines(P, cx, cy, s, a, reach=1.0, n=4):
    """Líneas de campo de una bobina plana (corte): óvalos a cada lado que pasan por el eje. s ∈ [-1, 1]."""
    m = abs(s)
    if a <= 0 or m < 0.02: return
    for k in range(n):
        rx = 85 + 45 * k
        ry = (110 + 60 * k) * reach * m
        al = a * (0.75 - 0.12 * k) * clamp(m * 1.6)
        for side in (-1, 1):
            r = skia.Rect(cx + side * rx - rx, cy - ry, cx + side * rx + rx, cy + ry)
            P.c.drawOval(r, paint(L.FG, al, 3.2))
        # flecha en el eje (dirección del campo)
        if k == 0:
            d = -1 if s > 0 else 1
            P.arrow(cx, cy - d * 30, cx, cy + d * 130 * m * reach, L.RED, a * clamp(m * 2), w=7, head=26)


def battery_h(P, cx, cy, fill, a, col=None):
    if a <= 0: return
    P.rect(cx - 80, cy - 34, cx + 80, cy + 34, L.FG, a, stroke=5, radius=12)
    P.rect(cx + 80, cy - 12, cx + 92, cy + 12, L.FG, a, radius=4)
    P.rect(cx - 70, cy - 24, cx - 70 + 140 * clamp(fill), cy + 24, col or L.FG, a, radius=6)


def magnet(P, cx, cy, a, w=230, h=86, vertical=False):
    if a <= 0: return
    with P.layer(a):
        if vertical:
            P.rect(cx - h / 2, cy - w / 2, cx + h / 2, cy, L.RED, 1, radius=10)
            P.rect(cx - h / 2, cy, cx + h / 2, cy + w / 2, L.GRAY, 1, radius=10)
            P.text("N", cx, cy - w / 4 + 14, 40, L.WHITE, 1, face=C.FONT_BLACK)
            P.text("S", cx, cy + w / 4 + 14, 40, L.BG, 1, face=C.FONT_BLACK)
        else:
            P.rect(cx - w / 2, cy - h / 2, cx, cy + h / 2, L.GRAY, 1, radius=10)
            P.rect(cx, cy - h / 2, cx + w / 2, cy + h / 2, L.RED, 1, radius=10)
            P.text("S", cx - w / 4, cy + 14, 40, L.BG, 1, face=C.FONT_BLACK)
            P.text("N", cx + w / 4, cy + 14, 40, L.WHITE, 1, face=C.FONT_BLACK)


# =============================================================== escenas
def hook_scene(P, t):
    c = CUE
    a = 1 - prog(t, c["d0"] - 0.35, c["d0"] + 0.15, in_out_cubic)
    if a <= 0: return
    drop = prog(t, c["encima"] - 0.15, c["encima"] + 0.45, out_back)
    hover = 4 * math.sin(t * 2.4) * (1 - drop)
    charge = prog(t, c["carga"] - 0.1, c["carga"] + 0.3)
    q = prog(t, c["aire"] - 0.2, c["aire"] + 0.25)
    with P.transform(0, 0, 1 - 0.25 * (1 - a), cx=540, cy=900):
        top_view(P, t, a, phone_dy=lerp(-240, 0, drop) + hover, phone_s=lerp(1.1, 1.0, drop), charge=charge,
                 bolt_a=charge * (1 - q), q=q, rings=charge * (1 - q) * 0.0)
    # tachar el cable
    ca = window(t, c["cable"] - 0.15, c["aire"] - 0.1, 0.2, 0.3)
    if ca > 0:
        P.line(820, 1190, 1000, 1250, L.GRAY, ca, w=10)
        P.rect(780, 1170, 830, 1210, L.GRAY, ca, radius=8)
        cross(P, 900, 1220, 1.0, ca * prog(t, c["cable"], c["cable"] + 0.2))


def side_scene(P, t):
    """Corte lateral: base + celular, de «dentro» a «habla» (excepto durante el imán)."""
    c = CUE
    a_in = prog(t, c["d0"] - 0.2, c["d0"] + 0.4)
    a_out = 1 - prog(t, c["ci0"] - 0.35, c["ci0"] + 0.1)
    im_gap = 1 - window(t, c["im0"] - 0.35, c["tr0"] + 0.1, 0.35, 0.4)
    a = min(a_in, a_out, im_gap)
    if a <= 0: return
    with P.layer(a):
        # --- posición del celular (corrido y centrado)
        dx = 200 * prog(t, c["corrido"] - 0.1, c["corrido"] + 0.45, in_out_cubic) \
            * (1 - prog(t, c["centran"] - 0.25, c["centran"] + 0.35, out_back))
        ph_a = prog(t, c["celular"] - 0.25, c["celular"] + 0.1)
        ph_a *= 1 - 0.8 * window(t, c["tr0"] - 0.2, c["cruza"] - 0.1, 0.3, 0.4)
        pad_a = prog(t, c["d0"] - 0.1, c["d0"] + 0.4)
        coils = prog(t, c["bobinas"] - 0.1, c["bobinas"] + 0.35)
        # --- campo de la base (truco → habla)
        f_on = prog(t, c["cambia"] - 0.2, c["cambia"] + 0.4)
        f_off = 1 - prog(t, c["apague"] - 0.1, c["apague"] + 0.5)
        tc = c["crece"]; ta = c["apaga"]; ti = c["invierte"]
        if t < tc:
            s = math.sin(2 * math.pi * 1.1 * (t - c["cambia"])) * 0.35
        elif t < ta:
            s = lerp(math.sin(2 * math.pi * 1.1 * (tc - c["cambia"])) * 0.35, 1.0, prog(t, tc, ta - 0.05, in_out_cubic))
        elif t < ti:
            s = lerp(1.0, 0.0, prog(t, ta, ti - 0.05, in_out_cubic))
        elif t < c["iman2"]:
            s = lerp(0.0, -1.0, prog(t, ti, ti + 0.45, in_out_cubic))
        else:
            s = -math.cos(2 * math.pi * 0.85 * (t - c["iman2"]))
        s *= f_on * f_off
        reach = lerp(1.0, 1.45, prog(t, c["cruza"] - 0.3, c["atraviesa"] + 0.2, in_out_cubic))
        # --- láminas y bobinas
        slab(P, PAD_X0, PAD_TOP, PAD_X1, PAD_BOT, pad_a)
        with P.clip_rect(0, 380, 1080, 1265):
            field_lines(P, CX, COIL_PAD_Y, s, f_on * f_off, reach=reach)
        coil_row(P, COIL_PAD_Y, 0, coils * pad_a, cur=s, glow=abs(s) * f_on)
        with P.layer(ph_a):
            slab(P, PH_X0 + dx, PH_TOP, PH_X1 + dx, PH_BOT, 1)
            # el celular recibe: corriente cuando el campo cambia y atraviesa su bobina
            overlap = 1 - clamp(dx / 200) * 0.75
            recv = prog(t, c["atraviesa"], c["crea"] + 0.2) * overlap * f_off
            ds = -math.sin(2 * math.pi * 0.85 * (t - c["iman2"]))
            coil_row(P, COIL_PH_Y, dx, coils, cur=ds * recv, glow=recv * (0.6 + 0.4 * abs(ds)))
        # imanes de alineación (Qi2)
        ma = prog(t, c["imanes"] - 0.2, c["imanes"] + 0.25) * (1 - prog(t, c["ci0"] - 0.4, c["ci0"]))
        if ma > 0:
            for ox in (-225, 225):
                P.rect(CX + ox - 16, PAD_TOP - 6, CX + ox + 16, PAD_TOP + 22, L.RED, ma * pad_a, radius=5)
                P.rect(CX + ox - 16 + dx, PH_BOT - 22, CX + ox + 16 + dx, PH_BOT + 6, L.RED, ma * ph_a, radius=5)
            pull = pulse(t, c["centran"] - 0.1, 0.7)
            if pull > 0:
                for ox in (-225, 225):
                    P.arrow(CX + ox + dx, PH_BOT + 40, CX + ox, PAD_TOP - 40, L.RED, pull * 0.8, w=5, head=18)
        # --- etiquetas
        P.pill("base", 150, PAD_TOP + 35, 30, L.GRAY, pad_a * window(t, c["base"] - 0.2, c["metal"] - 0.2, 0.3, 0.4), fill_a=0.06)
        P.pill("celular", 150 + dx * 0, PH_TOP - 50, 30, L.GRAY, ph_a * window(t, c["celular"] - 0.2, c["metal"] - 0.2, 0.3, 0.4), fill_a=0.06)
        P.pill("cobre", 540, 1180, 30, COPPER, coils * window(t, c["bobinas"], c["tocan"] + 0.4, 0.3, 0.4), fill_a=0.08)
        ga = window(t, c["tocan"] - 0.15, c["metal"] - 0.1, 0.25, 0.35)
        if ga > 0:
            P.line(CX, PH_BOT + 18, CX, PAD_TOP - 18, L.RED, ga, w=6, frac=prog(t, c["tocan"] - 0.15, c["tocan"] + 0.25))
            P.line(CX - 26, PH_BOT + 18, CX + 26, PH_BOT + 18, L.RED, ga, w=6)
            P.line(CX - 26, PAD_TOP - 18, CX + 26, PAD_TOP - 18, L.RED, ga, w=6)
        problema_layer(P, t)
        # --- batería del celular (desde «crea» hasta «habla»)
        ba = prog(t, c["crea"] - 0.4, c["crea"]) * (1 - prog(t, c["ci0"] - 0.4, c["ci0"]))
        if ba > 0:
            # llenado: rápido centrado, lento corrido, completo al «llena»
            f = 0.15 + 0.35 * prog(t, c["crea"], c["lento"])
            f += 0.06 * prog(t, c["lento"], c["imanes"])
            f += 0.25 * prog(t, c["centran"], c["avisa"])
            f = lerp(f, 1.0, prog(t, c["llena"] - 0.2, c["llena"] + 0.4))
            slow = window(t, c["corrido"], c["centran"], 0.3, 0.3)
            bx, by = CX + dx, 640
            P.line(bx, PH_TOP - 4, bx, by + 40, L.FG, ba, w=5)
            # puntos de corriente subiendo por el cable
            for k in range(4):
                u = (t * (1.6 - 1.1 * slow) + k / 4) % 1.0
                P.circle(bx, lerp(PH_TOP - 10, by + 44, u), 7, L.RED, ba * (1 - prog(t, c["apague"], c["apague"] + 0.3)))
            done = prog(t, c["llena"] - 0.1, c["llena"] + 0.3)
            battery_h(P, bx, by, f, ba, col=lerp_c(L.FG, L.RED, done))
            P.text("lento", bx + 170, by + 14, 40, L.RED, ba * slow, face=C.FONT_BLACK)
            P.text("100 %", bx, by - 62, 44, L.RED, ba * done, face=C.FONT_BLACK)
        ia = window(t, c["induccion"] - 0.2, c["c_lento"] - 0.25, 0.3, 0.35)
        if ia > 0:
            with P.transform(0, 0, 0.85 + 0.15 * out_back(prog(t, c["induccion"] - 0.2, c["induccion"] + 0.3)), cx=540, cy=530):
                P.text("inducción magnética", 540, 548, 62, L.RED, ia, face=C.FONT_BLACK)
        # imán fantasma que sube y baja con el campo («un imán que se mueve… sin moverse»)
        ga2 = window(t, c["iman2"] - 0.2, c["cruza"] - 0.1, 0.3, 0.4)
        if ga2 > 0:
            magnet(P, 930, 820 - 90 * s, ga2 * 0.9, w=190, h=70, vertical=True)
        # paquetes de aviso (celular → base)
        pa = window(t, c["avisa"] - 0.2, c["apague"] + 0.3, 0.2, 0.3)
        if pa > 0:
            for k in range(3):
                u = ((t - c["avisa"]) * 1.4 + k / 3) % 1.0
                y = lerp(PH_BOT + 12, PAD_TOP - 12, u)
                P.rect(CX - 40 - 12, y - 8, CX - 40 + 12, y + 8, L.RED, pa * (1 - abs(u - 0.5) * 1.4), radius=4)
            off = prog(t, c["apague"] - 0.05, c["apague"] + 0.3)
            P.pill("apagar", 820, PAD_TOP + 40, 30, L.RED, off * pa, fill_a=0.1)


def problema_layer(P, t):
    c = CUE
    a = window(t, c["metal"] - 0.35, c["im0"] - 0.1, 0.35, 0.3)
    if a <= 0: return
    dis = prog(t, c["aire2"] - 0.1, c["aire2"] + 0.5)
    # cable de metal que uniría las dos bobinas por el costado
    pts = [(CX + 175, COIL_PAD_Y), (930, COIL_PAD_Y), (930, COIL_PH_Y), (CX + 175, COIL_PH_Y)]
    with P.layer(a * (1 - 0.85 * dis)):
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            P.line(x0, y0, x1, y1, L.FG, 1, w=10, frac=prog(t, c["metal"] - 0.2, c["metal"] + 0.4))
        if t > c["metal"]:
            L_ = [math.dist(pts[i], pts[i + 1]) for i in range(3)]; tot = sum(L_)
            for k in range(6):
                u = ((t - c["metal"]) * 0.7 + k / 6) % 1.0
                d = u * tot; i = 0
                while i < 2 and d > L_[i]: d -= L_[i]; i += 1
                f = d / L_[i]
                x = lerp(pts[i][0], pts[i + 1][0], f); y = lerp(pts[i][1], pts[i + 1][1], f)
                P.circle(x, y, 9, L.RED, 1)
    if dis > 0:
        cross(P, 930, 960, 1.4, a * dis)
        P.pill("aire", CX, (PH_BOT + PAD_TOP) / 2, 32, L.FG, a * dis, fill_a=0.06)
    qa = prog(t, c["entonces"] - 0.2, c["entonces"] + 0.25) * a
    if qa > 0:
        P.text("?", 930, 720 + 6 * math.sin(t * 3), 120, L.RED, qa, face=C.FONT_BLACK)


def iman_scene(P, t):
    c = CUE
    a = window(t, c["im0"] - 0.25, c["tr0"] + 0.05, 0.4, 0.35)
    if a <= 0: return
    with P.layer(a):
        cy = 760
        # imán: quieto, luego entra y sale
        t0 = c["acercas"] - 0.1
        if t < t0:
            x = 210; v = 0.0
        else:
            w = 2 * math.pi * 0.95
            x = 330 - 120 * math.cos(w * (t - t0)); v = 120 * w * math.sin(w * (t - t0))
        ma = prog(t, c["iman"] - 0.3, c["iman"] + 0.1, out_cubic)
        # bobina (hélice vista de lado)
        for k in range(7):
            xx = 470 + k * 42
            P.c.drawOval(skia.Rect(xx - 26, cy - 120, xx + 26, cy + 120), paint(COPPER, 1, 9))
        magnet(P, x, cy, ma)
        # cables al medidor
        P.line(470, cy + 120, 470, 1090, COPPER, 1, w=6)
        P.line(722, cy + 120, 722, 1090, COPPER, 1, w=6)
        # medidor (aguja)
        gx, gy = 596, 1190
        P.c.drawArc(skia.Rect(gx - 150, gy - 150, gx + 150, gy + 150), 200, 140, False, paint(L.GRAY, 1, 6))
        P.rect(gx - 170, gy - 4, gx + 170, gy + 40, L.CARD, 1, radius=10)
        for k in range(-3, 4):
            ang = math.radians(-90 + k * 20)
            P.line(gx + 128 * math.cos(ang), gy + 128 * math.sin(ang), gx + 146 * math.cos(ang), gy + 146 * math.sin(ang), L.GRAY, 1, w=4)
        on = prog(t, c["acercas"] - 0.2, c["acercas"] + 0.3)
        needle = clamp(v / 700, -1, 1) * 60 * on
        ang = math.radians(-90 + needle)
        hot = prog(t, c["corriente"] - 0.15, c["corriente"] + 0.2)
        P.line(gx, gy, gx + 135 * math.cos(ang), gy + 135 * math.sin(ang), lerp_c(L.FG, L.RED, hot), 1, w=8)
        P.circle(gx, gy, 14, L.FG, 1)
        # puntos de corriente por los cables cuando hay movimiento
        if on > 0:
            m = abs(v) / 720
            for k in range(3):
                u = (t * 2.0 + k / 3) % 1.0
                yy = lerp(cy + 130, 1080, u if v > 0 else 1 - u)
                P.circle(470, yy, 8, L.RED, on * clamp(m * 1.5))
                P.circle(722, yy, 8, L.RED, on * clamp(m * 1.5))
        P.pill("corriente", 596, 560, 34, L.RED, hot, fill_a=0.1)


def cierre_scene(P, t):
    c = CUE
    a = prog(t, c["ci0"] - 0.3, c["ci0"] + 0.3, in_out_cubic)
    if a <= 0: return
    end = c["end"]
    loop = prog(t, end - 1.1, end - 0.1, in_out_cubic)
    rings = prog(t, c["c_campo"] - 0.2, c["c_campo"] + 0.4) * (1 - loop)
    red = prog(t, c["c_corr"] - 0.15, c["c_corr"] + 0.25) * (1 - loop)
    with P.transform(0, 0, 0.8 + 0.2 * a, cx=540, cy=900):
        top_view(P, t, a, phone_dy=lerp(0, -240, loop) + 4 * math.sin(t * 2.4) * loop, phone_s=lerp(1.0, 1.1, loop),
                 charge=1 - loop, bolt_a=(1 - loop), rings=rings, bolt_red=red)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["encima"] = T("hook", "encima"); c["carga"] = T("hook", "carga"); c["cable"] = T("hook", "cable")
    c["aire"] = T("hook", "aire")
    c["d0"] = T("dentro"); c["bobinas"] = T("dentro", "bobinas"); c["base"] = T("dentro", "base")
    c["celular"] = T("dentro", "celular"); c["tocan"] = T("dentro", "tocan")
    c["p0"] = T("problema"); c["metal"] = T("problema", "metal"); c["aire2"] = T("problema", "aire")
    c["entonces"] = T("problema", "Entonces")
    c["im0"] = T("iman"); c["iman"] = T("iman", "imán"); c["acercas"] = T("iman", "acercas")
    c["corriente"] = T("iman", "corriente")
    c["tr0"] = T("truco"); c["cambia"] = T("truco", "cambia"); c["crece"] = T("truco", "crece")
    c["apaga"] = T("truco", "apaga"); c["invierte"] = T("truco", "invierte"); c["iman2"] = T("truco", "imán")
    c["cruza"] = T("induccion", "cruza"); c["atraviesa"] = T("induccion", "atraviesa"); c["crea"] = T("induccion", "crea")
    c["induccion"] = T("induccion", "inducción")
    c["c_lento"] = T("centrar"); c["lento"] = T("centrar", "lento"); c["corrido"] = T("centrar", "corrido")
    c["imanes"] = T("centrar", "imanes"); c["centran"] = T("centrar", "centran")
    c["avisa"] = T("habla", "avisa"); c["llena"] = T("habla", "llena"); c["apague"] = T("habla", "apague")
    c["ci0"] = T("cierre"); c["c_campo"] = T("cierre", "campo"); c["c_corr"] = T("cierre", "corriente")
    c["end"] = tl.duration
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["corriente"] - 0.2, 1.3) + 0.6 * pulse(t, c["induccion"] - 0.2, 1.4) \
        + 0.4 * pulse(t, c["centran"] - 0.1, 1.0)
    L.background(P, t, glow=glow)
    with P.transform(0, 45):
        hook_scene(P, t)
        side_scene(P, t)
        iman_scene(P, t)
        cierre_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    P.text("¿CÓMO PASA", 540, 520, 100, L.FG, 1, face=C.FONT_BLACK)
    P.text("LA ENERGÍA", 540, 625, 100, L.FG, 1, face=C.FONT_BLACK)
    P.text("POR EL AIRE?", 540, 735, 104, L.RED, 1, face=C.FONT_BLACK)
    with P.transform(0, 250, 0.62, cx=540, cy=900):
        top_view(P, 2.0, 1.0, phone_dy=-120, phone_s=1.05, charge=1.0, bolt_a=1.0, rings=1.0)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (c["encima"] + 0.1, "thump", 0.5), (c["carga"], "ding", 0.4),
            (c["cable"], "pop_low", 0.35), (c["aire"], "pop", 0.4),
            (c["d0"] - 0.3, "whoosh", 0.35), (c["bobinas"], "tick", 0.35), (c["tocan"], "pop", 0.4),
            (c["metal"], "whoosh", 0.3), (c["aire2"], "pop_low", 0.45), (c["entonces"], "pop", 0.35),
            (c["im0"] - 0.3, "whoosh", 0.35), (c["acercas"], "whoosh", 0.3), (c["corriente"], "ding", 0.55),
            (c["tr0"] - 0.3, "whoosh", 0.35), (c["crece"], "riser", 0.3), (c["invierte"], "rewind", 0.35),
            (c["cruza"], "whoosh", 0.3), (c["crea"], "pop", 0.4), (c["induccion"], "ding", 0.6),
            (c["lento"], "pop_low", 0.4), (c["imanes"], "tick", 0.4), (c["centran"], "thump", 0.5),
            (c["avisa"], "tick", 0.35), (c["llena"], "ding", 0.45), (c["apague"], "pop_low", 0.4),
            (c["ci0"] - 0.3, "whoosh", 0.35), (c["c_corr"], "ding", 0.45)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["im0"], "pulse": (c["tr0"], c["ci0"]), "quiet": [(c["entonces"] - 0.1, c["iman"])]}
