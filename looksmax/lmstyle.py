"""Identidad visual de la cuenta de looksmaxing basado en evidencia (distinta de Detrás del Algoritmo).
Fondo negro mate, blancos y grises, acento dorado/ámbar #E8B04B solo para destacar. Tipografía Inter."""
import math
import skia
from reelforge import config as C
from reelforge.draw import color4, paint

def hx(h): return C.hex2rgb(h)

BLACK = hx("#0A0A0B")
BLACK2 = hx("#161618")
CARD = hx("#1E1E21")
LINE = hx("#2C2C30")
WHITE = hx("#F4F4F2")
GRAY = hx("#9A9A9F")
DIM = hx("#55555B")
GOLD = hx("#E8B04B")
RED = hx("#D9534F")      # solo para «mito / error», uso mínimo
SKIN = hx("#C9A27E")
SKIN2 = hx("#A8805E")


def background(p, t=0.0, glow=0.0):
    c = p.c
    c.clear(color4(BLACK))
    r = 1150 + 40 * math.sin(t * 0.5)
    sh = skia.GradientShader.MakeRadial((C.W * 0.5, C.H * 0.42), r,
                                        [color4(BLACK2, 1.0), color4(BLACK, 0.0)])
    c.drawPaint(skia.Paint(Shader=sh))
    if glow > 0:
        sh2 = skia.GradientShader.MakeRadial((C.W * 0.5, C.H * 0.45), 650,
                                             [color4(GOLD, 0.08 * glow), color4(BLACK, 0.0)])
        c.drawPaint(skia.Paint(Shader=sh2))
    # grano sutil fijo (mate)
    import random
    rnd = random.Random(int(t * 30) % 7)
    pp = paint(WHITE, 0.025)
    for _ in range(260):
        c.drawCircle(rnd.uniform(0, C.W), rnd.uniform(0, C.H), 1.2, pp)


def vignette(p, s=0.6):
    sh = skia.GradientShader.MakeRadial((C.W / 2, C.H * 0.45), C.H * 0.75,
                                        [color4(BLACK, 0.0), color4(BLACK, 0.0), color4((0, 0, 0), s)], [0, 0.55, 1])
    p.c.drawPaint(skia.Paint(Shader=sh))


def head(p, x, y, s=1.0, skin=SKIN, a=1.0, hair=(0.12, 0.1, 0.09), eyes_closed=False, tired=0.0, wrinkles=0.0, spots=0.0, smile=0.0):
    """Cabeza estilizada genérica (sin rasgos de nadie real)."""
    c = p.c
    # cuello
    p.rect(x - 52 * s, y + 120 * s, x + 52 * s, y + 230 * s, SKIN2, a, radius=20 * s)
    # cara (óvalo)
    r = skia.Rect(x - 150 * s, y - 190 * s, x + 150 * s, y + 200 * s)
    c.drawOval(r, paint(skin, a))
    # orejas
    c.drawOval(skia.Rect(x - 178 * s, y - 30 * s, x - 132 * s, y + 60 * s), paint(SKIN2, a))
    c.drawOval(skia.Rect(x + 132 * s, y - 30 * s, x + 178 * s, y + 60 * s), paint(SKIN2, a))
    # pelo
    path = skia.Path()
    path.moveTo(x - 155 * s, y - 40 * s)
    path.cubicTo(x - 170 * s, y - 230 * s, x + 170 * s, y - 250 * s, x + 155 * s, y - 40 * s)
    path.cubicTo(x + 120 * s, y - 140 * s, x - 60 * s, y - 150 * s, x - 155 * s, y - 40 * s)
    c.drawPath(path, paint(hair, a))
    # ojos
    for dx in (-60, 60):
        ex, ey = x + dx * s, y - 10 * s
        if tired > 0:
            c.drawOval(skia.Rect(ex - 40 * s, ey + 8 * s, ex + 40 * s, ey + 42 * s), paint(hx("#6E5368"), 0.55 * tired * a))
        if eyes_closed:
            p.line(ex - 26 * s, ey, ex + 26 * s, ey, hx("#2a2018"), a, w=6 * s)
        else:
            c.drawOval(skia.Rect(ex - 26 * s, ey - 13 * s, ex + 26 * s, ey + 13 * s), paint(WHITE, a))
            p.circle(ex, ey, 10 * s, hx("#2a2018"), a)
            # párpado caído
            if tired > 0:
                p.rect(ex - 28 * s, ey - 16 * s, ex + 28 * s, ey - 16 * s + 14 * s * tired, skin, a)
        # ceja
        p.line(ex - 32 * s, ey - 42 * s, ex + 30 * s, ey - 46 * s + (8 * s * tired if dx < 0 else 8 * s * tired), hair, a, w=9 * s)
    # nariz y boca
    p.line(x, y + 10 * s, x - 12 * s, y + 62 * s, SKIN2, a, w=6 * s)
    path = skia.Path(); path.moveTo(x - 48 * s, y + 112 * s)
    path.quadTo(x, y + (112 + 22 * smile - 10 * tired) * s, x + 48 * s, y + 112 * s)
    c.drawPath(path, paint(hx("#7a4a3a"), a, stroke=7 * s))
    # arrugas / manchas (foto-envejecimiento ilustrativo)
    if wrinkles > 0:
        for k in range(3):
            p.line(x - 70 * s, y - (110 + k * 18) * s, x + 70 * s, y - (110 + k * 18) * s, SKIN2, wrinkles * a, w=4 * s)
        for sx in (-1, 1):
            for k in range(3):
                p.line(x + sx * 100 * s, y - (20 - k * 14) * s, x + sx * 125 * s, y - (28 - k * 22) * s, SKIN2, wrinkles * a, w=4 * s)
    if spots > 0:
        import random
        rnd = random.Random(3)
        for _ in range(14):
            p.circle(x + rnd.uniform(-110, 110) * s, y + rnd.uniform(-120, 90) * s, rnd.uniform(6, 13) * s, hx("#8C6446"), spots * 0.7 * a)


def sun(p, x, y, r, a=1.0, t=0.0):
    p.circle(x, y, r * 1.9, GOLD, 0.10 * a, blur=r * 0.6)
    for k in range(12):
        ang = k * math.pi / 6 + t * 0.4
        p.line(x + math.cos(ang) * r * 1.25, y + math.sin(ang) * r * 1.25,
               x + math.cos(ang) * r * 1.6, y + math.sin(ang) * r * 1.6, GOLD, a, w=r * 0.12)
    p.circle(x, y, r, GOLD, a)


def moon(p, x, y, r, a=1.0):
    p.circle(x, y, r, WHITE, a)
    p.circle(x + r * 0.45, y - r * 0.25, r * 0.9, BLACK, a)


def bottle(p, x, y, s=1.0, a=1.0, label="FPS 50"):
    p.rect(x - 70 * s, y - 150 * s, x + 70 * s, y + 170 * s, WHITE, a, radius=34 * s)
    p.rect(x - 34 * s, y - 210 * s, x + 34 * s, y - 145 * s, GRAY, a, radius=10 * s)
    p.rect(x - 70 * s, y - 20 * s, x + 70 * s, y + 70 * s, GOLD, a)
    p.text(label, x, y + 40 * s, 34 * s, BLACK, a, face=C.FONT_BLACK)
