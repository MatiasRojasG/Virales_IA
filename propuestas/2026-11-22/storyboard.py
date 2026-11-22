"""Storyboards 22-nov-2026: 5 bocetos por idea con el estilo de los reels (reelforge + marca)."""
import math, sys
from pathlib import Path
import numpy as np, skia
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from reelforge import config as C, marca as L
from reelforge.draw import P as Pc, frame_surface, paint

OUT = Path(__file__).resolve().parent
LOGO = None

def header(P):
    global LOGO
    if LOGO is None:
        im = Image.open(C.ROOT / "assets/marca/logo_blanco.png").convert("RGBA")
        h = 44; w = round(im.width * h / im.height); im = im.resize((w * 2, h * 2), Image.LANCZOS)
        LOGO = (skia.Image.fromarray(np.array(im), colorType=skia.kRGBA_8888_ColorType), w, h)
    img, w, h = LOGO
    P.img(img, 64, 256, 64 + w, 256 + h, 1, nearest=False)
    P.text(L.NAME, 64 + w + 18, 288, 26, L.FG, 0.85, face=C.FONT_BOLD, align="left", tracking=1.5)
    P.text("22 NOV 2026", 1016, 288, 24, L.FG, 0.7, face=C.FONT_SEMI, align="right", tracking=2)

def sub(P, s):
    L.sub_band(P)
    parts = [(seg, L.RED if i % 2 else L.FG) for i, seg in enumerate(s.split("*")) if seg]
    P.rich(parts, 540, 1410, 52, 1, face=C.FONT_BOLD)


# ---------------------------------------------------------------- objetos
def phone(P, x, y, s=1, crack=0.0):
    P.rect(x - 150*s, y - 290*s, x + 150*s, y + 290*s, L.FG, 1, stroke=8, radius=40*s)
    P.rect(x - 128*s, y - 262*s, x + 128*s, y + 262*s, L.CARD, 1, radius=26*s)
    P.rect(x - 40*s, y - 250*s, x + 40*s, y - 236*s, L.DIM, 1, radius=6)
    if crack:
        pts = [(x - 20*s, y - 40*s), (x + 30*s, y + 10*s), (x + 10*s, y + 70*s), (x + 60*s, y + 130*s)]
        for a, b in zip(pts, pts[1:]): P.line(*a, *b, L.RED, crack, w=5)

def hammer(P, x, y, s=1):
    P.line(x, y, x + 160*s, y - 160*s, L.BROWN, 1, w=22*s)
    P.rect(x + 110*s, y - 260*s, x + 280*s, y - 170*s, L.GRAY, 1, radius=10)

def ions(P, x0, y0, x1, y1, big_rows=0, arrows=False):
    rows = 6; cols = 10
    for j in range(rows):
        for i in range(cols):
            x = x0 + (x1 - x0) * (i + 0.5) / cols; y = y0 + (y1 - y0) * (j + 0.5) / rows
            if j < big_rows or j >= rows - big_rows: P.circle(x, y, 30, L.RED, 1)
            else: P.circle(x, y, 17, L.GRAY, 1)
    if arrows:
        for yy in (y0 - 40, y1 + 40):
            P.arrow(x0 - 70, yy, x0 + 50, yy, L.FG, 1, w=6); P.arrow(x1 + 70, yy, x1 - 50, yy, L.FG, 1, w=6)

ROOM = [(160, 560), (920, 560), (920, 900), (640, 900), (640, 1260), (160, 1260)]
def room(P, a=1.0, rgb=None):
    pth = skia.Path(); pth.moveTo(*ROOM[0])
    for p in ROOM[1:]: pth.lineTo(*p)
    pth.close(); P.c.drawPath(pth, paint(rgb or L.FG, a, stroke=6))
    P.rect(260, 640, 420, 760, L.DIM, a, radius=10)  # mueble

def robot(P, x, y, laser=False):
    P.circle(x, y, 60, L.CARD, 1); P.circle(x, y, 60, L.FG, 1, stroke=7)
    P.circle(x, y, 22, L.RED if laser else L.GRAY, 1)

