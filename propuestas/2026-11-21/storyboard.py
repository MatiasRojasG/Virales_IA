"""Storyboards 21-nov-2026: 5 bocetos por idea con el estilo de los reels (reelforge + marca)."""
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
    P.text("21 NOV 2026", 1016, 288, 24, L.FG, 0.7, face=C.FONT_SEMI, align="right", tracking=2)

def sub(P, s):
    L.sub_band(P)
    parts = [(seg, L.RED if i % 2 else L.FG) for i, seg in enumerate(s.split("*")) if seg]
    P.rich(parts, 540, 1410, 52, 1, face=C.FONT_BOLD)

# ---------------------------------------------------------------- objetos
def house(P, x, y, s=1, lit=False, panels=True):
    P.rect(x - 190*s, y - 60*s, x + 190*s, y + 200*s, L.FG, 1, stroke=6)
    pth = skia.Path(); pth.moveTo(x - 230*s, y - 50*s); pth.lineTo(x, y - 230*s); pth.lineTo(x + 230*s, y - 50*s)
    P.c.drawPath(pth, paint(L.FG, 1, stroke=6))
    if panels:
        for k in range(3):
            px = x + 20*s + k*60*s; py = y - 95*s - k*42*s
            P.rect(px - 26*s, py - 18*s, px + 26*s, py + 18*s, L.GRAY, 1)
            P.line(px, py - 18*s, px, py + 18*s, L.BG, 1, w=2)
    P.rect(x - 140*s, y + 10*s, x - 40*s, y + 100*s, L.CARD if not lit else L.FG, 1, radius=6)
    P.rect(x - 140*s, y + 10*s, x - 40*s, y + 100*s, L.FG, 1, stroke=4, radius=6)
    P.rect(x + 50*s, y + 60*s, x + 130*s, y + 200*s, L.FG, 1, stroke=5)
    bulb(P, x - 90*s, y + 55*s, 0.55*s, lit)

def bulb(P, x, y, s, lit):
    if lit: P.circle(x, y, 70*s, L.FG, 0.25, blur=30)
    P.circle(x, y, 26*s, L.FG if lit else L.DIM, 1)
    P.rect(x - 12*s, y + 22*s, x + 12*s, y + 42*s, L.GRAY, 1)

def pole(P, x, y0, y1):
    P.line(x, y0, x, y1, L.GRAY, 1, w=14)
    P.line(x - 70, y0 + 30, x + 70, y0 + 30, L.GRAY, 1, w=10)

def worker(P, x, y, s=1, a=1):
    P.circle(x, y - 70*s, 26*s, L.FG, a)
    P.rect(x - 32*s, y - 104*s, x + 32*s, y - 86*s, L.FG, a, radius=6)  # casco
    P.line(x, y - 44*s, x, y + 40*s, L.FG, a, w=10*s)
    P.line(x, y - 20*s, x - 40*s, y - 60*s, L.FG, a, w=8*s)
    P.line(x, y - 20*s, x + 40*s, y - 50*s, L.FG, a, w=8*s)
    P.line(x, y + 40*s, x - 30*s, y + 100*s, L.FG, a, w=8*s)
    P.line(x, y + 40*s, x + 30*s, y + 100*s, L.FG, a, w=8*s)

def wave(P, x0, x1, y, amp, cyc, rgb, a=1, w=6, flat_from=None):
    pth = skia.Path(); n = 200
    for k in range(n + 1):
        u = k / n; xx = x0 + (x1 - x0) * u
        v = math.sin(2 * math.pi * cyc * u)
        if flat_from is not None and u > flat_from: v = 0
        (pth.moveTo if k == 0 else pth.lineTo)(xx, y - amp * v)
    P.c.drawPath(pth, paint(rgb, a, stroke=w))

def face(P, x, y, s, variant):
    L.head(P, x, y, s, skin=L.SKIN if variant == 0 else L.hx("#B98C68"), smile=0.6 if variant else 0.3,
           hair=(0.12, 0.1, 0.09) if variant == 0 else (0.25, 0.18, 0.12))

