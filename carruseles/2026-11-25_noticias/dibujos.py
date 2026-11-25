"""Ilustraciones dibujadas por código para el carrusel del 25-nov-2026.

Ese día Wikimedia Commons no era accesible desde la sesión (proxy 403), así que en vez de fotos cada lámina
lleva un dibujo propio en blanco y negro (sin logos ni marcas de terceros).

    python carruseles/2026-11-25_noticias/dibujos.py
"""
import math, sys
from pathlib import Path
import numpy as np
import skia
from PIL import Image

HERE = Path(__file__).resolve().parent
W, H = 1600, 1000
FG = skia.Color4f(0.95, 0.95, 0.95, 1)
GR = skia.Color4f(0.55, 0.55, 0.55, 1)
DK = skia.Color4f(0.22, 0.22, 0.22, 1)


def pnt(c, stroke=0, a=1.0, cap=True):
    p = skia.Paint(AntiAlias=True, Color4f=skia.Color4f(c.fR, c.fG, c.fB, a))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        if cap: p.setStrokeCap(skia.Paint.kRound_Cap); p.setStrokeJoin(skia.Paint.kRound_Join)
    return p


def lienzo():
    arr = np.zeros((H, W, 4), np.uint8); s = skia.Surface(arr); c = s.getCanvas()
    sh = skia.GradientShader.MakeRadial((W * 0.5, H * 0.45), 900,
                                        [skia.Color4f(0.17, 0.17, 0.17, 1), skia.Color4f(0.03, 0.03, 0.03, 1)])
    c.drawPaint(skia.Paint(Shader=sh))
    # rejilla tenue
    for x in range(0, W, 80): c.drawLine(x, 0, x, H, pnt(GR, 1, 0.08))
    for y in range(0, H, 80): c.drawLine(0, y, W, y, pnt(GR, 1, 0.08))
    return arr, c


def guardar(arr, nombre):
    Image.fromarray(arr[..., :3].copy()).save(HERE / "img" / nombre, quality=95)


def musica():
    """Ondas de canciones en fila; las generadas por IA, tachadas y cayendo."""
    arr, c = lienzo()
    rng = np.random.default_rng(3)
    for k in range(6):
        y = 330 + k * 118; ia = k in (1, 3, 4)
        x0 = 200
        c.drawCircle(x0, y, 34, pnt(FG if not ia else GR, 5))
        tri = skia.Path(); tri.moveTo(x0 - 10, y - 16); tri.lineTo(x0 + 18, y); tri.lineTo(x0 - 10, y + 16); tri.close()
        c.drawPath(tri, pnt(FG if not ia else GR))
        for j in range(60):
            x = 290 + j * 19
            h = (20 + 50 * abs(math.sin(j * 0.37 + k)) * rng.uniform(0.5, 1.0))
            c.drawLine(x, y - h / 2, x, y + h / 2, pnt(FG if not ia else GR, 8, 0.95 if not ia else 0.45))
        if ia:
            c.drawLine(180, y, 1460, y, pnt(FG, 9))
            f = skia.Font(skia.Typeface("DejaVu Sans", skia.FontStyle.Bold()), 40)
            c.drawString("IA", 1480, y + 14, f, pnt(FG))
    guardar(arr, "musica.jpg")


def juguete():
    """Osito de peluche con un globo de diálogo tachado."""
    arr, c = lienzo()
    cx, cy = 640, 520
    for (x, y, r) in ((cx - 150, cy - 250, 75), (cx + 150, cy - 250, 75)):
        c.drawCircle(x, y, r, pnt(FG)); c.drawCircle(x, y, r * 0.5, pnt(DK))
    c.drawCircle(cx, cy - 120, 200, pnt(FG))
    c.drawOval(skia.Rect(cx - 210, cy + 40, cx + 210, cy + 400), pnt(FG))
    c.drawOval(skia.Rect(cx - 90, cy - 90, cx + 90, cy + 10), pnt(GR))
    c.drawCircle(cx - 70, cy - 170, 20, pnt(DK)); c.drawCircle(cx + 70, cy - 170, 20, pnt(DK))
    c.drawOval(skia.Rect(cx - 30, cy - 75, cx + 30, cy - 35), pnt(DK))
    c.drawCircle(cx - 230, cy + 160, 70, pnt(FG)); c.drawCircle(cx + 230, cy + 160, 70, pnt(FG))
    # altavoz en el pecho
    for r in (30, 55, 80):
        c.drawCircle(cx, cy + 210, r, pnt(DK, 8))
    # globo de diálogo
    bx, by = 1180, 430
    rr = skia.RRect.MakeRectXY(skia.Rect(bx - 260, by - 150, bx + 260, by + 130), 60, 60)
    c.drawRRect(rr, pnt(FG, 12))
    tail = skia.Path(); tail.moveTo(bx - 170, by + 120); tail.lineTo(bx - 290, by + 260); tail.lineTo(bx - 60, by + 128)
    c.drawPath(tail, pnt(FG, 12))
    for k in range(3):
        c.drawCircle(bx - 110 + k * 110, by - 10, 26, pnt(FG))
    c.drawLine(bx - 300, by + 190, bx + 300, by - 210, pnt(FG, 20))
    guardar(arr, "juguete.jpg")


