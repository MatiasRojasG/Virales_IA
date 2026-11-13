"""Primitivas de dibujo vectorial sobre skia, con la identidad visual de la serie."""
from __future__ import annotations
import math
from contextlib import contextmanager
import numpy as np
import skia
from . import config as C
from .ease import clamp, lerp

NEAREST = skia.SamplingOptions(skia.FilterMode.kNearest)
LINEAR = skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear)


def color4(rgb, a=1.0):
    return skia.Color4f(rgb[0], rgb[1], rgb[2], clamp(a))


def paint(rgb=C.WHITE, a=1.0, stroke=None, blur=0.0, cap="round"):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(color4(rgb, a))
    if stroke is not None:
        p.setStyle(skia.Paint.kStroke_Style)
        p.setStrokeWidth(stroke)
        p.setStrokeCap(skia.Paint.kRound_Cap if cap == "round" else skia.Paint.kButt_Cap)
        p.setStrokeJoin(skia.Paint.kRound_Join)
    if blur > 0:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    return p


_font_cache = {}
def font(size, face=C.FONT_SEMI):
    key = (round(size, 1), face)
    if key not in _font_cache:
        f = skia.Font(C.typeface(face), size)
        f.setSubpixel(True)
        f.setEdging(skia.Font.Edging.kAntiAlias)
        _font_cache[key] = f
    return _font_cache[key]


_img_cache = {}
def image(arr_or_key, arr=None):
    """Convierte un arreglo RGBA/gris (uint8) en skia.Image, con caché por clave."""
    if arr is None:
        arr, key = arr_or_key, id(arr_or_key)
    else:
        key = arr_or_key
    if key not in _img_cache:
        a = np.asarray(arr)
        if a.ndim == 2:
            a = np.dstack([a, a, a, np.full_like(a, 255)])
        _img_cache[key] = skia.Image.fromarray(np.ascontiguousarray(a, dtype=np.uint8))
    return _img_cache[key]


