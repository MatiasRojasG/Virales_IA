"""Ecuaciones vectoriales sin instalar LaTeX.

Usa el motor mathtext de matplotlib (subconjunto de LaTeX) para obtener los
contornos de los glifos y los convierte en skia.Path. Cada ecuación se arma
por partes para poder colorear, revelar y resaltar términos por separado.

    eq = Equation([r"P(y\\mid x)", r"\\propto", r"\\exp\\{", (r"\\alpha", "cyan"), ...])
    eq.draw(p, cx, cy, size=70, reveal=0.6, colors={3: CYAN})
"""
from __future__ import annotations
import matplotlib
matplotlib.use("Agg")
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MPath
import matplotlib as mpl
import skia
from . import config as C
from .draw import paint
from .ease import clamp, out_cubic, lerp_c

mpl.rcParams["mathtext.fontset"] = "cm"
_PROP = FontProperties(family="DejaVu Sans")
_UNIT = 100.0  # tamaño de referencia de TextPath


def _to_skia(tp: TextPath) -> skia.Path:
    sp = skia.Path()
    verts, codes = tp.vertices, tp.codes
    i = 0
    while i < len(verts):
        c = codes[i]; x, y = verts[i]
        if c == MPath.MOVETO:
            sp.moveTo(x, -y); i += 1
        elif c == MPath.LINETO:
            sp.lineTo(x, -y); i += 1
        elif c == MPath.CURVE3:
            (x2, y2) = verts[i + 1]; sp.quadTo(x, -y, x2, -y2); i += 2
        elif c == MPath.CURVE4:
            (x2, y2), (x3, y3) = verts[i + 1], verts[i + 2]
            sp.cubicTo(x, -y, x2, -y2, x3, -y3); i += 3
        elif c == MPath.CLOSEPOLY:
            sp.close(); i += 1
        else:
            i += 1
    return sp


class Equation:
    def __init__(self, parts, gap=0.18):
        """parts: lista de str (mathtext sin $) o (str, rgb)."""
        self.parts, self.colors = [], []
        x = 0.0
        self.paths, self.offsets, self.widths = [], [], []
        ymin, ymax = 0.0, 0.0
        for p in parts:
            s, col = (p, C.WHITE) if isinstance(p, str) else p
            tp = TextPath((0, 0), f"${s}$", size=_UNIT, prop=_PROP)
            ext = tp.get_extents()
            sk = _to_skia(tp)
            self.paths.append(sk)
            self.offsets.append(x - ext.x0)
            self.widths.append(ext.width)
            self.colors.append(col)
            x += ext.width + gap * _UNIT
            ymin, ymax = min(ymin, -ext.y1), max(ymax, -ext.y0)
        self.width = x - gap * _UNIT
        self.top, self.bottom = ymin, ymax  # en unidades, y hacia abajo

    def part_center(self, i, cx, cy, size):
        """Centro (x, y) en pantalla de la parte i (para anclar flechas/etiquetas)."""
        k = size / _UNIT
        x0 = cx - self.width * k / 2
        return (x0 + (self.offsets[i] + self.widths[i] / 2) * k,
                cy + (self.top + self.bottom) / 2 * k)

    def draw(self, P, cx, cy, size=72, a=1.0, reveal=1.0, colors=None, glow=None,
             rise=28, highlight=None, part_prog=None):
        """reveal ∈ [0,1] muestra progresivamente las partes (fade + subida).
        colors: dict índice -> rgb (sobrescribe). glow: dict índice -> intensidad.
        highlight: dict índice -> (rgb, intensidad) para fondo resaltado."""
        if a <= 0: return
        k = size / _UNIT
        n = len(self.paths)
        x0 = cx - self.width * k / 2
        ybase = cy - (self.top + self.bottom) / 2 * k
        for i, sp in enumerate(self.paths):
            # cada parte aparece escalonada
            if part_prog is not None:
                u = out_cubic(clamp(part_prog[i]))
            else:
                u = out_cubic(clamp(reveal * n - i * 0.75) if reveal < 1 else 1.0)
            if u <= 0: continue
            col = (colors or {}).get(i, self.colors[i])
            cv = P.c
            if highlight and i in highlight:
                hc, hi = highlight[i]
                if hi > 0:
                    px0 = x0 + (self.offsets[i] - 0.1 * _UNIT) * k
                    px1 = x0 + (self.offsets[i] + self.widths[i] + 0.1 * _UNIT) * k
                    P.rect(px0, ybase + self.top * k - 12, px1, ybase + self.bottom * k + 12,
                           hc, 0.16 * hi * a, radius=14)
            cv.save()
            cv.translate(x0 + self.offsets[i] * k, ybase + (1 - u) * rise)
            cv.scale(k, k)
            g = (glow or {}).get(i, 0)
            if g > 0:
                cv.drawPath(sp, paint(col, 0.6 * g * a * u, blur=8 / k))
            cv.drawPath(sp, paint(col, a * u))
            cv.restore()
