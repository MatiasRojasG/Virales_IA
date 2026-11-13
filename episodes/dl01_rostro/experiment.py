"""Experimento real del episodio «¿Cómo sabe tu celular que eres tú?».

1. Genera rostros sintéticos de 8 personas (geometría propia de cada una) con variaciones
   que NO cambian la identidad: peinado, lentes, luz, expresión, pequeños desplazamientos.
2. Muestra por qué comparar píxeles falla: una foto tuya con otra luz puede diferir más
   de tu foto base que la foto de otra persona.
3. Entrena desde cero (NumPy, descenso de gradiente con Adam) un perceptrón multicapa:
   32×32 píxeles → 128 neuronas → 32 neuronas («huella») → 8 personas.
   Se registra la pérdida (entropía cruzada) en cada época.
4. Proyecta en 2D (PCA) los píxeles y las huellas de fotos de prueba para comparar.
5. Prueba con una combinación de look que la red nunca vio en entrenamiento.

Es una ilustración: los sistemas reales de desbloqueo facial usan sensores (p. ej. de
profundidad), datos y redes propias de cada fabricante.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).parent
OUT = HERE / "build" / "experiment"
NP_ = 8
rng_global = np.random.default_rng(0)
PEOPLE = []
for k in range(NP_):
    r = np.random.default_rng(100 + k)
    PEOPLE.append(dict(
        fw=r.uniform(0.30, 0.40), fh=r.uniform(0.40, 0.48),
        eye_dx=r.uniform(0.13, 0.20), eye_y=r.uniform(-0.04, 0.04), eye_r=r.uniform(0.035, 0.055),
        nose=r.uniform(0.08, 0.16), mouth_w=r.uniform(0.08, 0.17), mouth_y=r.uniform(0.18, 0.25),
        brow=r.uniform(-0.25, 0.25), skin=r.uniform(0.55, 0.9), jaw=r.uniform(0.0, 1.0)))


def render(pid, hair=0, glasses=0, light=(0.0, 0.0), smile=0.0, dx=0.0, dy=0.0, size=128, color=False):
    p = PEOPLE[pid]
    S = size * 2
    img = Image.new("RGB", (S, S), (40, 44, 60))
    d = ImageDraw.Draw(img)
    cx, cy = S * (0.5 + dx), S * (0.52 + dy)
    sk = p["skin"]
    skin = (int(235 * sk), int(190 * sk), int(160 * sk))
    hair_c = (35, 28, 25)
    fw, fh = p["fw"] * S, p["fh"] * S
    # pelo largo detrás
    if hair == 2:
        d.rounded_rectangle([cx - fw * 1.15, cy - fh * 1.05, cx + fw * 1.15, cy + fh * 0.9], radius=int(fw * 0.9), fill=hair_c)
    # cara (mandíbula más o menos angulosa)
    d.ellipse([cx - fw, cy - fh, cx + fw, cy + fh], fill=skin)
    if p["jaw"] > 0.5:
        d.rectangle([cx - fw * 0.85, cy, cx + fw * 0.85, cy + fh * 0.75], fill=skin)
    # cuello
    d.rectangle([cx - fw * 0.35, cy + fh * 0.8, cx + fw * 0.35, S], fill=skin)
    # pelo
    if hair == 1:      # corto
        d.chord([cx - fw * 1.05, cy - fh * 1.12, cx + fw * 1.05, cy - fh * 0.05], 180, 360, fill=hair_c)
    elif hair == 2:    # largo
        d.chord([cx - fw * 1.08, cy - fh * 1.15, cx + fw * 1.08, cy - fh * 0.1], 180, 360, fill=hair_c)
    elif hair == 3:    # chasquilla
        d.chord([cx - fw * 1.05, cy - fh * 1.12, cx + fw * 1.05, cy + fh * 0.1], 180, 360, fill=hair_c)
        d.rectangle([cx - fw * 0.8, cy - fh * 0.6, cx + fw * 0.5, cy - fh * 0.32], fill=hair_c)
    ey = cy + p["eye_y"] * S - fh * 0.12
    for sgn in (-1, 1):
        ex = cx + sgn * p["eye_dx"] * S
        er = p["eye_r"] * S
        d.ellipse([ex - er * 1.4, ey - er, ex + er * 1.4, ey + er], fill=(245, 245, 245))
        d.ellipse([ex - er * 0.7, ey - er * 0.7, ex + er * 0.7, ey + er * 0.7], fill=(30, 25, 25))
        # cejas
        by = ey - er * 2.0
        d.line([ex - er * 1.6, by + sgn * p["brow"] * er * 2, ex + er * 1.6, by - sgn * p["brow"] * er * 2],
               fill=hair_c, width=max(2, int(S * 0.018)))
        if glasses:
            d.ellipse([ex - er * 2.4, ey - er * 2.0, ex + er * 2.4, ey + er * 2.0], outline=(20, 20, 20), width=max(2, int(S * 0.014)))
    if glasses:
        d.line([cx - p["eye_dx"] * S + p["eye_r"] * S * 2.4, ey, cx + p["eye_dx"] * S - p["eye_r"] * S * 2.4, ey],
               fill=(20, 20, 20), width=max(2, int(S * 0.012)))
    # nariz
    ny = ey + p["nose"] * S
    d.line([cx, ey + S * 0.02, cx - S * 0.03, ny], fill=(int(skin[0] * .7), int(skin[1] * .7), int(skin[2] * .7)), width=max(2, int(S * .014)))
    d.line([cx - S * 0.03, ny, cx + S * 0.02, ny], fill=(int(skin[0] * .7), int(skin[1] * .7), int(skin[2] * .7)), width=max(2, int(S * .014)))
    # boca
    my = cy + p["mouth_y"] * S
    mw = p["mouth_w"] * S
    d.arc([cx - mw, my - S * 0.04 - smile * S * 0.03, cx + mw, my + S * 0.04 + smile * S * 0.05], 10, 170,
          fill=(150, 60, 60), width=max(2, int(S * 0.016)))
    img = img.resize((size, size), Image.LANCZOS)
    a = np.asarray(img).astype(np.float32) / 255
    # iluminación: gradiente direccional
    yy, xx = np.mgrid[0:size, 0:size] / size - 0.5
    g = 1 + light[0] * xx * 2 + light[1] * yy * 2
    a = np.clip(a * g[..., None], 0, 1)
    return a if color else a.mean(axis=2)


def sample_variation(rng, holdout=False):
    hair = int(rng.integers(0, 4)); glasses = int(rng.random() < 0.4)
    light = (rng.uniform(-0.9, 0.9), rng.uniform(-0.5, 0.5))
    smile = rng.uniform(-0.3, 1.0); dx, dy = rng.uniform(-0.04, 0.04, 2)
    return dict(hair=hair, glasses=glasses, light=light, smile=smile, dx=dx, dy=dy)


def dataset(n_per, seed, exclude=None):
    rng = np.random.default_rng(seed)
    X, Y, V = [], [], []
    for pid in range(NP_):
        k = 0
        while k < n_per:
            v = sample_variation(rng)
            # combinación reservada para la prueba: persona 0 con chasquilla + lentes
            if exclude and pid == 0 and v["hair"] == 3 and v["glasses"] == 1:
                continue
            X.append(render(pid, size=32, **v).ravel()); Y.append(pid); V.append(v); k += 1
    X = np.array(X, np.float32); Y = np.array(Y)
    return X, Y, V


def relu(z): return np.maximum(z, 0)


def train(X, Y, epochs=60, lr=2e-3, seed=0):
    rng = np.random.default_rng(seed)
    mu, sd = X.mean(0), X.std(0) + 1e-3
    Xn = (X - mu) / sd
    sizes = [X.shape[1], 128, 32, NP_]
    W = [rng.normal(0, np.sqrt(2 / sizes[i]), (sizes[i], sizes[i + 1])).astype(np.float32) for i in range(3)]
    b = [np.zeros(sizes[i + 1], np.float32) for i in range(3)]
    params = W + b
    m = [np.zeros_like(p) for p in params]; v = [np.zeros_like(p) for p in params]
    losses = []; step_losses = []; step = 0
    for ep in range(epochs):
        idx = rng.permutation(len(X)); tot = 0
        for s in range(0, len(X), 64):
            bi = idx[s:s + 64]; x = Xn[bi]; y = Y[bi]
            z1 = x @ W[0] + b[0]; h1 = relu(z1)
            z2 = h1 @ W[1] + b[1]; h2 = relu(z2)
            z3 = h2 @ W[2] + b[2]
            z3 -= z3.max(1, keepdims=True); pr = np.exp(z3); pr /= pr.sum(1, keepdims=True)
            loss = -np.log(pr[np.arange(len(y)), y] + 1e-9).mean(); tot += loss * len(y); step_losses.append(float(loss))
            g3 = pr; g3[np.arange(len(y)), y] -= 1; g3 /= len(y)
            gW2 = h2.T @ g3; gb2 = g3.sum(0)
            g2 = (g3 @ W[2].T) * (z2 > 0); gW1 = h1.T @ g2; gb1 = g2.sum(0)
            g1 = (g2 @ W[1].T) * (z1 > 0); gW0 = x.T @ g1; gb0 = g1.sum(0)
            grads = [gW0, gW1, gW2, gb0, gb1, gb2]
            step += 1
            for i, (p, g) in enumerate(zip(params, grads)):
                m[i] = 0.9 * m[i] + 0.1 * g; v[i] = 0.999 * v[i] + 0.001 * g * g
                p -= lr * (m[i] / (1 - 0.9 ** step)) / (np.sqrt(v[i] / (1 - 0.999 ** step)) + 1e-8)
        losses.append(float(tot / len(X)))
    model = dict(W=W, b=b, mu=mu, sd=sd, step_losses=step_losses)
    return model, losses


def embed(model, X):
    x = (X - model["mu"]) / model["sd"]
    h1 = relu(x @ model["W"][0] + model["b"][0])
    return relu(h1 @ model["W"][1] + model["b"][1])


def predict(model, X):
    h2 = embed(model, X)
    return (h2 @ model["W"][2] + model["b"][2]).argmax(1)


def pca2(Z):
    Zc = Z - Z.mean(0)
    U, S, Vt = np.linalg.svd(Zc, full_matrices=False)
    P = Zc @ Vt[:2].T
    return P / np.abs(P).max(0)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    Xtr, Ytr, _ = dataset(220, seed=1, exclude=True)
    Xte, Yte, Vte = dataset(30, seed=2, exclude=True)
    model, losses = train(Xtr, Ytr)
    acc = float((predict(model, Xte) == Yte).mean())
    # foto nueva: persona 0 con chasquilla + lentes + luz lateral (combinación nunca vista)
    v_new = dict(hair=3, glasses=1, light=(0.8, -0.2), smile=0.6, dx=0.01, dy=0.0)
    x_new = render(0, size=32, **v_new).ravel()[None]
    pred_new = int(predict(model, x_new)[0])
    # comparación de píxeles (en 32x32, lo que ve la red)
    base = dict(hair=1, glasses=0, light=(0, 0), smile=0.2, dx=0, dy=0)
    a0 = render(0, size=32, **base); a_new = render(0, size=32, **v_new)
    b0 = render(3, size=32, **base)
    d_self = float(np.abs(a_new - a0).mean()); d_other = float(np.abs(b0 - a0).mean())
    ch_self = float((np.abs(a_new - a0) > 0.05).mean()); ch_other = float((np.abs(b0 - a0) > 0.05).mean())
    # proyecciones 2D: píxeles vs huellas
    E = embed(model, np.vstack([Xte, x_new]))
    Ppix = pca2(np.vstack([Xte, x_new])); Pemb = pca2(E)
    # vecino más cercano por huella / por píxeles para la foto nueva
    nn_emb = int(Yte[np.argmin(((E[:-1] - E[-1]) ** 2).sum(1))])
    Xall = np.vstack([Xte, x_new]); nn_pix = int(Yte[np.argmin(((Xall[:-1] - Xall[-1]) ** 2).sum(1))])
    np.savez_compressed(OUT / "arrays.npz", Ppix=Ppix, Pemb=Pemb, Yte=Yte, losses=np.array(losses), step_losses=np.array(model["step_losses"]))
    # imágenes de alta resolución para el video
    faces = {"base": render(0, size=256, color=True, **base),
             "new": render(0, size=256, color=True, **v_new),
             "other": render(3, size=256, color=True, **base)}
    for k, im in faces.items():
        Image.fromarray((im * 255).astype(np.uint8)).save(OUT / f"cara_{k}.png")
    emb3 = embed(model, np.stack([a0.ravel(), a_new.ravel(), b0.ravel()]).astype(np.float32))
    np.savez_compressed(OUT / "faces.npz", **faces, base32=a0, new32=a_new, other32=b0, emb3=emb3)
    grid = []
    for pid in range(NP_):
        row = [render(pid, size=64, color=True, **sample_variation(np.random.default_rng(50 + pid * 7 + j))) for j in range(4)]
        grid.append(np.hstack(row))
    Image.fromarray((np.vstack(grid) * 255).astype(np.uint8)).save(OUT / "dataset_muestra.png")
    res = dict(n_train=int(len(Xtr)), n_test=int(len(Xte)), test_accuracy=acc, losses=losses,
               new_photo_pred=pred_new, new_photo_nn_emb=nn_emb, new_photo_nn_pix=nn_pix,
               pixel_diff_self=d_self, pixel_diff_other=d_other,
               changed_frac_self=ch_self, changed_frac_other=ch_other,
               params=int(sum(w.size for w in model["W"]) + sum(bb.size for bb in model["b"])))
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    print(json.dumps({k: v for k, v in res.items() if k != "losses"}, indent=2), "\nloss:", [round(l, 3) for l in losses[::6]])


if __name__ == "__main__":
    main()
