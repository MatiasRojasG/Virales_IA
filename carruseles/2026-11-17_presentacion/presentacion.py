"""Carrusel de presentación de stheq.ia: qué va a encontrar quien siga la página.

    python carruseles/2026-11-17_presentacion/presentacion.py

Reutiliza los ayudantes de tools/carrusel.py (marca, logo, pie, degradados). Las «pantallas» que se
muestran son piezas reales de la cuenta: la portada del decálogo dec01 y la del carrusel de noticias.
"""
from __future__ import annotations
import sys
from pathlib import Path
from PIL import Image
import skia

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]
import carrusel as K
from reelforge import config as C
from reelforge import marca as M
from reelforge.draw import P, paint, color4

W, H, X0, X1 = K.W, K.H, K.X0, K.X1
FG, GRAY, DIM, RED, BG = K.FG, K.GRAY, K.DIM, K.RED, K.BG
FECHA = "17 NOV 2026"
N = 6


def base():
    arr, s = K.surface(); p = P(s.getCanvas()); p.c.clear(color4(BG))
    sh = skia.GradientShader.MakeRadial((W / 2, H * 0.45), 760, [color4(M.BG2, 1), color4(BG, 0)])
    p.c.drawPaint(skia.Paint(Shader=sh))
    return arr, p