class P:
    """Envoltura del canvas con helpers de alto nivel."""

    def __init__(self, canvas: skia.Canvas):
        self.c = canvas

    # ---------- estado / capas ----------
    @contextmanager
    def layer(self, alpha=1.0):
        if alpha >= 0.999:
            self.c.save(); yield; self.c.restore(); return
        self.c.saveLayerAlpha(None, int(255 * clamp(alpha)))
        yield
        self.c.restore()

    @contextmanager
    def transform(self, tx=0, ty=0, s=1.0, rot=0.0, cx=None, cy=None):
        self.c.save()
        if cx is not None:
            self.c.translate(cx, cy)
        self.c.translate(tx, ty)
        if rot: self.c.rotate(rot)
        if s != 1.0: self.c.scale(s, s)
        if cx is not None:
            self.c.translate(-cx, -cy)
        yield
        self.c.restore()

    @contextmanager
    def clip_rect(self, x0, y0, x1, y1):
        self.c.save(); self.c.clipRect(skia.Rect(x0, y0, x1, y1), doAntiAlias=True)
        yield
        self.c.restore()

    # ---------- fondo ----------
    def background(self, t, accent=0.0):
        c = self.c
        c.clear(color4(C.BG))
        # halo radial que respira lentamente
        r = 1100 + 60 * math.sin(t * 0.6)
        sh = skia.GradientShader.MakeRadial(
            (C.W * 0.5, C.H * 0.40), r,
            [color4(C.BG2, 0.95), color4(C.BG, 0.0)])
        c.drawPaint(skia.Paint(Shader=sh))
        if accent > 0:
            sh2 = skia.GradientShader.MakeRadial(
                (C.W * 0.5, C.H * 0.42), 700,
                [color4(C.CYAN, 0.10 * accent), color4(C.BG, 0.0)])
            c.drawPaint(skia.Paint(Shader=sh2))
        # retícula de puntos sutil con deriva
        p = paint(C.WHITE, 0.045)
        off = (t * 6) % 60
        for y in range(-60, C.H + 60, 60):
            for x in range(0, C.W + 60, 60):
                c.drawCircle(x, y + off, 1.6, p)

    # ---------- formas ----------
    def circle(self, x, y, r, rgb=C.WHITE, a=1.0, stroke=None, blur=0):
        if r <= 0 or a <= 0: return
        self.c.drawCircle(x, y, r, paint(rgb, a, stroke, blur))

    def glow_circle(self, x, y, r, rgb=C.CYAN, a=1.0, spread=2.2):
        if a <= 0: return
        self.c.drawCircle(x, y, r * spread, paint(rgb, 0.18 * a, blur=r * 0.9))
        self.c.drawCircle(x, y, r, paint(rgb, a))

    def rect(self, x0, y0, x1, y1, rgb=C.WHITE, a=1.0, stroke=None, radius=0, blur=0):
        if a <= 0: return
        r = skia.Rect(x0, y0, x1, y1)
        p = paint(rgb, a, stroke, blur)
        if radius: self.c.drawRoundRect(r, radius, radius, p)
        else: self.c.drawRect(r, p)

    def line(self, x0, y0, x1, y1, rgb=C.WHITE, a=1.0, w=4, frac=1.0, glow=False, cap="round"):
        if a <= 0 or frac <= 0: return
        x1, y1 = lerp(x0, x1, frac), lerp(y0, y1, frac)
        if glow:
            self.c.drawLine(x0, y0, x1, y1, paint(rgb, 0.35 * a, w * 3, blur=w * 1.5, cap=cap))
        self.c.drawLine(x0, y0, x1, y1, paint(rgb, a, w, cap=cap))

    def arrow(self, x0, y0, x1, y1, rgb=C.WHITE, a=1.0, w=4, head=22, frac=1.0, gap=0):
        if a <= 0 or frac <= 0: return
        ang = math.atan2(y1 - y0, x1 - x0)
        x0 += gap * math.cos(ang); y0 += gap * math.sin(ang)
        x1 -= gap * math.cos(ang); y1 -= gap * math.sin(ang)
        xe, ye = lerp(x0, x1, frac), lerp(y0, y1, frac)
        self.c.drawLine(x0, y0, xe - head * 0.6 * math.cos(ang), ye - head * 0.6 * math.sin(ang), paint(rgb, a, w))
        path = skia.Path()
        path.moveTo(xe, ye)
        for s in (+1, -1):
            path.lineTo(xe - head * math.cos(ang + s * 0.42), ye - head * math.sin(ang + s * 0.42))
        path.close()
        self.c.drawPath(path, paint(rgb, a))

    def arc_progress(self, x, y, r, frac, rgb=C.CYAN, a=1.0, w=10):
        rect = skia.Rect(x - r, y - r, x + r, y + r)
        self.c.drawArc(rect, -90, 360 * clamp(frac), False, paint(rgb, a, w))

    # ---------- texto ----------
    def text(self, s, x, y, size=56, rgb=C.WHITE, a=1.0, face=C.FONT_SEMI, align="center",
             glow=0.0, shadow=False, tracking=0.0):
        if a <= 0 or not s: return 0
        f = font(size, face)
        wdt = f.measureText(s) + tracking * (len(s) - 1)
        x0 = x - wdt / 2 if align == "center" else x - wdt if align == "right" else x
        if shadow:
            self.c.drawString(s, x0, y + 4, f, paint(C.BG, 0.85 * a, blur=10))
        if glow > 0:
            self.c.drawString(s, x0, y, f, paint(rgb, 0.55 * a * glow, blur=size * 0.18))
        if tracking:
            p = paint(rgb, a); cx = x0
            for ch in s:
                self.c.drawString(ch, cx, y, f, p); cx += f.measureText(ch) + tracking
        else:
            self.c.drawString(s, x0, y, f, paint(rgb, a))
        return wdt

    def text_width(self, s, size=56, face=C.FONT_SEMI):
        return font(size, face).measureText(s)

    def rich(self, parts, x, y, size=56, a=1.0, face=C.FONT_SEMI, align="center"):
        """parts: lista de (texto, rgb). Dibuja en una sola línea."""
        f = font(size, face)
        total = sum(f.measureText(s) for s, _ in parts)
        cx = x - total / 2 if align == "center" else x
        for s, rgb in parts:
            self.c.drawString(s, cx, y, f, paint(rgb, a)); cx += f.measureText(s)
        return total

    def pill(self, s, x, y, size=34, rgb=C.CYAN, a=1.0, face=C.FONT_BOLD, fill_a=0.14, pad=(22, 12), bg=True):
        """Etiqueta tipo chip centrada en (x, y). bg: respaldo oscuro (legible sobre fondos claros)."""
        if a <= 0: return
        f = font(size, face)
        w = f.measureText(s)
        x0, x1 = x - w / 2 - pad[0], x + w / 2 + pad[0]
        y0, y1 = y - size * 0.5 - pad[1], y + size * 0.5 + pad[1]
        if bg:
            self.rect(x0, y0, x1, y1, C.BG, 0.88 * a, radius=(y1 - y0) / 2)
        self.rect(x0, y0, x1, y1, rgb, fill_a * a, radius=(y1 - y0) / 2)
        self.rect(x0, y0, x1, y1, rgb, 0.65 * a, stroke=2.5, radius=(y1 - y0) / 2)
        self.c.drawString(s, x - w / 2, y + size * 0.36, f, paint(rgb, a))

    # ---------- imágenes ----------
    def img(self, im: skia.Image, x0, y0, x1, y1, a=1.0, nearest=True):
        p = skia.Paint(); p.setAlphaf(clamp(a))
        self.c.drawImageRect(im, skia.Rect(x0, y0, x1, y1), NEAREST if nearest else LINEAR, p)

    def img_src(self, im: skia.Image, src, dst, a=1.0, nearest=True):
        p = skia.Paint(); p.setAlphaf(clamp(a))
        self.c.drawImageRect(im, skia.Rect(*src), skia.Rect(*dst),
                             NEAREST if nearest else LINEAR, p)

    # ---------- grafos ----------
    def node(self, x, y, r, fill=C.BG2, ring=C.WHITE, a=1.0, ring_w=4, label=None,
             label_rgb=C.WHITE, label_size=None, glow=0.0, face=C.FONT_BOLD):
        if a <= 0 or r <= 0: return
        if glow > 0:
            self.c.drawCircle(x, y, r * 1.9, paint(ring, 0.30 * glow * a, blur=r * 0.8))
        self.c.drawCircle(x, y, r, paint(fill, a))
        self.c.drawCircle(x, y, r, paint(ring, a, ring_w))
        if label:
            ls = label_size or r * 0.9
            self.text(label, x, y + ls * 0.36, ls, label_rgb, a, face=face)


