"""Storyboards (5 fotogramas clave) de las 3 propuestas. Uso: python propuestas/2026-11-17/storyboard.py"""
import math, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from reelforge import config as C
from reelforge.draw import P, frame_surface
from reelforge import marca as L
from PIL import Image, ImageDraw, ImageFont


def sub(p, words, hi=None):
    parts = []
    for w in words.split(" "):
        parts.append((w + " ", L.GOLD if hi and w.strip("¿?.,…!") in hi else L.WHITE))
    p.rich(parts, 540, 1410, 60, face=C.FONT_XBOLD)


def split(p, ltxt, rtxt):
    p.line(540, 560, 540, 1220, L.LINE, 1, w=3)
    p.text(ltxt, 300, 1280, 38, L.GRAY, face=C.FONT_BOLD)
    p.text(rtxt, 780, 1280, 38, L.GOLD, face=C.FONT_BOLD)

# ---------------- A · protector solar
def A1(p):
    L.head(p, 540, 860, 1.25, wrinkles=0.9, spots=0.8)
    p.text("?", 840, 640, 160, L.GOLD, face=C.FONT_BLACK)
    sub(p, "¿Qué te envejece más rápido?", ["envejece"])
def A2(p):
    L.sun(p, 540, 820, 150, t=0.3)
    p.text("UV", 540, 845, 80, L.BLACK, face=C.FONT_BLACK)
    sub(p, "No es la edad… es el sol", ["sol"])
def A3(p):
    for k in range(5):
        for j in range(4):
            x, y = 250 + j * 190, 620 + k * 125
            p.circle(x, y, 38, L.GOLD if (k + j) % 2 else L.GRAY, 1)
    p.text("903 personas · 4,5 años", 540, 1270, 44, L.WHITE, face=C.FONT_BOLD)
    sub(p, "Un estudio siguió a 903 personas", ["903"])
def A4(p):
    split(p, "a veces", "todos los días")
    L.head(p, 300, 860, 0.85, wrinkles=0.8, spots=0.6)
    L.head(p, 780, 860, 0.85, smile=0.6)
    sub(p, "24 % menos envejecimiento", ["24", "%"])
def A5(p):
    L.bottle(p, 540, 840, 1.3)
    p.pill("todos los días", 540, 1170, 40, L.GOLD)
    sub(p, "Entonces… ¿qué te envejece más?", ["Entonces…"])

# ---------------- B · dormir
def B1(p):
    split(p, "dormiste 5 h", "dormiste 8 h")
    L.head(p, 300, 860, 0.85, tired=1.0)
    L.head(p, 780, 860, 0.85, smile=0.5)
    sub(p, "¿Se nota que dormiste mal?", ["mal?"])
def B2(p):
    L.moon(p, 540, 760, 120)
    p.text("31 h despierto", 540, 1080, 64, L.GOLD, face=C.FONT_BLACK)
    sub(p, "Los mantuvieron 31 horas despiertos", ["31"])
