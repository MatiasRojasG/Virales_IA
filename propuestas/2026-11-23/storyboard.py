"""Storyboards 23-nov-2026: 5 bocetos por idea con el estilo de los reels (reelforge + marca)."""
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
    P.text("23 NOV 2026", 1016, 288, 24, L.FG, 0.7, face=C.FONT_SEMI, align="right", tracking=2)

def sub(P, s):
    L.sub_band(P)
    parts = [(seg, L.RED if i % 2 else L.FG) for i, seg in enumerate(s.split("*")) if seg]
    P.rich(parts, 540, 1410, 52, 1, face=C.FONT_BOLD)


# ---------------------------------------------------------------- objetos
def eye(P, x, y, s=1.0, open_=1.0, ir=False):
    w, h = 170*s, 90*s*max(open_, 0.04)
    pth = skia.Path(); pth.moveTo(x - w, y); pth.quadTo(x, y - 2*h, x + w, y); pth.quadTo(x, y + 2*h, x - w, y); pth.close()
    P.c.drawPath(pth, paint(L.FG, 1, stroke=7*s))
    if open_ > 0.15:
        P.circle(x, y, min(62*s, 1.6*h), L.RED if ir else L.GRAY, 1); P.circle(x, y, min(26*s, 0.7*h), L.BG, 1)
    P.line(x - w, y - 1.05*h - 4, x + w, y - 1.05*h - 4, L.FG, 0.0)

def car(P, x, y, s=1.0):
    P.rect(x - 300*s, y - 40*s, x + 300*s, y + 70*s, L.FG, 1, stroke=8, radius=40*s)
    pth = skia.Path(); pth.moveTo(x - 190*s, y - 40*s); pth.lineTo(x - 110*s, y - 140*s); pth.lineTo(x + 120*s, y - 140*s); pth.lineTo(x + 210*s, y - 40*s)
    P.c.drawPath(pth, paint(L.FG, 1, stroke=8))
    for dx in (-180, 180): P.circle(x + dx*s, y + 75*s, 55*s, L.BG, 1); P.circle(x + dx*s, y + 75*s, 55*s, L.FG, 1, stroke=8)

def gripper(P, x, y, gap, s=1.0, sensor=False):
    P.rect(x - 30*s, y - 330*s, x + 30*s, y - 170*s, L.GRAY, 1, radius=10)
    P.rect(x - gap - 60*s, y - 190*s, x + gap + 60*s, y - 150*s, L.GRAY, 1, radius=12)
    for sg in (-1, 1):
        fx = x + sg*(gap + 30*s)
        P.rect(fx - 30*s, y - 150*s, fx + 30*s, y + 60*s, L.FG, 1, radius=14)
        if sensor: P.rect(fx - 30*s if sg > 0 else fx + 8*s, y - 60*s, fx - 8*s if sg > 0 else fx + 30*s, y + 50*s, L.RED, 1, radius=8)

def egg(P, x, y, s=1.0, crack=False):
    P.c.drawOval(skia.Rect.MakeLTRB(x - 85*s, y - 115*s, x + 85*s, y + 105*s), paint(L.FG, 1))
    if crack:
        pts = [(x - 60*s, y - 30*s), (x - 25*s, y + 5*s), (x + 5*s, y - 25*s), (x + 40*s, y + 10*s), (x + 70*s, y - 10*s)]
        for a, b in zip(pts, pts[1:]): P.line(*a, *b, L.RED, 1, w=6)

def phone(P, x, y, s=1):
    P.rect(x - 150*s, y - 290*s, x + 150*s, y + 290*s, L.FG, 1, stroke=8, radius=40*s)
    P.rect(x - 128*s, y - 262*s, x + 128*s, y + 262*s, L.CARD, 1, radius=26*s)

