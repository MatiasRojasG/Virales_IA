"""Subtítulos karaoke incrustados: palabra actual resaltada, palabras clave en cyan."""
from __future__ import annotations
from . import config as C
from .draw import font, paint
from .ease import clamp, out_back, out_cubic

SIZE = 66
FACE = C.FONT_XBOLD
LINE_H = 84


def measure(s):
    f = font(SIZE, FACE)
    return f.measureText(s) + f.measureText(" ") * 0.5 * s.count(" ")


def draw(P, chunks, t, y=C.SUB_Y, a_global=1.0):
    ch = next((c for c in chunks if c["start"] - 0.02 <= t < c["end"]), None)
    if ch is None: return
    f = font(SIZE, FACE)
    toks = ch["tokens"]
    u_in = clamp((t - ch["start"]) / 0.16)
    s_in = 0.9 + 0.1 * out_back(u_in)
    a_in = out_cubic(u_in) * a_global
    nl = len(ch["lines"])
    y0 = y - (nl - 1) * LINE_H / 2
    sp = f.measureText(" ") * 1.5          # espacio generoso: la palabra activa crece sin pisar a la vecina
    cv = P.c
    cv.save(); cv.translate(C.W / 2, y); cv.scale(s_in, s_in); cv.translate(-C.W / 2, -y)
    for li, (i0, i1) in enumerate(ch["lines"]):
        words = toks[i0:i1]
        wd = sum(f.measureText(w.display) for w in words) + sp * (len(words) - 1)
        x = C.W / 2 - wd / 2
        yy = y0 + li * LINE_H + SIZE * 0.36
        for w in words:
            ww = f.measureText(w.display)
            spoken = t >= w.start
            current = w.start <= t < max(w.end, w.start + 0.12)
            rgb = C.CYAN if w.kw else C.WHITE
            alpha = (1.0 if spoken else 0.42) * a_in
            pop = 1.0
            if current:
                pop = 1.0 + 0.04 * (1 - clamp((t - w.start) / 0.25))
            cx = x + ww / 2
            cv.save(); cv.translate(cx, yy - SIZE * 0.35); cv.scale(pop, pop); cv.translate(-cx, -(yy - SIZE * 0.35))
            # contorno oscuro + sombra para legibilidad sobre cualquier fondo
            cv.drawString(w.display, x, yy + 5, f, paint(C.BG, 0.9 * alpha, blur=9))
            cv.drawString(w.display, x, yy, f, paint(C.BG, 0.95 * alpha, stroke=10))
            if w.kw and spoken:
                cv.drawString(w.display, x, yy, f, paint(C.CYAN, 0.45 * alpha, blur=14))
            cv.drawString(w.display, x, yy, f, paint(rgb, alpha))
            cv.restore()
            x += ww + sp
    cv.restore()