def B3(p):
    for k in range(6):
        x = 220 + (k % 3) * 320; y = 700 + (k // 3) * 330
        p.rect(x - 120, y - 140, x + 120, y + 140, L.CARD, 1, radius=24)
        L.head(p, x, y - 10, 0.45, tired=1.0 if k % 2 else 0.0)
    sub(p, "65 personas calificaron las fotos", ["65"])
def B4(p):
    for k, (lab, v) in enumerate([("cansado", 0.85), ("atractivo", 0.35), ("saludable", 0.4)]):
        y = 700 + k * 170
        p.text(lab, 170, y + 14, 42, L.GRAY, face=C.FONT_BOLD, align="left")
        p.rect(460, y - 25, 460 + 450 * v, y + 25, L.GOLD if k == 0 else L.WHITE, 1, radius=25)
    sub(p, "Más cansados y menos atractivos", ["atractivos"])
def B5(p):
    L.moon(p, 400, 760, 90)
    p.text("7–9 h", 650, 790, 110, L.GOLD, face=C.FONT_BLACK)
    sub(p, "Entonces… ¿se nota?", ["Entonces…"])

# ---------------- C · altura
def C1(p):
    for x, h, lab in [(320, 520, "papá"), (760, 420, "¿tú?")]:
        p.rect(x - 80, 1220 - h, x + 80, 1220, L.GOLD if lab == "¿tú?" else L.GRAY, 1, radius=40)
        p.circle(x, 1220 - h - 70, 60, L.GOLD if lab == "¿tú?" else L.GRAY, 1)
        p.text(lab, x, 1290, 44, L.WHITE, face=C.FONT_BOLD)
    sub(p, "¿Vas a ser más alto que tu papá?", ["alto"])
def C2(p):
    for k, t in enumerate(["colgarte de una barra", "estirarte 10 min", "suplementos «crecer»"]):
        y = 720 + k * 160
        p.rect(170, y - 60, 910, y + 60, L.CARD, 1, radius=30)
        p.text(t, 230, y + 14, 42, L.WHITE, face=C.FONT_BOLD, align="left")
        p.text("✗", 860, y + 18, 56, L.RED, face=C.FONT_BLACK)
    sub(p, "¿Estos trucos sirven?", ["trucos"])
def C3(p):
    p.circle(540, 840, 230, L.CARD, 1)
    p.c.drawArc(__import__("skia").Rect(310, 610, 770, 1070), -90, 0.8 * 360, False,
                __import__("reelforge.draw", fromlist=["paint"]).paint(L.GOLD, 1, stroke=46))
    p.text("~80 %", 540, 870, 96, L.GOLD, face=C.FONT_BLACK)
    p.text("genética", 540, 940, 40, L.GRAY, face=C.FONT_BOLD)
    sub(p, "Casi todo lo decide tu ADN", ["ADN"])
def C4(p):
    for k, t in enumerate(["dormir bien", "comer suficiente", "moverte"]):
        y = 720 + k * 160
        p.rect(170, y - 60, 910, y + 60, L.CARD, 1, radius=30)
        p.text(t, 230, y + 14, 46, L.WHITE, face=C.FONT_BOLD, align="left")
        p.text("✓", 860, y + 18, 56, L.GOLD, face=C.FONT_BLACK)
    sub(p, "Lo que sí suma mientras creces", ["sí"])
def C5(p):
    p.line(380, 1220, 380, 640, L.GRAY, 1, w=10)
    p.circle(540, 600, 60, L.WHITE, 1)
    p.rect(470, 680, 610, 1220, L.WHITE, 1, radius=40)
    p.text("+ postura", 800, 760, 46, L.GOLD, face=C.FONT_BOLD)
    sub(p, "Entonces… ¿más alto que tu papá?", ["Entonces…"])


def main():
    opts = {"A": [A1, A2, A3, A4, A5], "B": [B1, B2, B3, B4, B5], "C": [C1, C2, C3, C4, C5]}
    w, h = 324, 576
    fnt = ImageFont.truetype(str(C.FONTS / "Inter-Bold.otf"), 30)
    for name, fns in opts.items():
        sheet = Image.new("RGB", (w * 5 + 60, h + 80), (10, 10, 11))
        for i, fn in enumerate(fns):
            arr, surf = frame_surface(); p = P(surf.getCanvas())
            L.background(p, i * 0.7, glow=0.6); fn(p); L.vignette(p, 0.5)
            im = Image.fromarray(arr[..., :3].copy()).resize((w, h), Image.LANCZOS)
            sheet.paste(im, (10 + i * (w + 10), 70))
        ImageDraw.Draw(sheet).text((20, 18), f"Opción {name}", fill=(232, 176, 75), font=fnt)
        sheet.save(HERE / f"storyboard_{name}.png")
    print("ok")

if __name__ == "__main__":
    main()
