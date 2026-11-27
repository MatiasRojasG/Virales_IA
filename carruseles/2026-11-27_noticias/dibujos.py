"""Ilustraciones dibujadas por código para el carrusel del 27-nov-2026.

Wikimedia Commons no es accesible desde la sesión (proxy 403): cada lámina lleva un dibujo propio en blanco
y negro, sin logos ni marcas de terceros.

    python carruseles/2026-11-27_noticias/dibujos.py
"""
import math
from pathlib import Path
import numpy as np
import skia
from PIL import Image

HERE = Path(__file__).resolve().parent
W, H = 1600, 1000
FG = skia.Color4f(0.95, 0.95, 0.95, 1)
GR = skia.Color4f(0.55, 0.55, 0.55, 1)
DK = skia.Color4f(0.22, 0.22, 0.22, 1)
BOLD = skia.Typeface("DejaVu Sans", skia.FontStyle.Bold())


def pnt(c, stroke=0, a=1.0):
    p = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(c.fR, c.fG, c.fB, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def lienzo():
    arr = np.zeros((H, W, 4), np.uint8); s = skia.Surface(arr); c = s.getCanvas()
    sh = skia.GradientShader.MakeRadial((W * 0.5, H * 0.45), 900,
                                        [skia.Color4f(0.17, 0.17, 0.17, 1), skia.Color4f(0.03, 0.03, 0.03, 1)])
    c.drawPaint(skia.Paint(Shader=sh))
    for x in range(0, W, 80): c.drawLine(x, 0, x, H, pnt(GR, 1, 0.08))
    for y in range(0, H, 80): c.drawLine(0, y, W, y, pnt(GR, 1, 0.08))
    return arr, c


def guardar(arr, nombre):
    """Reduce el dibujo y lo baja para que la cabecera de marca (logo y fecha) no lo tape."""
    im = Image.fromarray(arr[..., :3].copy())
    from PIL import ImageFilter
    bg = Image.new("RGB", im.size, (8, 8, 8))
    sm = im.resize((round(W * 0.8), round(H * 0.8)), Image.LANCZOS)
    m = Image.new("L", sm.size, 0); m.paste(255, (60, 60, sm.width - 60, sm.height))
    m = m.filter(ImageFilter.GaussianBlur(40))
    bg.paste(sm, ((W - sm.width) // 2, H - sm.height), m)
    bg.save(HERE / "img" / nombre, quality=95)


def candado(c, cx, cy, s=1.0, abierto=True):
    body = skia.RRect.MakeRectXY(skia.Rect(cx - 140 * s, cy - 40 * s, cx + 140 * s, cy + 180 * s), 30 * s, 30 * s)
    c.drawRRect(body, pnt(FG))
    arco = skia.Path(); arco.moveTo(cx - 90 * s, cy - 40 * s); arco.lineTo(cx - 90 * s, cy - 120 * s)
    arco.arcTo(skia.Rect(cx - 90 * s, cy - 210 * s, cx + 90 * s, cy - 30 * s), 180, 180, False)
    arco.lineTo(cx + 90 * s, cy - (150 if abierto else 40) * s)
    if abierto:
        m = skia.Matrix(); m.setRotate(-28, cx + 90 * s, cy - 40 * s); arco.transform(m)
    c.drawPath(arco, pnt(FG, 30 * s))
    c.drawCircle(cx, cy + 50 * s, 26 * s, pnt(DK)); c.drawRect(skia.Rect(cx - 10 * s, cy + 60 * s, cx + 10 * s, cy + 130 * s), pnt(DK))


def balon(c, cx, cy, r):
    c.drawCircle(cx, cy, r, pnt(FG))
    pent = lambda x, y, rr, rot: [(x + rr * math.cos(rot + k * 2 * math.pi / 5), y + rr * math.sin(rot + k * 2 * math.pi / 5)) for k in range(5)]
    pts = pent(cx, cy, r * 0.3, -math.pi / 2)
    p = skia.Path(); p.moveTo(*pts[0]); [p.lineTo(*q) for q in pts[1:]]; p.close(); c.drawPath(p, pnt(DK))
    for k in range(5):
        a = -math.pi / 2 + k * 2 * math.pi / 5
        x0, y0 = pts[k]; x1, y1 = cx + r * 0.78 * math.cos(a), cy + r * 0.78 * math.sin(a)
        c.drawLine(x0, y0, x1, y1, pnt(DK, 8))
        q = pent(x1 + r * 0.12 * math.cos(a), y1 + r * 0.12 * math.sin(a), r * 0.2, a)
        pp = skia.Path(); pp.moveTo(*q[0]); [pp.lineTo(*z) for z in q[1:]]; pp.close()
        c.save(); c.clipPath(skia.Path().addCircle(cx, cy, r)); c.drawPath(pp, pnt(DK)); c.restore()


def fifa():
    """Balón de fútbol junto a carpetas de documentos que se escapan y un candado abierto."""
    arr, c = lienzo()
    balon(c, 470, 520, 260)
    for k in range(5):
        x, y = 950 + k * 95, 300 + k * 70
        c.save(); c.rotate(-8 + k * 5, x, y)
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, y, x + 230, y + 170), 14, 14), pnt(GR if k % 2 else FG))
        c.drawRect(skia.Rect(x, y - 22, x + 90, y + 6), pnt(GR if k % 2 else FG))
        for j in range(3): c.drawLine(x + 30, y + 50 + j * 35, x + 200, y + 50 + j * 35, pnt(DK, 8))
        c.restore()
    candado(c, 1200, 180, 0.45)
    guardar(arr, "fifa.jpg")