def frame_surface():
    arr = np.zeros((C.H, C.W, 4), np.uint8)
    return arr, skia.Surface(arr)


# ---------------------------------------------------------------- extras cinematográficos
CUBIC = skia.SamplingOptions(skia.CubicResampler.Mitchell())
_small = {}


def _small_surface(scale):
    """Superficies reducidas (por proceso) para desenfoques baratos."""
    key = scale
    if key not in _small:
        w, h = int(C.W * scale), int(C.H * scale)
        _small[key] = (skia.Surface(w, h), skia.Surface(w, h))
    return _small[key]


def draw_blurred(Pmain, draw_fn, sigma, alpha=1.0, scale=0.25):
    """Dibuja draw_fn(P) desenfocado con sigma (px de pantalla).
    Se renderiza a 1/4 de resolución, se desenfoca allí y se escala con filtro lineal."""
    if sigma < 0.6:
        if alpha >= 0.999:
            draw_fn(Pmain)
        else:
            with Pmain.layer(alpha):
                draw_fn(Pmain)
        return
    s1, s2 = _small_surface(scale)
    c1 = s1.getCanvas(); c1.clear(skia.ColorTRANSPARENT)
    c1.save(); c1.scale(scale, scale); draw_fn(P(c1)); c1.restore()
    img = s1.makeImageSnapshot()
    c2 = s2.getCanvas(); c2.clear(skia.ColorTRANSPARENT)
    bp = skia.Paint(); bp.setImageFilter(skia.ImageFilters.Blur(sigma * scale, sigma * scale))
    c2.drawImage(img, 0, 0, LINEAR, bp)
    img2 = s2.makeImageSnapshot()
    p = skia.Paint(); p.setAlphaf(clamp(alpha))
    Pmain.c.drawImageRect(img2, skia.Rect(0, 0, C.W, C.H), LINEAR, p)


def vignette(Pp, strength=0.55):
    sh = skia.GradientShader.MakeRadial(
        (C.W / 2, C.H * 0.45), C.H * 0.75,
        [color4(C.BG, 0.0), color4(C.BG, 0.0), color4((0, 0, 0), strength)], [0.0, 0.55, 1.0])
    Pp.c.drawPaint(skia.Paint(Shader=sh))


def vband(Pp, y0, y1, a0, a1, rgb=C.BG):
    """Banda con degradado vertical (legibilidad de subtítulos / cabecera)."""
    sh = skia.GradientShader.MakeLinear([(0, y0), (0, y1)], [color4(rgb, a0), color4(rgb, a1)])
    Pp.c.drawRect(skia.Rect(0, y0, C.W, y1), skia.Paint(Shader=sh))


def spring(u, freq=9.0, damp=5.5):
    """Respuesta de resorte amortiguado 0→1 con leve rebote."""
    import math as _m
    if u <= 0: return 0.0
    return 1 - _m.exp(-damp * u) * _m.cos(freq * u)
