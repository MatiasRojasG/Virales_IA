"""Escenas — «¿Cuánto tarda alguien en adivinar tu contraseña?» (stheq.ia, motion graphics).

Hilo visual: un campo de contraseña con 8 casillas. Gancho: las casillas empiezan a girar como tragamonedas y un
contador de intentos se dispara → tarjeta de inicio de sesión: tres intentos fallidos y candado → un servidor del
que sale la lista de claves; las claves se transforman en «huellas» (códigos revueltos) y la flecha de vuelta se
tacha → máquina de huellas: una clave inventada entra, sale su huella y se compara con la robada hasta que coinciden
→ tarjeta de video con ventiladores que escupe claves y contador > 100.000/s → dos barras de tiempo: 8 minúsculas
(≈ 2 semanas, casi no se ve) y 8 mezclados (132 años, se sale de la pantalla) → las 8 casillas se encienden una a
una y el contador de combinaciones se multiplica ×26 y luego ×95 → lista de claves filtradas que corre y se detiene
en la tuya → cierre: la clave «rara» se tacha, el campo se alarga a una frase al azar y vuelve al gancho (empalme).
Cifras de Hive Systems (2026); las multiplicaciones son aritmética propia.
"""
from __future__ import annotations
import math
import numpy as np
import skia
from PIL import Image
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic
from reelforge import marca as L

TL = None; EP = {}; CHUNKS = []; CUE = {}
_IMG = {}

LOW = "abcdefghijklmnopqrstuvwxyz"
ALL = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#$%&*?@"
HEXS = "./ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
MONO = C.FONT_MONO_B


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def rnd(*k):
    """Pseudoaleatorio determinista en [0, 1)."""
    h = 0
    for v in k:
        h = (h * 1000003 + int(v) * 2654435761 + 97) & 0xFFFFFFFF
    h ^= h >> 13; h = (h * 0x5bd1e995) & 0xFFFFFFFF; h ^= h >> 15
    return (h & 0xFFFFFF) / float(0x1000000)


def rchar(cs, *k):
    return cs[int(rnd(*k) * len(cs)) % len(cs)]


def fake_hash(seed, n=22):
    return "$2b$10$" + "".join(rchar(HEXS, seed, i) for i in range(n))


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
def cells(P, cx, cy, chars, a=1.0, cw=96, ch=132, gap=10, col=None, box_col=None, lit=None, size=64, lift=None):
    """Fila de casillas (una por carácter). chars: lista de str ('' = vacío, '•' = punto)."""
    if a <= 0: return
    n = len(chars)
    x0 = cx - (n * cw + (n - 1) * gap) / 2
    with P.layer(a):
        for i, s in enumerate(chars):
            x = x0 + i * (cw + gap)
            dy = lift[i] if lift else 0.0
            li = lit[i] if lit else 0.0
            P.rect(x, cy - ch / 2 + dy, x + cw, cy + ch / 2 + dy, L.CARD, 1, radius=16)
            P.rect(x, cy - ch / 2 + dy, x + cw, cy + ch / 2 + dy, lerp_c(box_col or L.DIM, L.RED, li), 1, stroke=4, radius=16)
            if s == "•":
                P.circle(x + cw / 2, cy + dy, 13, col or L.FG, 1)
            elif s:
                P.text(s, x + cw / 2, cy + size * 0.36 + dy, size, col or L.FG, 1, face=MONO)
    return x0


def field(P, cx, cy, w, h, text, a=1.0, col=None, border=None, size=52, cursor=None, red=0.0):
    if a <= 0: return
    with P.layer(a):
        P.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, L.CARD, 1, radius=h * 0.28)
        P.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, lerp_c(border or L.DIM, L.RED, red), 1, stroke=4, radius=h * 0.28)
        if text:
            tw = P.text(text, cx, cy + size * 0.36, size, col or L.FG, 1, face=MONO)
            if cursor is not None and (cursor % 1.0) < 0.55:
                P.rect(cx + tw / 2 + 8, cy - size * 0.45, cx + tw / 2 + 13, cy + size * 0.45, L.FG, 1)