def cripto():
    """Una gran moneda se parte en muchas pequeñas que pasan por un 'puente' y se dispersan."""
    arr, c = lienzo()
    f = skia.Font(BOLD, 150)
    c.drawCircle(300, 500, 210, pnt(FG)); c.drawCircle(300, 500, 170, pnt(DK, 10))
    c.drawString("$", 300 - f.measureText("$") / 2, 555, f, pnt(DK))
    # puente
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(650, 380, 950, 620), 40, 40), pnt(GR, 10))
    for k in range(4): c.drawLine(690 + k * 75, 400, 690 + k * 75, 600, pnt(GR, 6, 0.6))
    rng = np.random.default_rng(5)
    for k in range(14):
        t = k / 13
        x = 540 + t * 120; y = 500 + rng.uniform(-60, 60)
        c.drawCircle(x, y, 18, pnt(FG, 0, 0.8))
    for k in range(26):
        ang = rng.uniform(-0.9, 0.9); d = rng.uniform(120, 560)
        x = 980 + d * math.cos(ang); y = 500 + d * math.sin(ang)
        rr = rng.uniform(14, 30)
        c.drawCircle(x, y, rr, pnt(FG if k % 3 else GR, 0, 0.9))
        c.drawLine(960, 500, x, y, pnt(GR, 2, 0.25))
    guardar(arr, "cripto.jpg")


def cohete():
    """Cohete pequeño despegando con una columna de humo y un satélite en órbita."""
    arr, c = lienzo()
    rng = np.random.default_rng(2)
    for _ in range(80): c.drawCircle(rng.uniform(0, W), rng.uniform(0, 600), rng.uniform(1, 3), pnt(FG, 0, rng.uniform(0.2, 0.7)))
    c.drawOval(skia.Rect(700, 80, 1500, 380), pnt(GR, 4, 0.6))
    sx, sy = 1380, 160
    c.drawRect(skia.Rect(sx - 30, sy - 30, sx + 30, sy + 30), pnt(FG))
    c.drawRect(skia.Rect(sx - 130, sy - 18, sx - 40, sy + 18), pnt(GR)); c.drawRect(skia.Rect(sx + 40, sy - 18, sx + 130, sy + 18), pnt(GR))
    cx, top, bot = 560, 260, 720
    for k in range(10):
        c.drawCircle(cx + rng.uniform(-70, 70), bot + 120 + k * 22, 60 + k * 9, pnt(GR, 0, 0.18))
    nose = skia.Path(); nose.moveTo(cx - 38, top + 90); nose.quadTo(cx, top - 40, cx + 38, top + 90); nose.close()
    c.drawPath(nose, pnt(FG))
    c.drawRect(skia.Rect(cx - 38, top + 90, cx + 38, bot), pnt(FG))
    c.drawRect(skia.Rect(cx - 38, top + 300, cx + 38, top + 316), pnt(DK))
    fl = skia.Path(); fl.moveTo(cx - 30, bot); fl.quadTo(cx - 14, bot + 120, cx, bot + 170); fl.quadTo(cx + 14, bot + 120, cx + 30, bot); fl.close()
    c.drawPath(fl, pnt(FG, 0, 0.9))
    c.drawRect(skia.Rect(0, 930, W, H), pnt(DK))
    guardar(arr, "cohete.jpg")


