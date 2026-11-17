"""Escenas — «Glow up: 10 reglas con ciencia» (decálogo, marca stheq.ia).

Estructura fija para decálogos: número grande arriba, un ícono blanco animado en el centro que
reacciona a la palabra clave de la narración, una etiqueta corta y una fila de 10 puntos de avance.
Cada regla entra desde la derecha y sale hacia la izquierda (continuidad espacial).
"""
from __future__ import annotations
import math
import skia
from reelforge import config as C
from reelforge import subtitles as SUB
from reelforge import marca as L
from reelforge.draw import paint
from reelforge.ease import clamp, lerp, lerp_c, prog, window, pulse, out_cubic, out_back, in_out_cubic, smooth

TL = None; EP = {}; CHUNKS = []; CUE = {}
CX, CY = 540, 880                       # centro del ícono
NUM_Y, LAB_Y, DOTS_Y = 575, 1170, 1265
LABELS = ["dormir 7 h o más", "protector cada mañana", "frutas y verduras", "150 min + fuerza",
          "no fumar", "limpieza suave", "hidratar", "no reventar granos", "sonreír", "constancia"]
FG, GRAY, DIM, RED = L.FG, L.GRAY, L.DIM, L.RED


def T(beat, word=None, which=0, end=False):
    return TL.t(beat, word, which, end)


def cue(k, word):
    return CUE[f"r{k}_{word}"]


def X(P, x, y, s, rgb, a, w=10):
    P.line(x - s, y - s, x + s, y + s, rgb, a, w=w); P.line(x - s, y + s, x + s, y - s, rgb, a, w=w)


def check(P, x, y, s, rgb, a, frac=1.0, w=10):
    pts = [(x - s, y), (x - s * 0.3, y + s * 0.7), (x + s, y - s * 0.8)]
    f1 = clamp(frac * 2); f2 = clamp(frac * 2 - 1)
    P.line(*pts[0], lerp(pts[0][0], pts[1][0], f1), lerp(pts[0][1], pts[1][1], f1), rgb, a, w=w)
    if f2 > 0: P.line(*pts[1], lerp(pts[1][0], pts[2][0], f2), lerp(pts[1][1], pts[2][1], f2), rgb, a, w=w)


# =============================================================== íconos por regla
def ic_sleep(P, t, lt, a):
    # luna, zzz y dos caras: descansada / sin dormir
    k = prog(t, cue(1, "estudio") - 0.2, cue(1, "estudio") + 0.4)
    m = in_out_cubic(k)
    L.moon(P, lerp(CX, 300, m), lerp(CY - 40, 690, m), lerp(130, 70, m), a)
    for j in range(3):
        u = (lt * 0.6 + j / 3) % 1
        P.text("z", lerp(CX + 120, 400, m) + u * 60, lerp(CY - 120, 640, m) - u * 120, 40 + 20 * u, FG, a * math.sin(math.pi * u) * (1 - m), face=C.FONT_BLACK)
    if m > 0:
        tired = prog(t, cue(1, "menos") - 0.3, cue(1, "menos") + 0.4)
        with P.layer(a * m):
            L.head(P, 420, 920, 0.62, smile=0.4)
            L.head(P, 720, 920, 0.62, tired=tired, smile=0.4 * (1 - tired))
            P.text("descansado", 420, 1095, 30, GRAY, 1, face=C.FONT_BOLD)
            P.text("sin dormir", 720, 1095, 30, RED if tired > 0.5 else GRAY, 1, face=C.FONT_BOLD)
    else:
        P.text("7 h+", CX, CY + 170, 64, FG, a, face=C.FONT_BLACK)


def ic_sun(P, t, lt, a):
    L.bottle(P, CX - 140, CY + 20, 1.05, a, label="FPS 30+")
    sx, sy = CX + 190, CY - 140
    # rayos que chocan contra un escudo
    for j in range(4):
        u = (lt * 1.1 + j / 4) % 1
        x0, y0 = sx - 40, sy + 40
        x1, y1 = lerp(x0, CX - 30, u), lerp(y0, CY - 30, u)
        P.line(x1 - 22, y1 - 18, x1, y1, FG, a * (1 - u) * 0.9, w=6)
    P.c.save(); P.c.translate(sx, sy); P.c.restore()
    for k in range(10):
        ang = k * math.pi / 5 + lt * 0.4
        P.line(sx + math.cos(ang) * 62, sy + math.sin(ang) * 62, sx + math.cos(ang) * 82, sy + math.sin(ang) * 82, FG, a, w=7)
    P.circle(sx, sy, 48, FG, a)
    sh = prog(t, cue(2, "diario") - 0.2, cue(2, "diario") + 0.4)
    if sh > 0:
        pth = skia.Path(); pth.addArc(skia.Rect(CX - 300, CY - 230, CX + 20, CY + 270), -60, 70)
        P.c.drawPath(pth, paint(FG, a * sh, stroke=8))