def rays(P, x, y, n=36, a=0.7):
    import itertools
    walls = list(zip(ROOM, ROOM[1:] + ROOM[:1])) + [((260, 640), (420, 640)), ((260, 760), (420, 760)), ((260, 640), (260, 760)), ((420, 640), (420, 760))]
    hits = []
    for k in range(n):
        ang = 2 * math.pi * k / n; dx, dy = math.cos(ang), math.sin(ang); best = 1e9
        for (ax, ay), (bx, by) in walls:
            ex, ey = bx - ax, by - ay; den = dx * ey - dy * ex
            if abs(den) < 1e-9: continue
            t = ((ax - x) * ey - (ay - y) * ex) / den; u = ((ax - x) * dy - (ay - y) * dx) / den
            if t > 0 and 0 <= u <= 1: best = min(best, t)
        hx, hy = x + dx * best, y + dy * best; hits.append((hx, hy))
        if a: P.line(x, y, hx, hy, L.RED, a * 0.5, w=2)
    return hits

def ad(P, x, y, s=1):
    phone(P, x, y, s)
    P.rect(x - 110*s, y - 200*s, x + 110*s, y + 20*s, L.FG, 1, radius=16)
    P.circle(x, y - 90*s, 60*s, L.GRAY, 1)
    P.text("-80 %", x, y + 90*s, 64*s, L.RED, 1, face=C.FONT_BLACK)
    P.rect(x - 100*s, y + 140*s, x + 100*s, y + 200*s, L.RED, 1, radius=12)
    P.text("COMPRAR", x, y + 182*s, 30*s, L.FG, 1, face=C.FONT_BOLD)

def box(P, x, y, s=1, empty=True):
    P.rect(x - 130*s, y - 90*s, x + 130*s, y + 110*s, L.BROWN, 1, radius=8)
    P.line(x - 130*s, y - 20*s, x + 130*s, y - 20*s, L.BG, 0.6, w=4)
    if empty: P.text("?", x, y + 80*s, 110*s, L.FG, 1, face=C.FONT_BLACK)

# ---------------------------------------------------------------- escenas
def A1(P):
    phone(P, 540, 900, 1.15); hammer(P, 700, 820, 1.0)
    P.text("?", 540, 950, 160, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "¿Por qué *no se rompe*?")
def A2(P):
    P.rect(140, 760, 940, 960, L.FG, 0.15); P.rect(140, 760, 940, 960, L.FG, 1, stroke=5)
    pth = skia.Path(); pth.moveTo(510, 760); pth.lineTo(540, 840); pth.lineTo(570, 760)
    P.c.drawPath(pth, paint(L.RED, 1, stroke=6))
    P.arrow(480, 700, 260, 700, L.RED, 1, w=8); P.arrow(600, 700, 820, 700, L.RED, 1, w=8)
    P.text("grieta diminuta", 540, 1060, 48, L.GRAY, 1, face=C.FONT_BOLD)
    sub(P, "El vidrio se rompe *desde una grieta*")