def padlock(P, cx, cy, s, a, closed=1.0, col=None):
    if a <= 0: return
    col = col or L.FG
    with P.layer(a):
        sh = skia.Path()
        lift = (1 - closed) * 40 * s
        r = 52 * s
        sh.addArc(skia.Rect(cx - r, cy - 70 * s - r - lift, cx + r, cy - 70 * s + r - lift), 180, 180)
        sh.moveTo(cx - r, cy - 70 * s - lift); sh.lineTo(cx - r, cy - 20 * s - lift)
        sh.moveTo(cx + r, cy - 70 * s - lift); sh.lineTo(cx + r, cy - 20 * s)
        p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=18 * s,
                       StrokeCap=skia.Paint.kRound_Cap, Color=skia.Color4f(*col, 1.0))
        P.c.drawPath(sh, p)
        P.rect(cx - 82 * s, cy - 30 * s, cx + 82 * s, cy + 100 * s, col, 1, radius=20 * s)
        P.circle(cx, cy + 28 * s, 16 * s, L.BG, 1)
        P.rect(cx - 6 * s, cy + 30 * s, cx + 6 * s, cy + 66 * s, L.BG, 1, radius=4 * s)


def server(P, cx, cy, a, t, s=1.0):
    if a <= 0: return
    with P.layer(a):
        for k in range(3):
            y = cy + (k - 1) * 92 * s
            P.rect(cx - 110 * s, y - 38 * s, cx + 110 * s, y + 38 * s, L.CARD, 1, radius=14 * s)
            P.rect(cx - 110 * s, y - 38 * s, cx + 110 * s, y + 38 * s, L.DIM, 1, stroke=3, radius=14 * s)
            for j in range(3):
                on = 0.4 + 0.6 * (rnd(int(t * 6), k, j) > 0.4)
                P.circle(cx - 78 * s + j * 26 * s, y, 7 * s, L.FG, on)
            P.line(cx + 10 * s, y, cx + 84 * s, y, L.DIM, 1, w=6 * s)


def gpu(P, cx, cy, a, t, spin=1.0, s=1.0):
    if a <= 0: return
    with P.layer(a):
        w, h = 760 * s, 280 * s
        P.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, L.CARD, 1, radius=26 * s)
        P.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, L.GRAY, 1, stroke=4, radius=26 * s)
        # contactos
        for k in range(16):
            x = cx - w / 2 + 120 * s + k * 26 * s
            P.rect(x, cy + h / 2, x + 16 * s, cy + h / 2 + 30 * s, L.GRAY, 1, radius=3)
        for fx in (cx - 180 * s, cx + 180 * s):
            r = 105 * s
            P.circle(fx, cy, r, L.BG, 1)
            P.circle(fx, cy, r, L.DIM, 1, stroke=4)
            ang0 = t * 14 * spin
            for k in range(7):
                ang = ang0 + k * 2 * math.pi / 7
                P.line(fx + 22 * s * math.cos(ang), cy + 22 * s * math.sin(ang),
                       fx + (r - 14 * s) * math.cos(ang + 0.35), cy + (r - 14 * s) * math.sin(ang + 0.35), L.FG, 0.8, w=12 * s)
            P.circle(fx, cy, 24 * s, L.FG, 1)


def check(P, x, y, s, a, col=None):
    if a <= 0: return
    pth = skia.Path(); pth.moveTo(x - 30 * s, y); pth.lineTo(x - 8 * s, y + 24 * s); pth.lineTo(x + 34 * s, y - 26 * s)
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=12 * s, StrokeCap=skia.Paint.kRound_Cap,
                   StrokeJoin=skia.Paint.kRound_Join, Color=skia.Color4f(*(col or L.RED), a))
    P.c.drawPath(pth, p)


def cross(P, x, y, s, a, col=None):
    if a <= 0: return
    P.line(x - 26 * s, y - 26 * s, x + 26 * s, y + 26 * s, col or L.RED, a, w=11 * s)
    P.line(x + 26 * s, y - 26 * s, x - 26 * s, y + 26 * s, col or L.RED, a, w=11 * s)


def fmt(n):
    return f"{int(n):,}".replace(",", ".")


