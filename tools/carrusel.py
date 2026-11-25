"""Carruseles de noticias de stheq.ia (Instagram, 1080×1350, 4:5) a partir de un JSON.

    python tools/carrusel.py carruseles/<fecha>_noticias/noticias.json

Genera <carpeta>/slides/01.png … NN.png y <carpeta>/hoja.png (vista de control).
Estilo de marca (reelforge/marca.py): fondo negro, texto blanco, rojo solo para acentos, logo
arriba, fotos de Wikimedia Commons en blanco y negro con crédito (autor · licencia) en cada lámina.

Formato del JSON:
{
 "fecha": "18 NOV 2026",
 "portada": {"kicker": "...", "titulo": ["LÍNEA 1", "LÍNEA 2"], "rojo": [1], "imagenes": ["img/a.jpg", ...],
             "focos": [[0.5, 0.4], ...]},
 "noticias": [{"cat": "EMPRESAS", "titulo": "...", "texto": "...", "importa": "...", "fuente": "...",
               "img": "img/a.jpg", "foco": [0.45, 0.35]}],
 "cierre": {"pregunta": "...", "cta": "..."}
}
El crédito de cada foto se lee de img/<nombre>.json (lo crea tools/commons.py).
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import skia
from PIL import Image, ImageEnhance, ImageOps

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from reelforge import config as C
from reelforge import marca as M
from reelforge.draw import P, paint, color4, font

W, H = 1080, 1350
X0, X1 = 64, 1016                     # márgenes
FG, GRAY, DIM, RED, BG = M.FG, M.GRAY, M.DIM, M.RED, M.BG
LOGO = ROOT / "assets" / "marca" / "logo_blanco.png"


# ------------------------------------------------------------------ utilidades
def surface():
    arr = np.zeros((H, W, 4), np.uint8)
    return arr, skia.Surface(arr)


def skimg(pil):
    a = np.array(pil.convert("RGBA"))
    return skia.Image.fromarray(a, colorType=skia.kRGBA_8888_ColorType)


def foto(path, w, h, foco=(0.5, 0.5), zoom=1.0, gris=True):
    """Recorta la foto a w×h centrada en `foco` (fracciones, con `zoom` ≥ 1) y la pasa a blanco y negro."""
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height) * zoom
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    cx, cy = foco[0] * im.width, foco[1] * im.height
    x0 = int(min(max(0, cx - w / 2), im.width - w)); y0 = int(min(max(0, cy - h / 2), im.height - h))
    im = im.crop((x0, y0, x0 + w, y0 + h))
    if gris:
        im = ImageOps.grayscale(im).convert("RGB")
        im = ImageEnhance.Contrast(im).enhance(1.18)
        im = ImageEnhance.Brightness(im).enhance(0.92)
    return skimg(im)


def credito(path):
    j = Path(path).with_suffix(".json")
    if not j.exists(): return ""
    d = json.loads(j.read_text())
    autor = d["autor"].replace("\n", " ").strip() or "autor desconocido"
    return f"Foto: {autor} · {d['licencia']} · Wikimedia Commons"


def wrap(text, size, face, maxw):
    f = font(size, face); words = [x for x in text.split(" ") if x]; lines, cur = [], ""   # NBSP no corta
    for w_ in words:
        t = (cur + " " + w_).strip()
        if f.measureText(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return [l.replace("\u00a0", " ") for l in lines]


def degradado(p, y0, y1, a0, a1):
    sh = skia.GradientShader.MakeLinear([(0, y0), (0, y1)], [color4(BG, a0), color4(BG, a1)])
    p.c.drawRect(skia.Rect(0, y0, W, y1), skia.Paint(Shader=sh))


def cabecera(p, fecha):
    logo = Image.open(LOGO); h = 46; w = round(logo.width * h / logo.height)
    p.img(skimg(logo.resize((w * 2, h * 2), Image.LANCZOS)), X0, 54, X0 + w, 54 + h, nearest=False)
    p.text(M.NAME, X0 + w + 18, 86, 26, FG, 0.85, face=C.FONT_BOLD, align="left", tracking=1.5)
    p.text(fecha, X1, 86, 24, FG, 0.75, face=C.FONT_SEMI, align="right", tracking=2)


def pie(p, izq, k, n, y=1290):
    p.line(X0, y - 40, X1, y - 40, FG, 0.14, w=2)
    if izq: p.text(izq, X0, y, 22, GRAY, 1, face=C.FONT_MED, align="left")
    p.text(f"{k}/{n}", X1, y, 22, GRAY, 1, face=C.FONT_SEMI, align="right")


def pill(p, s, x, y, rgb):
    f = font(24, C.FONT_BOLD); w = f.measureText(s) + 2.5 * (len(s) - 1)
    p.rect(x, y - 30, x + w + 36, y + 10, rgb, 1, radius=20)
    p.text(s, x + 18, y - 2, 24, BG if rgb != BG else FG, 1, face=C.FONT_BOLD, align="left", tracking=2.5)
    return w + 36


# ------------------------------------------------------------------ láminas
def portada(spec, base, k, n):
    arr, s = surface(); p = P(s.getCanvas()); p.c.clear(color4(BG))
    pc = spec["portada"]; ims = pc["imagenes"]; focos = pc.get("focos", [[0.5, 0.5]] * len(ims))
    zooms = pc.get("zooms", [1.0] * len(ims))
    g = 6; cw, ch = (W - g) // 2, 380
    for i, (im, fc) in enumerate(zip(ims[:4], focos)):
        x, y = (i % 2) * (cw + g), (i // 2) * (ch + g)
        p.img(foto(base / im, cw, ch, fc, zooms[i]), x, y, x + cw, y + ch, nearest=False)
    degradado(p, 0, 200, 0.85, 0.0)
    degradado(p, 420, 770, 0.0, 1.0)
    cabecera(p, spec["fecha"])
    y = 830
    p.text(pc["kicker"], X0, y, 28, RED, 1, face=C.FONT_BOLD, align="left", tracking=3)
    y += 100
    for i, ln in enumerate(pc["titulo"]):
        p.text(ln, X0 - 4, y, 92, RED if i in pc.get("rojo", []) else FG, 1, face=C.FONT_BLACK, align="left")
        y += 98
    # «desliza»
    p.text("Desliza", X1 - 64, 1290, 26, FG, 0.9, face=C.FONT_BOLD, align="right")
    p.arrow(X1 - 50, 1281, X1, 1281, RED, 1, w=4, head=18)
    p.text(f"{k}/{n}", X0, 1290, 22, GRAY, 1, face=C.FONT_SEMI, align="left")
    return arr


def noticia(spec, nt, i, base, k, n):
    arr, s = surface(); p = P(s.getCanvas()); p.c.clear(color4(BG))
    ih = 640
    p.img(foto(base / nt["img"], W, ih, nt.get("foco", [0.5, 0.5]), nt.get("zoom", 1.0)), 0, 0, W, ih, nearest=False)
    degradado(p, 0, 190, 0.85, 0.0)
    degradado(p, ih - 300, ih + 2, 0.0, 1.0)
    cabecera(p, spec["fecha"])
    cr = credito(base / nt["img"])
    if nt.get("pie"): cr = nt["pie"] + ("  ·  " + cr if cr else "")
    if cr: p.text(cr, X1, ih - 18, 18, FG, 0.55, face=C.FONT_MED, align="right")
    # número + categoría
    y = ih + 64
    p.text(f"{i:02d}", X0, y, 40, RED, 1, face=C.FONT_BLACK, align="left")
    pill(p, nt["cat"], X0 + 78, y - 2, FG)
    # titular, texto y «por qué importa» con tamaños que caben
    for ts, bs in ((60, 31), (54, 29), (50, 27)):
        tl = wrap(nt["titulo"], ts, C.FONT_BLACK, X1 - X0)
        bl = wrap(nt["texto"], bs, C.FONT_MED, X1 - X0)
        il = wrap(nt["importa"], bs, C.FONT_SEMI, X1 - X0 - 28)
        alto = 34 + len(tl) * ts * 1.1 + 24 + len(bl) * bs * 1.42 + 56 + 34 + len(il) * bs * 1.38
        if y + alto < 1225: break
    y += 34
    for ln in tl:
        y += ts * 1.1; p.text(ln, X0 - 2, y - ts * 0.18, ts, FG, 1, face=C.FONT_BLACK, align="left")
    y += 24
    for ln in bl:
        y += bs * 1.42; p.text(ln, X0, y - bs * 0.3, bs, FG, 0.78, face=C.FONT_MED, align="left")
    y += 56
    y0 = y
    p.text("POR QUÉ IMPORTA", X0 + 28, y + 6, 21, RED, 1, face=C.FONT_BOLD, align="left", tracking=3)
    y += 34
    for ln in il:
        y += bs * 1.38; p.text(ln, X0 + 28, y - bs * 0.3, bs, FG, 1, face=C.FONT_SEMI, align="left")
    p.rect(X0, y0 - 18, X0 + 6, y + 4, RED, 1, radius=3)
    pie(p, "Fuente: " + nt["fuente"], k, n)
    return arr


def cierre(spec, base, k, n):
    arr, s = surface(); p = P(s.getCanvas()); M.background(p, 1.0); p.c.clear(color4(BG))
    sh = skia.GradientShader.MakeRadial((W / 2, H * 0.42), 700, [color4(M.BG2, 1), color4(BG, 0)])
    p.c.drawPaint(skia.Paint(Shader=sh))
    logo = Image.open(LOGO); lw = 520; lh = round(logo.height * lw / logo.width)
    p.img(skimg(logo.resize((lw * 2, lh * 2), Image.LANCZOS)), (W - lw) / 2, 250, (W + lw) / 2, 250 + lh, nearest=False)
    cz = spec["cierre"]; y = 250 + lh + 170
    for ln in wrap(cz["pregunta"], 64, C.FONT_BLACK, X1 - X0 - 40):
        p.text(ln, W / 2, y, 64, FG, 1, face=C.FONT_BLACK); y += 76
    p.rect(W / 2 - 40, y - 10, W / 2 + 40, y - 4, RED, 1, radius=3)
    y += 70
    for ln in wrap(cz["cta"], 34, C.FONT_MED, X1 - X0 - 80):
        p.text(ln, W / 2, y, 34, FG, 0.8, face=C.FONT_MED); y += 48
    p.text(M.NAME, W / 2, 1210, 30, FG, 0.85, face=C.FONT_BOLD, tracking=3)
    p.text(f"{k}/{n}", X1, 1290, 22, GRAY, 1, face=C.FONT_SEMI, align="right")
    return arr


def main():
    js = Path(sys.argv[1]).resolve(); base = js.parent
    spec = json.loads(js.read_text())
    n = 2 + len(spec["noticias"])
    out = base / "slides"; out.mkdir(exist_ok=True)
    for f in out.glob("*.png"): f.unlink()
    arrs = [portada(spec, base, 1, n)]
    arrs += [noticia(spec, nt, i + 1, base, i + 2, n) for i, nt in enumerate(spec["noticias"])]
    arrs.append(cierre(spec, base, n, n))
    ims = []
    for k, a in enumerate(arrs, 1):
        im = Image.fromarray(a[..., :3].copy()); im.save(out / f"{k:02d}.jpg", quality=95); ims.append(im)
    tw, th = 360, 450
    sheet = Image.new("RGB", (tw * min(4, n), th * ((n + 3) // 4)), (30, 30, 30))
    for k, im in enumerate(ims):
        sheet.paste(im.resize((tw, th), Image.LANCZOS), ((k % 4) * tw, (k // 4) * th))
    sheet.save(base / "hoja.png")
    print(f"{n} láminas en {out}")


if __name__ == "__main__":
    main()