def bubble(P, x0, y0, x1, y1, txt, size=34, rgb=None, me=False):
    P.rect(x0, y0, x1, y1, L.FG if me else L.LINE, 1, radius=22)
    P.text(txt, (x0 + x1)/2, (y0 + y1)/2 + size*0.36, size, rgb or (L.BG if me else L.FG), 1, face=C.FONT_BOLD)

def lock(P, x, y, s=1.0, rgb=None):
    rgb = rgb or L.FG
    P.c.drawArc(skia.Rect.MakeLTRB(x - 70*s, y - 150*s, x + 70*s, y - 10*s), 180, 180, False, paint(rgb, 1, stroke=18*s))
    P.line(x - 70*s, y - 80*s, x - 70*s, y - 10*s, rgb, 1, w=18*s); P.line(x + 70*s, y - 80*s, x + 70*s, y - 10*s, rgb, 1, w=18*s)
    P.rect(x - 110*s, y - 20*s, x + 110*s, y + 140*s, rgb, 1, radius=20*s)

# ---------------------------------------------------------------- A · auto
def A1(P):
    for k in range(2): P.line(540, 1300 - k*150, 540, 1240 - k*150, L.DIM, 1, w=10)
    car(P, 540, 1060, 0.9); eye(P, 540, 700, 1.0, open_=0.25)
    P.text("?", 800, 720, 130, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "¿Y si te *duermes manejando*?")