def ic_food(P, t, lt, a):
    # manzana y zanahoria en trazo blanco; la cara gana un tono más cálido
    ax, ay = CX - 170, CY - 60
    pth = skia.Path()
    pth.moveTo(ax, ay - 70); pth.cubicTo(ax - 120, ay - 130, ax - 150, ay + 60, ax - 40, ay + 110)
    pth.cubicTo(ax - 10, ay + 125, ax + 10, ay + 125, ax + 40, ay + 110)
    pth.cubicTo(ax + 150, ay + 60, ax + 120, ay - 130, ax, ay - 70)
    P.c.drawPath(pth, paint(FG, a, stroke=8))
    P.line(ax, ay - 70, ax + 12, ay - 120, FG, a, w=8)
    P.c.drawOval(skia.Rect(ax + 15, ay - 140, ax + 75, ay - 110), paint(FG, a, stroke=6))
    cx, cy = CX - 170, CY + 190
    pth = skia.Path(); pth.moveTo(cx - 110, cy - 25); pth.lineTo(cx + 120, cy); pth.lineTo(cx - 110, cy + 25); pth.close()
    P.c.drawPath(pth, paint(FG, a, stroke=7))
    for k in range(3):
        P.line(cx - 110, cy, cx - 160, cy - 30 + k * 30, FG, a, w=6)
    # semanas y tono de piel
    w = prog(t, cue(3, "seis") - 0.1, cue(3, "saludable") + 0.3, lambda u: u)
    tone = lerp_c(lerp_c(L.SKIN, (0.62, 0.62, 0.6), 0.45), lerp_c(L.SKIN, (0.95, 0.68, 0.45), 0.25), smooth(w))
    L.head(P, CX + 200, CY - 50, 0.7, skin=tone, a=a, smile=0.3)
    for k in range(6):
        on = clamp(w * 6 - k)
        P.circle(CX + 75 + k * 50, CY + 175, 12, FG if on > 0.5 else DIM, a)
    P.text("6 semanas", CX + 200, CY + 235, 30, GRAY, a * prog(t, cue(3, "seis") - 0.1, cue(3, "seis") + 0.3), face=C.FONT_BOLD)


def ic_move(P, t, lt, a):
    # mancuerna que sube y baja + semana de 7 días
    yy = CY - 80 - 40 * (0.5 + 0.5 * math.sin(lt * 4))
    P.rect(CX - 150, yy - 8, CX + 150, yy + 8, FG, a, radius=8)
    for sx in (-1, 1):
        P.rect(CX + sx * 150 - 26, yy - 70, CX + sx * 150 + 26, yy + 70, FG, a, radius=12)
        P.rect(CX + sx * 200 - 18, yy - 50, CX + sx * 200 + 18, yy + 50, FG, a, radius=10)
    days = "LMMJVSD"
    f = prog(t, cue(4, "ciento") - 0.1, cue(4, "semana") + 0.2, lambda u: u)
    fz = prog(t, cue(4, "fuerza") - 0.1, cue(4, "fuerza") + 0.3)
    for k, d in enumerate(days):
        x = CX - 300 + k * 100; y = CY + 120
        fill = clamp(f * 7 - k)
        P.rect(x - 34, y - 34, x + 34, y + 34, FG, a * 0.9, stroke=4, radius=12)
        P.rect(x - 34, y + 34 - 68 * fill * 0.7, x + 34, y + 34, FG, a * 0.35, radius=12)
        if k in (1, 4) and fz > 0:
            P.rect(x - 34, y - 34, x + 34, y + 34, FG, a * fz, radius=12)
            P.text("F", x, y + 14, 38, L.BG, a * fz, face=C.FONT_BLACK)
        P.text(d, x, y + 80, 28, GRAY, a, face=C.FONT_BOLD)