def frontera():
    """Línea de frontera punteada, playa con restos y la trayectoria de un cohete que cruza el cielo."""
    arr, c = lienzo()
    for k in range(5):
        y = 800 + k * 36
        pth = skia.Path(); pth.moveTo(0, y)
        for x in range(0, W + 40, 40): pth.lineTo(x, y + 8 * math.sin(x / 60 + k))
        c.drawPath(pth, pnt(GR, 4, 0.7 - 0.1 * k))
    c.drawRect(skia.Rect(0, 720, W, 790), pnt(DK))
    for x, w in ((300, 50), (520, 30), (980, 60), (1250, 36)):
        c.drawRect(skia.Rect(x, 742, x + w, 760), pnt(GR))
    for y in range(40, 790, 46): c.drawLine(800, y, 800, y + 22, pnt(FG, 6))
    arc = skia.Path(); arc.moveTo(1450, 720); arc.cubicTo(1300, 300, 800, 120, 150, 140)
    c.drawPath(arc, pnt(FG, 7, 0.9))
    c.save(); c.translate(150, 140); c.rotate(185)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-20, -60, 20, 60), 16, 16), pnt(FG)); c.restore()
    guardar(arr, "frontera.jpg")


def servidores():
    """Racks de servidores con luces, conectados a pequeñas empresas (casitas)."""
    arr, c = lienzo()
    for k in range(4):
        x = 180 + k * 190
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, 180, x + 150, 820), 12, 12), pnt(DK))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x, 180, x + 150, 820), 12, 12), pnt(FG, 5))
        for j in range(10):
            y = 215 + j * 60
            c.drawRect(skia.Rect(x + 18, y, x + 132, y + 36), pnt(GR, 0, 0.5))
            c.drawCircle(x + 112, y + 18, 7, pnt(FG, 0, 0.95 if (j + k) % 3 else 0.3))
    for k, y in enumerate((260, 500, 740)):
        hx = 1330
        c.drawLine(950, 500, hx - 90, y, pnt(GR, 4, 0.7))
        roof = skia.Path(); roof.moveTo(hx - 95, y); roof.lineTo(hx, y - 85); roof.lineTo(hx + 95, y); roof.close()
        c.drawPath(roof, pnt(FG))
        c.drawRect(skia.Rect(hx - 75, y, hx + 75, y + 90), pnt(FG))
        c.drawRect(skia.Rect(hx - 20, y + 30, hx + 20, y + 90), pnt(DK))
    guardar(arr, "servidores.jpg")


def memoria():
    """Chip de memoria apilado (capas) con muchísimas patitas de datos."""
    arr, c = lienzo()
    cx, cy = 800, 520
    for k in range(8):
        y = cy + 120 - k * 42
        pth = skia.Path(); pth.moveTo(cx - 330, y); pth.lineTo(cx, y + 110); pth.lineTo(cx + 330, y); pth.lineTo(cx, y - 110); pth.close()
        c.drawPath(pth, pnt(DK if k % 2 else GR))
        c.drawPath(pth, pnt(FG, 4))
    for j in range(40):
        t = j / 39
        x0 = cx - 330 + t * 330; y0 = cy + 120 + t * 110
        c.drawLine(x0, y0, x0, y0 + 70, pnt(FG, 4, 0.85))
        x1 = cx + t * 330; y1 = cy + 230 - t * 110
        c.drawLine(x1, y1, x1, y1 + 70, pnt(FG, 4, 0.85))
    guardar(arr, "memoria.jpg")


def portadas():
    for n in ("fifa", "cripto", "cohete", "memoria"):
        im = Image.open(HERE / "img" / f"{n}.jpg")
        bg = Image.new("RGB", im.size, im.getpixel((5, 5)))
        sm = im.resize((round(im.width * 0.72), round(im.height * 0.72)), Image.LANCZOS)
        bg.paste(sm, ((im.width - sm.width) // 2, im.height - sm.height))
        bg.save(HERE / "img" / f"{n}_p.jpg", quality=95)


if __name__ == "__main__":
    (HERE / "img").mkdir(exist_ok=True)
    fifa(); cripto(); cohete(); frontera(); servidores(); memoria(); portadas()
    print("ok")
