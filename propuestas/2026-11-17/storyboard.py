"""Storyboard B/N (5 fotogramas clave) de las 3 propuestas del 17-nov-2026.
Uso: python propuestas/2026-11-17/storyboard.py"""
import math, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from reelforge import config as C
from reelforge.draw import P, frame_surface, vignette
from PIL import Image, ImageDraw

K = (0.0, 0.0, 0.0); W = (0.96, 0.96, 0.96); G1 = (0.62, 0.62, 0.62); G2 = (0.30, 0.30, 0.30); G3 = (0.14, 0.14, 0.14)
RED = (1.0, 0.30, 0.30)  # acento puntual
rng = np.random.default_rng(3)


def bg(p):
    p.c.clear(0xFF000000)


def sub(p, txt):
    p.text(txt, 540, 1410, 58, W, 1, face=C.FONT_XBOLD)


def face_blocks(p, cx, cy, n, size, seed=0):
    """Cara pixelada: bloques de gris en un óvalo."""
    r = np.random.default_rng(seed); cell = size / n
    for i in range(n):
        for j in range(n):
            x = cx - size / 2 + (j + .5) * cell; y = cy - size / 2 + (i + .5) * cell
            dx, dy = (x - cx) / (size * .38), (y - cy) / (size * .5)
            if dx * dx + dy * dy > 1: continue
            v = 0.35 + 0.4 * r.random()
            if abs(dy + .15) < .12 and abs(abs(dx) - .4) < .18: v = 0.12
            if abs(dy - .45) < .08 and abs(dx) < .3: v = 0.2
            p.rect(x - cell / 2, y - cell / 2, x + cell / 2, y + cell / 2, (v, v, v), 1)


def face_smooth(p, cx, cy, s, a=1.0, variant=0):
    p.circle(cx, cy, 170 * s, G1, a)
    for dx in (-60, 60): p.circle(cx + dx * s, cy - 30 * s, 16 * s, K, a)
    p.line(cx - 50 * s, cy + 70 * s, cx + 50 * s, cy + 70 * s, K, a, w=8 * s)
    if variant == 1: p.rect(cx - 170 * s, cy - 190 * s, cx + 170 * s, cy - 90 * s, G2, a, radius=60 * s)
    if variant == 2: p.circle(cx, cy - 150 * s, 90 * s, G2, a)


# ---------------------------------------------------------------- A · foto pixelada → la IA inventa
def A1(p):
    face_blocks(p, 540, 840, 9, 520, 1)
    p.text("16 × 16 px", 540, 520, 44, G1, 1, face=C.FONT_BOLD)
    sub(p, "¿Esta cara es real?")


def A2(p):
    face_blocks(p, 300, 840, 9, 360, 1)
    p.arrow(500, 840, 620, 840, W, 1, w=8)
    face_smooth(p, 800, 840, 0.85)
    p.text("IA", 560, 800, 40, W, 1, face=C.FONT_BLACK)
    sub(p, "La IA la convierte en 4K…")


def A3(p):
    face_blocks(p, 540, 640, 7, 260, 1)
    for k, v in enumerate((0, 1, 2)):
        face_smooth(p, 220 + k * 320, 1050, 0.6, 1, v)
    p.text("misma foto · 3 caras", 540, 1290, 36, G1, 1, face=C.FONT_SEMI)
    sub(p, "…pero hay mil caras posibles.")


def A4(p):
    p.text("2020", 540, 640, 140, W, 1, face=C.FONT_BLACK)
    p.text("PULSE", 540, 780, 70, G1, 1, face=C.FONT_BOLD)
    p.text("una foto pixelada de Obama", 540, 900, 40, W, 1, face=C.FONT_SEMI)
    p.text("→ un hombre blanco", 540, 960, 40, RED, 1, face=C.FONT_BOLD)
    sub(p, "Y el resultado fue otra persona.")


def A5(p):
    face_smooth(p, 540, 840, 1.1)
    p.text("detalle inventado", 540, 1160, 46, W, 1, face=C.FONT_BOLD)
    sub(p, "No recupera: imagina.")


# ---------------------------------------------------------------- B · ¿por qué se nota que lo escribió una IA?
def B1(p):
    p.rect(110, 560, 970, 1220, G3, 1, radius=36)
    lines = ["En el vertiginoso mundo", "actual, es crucial", "profundizar en este", "fascinante tapiz…"]
    for k, l in enumerate(lines): p.text(l, 160, 680 + k * 90, 52, W, 1, face=C.FONT_SEMI, align="left")
    sub(p, "Lo lees… y sabes que fue una IA.")