def ic_smoke(P, t, lt, a):
    old = prog(t, cue(5, "mayor") - 0.4, cue(5, "mayor") + 0.5)
    L.head(P, CX - 170, CY + 10, 0.66, a=a, smile=0.2)
    L.head(P, CX + 170, CY + 10, 0.66, a=a, wrinkles=0.9 * old, spots=0.5 * old, smile=0.2 * (1 - old))
    # cigarro tachado
    x0, y0 = CX - 100, CY + 160
    P.rect(x0, y0 - 14, x0 + 200, y0 + 14, FG, a, radius=6); P.rect(x0 + 150, y0 - 14, x0 + 200, y0 + 14, GRAY, a, radius=6)
    for j in range(3):
        u = (lt * 0.7 + j / 3) % 1
        P.circle(x0 + 205 + 20 * math.sin(u * 6), y0 - 30 - u * 110, 10 + 14 * u, GRAY, a * 0.5 * (1 - u))
    X(P, x0 + 100, y0, 42, RED, a * prog(t, T("r5") + 0.2, T("r5") + 0.6), w=10)
    P.text("gemelos", CX, CY - 215, 32, GRAY, a * prog(t, cue(5, "gemelos") - 0.1, cue(5, "gemelos") + 0.3), face=C.FONT_BOLD)


def ic_wash(P, t, lt, a):
    L.head(P, CX, CY + 10, 0.75, a=a, eyes_closed=True, smile=0.3)
    # espuma suave: burbujas que flotan
    for k in range(9):
        u = (lt * 0.35 + k / 9) % 1
        x = CX - 120 + (k * 37) % 240; y = CY + 60 - u * 260
        P.circle(x, y, 14 + 10 * math.sin(k), FG, a * 0.7 * math.sin(math.pi * u), stroke=4)
    ir = prog(t, cue(6, "irrita") - 0.4, cue(6, "irrita") + 0.2)
    if ir > 0:
        # cepillo que frota: tachado
        bx = CX + 250 + 30 * math.sin(lt * 14) * ir
        P.rect(bx - 60, CY - 30, bx + 60, CY + 10, GRAY, a * ir, radius=10)
        for k in range(6): P.line(bx - 50 + k * 20, CY + 10, bx - 50 + k * 20, CY + 40, GRAY, a * ir, w=5)
        X(P, bx, CY, 70, RED, a * ir, w=9)


def ic_hydrate(P, t, lt, a):
    # gota que cae sobre una superficie y se expande
    u = (lt % 1.6) / 1.6
    yd = lerp(CY - 250, CY + 10, in_out_cubic(clamp(u * 1.6)))
    pth = skia.Path(); r = 70
    pth.moveTo(CX, yd - r * 1.8); pth.cubicTo(CX + r * 1.1, yd - r * 0.5, CX + r, yd + r, CX, yd + r)
    pth.cubicTo(CX - r, yd + r, CX - r * 1.1, yd - r * 0.5, CX, yd - r * 1.8)
    P.c.drawPath(pth, paint(FG, a * (1 - prog(u, 0.62, 0.7))))
    P.line(CX - 300, CY + 80, CX + 300, CY + 80, FG, a, w=6)
    v = clamp((u - 0.62) / 0.38)
    if v > 0:
        for s_ in (1, 0.6):
            P.c.drawOval(skia.Rect(CX - 220 * v * s_, CY + 80 - 22 * v * s_, CX + 220 * v * s_, CY + 80 + 22 * v * s_),
                         paint(FG, a * (1 - v), stroke=4))
    P.text("después de lavar", CX, CY + 200, 34, GRAY, a * prog(t, cue(7, "después") - 0.1, cue(7, "después") + 0.3), face=C.FONT_BOLD)


def ic_pimple(P, t, lt, a):
    r = 210
    P.circle(CX, CY, r, L.SKIN, a)
    P.circle(CX, CY, r, FG, a * 0.25, stroke=3)
    mk = prog(t, cue(8, "manchas") - 0.2, cue(8, "manchas") + 0.5)
    P.circle(CX + 10, CY - 10, 34, lerp_c((0.85, 0.45, 0.42), L.BROWN, mk), a)
    P.circle(CX + 2, CY - 20, 12, lerp_c((0.98, 0.92, 0.8), L.BROWN, mk), a * (1 - mk))
    # dedos que se acercan y se tachan
    ap = prog(t, T("r8") + 0.1, T("r8") + 0.6)
    for sx in (-1, 1):
        x = CX + sx * lerp(340, 140, ap)
        P.rect(x - 34, CY - 80, x + 34, CY + 80, L.SKIN2, a, radius=34)
        P.c.drawOval(skia.Rect(x - 22, CY - 70, x + 22, CY - 30), paint(L.SKIN, a))
    X(P, CX, CY, 120, RED, a * prog(t, T("r8") + 0.7, T("r8") + 1.0), w=12)