def red():
    """Red de computadores con un candado abierto en el centro."""
    arr, c = lienzo()
    rng = np.random.default_rng(7)
    nodos = [(rng.uniform(120, 1480), rng.uniform(100, 900)) for _ in range(26)]
    for i, a in enumerate(nodos):
        for b in nodos[i + 1:]:
            if math.dist(a, b) < 330: c.drawLine(*a, *b, pnt(GR, 3, 0.6))
    for (x, y) in nodos:
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 34, y - 24, x + 34, y + 24), 6, 6), pnt(DK))
        c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(x - 34, y - 24, x + 34, y + 24), 6, 6), pnt(FG, 4))
    cx, cy = 800, 540
    c.drawCircle(cx, cy, 250, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(0.03, 0.03, 0.03, 0.85)))
    body = skia.RRect.MakeRectXY(skia.Rect(cx - 140, cy - 40, cx + 140, cy + 180), 30, 30)
    c.drawRRect(body, pnt(FG))
    arco = skia.Path(); arco.moveTo(cx - 90, cy - 40); arco.lineTo(cx - 90, cy - 120)
    arco.arcTo(skia.Rect(cx - 90, cy - 210, cx + 90, cy - 30), 180, 180, False)
    arco.lineTo(cx + 90, cy - 150)
    m = skia.Matrix(); m.setRotate(-28, cx + 90, cy - 40)
    arco.transform(m)
    c.drawPath(arco, pnt(FG, 30))
    c.drawCircle(cx, cy + 50, 26, pnt(DK)); c.drawRect(skia.Rect(cx - 10, cy + 60, cx + 10, cy + 130), pnt(DK))
    guardar(arr, "red.jpg")


def tribunal():
    """Mazo de juez sobre su base y una balanza."""
    arr, c = lienzo()
    # balanza
    bx, by = 1080, 160
    c.drawLine(bx, by, bx, by + 620, pnt(FG, 14))
    c.drawLine(bx - 320, by + 60, bx + 320, by + 60, pnt(FG, 14))
    c.drawCircle(bx, by, 22, pnt(FG))
    for sx in (-320, 320):
        x = bx + sx
        c.drawLine(x, by + 60, x - 110, by + 300, pnt(GR, 5)); c.drawLine(x, by + 60, x + 110, by + 300, pnt(GR, 5))
        bowl = skia.Path(); bowl.moveTo(x - 130, by + 300)
        bowl.arcTo(skia.Rect(x - 130, by + 230, x + 130, by + 370), 180, -180, False); bowl.close()
        c.drawPath(bowl, pnt(FG))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(bx - 180, by + 640, bx + 180, by + 680), 12, 12), pnt(FG))
    c.drawRect(skia.Rect(bx - 90, by + 615, bx + 90, by + 645), pnt(FG))
    # mazo
    c.save(); c.translate(460, 520); c.rotate(-35)
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-30, -40, 380, 40), 18, 18), pnt(GR))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-150, -130, 40, 130), 30, 30), pnt(FG))
    c.drawRect(skia.Rect(-150, -80, 40, -60), pnt(DK)); c.drawRect(skia.Rect(-150, 60, 40, 80), pnt(DK))
    c.restore()
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(180, 800, 620, 880), 20, 20), pnt(FG))
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(240, 760, 560, 810), 16, 16), pnt(GR))
    guardar(arr, "tribunal.jpg")


def cohete():
    """Primera etapa de un cohete reutilizable aterrizando sobre una barcaza en el mar."""
    arr, c = lienzo()
    # mar
    for k in range(6):
        y = 820 + k * 34
        pth = skia.Path(); pth.moveTo(0, y)
        for x in range(0, W + 40, 40): pth.lineTo(x, y + 8 * math.sin(x / 60 + k))
        c.drawPath(pth, pnt(GR, 4, 0.7 - 0.08 * k))
    # barcaza
    c.drawRect(skia.Rect(420, 770, 1180, 830), pnt(FG))
    c.drawRect(skia.Rect(450, 745, 1150, 770), pnt(GR))
    c.drawCircle(800, 757, 40, pnt(DK, 6))
    # etapa
    cx, top, bot = 800, 120, 600
    c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(cx - 45, top, cx + 45, bot), 10, 10), pnt(FG))
    c.drawRect(skia.Rect(cx - 45, top + 60, cx + 45, top + 80), pnt(DK))
    for sx in (-1, 1):   # patas
        c.drawLine(cx + sx * 40, bot - 90, cx + sx * 150, bot + 90, pnt(FG, 12))
    for sx in (-1, 1):   # aletas
        c.drawRect(skia.Rect(cx + sx * 45 - (30 if sx < 0 else 0), top + 10, cx + sx * 45 + (30 if sx > 0 else 0), top + 40), pnt(GR))
    # llama
    fl = skia.Path(); fl.moveTo(cx - 35, bot); fl.quadTo(cx - 20, bot + 110, cx, bot + 150)
    fl.quadTo(cx + 20, bot + 110, cx + 35, bot); fl.close()
    c.drawPath(fl, pnt(FG, 0, 0.9))
    c.drawCircle(cx, bot + 150, 70, skia.Paint(AntiAlias=True, Color4f=skia.Color4f(1, 1, 1, 0.12),
                                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 30)))
    guardar(arr, "cohete.jpg")


if __name__ == "__main__":
    (HERE / "img").mkdir(exist_ok=True)
    musica(); juguete(); red(); tribunal(); cohete()
    print("ok")


def portadas():
    """Copias reducidas y bajadas para la portada (la cabecera de marca no tapa el dibujo)."""
    for n in ("musica", "juguete", "cohete", "red"):
        im = Image.open(HERE / "img" / f"{n}.jpg")
        bg = Image.new("RGB", im.size, im.getpixel((5, 5)))
        sm = im.resize((round(im.width * 0.72), round(im.height * 0.72)), Image.LANCZOS)
        bg.paste(sm, ((im.width - sm.width) // 2, im.height - sm.height))
        bg.save(HERE / "img" / f"{n}_p.jpg", quality=95)


if __name__ == "__main__":
    portadas()