def car(P, x, y, s=1, glow_brake=0.0):
    P.rect(x - 260*s, y - 70*s, x + 260*s, y + 50*s, L.FG, 1, radius=40*s)
    pth = skia.Path(); pth.moveTo(x - 150*s, y - 70*s); pth.lineTo(x - 90*s, y - 150*s); pth.lineTo(x + 110*s, y - 150*s); pth.lineTo(x + 180*s, y - 70*s)
    P.c.drawPath(pth, paint(L.FG, 1))
    P.rect(x - 80*s, y - 135*s, x + 100*s, y - 80*s, L.BG, 0.9, radius=8)
    for wx in (-160, 160):
        P.circle(x + wx*s, y + 50*s, 62*s, L.BG, 1); P.circle(x + wx*s, y + 50*s, 62*s, L.FG, 1, stroke=10*s)
        P.circle(x + wx*s, y + 50*s, 24*s, L.GRAY, 1)
        if glow_brake: P.circle(x + wx*s, y + 50*s, 50*s, L.RED, 0.6 * glow_brake, blur=22)

def motor(P, x, y, r, label, rot=0.0, rgb=None):
    rgb = rgb or L.FG
    P.circle(x, y, r, L.CARD, 1); P.circle(x, y, r, rgb, 1, stroke=8)
    for k in range(6):
        a = rot + k * math.pi / 3
        P.line(x, y, x + math.cos(a) * r * 0.75, y + math.sin(a) * r * 0.75, rgb, 1, w=8)
    P.text(label, x, y + r + 60, 40, L.GRAY, 1, face=C.FONT_BOLD)

def battery(P, x, y, w, h, f, rgb=None):
    P.rect(x - w/2, y - h/2, x + w/2, y + h/2, L.FG, 1, stroke=6, radius=14)
    P.rect(x - 24, y - h/2 - 18, x + 24, y - h/2, L.FG, 1, radius=4)
    P.rect(x - w/2 + 12, y + h/2 - 12 - (h - 24) * f, x + w/2 - 12, y + h/2 - 12, rgb or L.FG, 1, radius=6)

# ---------------------------------------------------------------- escenas
def A1(P):
    L.sun(P, 830, 560, 60); house(P, 470, 900, 1.2); P.text("?", 470, 1240, 120, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "Hay sol… y se cortó la luz")
def A2(P):
    house(P, 250, 900, 0.7); pole(P, 760, 560, 1250); P.line(390, 780, 690, 590, L.FG, 1, w=5)
    P.line(830, 590, 1000, 650, L.FG, 1, w=5); worker(P, 760, 760, 0.9)
    P.text("SIN LUZ", 880, 1050, 44, L.GRAY, 1, face=C.FONT_BLACK)
    sub(P, "Alguien repara el cable")
def A3(P):
    house(P, 250, 900, 0.7); pole(P, 760, 560, 1250); worker(P, 760, 760, 0.9)
    P.line(390, 780, 690, 590, L.RED, 1, w=10); P.circle(540, 690, 60, L.RED, 0.35, blur=30)
    P.text("¡PELIGRO!", 540, 1180, 64, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "Tus paneles podrían *electrocutarlo*")
def A4(P):
    P.rect(390, 560, 690, 860, L.FG, 1, stroke=6, radius=24); P.text("INVERSOR", 540, 720, 40, L.FG, 1, face=C.FONT_BLACK)
    wave(P, 120, 960, 1000, 70, 5, L.FG, flat_from=0.6); P.text("50 Hz", 250, 1120, 44, L.GRAY, 1, face=C.FONT_BOLD)
    P.text("< 2 s", 800, 1160, 96, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "Si la red calla, se *desconecta*")
def A5(P):
    L.sun(P, 830, 560, 50); house(P, 430, 880, 1.0, lit=True); battery(P, 820, 1040, 120, 200, 0.7)
    P.line(640, 1040, 760, 1040, L.FG, 1, w=6); P.text("BATERÍA", 820, 1200, 36, L.GRAY, 1, face=C.FONT_BOLD)
    sub(P, "Con batería, tu casa es una *isla*")

def B1(P):
    face(P, 300, 830, 0.95, 0); face(P, 780, 830, 0.95, 1)
    P.text("¿Cuál es real?", 540, 1210, 70, L.FG, 1, face=C.FONT_BLACK)
    sub(P, "Una es real. La otra, IA")