def A3(P):
    P.rect(160, 620, 920, 1180, L.RED, 0.12, radius=30); P.rect(160, 620, 920, 1180, L.FG, 1, stroke=5, radius=30)
    P.rect(300, 760, 780, 1040, L.FG, 0.2); P.text("≈ 400 °C", 540, 700, 56, L.RED, 1, face=C.FONT_BLACK)
    P.circle(250, 900, 17, L.GRAY, 1); P.arrow(270, 900, 340, 870, L.GRAY, 1, w=4)
    P.circle(830, 900, 30, L.RED, 1); P.arrow(800, 900, 740, 900, L.RED, 1, w=5)
    P.text("sodio sale · potasio entra", 540, 1120, 40, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Un baño de *sal fundida*")
def A4(P):
    ions(P, 220, 660, 860, 1100, big_rows=1, arrows=True)
    P.text("COMPRIMIDO", 540, 1230, 52, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "Iones grandes: la superficie *se aprieta*")
def A5(P):
    phone(P, 540, 900, 1.15, crack=0.0); P.text("más difícil de romper", 540, 1290, 46, L.FG, 1, face=C.FONT_BOLD)
    P.arrow(300, 900, 380, 900, L.RED, 1, w=8); P.arrow(780, 900, 700, 900, L.RED, 1, w=8)
    sub(P, "Aprieta las grietas… *no es irrompible*")

def B1(P):
    room(P, 0.35); robot(P, 400, 1050); P.text("?", 400, 940, 110, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "¿Cómo sabe *dónde está*?")
def B2(P):
    room(P, 0.25); rays(P, 400, 1050, 48); robot(P, 400, 1050, True)
    P.text("≈ 6 vueltas/s", 800, 1100, 44, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "Un láser que *gira* y mide")
def B3(P):
    for hx_, hy_ in rays(P, 400, 1050, 180, a=0): P.circle(hx_, hy_, 5, L.FG, 1)
    robot(P, 400, 1050, True); P.text("miles de puntos", 540, 1320 - 30, 1, L.BG, 0)
    sub(P, "Cada rebote, *un punto*")
def B4(P):
    room(P, 1.0); robot(P, 700, 700, True)
    P.circle(400, 1050, 10, L.GRAY, 1); P.line(400, 1050, 560, 860, L.GRAY, 1, w=3); P.line(560, 860, 700, 700, L.GRAY, 1, w=3)
    P.text("MAPA + UBICACIÓN", 540, 1320 - 20, 1, L.BG, 0)
    sub(P, "Mapa y ubicación *a la vez*")
def B5(P):
    room(P, 1.0)
    for k in range(9):
        y = 800 + k * 52; x1 = 900 if y < 900 else 620
        P.line(190, y, x1, y, L.RED, 0.8, w=6)
    robot(P, 560, 1216, True)
    sub(P, "Por eso limpia *en franjas*")

def C1(P):
    ad(P, 330, 880, 0.95); P.arrow(520, 900, 640, 900, L.FG, 1, w=8); box(P, 820, 920, 0.95)
    sub(P, "Lo compraste… ¿y *nunca llegó*?")
def C2(P):
    P.text("≈ 30 %", 540, 820, 170, L.RED, 1, face=C.FONT_BLACK)
    P.text("de las víctimas de estafas", 540, 960, 44, L.FG, 1, face=C.FONT_BOLD)
    P.text("dijo que empezó en redes", 540, 1020, 44, L.FG, 1, face=C.FONT_BOLD)
    P.text("FTC · EE. UU. · 2025", 540, 1140, 36, L.GRAY, 1, face=C.FONT_SEMI)
    sub(P, "Muchas empiezan *en redes*")
def C3(P):
    for i in range(10):
        x = 190 + i * 78; c = L.RED if i < 4 else L.DIM
        P.circle(x, 820, 26, c, 1); P.rect(x - 26, 856, x + 26, 940, c, 1, radius=14)
    P.text("> 40 %", 540, 1080, 110, L.RED, 1, face=C.FONT_BLACK)
    P.text("de quienes perdieron plata en redes", 540, 1170, 40, L.FG, 1, face=C.FONT_BOLD)
    P.text("compró algo visto en un anuncio", 540, 1225, 40, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Más de *4 de cada 10*")
def C4(P):
    P.rect(150, 700, 930, 800, L.CARD, 1, radius=20); P.text("marcafamosa-ofertas.shop", 540, 768, 44, L.RED, 1, face=C.FONT_BOLD)
    P.rect(150, 860, 930, 960, L.CARD, 1, radius=20); P.text("marcafamosa.com", 540, 928, 44, L.FG, 1, face=C.FONT_BOLD)
    P.text("✗", 980, 770, 60, L.RED, 1, face=C.FONT_BLACK); P.text("✓", 980, 930, 60, L.FG, 1, face=C.FONT_BLACK)
    sub(P, "Sitios que *imitan* a una marca")
def C5(P):
    ad(P, 540, 880, 0.95); P.circle(540, 880, 330, L.RED, 1, stroke=10); P.line(310, 1110, 770, 650, L.RED, 1, w=10)
    sub(P, "Antes de pagar, *busca al vendedor*")

IDEAS = {"A": ([A1, A2, A3, A4, A5], "DÍA A DÍA · ¿Por qué la pantalla del celular aguanta tanto?"),
         "B": ([B1, B2, B3, B4, B5], "ROBÓTICA · ¿Cómo sabe tu robot aspiradora dónde está?"),
         "C": ([C1, C2, C3, C4, C5], "CIBERSEGURIDAD · El anuncio perfecto… y el paquete que nunca llega")}

def render(fn):
    arr, surf = frame_surface(); P = Pc(surf.getCanvas()); L.background(P, 0)
    header(P); fn(P); L.vignette(P, 0.4)
    import re
    return Image.fromarray(arr[..., :3].copy())

def strip(key):
    fns, title = IDEAS[key]
    tw, th, pad = 360, 640, 16
    out = Image.new("RGB", (pad + 5 * (tw + pad), th + 2 * pad + 70), (10, 10, 10))
    d = ImageDraw.Draw(out); f = ImageFont.truetype(str(C.FONTS / C.FONT_BOLD), 30)
    d.text((pad, 18), f"{key} · {title}", fill=(242, 242, 242), font=f)
    for i, fn in enumerate(fns):
        out.paste(render(fn).resize((tw, th), Image.LANCZOS), (pad + i * (tw + pad), 70 + pad))
    out.save(OUT / f"storyboard_{key}.png")

if __name__ == "__main__":
    for k in IDEAS: strip(k)