def ic_smile(P, t, lt, a):
    s = prog(t, cue(9, "sonríe") - 0.2, cue(9, "sonríe") + 0.6, smooth)
    L.head(P, CX, CY - 30, 0.9, a=a, smile=lerp(-0.2, 1.4, s))
    at = prog(t, cue(9, "atractiva") - 0.2, cue(9, "atractiva") + 0.3)
    if at > 0:
        for k in range(8):
            ang = k * math.pi / 4 + lt * 0.3
            P.line(CX + math.cos(ang) * 230, CY - 30 + math.sin(ang) * 230, CX + math.cos(ang) * (230 + 30 * at),
                   CY - 30 + math.sin(ang) * (230 + 30 * at), FG, a * at, w=6)


def ic_streak(P, t, lt, a):
    # calendario de 4 semanas: un día no cambia nada; las semanas sí
    f = prog(t, cue(10, "nada") - 0.2, cue(10, "semanas") + 0.4, lambda u: u)
    big = prog(t, cue(10, "semanas") - 0.2, cue(10, "semanas") + 0.4)
    for k in range(28):
        i, j = k % 7, k // 7
        x = CX - 300 + i * 100; y = CY - 170 + j * 100
        P.rect(x - 38, y - 38, x + 38, y + 38, FG, a * 0.5, stroke=3, radius=12)
        on = clamp(f * 28 * (0.04 if big <= 0 else 1) - k) if big > 0 else (1.0 if k == 0 and f > 0 else 0.0)
        if on > 0: check(P, x, y, 22, FG, a, frac=on, w=7)
    if big > 0:
        P.rect(CX - 345, CY - 215, CX + 345, CY + 215, FG, a * big, stroke=6, radius=20)


ICONS = [ic_sleep, ic_sun, ic_food, ic_move, ic_smoke, ic_wash, ic_hydrate, ic_pimple, ic_smile, ic_streak]


# =============================================================== composición
def rule(P, t, k):
    t0, t1 = T(f"r{k}"), T(f"r{k}", end=True)
    ain = prog(t, t0 - 0.35, t0 + 0.3)
    aout = prog(t, t1 - 0.3, t1 + 0.25) if k < 10 else prog(t, t1 - 0.3, t1 + 0.4)
    a = ain * (1 - aout)
    if a <= 0: return
    dx = 140 * (1 - out_cubic(ain)) - 140 * in_out_cubic(aout)
    lt = t - t0
    with P.transform(dx, 0):
        # número grande
        sn = 0.85 + 0.15 * out_back(prog(t, t0 - 0.1, t0 + 0.35, lambda u: u))
        with P.transform(0, 0, sn, cx=CX, cy=NUM_Y - 40):
            P.text(str(k), CX, NUM_Y, 150, FG, a, face=C.FONT_BLACK)
        ICONS[k - 1](P, t, lt, a)
        P.text(LABELS[k - 1], CX, LAB_Y, 44, FG, a * prog(t, t0 + 0.2, t0 + 0.6), face=C.FONT_BOLD)


def dots(P, t):
    a = prog(t, T("r1") - 0.3, T("r1") + 0.2) * (1 - prog(t, T("cierre") + 0.2, T("cierre") + 0.7))
    if a <= 0: return
    cur = 0
    for k in range(1, 11):
        if t >= T(f"r{k}") - 0.1: cur = k
    for k in range(1, 11):
        x = CX - 270 + (k - 1) * 60
        if k == cur:
            P.circle(x, DOTS_Y, 11, FG, a)
        else:
            P.circle(x, DOTS_Y, 7, FG if k < cur else DIM, a * (0.8 if k < cur else 1))


def hook(P, t):
    c = CUE
    a = 1 - prog(t, T("r1") - 0.4, T("r1") + 0.1)
    if a <= 0: return
    # cara + tres cosas que no hacen falta (filtro, bisturí, billetes) que se tachan
    L.head(P, CX, 820, 0.85, a=a, smile=0.3)
    items = [("filtros", c["filtros"]), ("cirugías", c["cirugias"]), ("fortuna", c["fortuna"])]
    for j, (lab, tw) in enumerate(items):
        x = CX - 300 + j * 300; y = 1130
        ap = prog(t, tw - 0.2, tw + 0.2)
        P.pill(lab, x, y, 34, FG, a * ap, fill_a=0.06, bg=False)
        X(P, x, y, 30, RED, a * prog(t, tw + 0.25, tw + 0.5), w=7)
    # «10 reglas»: aparecen los 10 puntos
    ar = prog(t, c["diez"] - 0.2, c["diez"] + 0.4)
    if ar > 0:
        P.text("10", CX, 560, 130, FG, a * ar, face=C.FONT_BLACK)
        for k in range(10):
            P.circle(CX - 270 + k * 60, DOTS_Y, 7, FG, a * clamp(ar * 10 - k))


