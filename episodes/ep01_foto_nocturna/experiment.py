"""Simulación del episodio «La foto nocturna».

1. Genera una escena nocturna sintética (cielo, edificios, ventanas, farol, letrero).
2. Simula una foto con poca luz: cada punto del sensor recibe pocos fotones (ruido de Poisson).
3. Restaura con un campo aleatorio de Markov (4 vecinos):
       E(x) = Σ_i (x_i − y_i)²  +  β Σ_{i~j} ρ(x_i − x_j)
   - término de datos: desacuerdo con lo que vio la cámara (resorte hacia y_i)
   - término de vecinos: desacuerdo entre vecinos (resortes entre puntos)
   - ρ cuadrática  → "solo promediar": borra bordes
   - ρ robusta (Lorentziana): el resorte "se suelta" si los vecinos son muy distintos
   La minimización es local e iterativa (cada punto toma el valor que minimiza su
   energía dados sus vecinos, todos a la vez, como en el código de la clase).
   P(x | y) ∝ exp(−E(x)): la foto de menor energía es la más probable.

Es una ilustración: los celulares reales combinan varias tomas y redes neuronales.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).parent
OUT = HERE / "build" / "experiment"
ROOT = HERE.parent.parent
W, H = 360, 640
PHOTONS = 6           # fotones que recibe un punto blanco puro (muy poca luz)
SEED = 3


def scene(scale=3):
    w, h = W * scale, H * scale
    rng = np.random.default_rng(1)
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    # cielo
    for y in range(h):
        u = y / h
        c = (int(10 + 30 * u), int(14 + 20 * u), int(40 + 45 * u))
        d.line([(0, y), (w, y)], fill=c)
    for _ in range(70):
        x, y = rng.integers(0, w), rng.integers(0, int(h * 0.35))
        r = rng.integers(2, 5); d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 210, 255))
    # luna
    mx, my, mr = int(w * 0.76), int(h * 0.12), int(w * 0.075)
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(245, 240, 215))
    # edificios
    blds = [(-20, 0.36, 0.30, (34, 38, 56)), (0.25, 0.28, 0.22, (28, 31, 48)),
            (0.45, 0.42, 0.28, (40, 36, 52)), (0.70, 0.32, 0.36, (30, 34, 50))]
    for x0, top, wd, col in blds:
        X0 = int(x0 * w) if x0 >= 0 else x0 * scale
        X1 = X0 + int(wd * w); Y0 = int(top * h)
        d.rectangle([X0, Y0, X1, h], fill=col)
        for yy in range(Y0 + 30 * scale // 3, int(h * 0.62), 26 * scale // 3 * 2):
            for xx in range(X0 + 12 * scale // 3 * 2, X1 - 20, 22 * scale // 3 * 2):
                if rng.random() < 0.45:
                    d.rectangle([xx, yy, xx + 9 * scale, yy + 13 * scale], fill=(255, 196, 110))
                else:
                    d.rectangle([xx, yy, xx + 9 * scale, yy + 13 * scale], fill=(18, 20, 30))
    # fachada baja con muro parejo (zona para mostrar el ruido)
    d.rectangle([0, int(h * 0.62), w, h], fill=(70, 62, 66))
    # tienda con letrero luminoso
    sx0, sy0, sx1, sy1 = int(w * 0.10), int(h * 0.655), int(w * 0.90), int(h * 0.715)
    d.rounded_rectangle([sx0, sy0, sx1, sy1], radius=8 * scale, fill=(12, 30, 34))
    f = ImageFont.truetype(str(ROOT / "assets/fonts/Inter-Black.otf"), 25 * scale)
    txt = "FARMACIA"
    tw = d.textlength(txt, font=f)
    d.text(((sx0 + sx1) / 2 - tw / 2, sy0 + 3 * scale), txt, font=f, fill=(120, 255, 200))
    # vitrina y puerta
    d.rectangle([int(w * 0.12), int(h * 0.75), int(w * 0.55), int(h * 0.86)], fill=(150, 175, 160))
    d.rectangle([int(w * 0.62), int(h * 0.75), int(w * 0.82), int(h * 0.90)], fill=(25, 22, 26))
    # vereda / calle
    d.rectangle([0, int(h * 0.90), w, h], fill=(36, 36, 44))
    for k in range(6):
        x = int(w * (0.05 + 0.18 * k)); d.rectangle([x, int(h * 0.95), x + 30 * scale, int(h * 0.955)], fill=(150, 140, 110))
    # farol
    lx = int(w * 0.92)
    d.rectangle([lx - 3 * scale, int(h * 0.50), lx + 3 * scale, h], fill=(20, 20, 26))
    d.ellipse([lx - 12 * scale, int(h * 0.49) - 12 * scale, lx + 12 * scale, int(h * 0.49) + 12 * scale], fill=(255, 225, 150))
    img = img.resize((W, H), Image.LANCZOS)
    a = np.asarray(img).astype(np.float32) / 255
    # halos de luz
    glow = Image.fromarray((np.clip(a - 0.55, 0, 1) * 2 * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))
    a = np.clip(a + np.asarray(glow).astype(np.float32) / 255 * 0.55, 0, 1)
    return a


def luminance(a):
    return a @ np.array([0.299, 0.587, 0.114], np.float32)


def shoot(clean, photons=PHOTONS, seed=SEED, return_counts=False):
    """Foto con poca luz: cada punto cuenta fotones al azar (ruido de Poisson sobre el brillo),
    más un poco de ruido de color y de lectura del sensor."""
    rng = np.random.default_rng(seed)
    L = luminance(clean)
    counts = rng.poisson(L * photons)
    Ln = (counts + rng.normal(0, 0.35, L.shape)) / photons
    chroma = clean / np.maximum(L, 0.02)[..., None]
    noisy = chroma * Ln[..., None] + rng.normal(0, 0.025, clean.shape)
    noisy = np.clip(noisy, 0, 1).astype(np.float32)
    return (noisy, counts) if return_counts else noisy


def mrf(y, beta, delta=None, iters=40, keep=(), R=2, sig=1.2):
    """Minimiza E por actualizaciones locales simultáneas sobre un vecindario de (2R+1)²
    (peso espacial gaussiano). delta=None → ρ cuadrática (resortes que nunca se sueltan);
    con delta, el peso cae si los vecinos son muy distintos (resorte que se suelta)."""
    x = y.copy(); hist = {}; H, W, _ = y.shape
    offs = [(dy, dx, np.exp(-(dy * dy + dx * dx) / (2 * sig * sig)))
            for dy in range(-R, R + 1) for dx in range(-R, R + 1) if (dy, dx) != (0, 0)]
    for it in range(1, iters + 1):
        P = np.pad(x, ((R, R), (R, R), (0, 0)), mode="edge")
        # «qué tan distinto es el vecino» se mide sobre una guía con mediana 3×3 (respeta bordes):
        # así un punto suelto (ruido) no puede soltar sus propios resortes y protegerse.
        from scipy.ndimage import median_filter
        L = median_filter(x.mean(2), size=3)
        LP = np.pad(L, R, mode="edge")
        num = y.copy(); den = np.ones((H, W, 1), np.float32)
        for dy, dx, ws in offs:
            nb = P[R + dy:R + dy + H, R + dx:R + dx + W]
            if delta is None:
                w = np.full((H, W, 1), ws, np.float32)
            else:
                d = (L - LP[R + dy:R + dy + H, R + dx:R + dx + W])[..., None]
                w = ws / (1.0 + (d / delta) ** 2)
            num += beta * w * nb; den += beta * w
        x = num / den
        if it in keep: hist[it] = x.copy()
    return x, hist


def energy(x, y, beta, delta):
    e = ((x - y) ** 2).sum()
    for dx, dy in ((1, 0), (0, 1)):
        d = (x[dy:, dx:] - x[:x.shape[0] - dy, :x.shape[1] - dx]).mean(axis=2)
        e += beta * (delta ** 2 * np.log1p((d / delta) ** 2)).sum()
    return float(e)


def psnr(a, b):
    return float(10 * np.log10(1 / ((a - b) ** 2).mean()))


def save(a, name):
    Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).save(OUT / name)


BETA, DELTA, ITERS = 3.0, 0.08, 20
BETA_BLUR = 60.0      # "solo promediar": vecinos con mucho peso y resortes que nunca se sueltan


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    clean = scene()
    noisy, counts = shoot(clean, return_counts=True)
    keep = (1, 2, 3, 4, 6, 9, 13, 20)
    good, hist = mrf(noisy, BETA, DELTA, ITERS, keep=keep)
    blur, _ = mrf(noisy, 8.0, None, 60, R=2, sig=1.5)
    weak, _ = mrf(noisy, 0.4, DELTA, 8)
    np.savez_compressed(OUT / "arrays.npz", clean=clean, noisy=noisy, counts=counts, good=good, blur=blur, weak=weak,
                        **{f"it{k}": v for k, v in hist.items()})
    for a, n in [(clean, "escena.png"), (noisy, "foto_ruido.png"), (good, "restaurada.png"),
                 (blur, "solo_promediar.png"), (weak, "poco_vecinos.png")]:
        save(a, n)
    res = {"W": W, "H": H, "photons": PHOTONS, "beta": BETA, "delta": DELTA, "iters": ITERS,
           "beta_blur": BETA_BLUR,
           "psnr_noisy": psnr(noisy, clean), "psnr_good": psnr(good, clean),
           "psnr_blur": psnr(blur, clean), "psnr_weak": psnr(weak, clean),
           "psnr_by_iter": {k: psnr(v, clean) for k, v in hist.items()},
           "energy_noisy": energy(noisy, noisy, BETA, DELTA), "energy_good": energy(good, noisy, BETA, DELTA),
           "combinaciones_12MP_log10": 12e6 * np.log10(256)}
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