# =============================================================== escenas
def hook_scene(P, t):
    c = CUE
    a = 1 - prog(t, c["b0"] - 0.3, c["b0"] + 0.1, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        spin = prog(t, c["adiv"] - 0.35, c["adiv"])
        chars = []
        for i in range(8):
            if spin > 0 and rnd(i, 77) < spin * 1.4:
                chars.append(rchar(LOW, int(t * 22), i))
            else:
                chars.append("•")
        lit = [pulse(t, c["ocho"] + 0.05 * i, 0.5) for i in range(8)]
        cells(P, 540, 740, chars, 1, lit=lit, col=lerp_c(L.FG, L.RED, 0.0))
        # número de casilla al decir «ocho»
        na = window(t, c["ocho"] - 0.1, c["adiv"] - 0.1, 0.25, 0.3)
        if na > 0:
            for i in range(8):
                P.text(str(i + 1), 540 + (i - 3.5) * 106, 850, 34, L.RED, na * prog(t, c["ocho"] + 0.04 * i, c["ocho"] + 0.04 * i + 0.2), face=C.FONT_BOLD)
        # contador de intentos
        ca = prog(t, c["adiv"] - 0.2, c["adiv"] + 0.2)
        if ca > 0:
            n = 1 + (max(0.0, t - c["adiv"] + 0.2) ** 2.2) * 900_000
            P.text(fmt(n), 540, 960, 76, L.FG, ca, face=MONO)
            P.text("intentos", 540, 1020, 32, L.GRAY, ca, face=C.FONT_SEMI)
        qa = prog(t, c["cuanto"] - 0.15, c["cuanto"] + 0.2)
        if qa > 0:
            P.text("?", 540, 600 + 6 * math.sin(t * 3), 130, L.RED, out_back(qa) * clamp(qa * 2), face=C.FONT_BLACK)


def bloqueo_scene(P, t):
    c = CUE
    a = window(t, c["b0"] - 0.3, c["r0"] + 0.05, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        lk = prog(t, c["bloquea"] - 0.1, c["bloquea"] + 0.3, in_out_cubic)
        with P.layer(1 - 0.65 * lk):
            P.rect(250, 540, 830, 1180, L.CARD, 0.6, radius=34)
            P.rect(250, 540, 830, 1180, L.DIM, 1, stroke=3, radius=34)
            # usuario
            P.circle(540, 660, 46, L.GRAY, 1)
            P.rect(470, 715, 610, 770, L.GRAY, 1, radius=26)
            # intentos
            att = [c["a1"], c["a2"], c["a3"]]
            k = sum(1 for x in att if t >= x)
            shake = sum(math.sin((t - x) * 60) * 18 * (1 - prog(t, x, x + 0.35)) for x in att if t >= x)
            red = max([1 - prog(t, x + 0.1, x + 0.6) for x in att if t >= x] + [0.0])
            red = max(red, lk)
            nd = int(clamp((t - (att[k - 1] if k else c["b0"]) + 0.05) / 0.25) * 8) if k < 3 else 8
            with P.transform(shake, 0):
                field(P, 540, 880, 460, 104, "•" * max(nd, 0) if nd else "", 1, size=44, red=red)
            P.rect(370, 970, 710, 1060, L.FG, 1, radius=46)
            P.text("Entrar", 540, 1028, 40, L.BG, 1, face=C.FONT_BOLD)
            for j in range(3):
                P.circle(480 + j * 60, 1120, 13, L.RED if j < k else L.DIM, 1)
        padlock(P, 540, 800, 1.3, lk, closed=prog(t, c["bloquea"] + 0.15, c["bloquea"] + 0.45, out_back), col=L.RED)


ROWS = ["ana", "luis", "sofi", "tomás", "pía"]


def robo_scene(P, t):
    c = CUE
    a = window(t, c["r0"] - 0.3, c["i0"] + 0.4, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        sv = 1 - prog(t, c["i0"] - 0.2, c["i0"] + 0.3)
        server(P, 540, 620, sv * prog(t, c["r0"] - 0.2, c["r0"] + 0.2), t, s=0.8)
        la = prog(t, c["lista"] - 0.3, c["lista"] + 0.35, in_out_cubic)
        hs = prog(t, c["huellas"] - 0.1, c["huellas"] + 0.6)
        back = 1 - prog(t, c["i0"] - 0.3, c["i0"] + 0.2)
        if la > 0:
            y0 = lerp(620, 800, la)
            with P.layer(la * back):
                P.rect(130, y0 - 30, 950, y0 + 5 * 78 + 10, L.CARD, 0.9, radius=24)
                for k, nm in enumerate(ROWS):
                    y = y0 + 30 + k * 78
                    P.text(nm, 170, y + 12, 36, L.GRAY, 1, face=C.FONT_SEMI, align="left")
                    hk = clamp(hs * 1.6 - k * 0.15)
                    if hk < 1:
                        P.text("•" * 8, 400, y + 12, 36, L.FG, 1 - hk, face=MONO, align="left")
                    if hk > 0:
                        hsh = fake_hash(k)
                        nshow = int(len(hsh) * hk)
                        s = hsh[:nshow] + "".join(rchar(HEXS, int(t * 30), k, i) for i in range(len(hsh) - nshow)) if hk < 1 else hsh
                        P.text(s[:26] + "…", 400, y + 12, 32, L.RED if k == 0 else L.FG, hk, face=MONO, align="left")
        # no se puede deshacer
        da = prog(t, c["deshacer"] - 0.4, c["deshacer"] + 0.1) * back
        if da > 0:
            P.arrow(700, 1255, 400, 1255, L.GRAY, da, w=8, head=28)
            P.text("•" * 8, 300, 1268, 34, L.GRAY, da, face=MONO)
            P.text("$2b$10$…", 790, 1268, 32, L.FG, da, face=MONO)
            cross(P, 550, 1255, 1.1, prog(t, c["deshacer"], c["deshacer"] + 0.25))


GUESSES = ["hola123", "sol2020", "perro01", "qwerty", "chile18", "luna456", "mar2021", "gato2019"]


def imitar_scene(P, t):
    c = CUE
    a = window(t, c["i0"] - 0.2, c["g0"] + 0.1, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        ma = prog(t, c["imitar"] - 0.2, c["imitar"] + 0.3)
        t0 = c["inventan"]; t1 = c["encontr"]
        n = len(GUESSES) - 1
        if t < t0: gi = -1
        elif t >= t1 - 0.25: gi = n
        else: gi = min(n - 1, int((t - t0) / ((t1 - 0.25 - t0) / n)))
        ph = 0.0 if gi < 0 else (1.0 if gi == n else ((t - t0) / ((t1 - 0.25 - t0) / n)) % 1.0)
        match = prog(t, t1 - 0.05, t1 + 0.25)
        guess = GUESSES[gi] if gi >= 0 else ""
        field(P, 540, 560, 520, 104, guess, prog(t, t0 - 0.3, t0), size=48, red=match)
        # máquina de huellas
        with P.layer(ma):
            P.arrow(540, 620, 540, 690, L.GRAY, 1, w=6, head=22)
            P.rect(330, 700, 750, 850, L.CARD, 1, radius=28)
            P.rect(330, 700, 750, 850, L.GRAY, 1, stroke=4, radius=28)
            for k in range(5):   # «revolver»
                ang = t * 6 + k * 1.2
                P.circle(540 + 120 * math.cos(ang) * 0.9, 775 + 32 * math.sin(ang * 1.3), 9, L.FG, 0.7)
            P.text("huella", 540, 790, 40, L.FG, 1, face=C.FONT_BOLD)
            P.arrow(540, 860, 540, 930, L.GRAY, 1, w=6, head=22)
        # huella calculada (aparece y cambia con cada intento)
        if gi >= 0:
            hk = clamp(ph * 3) if gi < n else 1.0
            hsh = fake_hash(0) if gi == n else fake_hash(100 + gi)
            s = hsh if hk >= 1 else "".join(rchar(HEXS, int(t * 30), i) for i in range(len(hsh)))
            P.text(s[:26] + "…", 540, 990, 34, lerp_c(L.FG, L.RED, match), 1, face=MONO)
        # huella robada
        P.text(fake_hash(0)[:26] + "…", 540, 1150, 34, L.RED, ma, face=MONO)
        P.text("robada · ana", 540, 1210, 28, L.GRAY, ma, face=C.FONT_SEMI)
        # comparar
        if gi >= 0:
            P.line(540, 1030, 540, 1100, L.DIM, 1, w=4)
            if gi < n and ph > 0.45:
                cross(P, 620, 1065, 0.55, 0.8, col=L.GRAY)
        if match > 0:
            check(P, 540, 1066, 1.2, match)
            P.circle(540, 1066, 60 + 60 * match, L.RED, 0.4 * (1 - match), stroke=5)


def gpu_scene(P, t):
    c = CUE
    a = window(t, c["g0"] - 0.3, c["c0"] + 0.1, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        ga = prog(t, c["tarjetas"] - 0.3, c["tarjetas"] + 0.3, out_cubic)
        with P.transform(0, (1 - ga) * 60):
            gpu(P, 540, 700, ga, t, spin=1 + 2 * prog(t, c["cien"] - 0.5, c["cien"]))
        # chorro de claves que sale de la tarjeta
        sa = prog(t, c["prueban"] - 0.3, c["prueban"]) * ga
        if sa > 0:
            for k in range(14):
                u = ((t * 1.3 + rnd(k, 5)) % 1.0)
                x = lerp(540 + (rnd(k, 6) - 0.5) * 500, 540 + (rnd(k, 7) - 0.5) * 900, u)
                y = lerp(560, 470, u)
                s = "".join(rchar(LOW, int(t * 4) + k, i) for i in range(6))
                P.text(s, x, y, 26, L.GRAY, sa * (1 - u) * 0.9, face=MONO)
        ca = prog(t, c["cien"] - 0.4, c["cien"] + 0.1)
        if ca > 0:
            v = 100_000 * prog(t, c["cien"] - 0.4, c["cien"] + 0.5, out_cubic)
            P.text(("+" if v >= 99_999 else "") + fmt(v), 540, 1010, 110, L.RED, ca, face=C.FONT_BLACK)
            P.text("claves por segundo", 540, 1080, 38, L.GRAY, prog(t, c["segundo"] - 0.2, c["segundo"] + 0.2), face=C.FONT_SEMI)


def bar_row(P, y, label_txt, a, fill, overflow=False, col=None):
    """Pista de tiempo de 120 a 960 px; fill en px."""
    if a <= 0: return
    with P.layer(a):
        P.line(120, y, 960, y, L.DIM, 1, w=18)
        P.line(120, y, min(120 + fill, 1080 if overflow else 960), y, col or L.FG, 1, w=18)
        if overflow and fill > 840:
            P.arrow(960, y, 1040, y, col or L.RED, 1, w=10, head=28)


def cifras_scene(P, t):
    c = CUE
    a = window(t, c["c0"] - 0.3, c["p0"] + 0.1, 0.4, 0.4)
    if a <= 0: return
    with P.layer(a):
        P.pill("Hive Systems · 2026", 540, 520, 30, L.GRAY, prog(t, c["empresa"] - 0.2, c["empresa"] + 0.2), fill_a=0.08)
        # fila 1: 8 minúsculas
        r1 = prog(t, c["ocho1"] - 0.3, c["ocho1"] + 0.2)
        cells(P, 540, 660, list("qmzkatrw"), r1, cw=78, ch=100, gap=8, size=52)
        f1 = prog(t, c["dos"] - 0.4, c["dos"] + 0.2, out_cubic) * 10
        bar_row(P, 760, "", r1, f1)
        ta = prog(t, c["dos"] - 0.1, c["dos"] + 0.25)
        if ta > 0:
            P.circle(130, 760, 22, L.FG, ta)
            P.text("≈ 2 semanas", 540, 855, 56, L.FG, ta, face=C.FONT_BLACK)
        # fila 2: 8 mezclados
        r2 = prog(t, c["ocho2"] - 0.3, c["ocho2"] + 0.2)
        cells(P, 540, 960, list("Q7#m!zK2"), r2, cw=78, ch=100, gap=8, size=52)
        f2 = prog(t, c["ocho2"] + 0.8, c["n132"] + 0.1, in_out_cubic) * 980
        bar_row(P, 1080, "", r2, f2, overflow=True, col=lerp_c(L.FG, L.RED, prog(t, c["n132"] - 0.2, c["n132"] + 0.2)))
        ya = prog(t, c["n132"] - 0.1, c["n132"] + 0.3)
        if ya > 0:
            with P.transform(0, 0, 0.7 + 0.3 * out_back(ya), cx=540, cy=1200):
                P.text("132 años", 540, 1230, 104, L.RED, clamp(ya * 2), face=C.FONT_BLACK)


def porque_scene(P, t):
    c = CUE
    a = window(t, c["p0"] - 0.3, c["tr0"] - 0.05, 0.4, 0.25)
    if a <= 0: return
    with P.layer(a):
        qa = prog(t, c["p0"] - 0.1, c["p0"] + 0.3) * (1 - prog(t, c["mult"] - 0.4, c["mult"]))
        t0 = c["mult"]; t1 = c["n26"] + 0.3
        k = int(clamp((t - t0) / (t1 - t0)) * 8 + (1 if t >= t0 else 0))
        k = min(k, 8)
        tb = c["teclado"] - 0.3
        sw = prog(t, c["casi"] - 0.2, tb + 0.4)
        chars = []
        for i in range(8):
            if i < k:
                cs = ALL if sw > 0 else LOW
                chars.append(rchar(cs, int(t * 12), i))
            else:
                chars.append("")
        lit = [pulse(t, t0 + (i - 0.5) * (t1 - t0) / 8, 0.5) if i < k else 0.0 for i in range(8)]
        lit = [max(l, sw) for l in lit]
        cells(P, 540, 640, chars, prog(t, c["p0"] - 0.2, c["p0"] + 0.2), lit=lit, size=60)
        if k > 0:
            base = 26 if sw < 0.5 else 95
            val = base ** k if sw < 1 else 95 ** 8
            if 0 < sw < 1:
                v0 = 26 ** 8; v1 = 95 ** 8
                val = v0 + (v1 - v0) * in_out_cubic(sw)
            s = fmt(val)
            size = 92 if len(s) < 16 else 60
            P.text(s, 540, 900, size, lerp_c(L.FG, L.RED, sw), 1, face=C.FONT_BLACK)
            P.text("combinaciones", 540, 970, 34, L.GRAY, 1, face=C.FONT_SEMI)
            # etiqueta ×26 / ×95 bajo la última casilla encendida
            xi = 540 + (k - 1 - 3.5) * 106
            ea = 1 - prog(t, c["n26"] + 0.6, c["casi"] - 0.1) if sw <= 0 else prog(t, c["casi"] - 0.1, c["casi"] + 0.2)
            lab = "×26" if sw <= 0 else "×95"
            if sw <= 0:
                P.text(lab, xi, 755, 40, L.RED, 1, face=C.FONT_BLACK)
            else:
                for i in range(8):
                    P.text("×95", 540 + (i - 3.5) * 106, 758, 34, L.RED, ea, face=C.FONT_BLACK)
            P.text("minúsculas" if sw < 0.5 else "todo el teclado", 540, 1080, 40, L.FG, 1, face=C.FONT_BOLD)


LEAKED = ["123456", "password", "qwerty", "111111", "iloveyou", "chile2024", "abc123", "colocolo",
          "admin", "pikachu", "superman", "camila2024", "123123", "dragon", "monkey", "sunshine"]


def trampa_scene(P, t):
    c = CUE
    a = window(t, c["tr0"] - 0.3, c["ci0"] + 0.1, 0.25, 0.4)
    if a <= 0: return
    with P.layer(a):
        hit = prog(t, c["seg"] - 0.15, c["seg"] + 0.15)
        field(P, 540, 560, 560, 110, "camila2024", 1, size=52, red=hit)
        la = prog(t, c["filtro"] - 0.3, c["filtro"] + 0.2)
        if la > 0:
            # la lista corre y frena justo en la clave
            row = 74
            target = LEAKED.index("camila2024")
            ts0 = c["filtro"]; ts1 = c["seg"]
            u = in_out_cubic(prog(t, ts0, ts1))
            pos = lerp(-6, target + 32, u)          # 32 vueltas de lista: ver abajo
            with P.layer(la):
                P.rect(240, 700, 840, 1240, L.CARD, 0.75, radius=24)
                P.rect(250, 935, 830, 1005, L.RED, 0.18 + 0.5 * hit, radius=14)
                with P.clip_rect(240, 706, 840, 1234):
                    for j in range(-5, 6):
                        idx = int(math.floor(pos)) + j
                        y = 970 + (idx - pos) * row
                        nm = LEAKED[idx % len(LEAKED)]
                        on = (j == 0 and hit > 0 and nm == "camila2024")
                        al = 1 - abs(y - 970) / 300
                        P.text(nm, 540, y + 14, 40, L.RED if on else L.FG, clamp(al) * (0.6 + 0.4 * on), face=MONO)
        if hit > 0:
            P.circle(540, 560, 140 + 120 * hit, L.RED, 0.45 * (1 - hit), stroke=6)


def cierre_scene(P, t):
    c = CUE
    a = prog(t, c["ci0"] - 0.3, c["ci0"] + 0.2, in_out_cubic)
    if a <= 0: return
    with P.layer(a):
        end = c["end"]
        ra = prog(t, c["rara"] - 0.4, c["rara"])
        lg = prog(t, c["larga"] - 0.25, c["larga"] + 0.35, in_out_cubic)
        az = prog(t, c["azar"] - 0.1, c["azar"] + 0.5)
        loop = prog(t, end - 1.1, end - 0.35, in_out_cubic)
        # 1) «¿cuánto tarda?» y la clave «rara»
        weird = "C@m1la!"
        wa = ra * (1 - lg)
        if wa > 0:
            field(P, 540, 700, 520, 110, weird, wa, size=52)
            cross(P, 540, 700, 2.2, prog(t, c["rara"] + 0.1, c["rara"] + 0.4) * wa)
            P.text("rara", 540, 830, 40, L.GRAY, wa, face=C.FONT_SEMI)
        qa = prog(t, c["ci0"] - 0.1, c["ci0"] + 0.3) * (1 - ra)
        if qa > 0:
            cells(P, 540, 740, ["•"] * 8, qa)
            P.text("?", 540, 600, 120, L.RED, qa, face=C.FONT_BLACK)
        # 2) larga y al azar
        if lg > 0 and loop < 1:
            phrase = "tetera-volcán-lluvia-mapa"
            w = lerp(520, 960, lg)
            shown = phrase[:int(len(phrase) * lg)]
            if az > 0 and az < 1:
                shown = "".join(ch if rnd(i, 9) < az else rchar(LOW, int(t * 25), i) for i, ch in enumerate(phrase))
            field(P, 540, 760, w, 120, shown, lg * (1 - loop), size=40, border=L.DIM, red=az * 0.0)
            P.text("larga", 300, 900, 46, L.FG, lg * (1 - loop), face=C.FONT_BLACK)
            P.text("al azar", 760, 900, 46, L.RED, az * (1 - loop), face=C.FONT_BLACK)
            check(P, 540, 1040, 1.4, prog(t, c["azar"] + 0.3, c["azar"] + 0.6) * (1 - loop))
        # 3) empalme con el gancho
        if loop > 0:
            cells(P, 540, 740, ["•"] * 8, loop)


# =============================================================== composición
def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {}
    c["ocho"] = T("hook", "ocho"); c["cuanto"] = T("hook", "Cuánto"); c["adiv"] = T("hook", "adivinarla")
    c["b0"] = T("bloqueo"); c["a1"] = T("bloqueo", "una"); c["a2"] = T("bloqueo", "página"); c["a3"] = T("bloqueo", "tercer")
    c["bloquea"] = T("bloqueo", "bloquea")
    c["r0"] = T("robo"); c["lista"] = T("robo", "lista"); c["huellas"] = T("robo", "huellas"); c["deshacer"] = T("robo", "deshacer")
    c["i0"] = T("imitar"); c["imitar"] = T("imitar", "imitar"); c["inventan"] = T("imitar", "inventan")
    c["coincide"] = T("imitar", "Coincide"); c["encontr"] = T("imitar", "encontraron")
    c["g0"] = T("gpu"); c["tarjetas"] = T("gpu", "tarjetas"); c["prueban"] = T("gpu", "prueban"); c["cien"] = T("gpu", "cien")
    c["segundo"] = T("gpu", "segundo")
    c["c0"] = T("cifras"); c["empresa"] = T("cifras", "empresa"); c["ocho1"] = T("cifras", "ocho")
    c["dos"] = T("cifras", "dos"); c["ocho2"] = T("cifras", "ocho", which=1); c["n132"] = T("cifras", "132")
    c["p0"] = T("porque"); c["mult"] = T("porque", "multiplica"); c["n26"] = T("porque", "26")
    c["casi"] = T("porque", "casi"); c["teclado"] = T("porque", "teclado")
    c["tr0"] = T("trampa"); c["filtro"] = T("trampa", "prueban"); c["seg"] = T("trampa", "segundos")
    c["ci0"] = T("cierre"); c["rara"] = T("cierre", "rara"); c["larga"] = T("cierre", "larga"); c["azar"] = T("cierre", "azar")
    c["end"] = tl.duration
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    c = CUE
    glow = 0.5 * pulse(t, c["encontr"] - 0.2, 1.3) + 0.6 * pulse(t, c["n132"] - 0.2, 1.4) + 0.5 * pulse(t, c["seg"] - 0.2, 1.3)
    L.background(P, t, glow=glow)
    with P.transform(0, 45):
        hook_scene(P, t)
        bloqueo_scene(P, t)
        robo_scene(P, t)
        imitar_scene(P, t)
        gpu_scene(P, t)
        cifras_scene(P, t)
        porque_scene(P, t)
        trampa_scene(P, t)
        cierre_scene(P, t)
    L.vignette(P, 0.5)
    header(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0, glow=0.6)
    P.text("¿CUÁNTO TARDAN", 540, 560, 92, L.FG, 1, face=C.FONT_BLACK)
    P.text("EN ADIVINAR", 540, 665, 92, L.FG, 1, face=C.FONT_BLACK)
    P.text("TU CLAVE?", 540, 770, 104, L.RED, 1, face=C.FONT_BLACK)
    cells(P, 540, 960, list("qm•k•t•w"), 1, lit=[0, 1, 0, 1, 0, 1, 0, 1])
    P.text(fmt(208_827_064_576), 540, 1150, 64, L.FG, 1, face=MONO)
    P.text("combinaciones", 540, 1205, 32, L.GRAY, 1, face=C.FONT_SEMI)
    L.vignette(P, 0.4)
    header(P)


def sfx_cues(tl):
    c = CUE
    return [(0.0, "swell", 0.3), (c["ocho"], "tick", 0.35), (c["adiv"], "riser", 0.3), (c["cuanto"], "pop", 0.4),
            (c["b0"] - 0.3, "whoosh", 0.35), (c["a1"], "tick", 0.4), (c["a2"], "tick", 0.4), (c["a3"], "tick", 0.45),
            (c["bloquea"] + 0.15, "thump", 0.55),
            (c["r0"] - 0.3, "whoosh", 0.35), (c["lista"], "whoosh_down", 0.35), (c["huellas"], "rewind", 0.35),
            (c["deshacer"], "pop_low", 0.45),
            (c["imitar"], "pop", 0.4), (c["inventan"], "tick", 0.3), (c["encontr"], "ding", 0.55),
            (c["g0"] - 0.3, "whoosh", 0.35), (c["tarjetas"], "thump", 0.4), (c["cien"], "riser", 0.3),
            (c["c0"] - 0.3, "whoosh", 0.35), (c["dos"], "pop", 0.45), (c["ocho2"] + 0.8, "riser", 0.35), (c["n132"], "ding", 0.6),
            (c["p0"] - 0.3, "whoosh", 0.35), (c["mult"], "tick", 0.35), (c["casi"], "pop", 0.4),
            (c["tr0"] - 0.3, "whoosh", 0.35), (c["filtro"], "rewind", 0.35), (c["seg"], "thump", 0.55),
            (c["ci0"] - 0.3, "whoosh", 0.35), (c["rara"] + 0.1, "pop_low", 0.4), (c["larga"], "whoosh", 0.3),
            (c["azar"] + 0.3, "ding", 0.45)]


def music_kw(tl):
    c = CUE
    return {"arp_from": c["i0"], "pulse": (c["c0"], c["ci0"]), "quiet": [(c["ocho2"] - 0.1, c["n132"] + 0.1)]}
