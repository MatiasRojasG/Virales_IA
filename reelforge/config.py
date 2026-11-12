from pathlib import Path
import skia

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "assets" / "fonts"

W, H, FPS = 1080, 1920, 30

# Zonas seguras para Reels/TikTok/Shorts (px). Arriba: barra de pestañas;
# abajo: descripción y botones; derecha: columna de acciones.
SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT, SAFE_RIGHT = 240, 1560, 70, 960
SUB_Y = 1390          # línea base central de los subtítulos

def hex2rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

BG = hex2rgb("#090D18")
BG2 = hex2rgb("#111A2E")
WHITE = (1.0, 1.0, 1.0)
GRAY = hex2rgb("#8A94AD")
DIM = hex2rgb("#3A4560")
CYAN = hex2rgb("#00D9FF")
VIOLET = hex2rgb("#9B6BFF")
PINK = hex2rgb("#FF4D8D")       # errores / alertas (uso mínimo)
GREEN = hex2rgb("#3DF5A7")      # éxito (uso mínimo)
PAPER = hex2rgb("#E9EEF7")
INK = hex2rgb("#0B1020")

_tf_cache = {}
def typeface(name="Inter-SemiBold.otf"):
    if name not in _tf_cache:
        _tf_cache[name] = skia.Typeface.MakeFromFile(str(FONTS / name))
    return _tf_cache[name]

FONT_REG = "Inter-Regular.otf"
FONT_MED = "Inter-Medium.otf"
FONT_SEMI = "Inter-SemiBold.otf"
FONT_BOLD = "Inter-Bold.otf"
FONT_XBOLD = "Inter-ExtraBold.otf"
FONT_BLACK = "Inter-Black.otf"
FONT_MONO = "JetBrainsMono-Regular.ttf"
FONT_MONO_B = "JetBrainsMono-Bold.ttf"