def B2(P):
    for i in range(8):
        for j in range(4):
            x = 190 + i * 100; y = 620 + j * 120; v = (i * 3 + j * 5) % 7
            P.rect(x - 40, y - 50, x + 40, y + 50, L.CARD, 1, radius=12); P.circle(x, y - 8, 22, L.SKIN, 1)
            P.text("IA" if v < 3 else "REAL", x, y + 38, 18, L.RED if v < 3 else L.GRAY, 1, face=C.FONT_BOLD)
    P.text("315 personas · 128 caras", 540, 1180, 48, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Un experimento con *315* personas")
def B3(P):
    for k, (lab, v, rgb) in enumerate([("Personas", 48.2, L.RED), ("Moneda", 50.0, L.GRAY)]):
        x = 360 + k * 360
        P.rect(x - 90, 1150 - v * 10, x + 90, 1150, rgb, 1, radius=10)
        P.text(f"{v:.1f} %".replace(".", ","), x, 1150 - v * 10 - 30, 56, L.FG, 1, face=C.FONT_BLACK)
        P.text(lab, x, 1220, 40, L.GRAY, 1, face=C.FONT_BOLD)
    sub(P, "Igual que *lanzar una moneda*")
def B4(P):
    P.rect(150, 650, 450, 900, L.FG, 1, stroke=6, radius=30); P.text("DIBUJA", 300, 790, 44, L.FG, 1, face=C.FONT_BLACK)
    P.rect(630, 650, 930, 900, L.RED, 1, stroke=6, radius=30); P.text("JUZGA", 780, 790, 44, L.RED, 1, face=C.FONT_BLACK)
    P.arrow(460, 720, 620, 720, L.FG, 1, w=6); P.arrow(620, 840, 460, 840, L.RED, 1, w=6)
    P.text("millones de rondas", 540, 1060, 44, L.GRAY, 1, face=C.FONT_BOLD)
    sub(P, "Dos IAs que *compiten*")
def B5(P):
    face(P, 300, 830, 0.95, 0); face(P, 780, 830, 0.95, 1)
    P.text("+7,7 % confianza", 780, 1200, 50, L.RED, 1, face=C.FONT_BLACK); P.rect(560, 560, 1000, 1110, L.RED, 1, stroke=6, radius=30)
    sub(P, "Y le *creemos más* a la falsa")

def C1(P):
    car(P, 540, 900, 1.2, glow_brake=1.0); P.text("CALOR", 540, 1140, 56, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "Cada frenada se pierde en *calor*")
def C2(P):
    battery(P, 230, 860, 150, 260, 0.7); P.arrow(330, 860, 440, 860, L.FG, 1, w=8)
    motor(P, 560, 860, 110, "MOTOR", 0.3); P.arrow(690, 860, 790, 860, L.FG, 1, w=8)
    P.circle(890, 860, 90, L.FG, 1, stroke=14); sub(P, "La batería mueve el motor")
def C3(P):
    battery(P, 230, 860, 150, 260, 0.7); P.arrow(440, 860, 330, 860, L.RED, 1, w=8)
    motor(P, 560, 860, 110, "GENERADOR", 1.0, L.RED); P.arrow(790, 860, 690, 860, L.RED, 1, w=8)
    P.circle(890, 860, 90, L.FG, 1, stroke=14); sub(P, "Al frenar, la rueda lo *gira al revés*")
def C4(P):
    battery(P, 540, 860, 220, 380, 0.85, L.RED); P.text("+", 540, 640, 90, L.RED, 1, face=C.FONT_BLACK)
    P.text("Más en la ciudad", 540, 1170, 56, L.FG, 1, face=C.FONT_BLACK)
    sub(P, "La energía *vuelve a la batería*")
def C5(P):
    car(P, 540, 900, 1.2); P.text("frenos que duran más", 540, 1140, 50, L.GRAY, 1, face=C.FONT_BOLD)
    sub(P, "Frena… y *recarga*")

IDEAS = {"A": ([A1, A2, A3, A4, A5], "ENERGÍA · Paneles solares que se apagan en un corte"),
         "B": ([B1, B2, B3, B4, B5], "IA APLICADA · ¿Cara real o hecha con IA?"),
         "C": ([C1, C2, C3, C4, C5], "AUTOS Y MOVILIDAD · Frenar para recargar")}

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
