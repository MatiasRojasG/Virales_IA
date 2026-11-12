"""Recreación en Python del experimento de la clase (diapositivas 16-18).

Replica la lógica del código R de la clase:
  - documento binario (1 = tinta, 0 = papel)
  - el escáner invierte el 15 % de los píxeles
  - alpha = 0.5*log(0.85/0.15), beta = 1.2
  - 30 pasadas de la regla  lab <- (alpha*(2*obs-1) + beta*vecinos(lab) > 0)
    (actualización simultánea de todos los píxeles, igual que en el código R)
  - OCR con Tesseract (español) sobre el escaneo y sobre la restauración.

Los resultados de ESTA ejecución se guardan en results.json y son distintos de
los reportados en la clase (42 % -> 94 % de caracteres), que se citan como tales.
"""
from __future__ import annotations
import json, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
OUT = HERE / "build" / "experiment"
TEXT_LINES = ["Informe de operacion", "Turno nocturno del 14 de",
              "marzo. Sin fallas en la", "linea 3. Presion estable."]
FONT = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
NOISE = 0.15
SEED = 7
ALPHA = 0.5 * np.log(0.85 / 0.15)
BETA = 1.2
ITERS = 30


def make_document(font_px=42, pad=14, line_gap=1.18) -> np.ndarray:
    font = ImageFont.truetype(FONT, font_px)
    w = max(font.getbbox(t)[2] for t in TEXT_LINES) + 2 * pad
    h = int(len(TEXT_LINES) * font_px * line_gap + 2 * pad)
    img = Image.new("L", (w, h), 255)
    d = ImageDraw.Draw(img)
    for k, t in enumerate(TEXT_LINES):
        d.text((pad, pad + k * font_px * line_gap), t, font=font, fill=0)
    return (np.asarray(img) < 128).astype(np.int8)          # 1 = tinta


def neighbors_pm1(lab: np.ndarray) -> np.ndarray:
    """Suma de los 4 vecinos en escala -1/+1 (borde = 0), como vecinos() en R."""
    P = np.zeros((lab.shape[0] + 2, lab.shape[1] + 2))
    P[1:-1, 1:-1] = 2 * lab - 1
    return P[:-2, 1:-1] + P[2:, 1:-1] + P[1:-1, :-2] + P[1:-1, 2:]


def icm(obs: np.ndarray, alpha=ALPHA, beta=BETA, iters=ITERS):
    lab = obs.copy(); hist = [lab.copy()]
    for _ in range(iters):
        lab = ((alpha * (2 * obs - 1) + beta * neighbors_pm1(lab)) > 0).astype(np.int8)
        hist.append(lab.copy())
    return lab, hist


def levenshtein(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def ocr(img01: np.ndarray, scale=3) -> str:
    im = Image.fromarray(((1 - img01.astype(np.int32)) * 255).astype(np.uint8)).resize(
        (img01.shape[1] * scale, img01.shape[0] * scale), Image.NEAREST)
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "x.png"; im.save(p)
        r = subprocess.run(["tesseract", str(p), "-", "-l", "spa", "--psm", "6"],
                           capture_output=True, text=True)
    return r.stdout.strip()


def char_accuracy(txt: str) -> float:
    ref = " ".join(TEXT_LINES)
    hyp = " ".join(txt.split())
    return max(0.0, 1 - levenshtein(ref, hyp) / len(ref))


def save(img01, name, scale=1):
    im = Image.fromarray(((1 - img01.astype(np.int32)) * 255).astype(np.uint8))
    if scale > 1:
        im = im.resize((im.width * scale, im.height * scale), Image.NEAREST)
    im.save(OUT / name)


def beta_sweep(orig, obs, betas=(0.0, 0.3, 0.6, 1.2, 2.5, 5.0)):
    return {str(b): float((icm(obs, beta=b)[0] != orig).mean()) for b in betas}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    orig = make_document()
    rng = np.random.default_rng(SEED)
    noise = rng.random(orig.shape) < NOISE
    obs = np.where(noise, 1 - orig, orig).astype(np.int8)
    lab, hist = icm(obs)
    np.savez_compressed(OUT / "arrays.npz", orig=orig, obs=obs, noise=noise,
                        hist=np.stack(hist))
    for a, n in [(orig, "original.png"), (obs, "observado.png"), (lab, "restaurado.png")]:
        save(a, n, 3)
    t_obs, t_lab = ocr(obs), ocr(lab)
    res = {
        "shape": list(orig.shape), "noise": NOISE, "seed": SEED,
        "alpha": float(ALPHA), "beta": BETA, "iters": ITERS,
        "flipped_fraction": float(noise.mean()),
        "error_observed": float((obs != orig).mean()),
        "error_restored": float((lab != orig).mean()),
        "error_by_iter": [float((h != orig).mean()) for h in hist],
        "ocr_observed": t_obs, "ocr_restored": t_lab,
        "ocr_acc_observed": char_accuracy(t_obs),
        "ocr_acc_restored": char_accuracy(t_lab),
        "ocr_acc_original": char_accuracy(ocr(orig)),
        "beta_sweep_error": beta_sweep(orig, obs),
        "class_reported": {"error_observed": 0.15, "error_restored": 0.025,
                           "ocr_acc_observed": 0.42, "ocr_acc_restored": 0.94},
    }
    (OUT / "results.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in res.items() if k != "error_by_iter"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