def telefono(p, img_path, cx, cy, h, rot=0.0):
    """Maqueta de teléfono 9:16 con una pieza real de la cuenta en pantalla (centrada si es 4:5)."""
    im = Image.open(img_path).convert("RGB")
    w = h * 9 / 16
    if abs(im.width / im.height - 9 / 16) > 0.02:
        lien = Image.new("RGB", (1080, 1920), (10, 10, 10))
        im2 = im.resize((1080, round(im.height * 1080 / im.width)), Image.LANCZOS)
        lien.paste(im2, (0, (1920 - im2.height) // 2)); im = lien
    with p.transform(0, 0, 1, rot=rot, cx=cx, cy=cy):
        b = 18
        p.rect(cx - w / 2 - b, cy - h / 2 - b, cx + w / 2 + b, cy + h / 2 + b, (0.16, 0.16, 0.16), 1, radius=46)
        p.rect(cx - w / 2 - b, cy - h / 2 - b, cx + w / 2 + b, cy + h / 2 + b, FG, 0.25, stroke=2, radius=46)
        p.c.save()
        rr = skia.RRect.MakeRectXY(skia.Rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 30, 30)
        p.c.clipRRect(rr, doAntiAlias=True)
        p.img(K.skimg(im.resize((int(w * 2), int(h * 2)), Image.LANCZOS)), cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, nearest=False)
        p.c.restore()


def bloque(p, y, kicker, titulo, texto, size=72):
    p.text(kicker, X0, y, 26, RED, 1, face=C.FONT_BOLD, align="left", tracking=3)
    y += 24
    for ln in K.wrap(titulo, size, C.FONT_BLACK, X1 - X0):
        y += size * 1.05; p.text(ln, X0 - 3, y - size * 0.12, size, FG, 1, face=C.FONT_BLACK, align="left")
    y += 26
    for ln in K.wrap(texto, 34, C.FONT_MED, X1 - X0):
        y += 48; p.text(ln, X0, y - 10, 34, FG, 0.8, face=C.FONT_MED, align="left")
    return y


def s1():
    arr, p = base()
    logo = Image.open(K.LOGO); lw = 640; lh = round(logo.height * lw / logo.width)
    p.img(K.skimg(logo.resize((lw * 2, lh * 2), Image.LANCZOS)), (W - lw) / 2, 300, (W + lw) / 2, 300 + lh, nearest=False)
    y = 300 + lh + 150
    for ln, col in [("IA, ciencia y hábitos", FG), ("que sí funcionan.", RED)]:
        p.text(ln, W / 2, y, 68, col, 1, face=C.FONT_BLACK); y += 82
    y += 30
    for ln in K.wrap("Esto es lo que vas a encontrar aquí.", 34, C.FONT_MED, 820):
        p.text(ln, W / 2, y, 34, FG, 0.75, face=C.FONT_MED); y += 48
    p.text("Desliza", X1 - 64, 1290, 26, FG, 0.9, face=C.FONT_BOLD, align="right")
    p.arrow(X1 - 50, 1281, X1, 1281, RED, 1, w=4, head=18)
    p.text(f"1/{N}", X0, 1290, 22, GRAY, 1, face=C.FONT_SEMI, align="left")
    return arr


def s2():
    arr, p = base(); K.cabecera(p, FECHA)
    telefono(p, ROOT / "episodes/dec01_glow_up/output/portada.png", W / 2, 470, 560, rot=-4)
    bloque(p, 830, "REELS · TODOS LOS DÍAS", "Decálogos con ciencia",
           "10 reglas en un reel corto para cuidarte, estudiar, verte mejor, entrenar o dormir. Cada regla con su respaldo.")
    K.pie(p, "", 2, N)
    return arr


def s3():
    arr, p = base(); K.cabecera(p, FECHA)
    telefono(p, ROOT / "carruseles/2026-11-18_noticias/slides/01.jpg", W / 2, 470, 560, rot=4)
    bloque(p, 830, "CARRUSELES · LUNES, MIÉRCOLES Y VIERNES", "Noticias de IA",
           "Lo que pasó en las últimas 24 horas, verificado en la fuente y explicado en pocas líneas: qué pasó y por qué importa.")
    K.pie(p, "", 3, N)
    return arr


def s4():
    arr, p = base(); K.cabecera(p, FECHA)
    # semana tipo
    dias = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB", "DOM"]
    cw, gap, y0 = 120, 16, 260
    x = (W - (7 * cw + 6 * gap)) / 2
    for i, d in enumerate(dias):
        xx = x + i * (cw + gap)
        p.rect(xx, y0, xx + cw, y0 + 420, FG, 0.06, radius=22)
        p.rect(xx, y0, xx + cw, y0 + 420, FG, 0.18, stroke=2, radius=22)
        p.text(d, xx + cw / 2, y0 + 56, 26, FG, 0.9, face=C.FONT_BOLD, tracking=2)
        # reel diario
        p.rect(xx + 18, y0 + 90, xx + cw - 18, y0 + 230, FG, 1, radius=14)
        tri = skia.Path(); cx, cy = xx + cw / 2, y0 + 160
        tri.moveTo(cx - 14, cy - 20); tri.lineTo(cx + 20, cy); tri.lineTo(cx - 14, cy + 20); tri.close()
        p.c.drawPath(tri, paint(BG, 1))
        if i in (0, 2, 4):
            for k in range(3):
                p.rect(xx + 26 + k * 8, y0 + 262 + k * 8, xx + cw - 34 + k * 8, y0 + 380 + k * 8, RED if k == 2 else GRAY, 1 if k == 2 else 0.5, radius=10)
    ly = y0 + 470
    p.rect(X0 + 150, ly - 18, X0 + 190, ly + 8, FG, 1, radius=6)
    p.text("reel decálogo", X0 + 205, ly + 4, 28, FG, 0.85, face=C.FONT_SEMI, align="left")
    p.rect(X0 + 520, ly - 22, X0 + 556, ly + 12, RED, 1, radius=6)
    p.text("noticias de IA", X0 + 572, ly + 4, 28, FG, 0.85, face=C.FONT_SEMI, align="left")
    bloque(p, 830, "TU SEMANA EN STHEQ", "10 publicaciones por semana",
           "Un reel cada día y tres carruseles de noticias. Siempre a la hora en que más gente está conectada.")
    K.pie(p, "", 4, N)
    return arr


def s5():
    arr, p = base(); K.cabecera(p, FECHA)
    y = 290
    p.text("NUESTRAS REGLAS", X0, y, 26, RED, 1, face=C.FONT_BOLD, align="left", tracking=3)
    y += 30
    reglas = [("Todo con fuente.", "Estudios, organismos oficiales y medios verificados. Siempre citados."),
              ("Nada de rumores.", "Si una noticia no se confirma en la fuente original, no se publica."),
              ("Sin promesas milagrosas.", "Hábitos que funcionan, no atajos ni productos mágicos."),
              ("Directo al punto.", "Lo que pasó, por qué importa y qué puedes hacer tú.")]
    for i, (t, d) in enumerate(reglas):
        y += 112
        p.text(f"{i + 1:02d}", X0, y, 52, RED, 1, face=C.FONT_BLACK, align="left")
        p.text(t, X0 + 110, y, 54, FG, 1, face=C.FONT_BLACK, align="left")
        yy = y + 8
        for ln in K.wrap(d, 31, C.FONT_MED, X1 - X0 - 110):
            yy += 44; p.text(ln, X0 + 110, yy, 31, FG, 0.72, face=C.FONT_MED, align="left")
        y = yy + 14
    K.pie(p, "", 5, N)
    return arr


def s6():
    arr, p = base()
    logo = Image.open(K.LOGO); lw = 520; lh = round(logo.height * lw / logo.width)
    p.img(K.skimg(logo.resize((lw * 2, lh * 2), Image.LANCZOS)), (W - lw) / 2, 240, (W + lw) / 2, 240 + lh, nearest=False)
    y = 240 + lh + 160
    for ln in K.wrap("¿Qué decálogo quieres ver primero?", 64, C.FONT_BLACK, X1 - X0 - 40):
        p.text(ln, W / 2, y, 64, FG, 1, face=C.FONT_BLACK); y += 76
    y += 20
    ops = ["estudiar", "dormir", "entrenar", "piel"]
    f_w = [K.font(32, C.FONT_BOLD).measureText(o) + 48 for o in ops]
    tot = sum(f_w) + 16 * (len(ops) - 1); x = (W - tot) / 2
    for o, w in zip(ops, f_w):
        p.rect(x, y - 30, x + w, y + 22, FG, 0.9, stroke=2.5, radius=26)
        p.text(o, x + w / 2, y + 4, 32, FG, 1, face=C.FONT_BOLD); x += w + 16
    y += 110
    p.rect(W / 2 - 40, y - 10, W / 2 + 40, y - 4, RED, 1, radius=3)
    y += 70
    for ln in K.wrap("Coméntalo y síguenos para no perderte ninguno.", 34, C.FONT_MED, X1 - X0 - 80):
        p.text(ln, W / 2, y, 34, FG, 0.8, face=C.FONT_MED); y += 48
    p.text(M.NAME, W / 2, 1210, 30, FG, 0.85, face=C.FONT_BOLD, tracking=3)
    p.text(f"{N}/{N}", X1, 1290, 22, GRAY, 1, face=C.FONT_SEMI, align="right")
    return arr


def main():
    out = HERE / "slides"; out.mkdir(exist_ok=True)
    ims = []
    for k, fn in enumerate([s1, s2, s3, s4, s5, s6], 1):
        im = Image.fromarray(fn()[..., :3].copy()); im.save(out / f"{k:02d}.jpg", quality=95); ims.append(im)
    tw, th = 360, 450
    sheet = Image.new("RGB", (tw * 3, th * 2), (30, 30, 30))
    for k, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), ((k % 3) * tw, (k // 3) * th))
    sheet.save(HERE / "hoja.png")
    print("ok")


if __name__ == "__main__":
    main()