def closing(P, t):
    c = CUE
    a = prog(t, T("cierre") - 0.2, T("cierre") + 0.4)
    if a <= 0: return
    L.head(P, CX, 820, 0.85, a=a, smile=1.2)
    # las 10 reglas como una lista compacta de puntos con check
    g = prog(t, c["gratis"] - 0.3, c["gratis"] + 0.3)
    P.text("gratis", CX, 1135, 60, RED, a * g, face=C.FONT_BLACK)
    for k in range(10):
        x = CX - 270 + k * 60
        P.circle(x, DOTS_Y, 9, FG, a)
    sv = prog(t, c["guardalo"] - 0.2, c["guardalo"] + 0.4)
    if sv > 0:
        # ícono de guardar (marcador)
        bx, by = CX + 300, 610
        pth = skia.Path(); pth.moveTo(bx - 32, by - 45); pth.lineTo(bx + 32, by - 45); pth.lineTo(bx + 32, by + 45)
        pth.lineTo(bx, by + 20); pth.lineTo(bx - 32, by + 45); pth.close()
        P.c.drawPath(pth, paint(FG, a * sv))


def setup(tl, data, episode):
    global TL, EP, CHUNKS, CUE
    TL, EP = tl, episode
    c = {"filtros": T("hook", "filtros"), "cirugias": T("hook", "cirugías"), "fortuna": T("hook", "fortuna"),
         "diez": T("hook", "diez"), "gratis": T("cierre", "gratis"), "guardalo": T("cierre", "guárdalo")}
    words = {1: ["estudio", "menos"], 2: ["diario"], 3: ["seis", "saludable"], 4: ["ciento", "semana", "fuerza"],
             5: ["gemelos", "mayor"], 6: ["irrita"], 7: ["después"], 8: ["manchas"], 9: ["sonríe", "atractiva"],
             10: ["nada", "semanas"]}
    for k, ws in words.items():
        for w in ws:
            c[f"r{k}_{w}"] = T(f"r{k}", w)
    CUE = c
    CHUNKS = tl.chunks(SUB.measure, max_words=4)


def draw_frame(P, t):
    L.background(P, t, glow=0.4 * pulse(t, CUE["gratis"], 1.5))
    hook(P, t)
    for k in range(1, 11):
        rule(P, t, k)
    dots(P, t)
    closing(P, t)
    L.vignette(P, 0.5)
    L.title(P)
    L.sub_band(P)
    SUB.draw(P, CHUNKS, t, **L.SUB_COLORS)


def draw_cover(P, t=0.0):
    L.background(P, 1.0)
    P.text("10 REGLAS", 540, 470, 120, FG, 1, face=C.FONT_BLACK)
    P.text("DEL GLOW UP", 540, 590, 96, FG, 1, face=C.FONT_BLACK)
    P.text("QUE SÍ TIENEN CIENCIA", 540, 680, 52, RED, 1, face=C.FONT_BLACK)
    L.head(P, 540, 1000, 0.85, smile=1.0)
    for k in range(10):
        P.circle(540 - 270 + k * 60, 1300, 9, FG, 1)
    L.vignette(P, 0.4)
    L.title(P)


def sfx_cues(tl):
    c = CUE
    cues = [(0.0, "swell", 0.35), (c["filtros"] + 0.25, "pop_low", 0.35), (c["cirugias"] + 0.25, "pop_low", 0.35),
            (c["fortuna"] + 0.25, "pop_low", 0.35), (c["diez"] - 0.2, "riser", 0.35)]
    for k in range(1, 11):
        t0 = T(f"r{k}")
        cues += [(t0 - 0.3, "whoosh", 0.35), (t0, "tick", 0.55)]
    cues += [(c["r1_menos"], "pop_low", 0.35), (c["r2_diario"], "pop", 0.35), (c["r3_saludable"], "ding", 0.35),
             (c["r4_fuerza"], "thump", 0.4), (c["r5_mayor"], "pop_low", 0.4), (c["r6_irrita"], "pop_low", 0.35),
             (c["r8_manchas"], "pop_low", 0.35), (c["r9_atractiva"], "ding", 0.4), (c["r10_semanas"], "ding", 0.45),
             (T("cierre") - 0.3, "whoosh_down", 0.4), (c["gratis"], "ding", 0.6), (c["gratis"] - 0.2, "swell", 0.35)]
    return cues


def music_kw(tl):
    return {"arp_from": T("r1"), "pulse": (T("r4"), T("r10")), "quiet": []}