def A2(P):
    P.circle(300, 900, 70, L.CARD, 1); P.circle(300, 900, 70, L.FG, 1, stroke=7); P.circle(300, 900, 26, L.RED, 1)
    for k in range(7):
        P.line(380, 900, 820, 700 + k*65, L.RED, 0.55, w=3)
    eye(P, 800, 900, 0.8, open_=1.0, ir=True)
    P.text("luz infrarroja", 540, 1180, 50, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Una cámara que *ve en la oscuridad*")
def A3(P):
    eye(P, 540, 820, 1.2, open_=0.18)
    P.rect(240, 1040, 840, 1080, L.CARD, 1, radius=20); P.rect(240, 1040, 240 + 600*0.82, 1080, L.RED, 1, radius=20)
    P.text("82 % cerrado", 540, 1170, 56, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "Mide *cuánto se cierran* tus párpados")
def A4(P):
    P.text("1 minuto", 540, 720, 44, L.GRAY, 1, face=C.FONT_BOLD)
    for i in range(30):
        x = 160 + i*25; closed = i in (6, 7, 13, 14, 15, 21, 22, 23, 24)
        P.rect(x, 800 if not closed else 760, x + 18, 1000, L.RED if closed else L.DIM, 1, radius=6)
    P.text("ojos cerrados: 30 %", 540, 1120, 56, L.FG, 1, face=C.FONT_BLACK)
    sub(P, "No un parpadeo: *el tiempo cerrado*")
def A5(P):
    car(P, 540, 1060, 0.9)
    P.circle(540, 680, 110, L.RED, 0.18); P.circle(540, 680, 110, L.RED, 1, stroke=10)
    P.text("!", 540, 728, 140, L.RED, 1, face=C.FONT_BLACK)
    P.text("¡descansa!", 540, 870, 50, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Te avisa *antes* del accidente")

# ---------------------------------------------------------------- B · robot y huevo
def B1(P):
    gripper(P, 540, 900, 70); egg(P, 540, 950, 1.0, crack=True)
    P.text("?", 840, 760, 130, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "¿Cómo no *aplastar un huevo*?")
def B2(P):
    P.rect(380, 640, 700, 1200, L.SKIN, 1, radius=160)
    for i in range(40):
        P.circle(430 + (i % 8)*31, 720 + (i // 8)*60, 8, L.RED, 1)
    P.text("miles de sensores", 540, 1290, 46, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Tu dedo *siente* la presión")
def B3(P):
    P.rect(260, 700, 820, 860, L.GRAY, 0.35, radius=40); P.rect(260, 700, 820, 860, L.FG, 1, stroke=6, radius=40)
    pth = skia.Path(); pth.moveTo(260, 860); pth.lineTo(470, 860); pth.quadTo(540, 790, 610, 860); pth.lineTo(820, 860)
    P.c.drawPath(pth, paint(L.RED, 1, stroke=8)); P.circle(540, 905, 40, L.FG, 1)
    P.rect(480, 560, 600, 640, L.FG, 1, radius=12); P.circle(540, 600, 26, L.RED, 1)
    P.arrow(540, 650, 540, 760, L.RED, 0.8, w=4)
    P.text("gel blando + cámara", 540, 1080, 50, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Una *yema de gel* con una cámara")
def B4(P):
    P.line(200, 1150, 900, 1150, L.GRAY, 1, w=4); P.line(200, 1150, 200, 680, L.GRAY, 1, w=4)
    pts = [(200 + i*14, 1150 - 420*(1 - math.exp(-i/14))) for i in range(50)]
    for a, b in zip(pts, pts[1:]): P.line(*a, *b, L.FG, 1, w=6)
    P.line(200, 800, 900, 800, L.RED, 1, w=4); P.text("hasta aquí", 420, 780, 40, L.RED, 1, face=C.FONT_BOLD)
    P.text("fuerza", 260, 660, 40, L.GRAY, 1, face=C.FONT_BOLD, align="left")
    sub(P, "Aprieta… y *se detiene a tiempo*")
def B5(P):
    gripper(P, 540, 900, 85, sensor=True); egg(P, 540, 950, 1.0)
    P.text("✓", 840, 780, 110, L.FG, 1, face=C.FONT_BLACK)
    sub(P, "Firme, pero *sin romperlo*")

# ---------------------------------------------------------------- C · código de WhatsApp
def C1(P):
    phone(P, 540, 900, 1.15)
    bubble(P, 400, 700, 690, 790, "Código: 482-913", 34)
    bubble(P, 380, 840, 690, 990, "", 30); P.text("me llegó tu código", 535, 905, 30, L.FG, 1, face=C.FONT_BOLD); P.text("¿me lo reenvías?", 535, 955, 30, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Un código que *no pediste*")
def C2(P):
    P.text("482-913", 540, 820, 150, L.RED, 1, face=C.FONT_BLACK)
    P.text("= la llave de tu número", 540, 960, 52, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Ese código *abre tu cuenta*")
def C3(P):
    phone(P, 300, 900, 0.8); phone(P, 780, 900, 0.8)
    P.arrow(440, 900, 640, 900, L.RED, 1, w=10)
    P.text("tú", 300, 1180, 44, L.GRAY, 1, face=C.FONT_BOLD); P.text("otra persona", 780, 1180, 44, L.RED, 1, face=C.FONT_BOLD)
    P.text("✗", 300, 930, 120, L.RED, 1, face=C.FONT_BLACK)
    sub(P, "Tu WhatsApp *pasa a otro teléfono*")
def C4(P):
    lock(P, 540, 900, 1.4)
    P.text("verificación en dos pasos", 540, 1180, 48, L.FG, 1, face=C.FONT_BOLD)
    sub(P, "Un *segundo candado*")
def C5(P):
    phone(P, 540, 900, 1.15); bubble(P, 400, 760, 690, 850, "Código: 482-913", 34)
    P.circle(540, 900, 330, L.RED, 1, stroke=10); P.line(310, 1130, 770, 670, L.RED, 1, w=10)
    sub(P, "El código *no se comparte*")

IDEAS = {"A": ([A1, A2, A3, A4, A5], "AUTOS Y MOVILIDAD · ¿Cómo sabe tu auto que te estás durmiendo?"),
         "B": ([B1, B2, B3, B4, B5], "ROBÓTICA · ¿Cómo toma un robot un huevo sin romperlo?"),
         "C": ([C1, C2, C3, C4, C5], "CIBERSEGURIDAD · El código de WhatsApp que no pediste")}

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