def B2(p):
    p.text("Hoy quiero…", 540, 620, 64, W, 1, face=C.FONT_BLACK)
    opts = [("ayudarte", .62), ("contarte", .21), ("bailar", .04)]
    for k, (w_, pr) in enumerate(opts):
        y = 760 + k * 150
        p.rect(170, y, 170 + 560 * pr / .62, y + 90, W if k == 0 else G2, 1, radius=18)
        p.text(w_, 190, y + 62, 46, K if k == 0 else W, 1, face=C.FONT_BOLD, align="left")
        p.text(f"{int(pr*100)} %", 920, y + 62, 42, G1, 1, face=C.FONT_BOLD, align="right")
    sub(p, "Siempre elige la palabra segura.")


def B3(p):
    xs = np.linspace(160, 920, 30); ys = 1200 - np.r_[np.full(22, 40), [60, 120, 260, 420, 520, 560, 570, 575]]
    for a, b, c, d in zip(xs, ys, xs[1:], ys[1:]): p.line(a, b, c, d, W, 1, w=7)
    p.text("«delve» en artículos científicos", 540, 600, 40, W, 1, face=C.FONT_BOLD)
    p.text("2022", 160, 1270, 32, G1, 1, face=C.FONT_SEMI, align="left"); p.text("2024", 920, 1270, 32, G1, 1, face=C.FONT_SEMI, align="right")
    sub(p, "Una palabra se disparó.")


def B4(p):
    for k in range(40):
        x = 150 + (k % 8) * 110; y = 640 + (k // 8) * 120
        p.circle(x, y, 34, W if k != 21 else G2, 1)
    p.text("promedio", 540, 1300 - 40, 46, G1, 1, face=C.FONT_BOLD)
    sub(p, "Suena al promedio de todos.")


def B5(p):
    p.rect(110, 600, 970, 1150, G3, 1, radius=36)
    p.text("Hoy quiero…", 540, 760, 70, W, 1, face=C.FONT_BLACK)
    p.text("¿?", 540, 960, 140, G1, 1, face=C.FONT_BLACK)
    sub(p, "Entonces… ¿se nota?")


# ---------------------------------------------------------------- C · el filtro de CV que descartaba mujeres
def doc(p, x, y, s=1.0, a=1.0, mark=None):
    p.rect(x - 90 * s, y - 120 * s, x + 90 * s, y + 120 * s, W, a, radius=10 * s)
    for k in range(5): p.line(x - 60 * s, y - 70 * s + k * 36 * s, x + 60 * s, y - 70 * s + k * 36 * s, G1, a, w=8 * s)


def C1(p):
    doc(p, 540, 820, 1.6)
    p.line(400, 640, 680, 1000, RED, 1, w=26); p.line(680, 640, 400, 1000, RED, 1, w=26)
    sub(p, "Tu CV ni siquiera llegó a un humano.")


def C2(p):
    p.text("2014–2017", 540, 600, 60, G1, 1, face=C.FONT_BOLD)
    for k in range(10):
        doc(p, 180 + (k % 5) * 180, 820 + (k // 5) * 300, 0.55)
    sub(p, "Una gran empresa entrenó una IA…")


def C3(p):
    for k in range(10):
        doc(p, 180 + (k % 5) * 180, 760 + (k // 5) * 300, 0.55, 1, None)
    p.text("10 años de CV · casi todos hombres", 540, 1260, 38, W, 1, face=C.FONT_SEMI)
    sub(p, "…con los currículums de diez años.")


def C4(p):
    doc(p, 540, 820, 1.4)
    p.rect(330, 860, 750, 930, RED, 0.25, radius=10)
    p.text("«capitana del club de ajedrez femenino»", 540, 1150, 32, W, 1, face=C.FONT_SEMI)
    p.text("−", 820, 920, 120, RED, 1, face=C.FONT_BLACK)
    sub(p, "Aprendió a castigar «femenino».")


def C5(p):
    p.text("La IA no inventó el sesgo.", 540, 780, 54, W, 1, face=C.FONT_BLACK)
    p.text("Lo copió.", 540, 880, 90, W, 1, face=C.FONT_BLACK)
    sub(p, "Entonces… ¿quién leyó tu CV?")


OPTS = {"A": [A1, A2, A3, A4, A5], "B": [B1, B2, B3, B4, B5], "C": [C1, C2, C3, C4, C5]}


def main():
    w, h = 324, 576
    for name, frames in OPTS.items():
        sheet = Image.new("RGB", (w * 5 + 40, h + 70), (0, 0, 0))
        for j, fn in enumerate(frames):
            arr, surf = frame_surface(); p = P(surf.getCanvas())
            bg(p); fn(p); vignette(p, 0.3)
            im = Image.fromarray(arr[..., :3].copy()).resize((w, h), Image.LANCZOS)
            sheet.paste(im, (20 + j * w, 50))
        ImageDraw.Draw(sheet).text((24, 14), f"Opcion {name}", fill=(255, 255, 255))
        sheet.save(HERE / f"storyboard_{name}.png")
    print("ok")


if __name__ == "__main__":
    main()
