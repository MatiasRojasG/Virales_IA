"""Experimento real: sobreajuste y dropout (datos simulados).

Cada punto es un día simulado: (humedad, presión) → ¿llovió? La regla verdadera es una curva
suave, pero el 15 % de los días tiene la etiqueta invertida («días raros»).
Se entrenan dos MLP idénticos (2 → 256 → 256 → 1, ReLU, Adam, lote completo):
  - sin dropout
  - con dropout p = 0,5 en ambas capas ocultas (solo durante el entrenamiento; al predecir
    se usan todas las neuronas, con la escala estándar de «inverted dropout»).
Se mide la exactitud en los días conocidos (entrenamiento) y en 5.000 días nuevos generados
con la misma regla y el mismo ruido. Se repite con varias semillas para no depender de una corrida.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "build" / "experiment"
NOISE = 0.15


def true_rule(X):
    h, p = X[:, 0], X[:, 1]                       # ambas en [-1, 1] (humedad, presión normalizadas)
    return (h - 0.35 * np.sin(2.2 * p) - 0.25 * p > 0.05).astype(float)


def make(n, rng):
    X = rng.uniform(-1, 1, (n, 2))
    y = true_rule(X)
    flip = rng.random(n) < NOISE
    return X, np.where(flip, 1 - y, y), flip


def init(rng, sizes=(2, 256, 256, 1)):
    W = [rng.normal(0, np.sqrt(2 / a), (a, b)) for a, b in zip(sizes[:-1], sizes[1:])]
    b = [np.zeros(s) for s in sizes[1:]]
    return W, b


def forward(W, b, X, p_drop=0.0, rng=None):
    h = X; masks = []; acts = [X]
    for i in range(len(W) - 1):
        z = h @ W[i] + b[i]; h = np.maximum(z, 0)
        if p_drop > 0 and rng is not None:
            m = (rng.random(h.shape) > p_drop) / (1 - p_drop); h = h * m; masks.append(m)
        else:
            masks.append(None)
        acts.append(h)
    out = 1 / (1 + np.exp(-(h @ W[-1] + b[-1])))
    return out[:, 0], acts, masks


def train(X, y, p_drop, seed, epochs=4000, lr=3e-3, snaps=(), width=256):
    rng = np.random.default_rng(seed)
    W, b = init(rng, (2, width, width, 1))
    params = W + b
    m = [np.zeros_like(q) for q in params]; v = [np.zeros_like(q) for q in params]
    hist = {}; losses = []
    for ep in range(1, epochs + 1):
        o, acts, masks = forward(W, b, X, p_drop, rng)
        losses.append(float(-np.mean(y * np.log(o + 1e-9) + (1 - y) * np.log(1 - o + 1e-9))))
        g = ((o - y) / len(y))[:, None]
        gW, gb = [None] * len(W), [None] * len(W)
        for i in range(len(W) - 1, -1, -1):
            gW[i] = acts[i].T @ g; gb[i] = g.sum(0)
            if i > 0:
                g = (g @ W[i].T) * (acts[i] > 0)
                if masks[i - 1] is not None: g = g * masks[i - 1]
        grads = gW + gb
        for k, (q, gg) in enumerate(zip(params, grads)):
            m[k] = 0.9 * m[k] + 0.1 * gg; v[k] = 0.999 * v[k] + 0.001 * gg * gg
            q -= lr * (m[k] / (1 - 0.9 ** ep)) / (np.sqrt(v[k] / (1 - 0.999 ** ep)) + 1e-8)
        if ep in snaps: hist[ep] = grid_prob(W, b)
    return (W, b), losses, hist


def grid_prob(W, b, n=140):
    u = np.linspace(-1, 1, n); X, Y = np.meshgrid(u, u)
    return forward(W, b, np.stack([X.ravel(), Y.ravel()], 1))[0].reshape(n, n)


def acc(model, X, y):
    return float(((forward(*model, X)[0] > 0.5) == y).mean())


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    snaps = (1, 25, 100, 300, 800, 1600, 4000)
    for seed in range(5):
        rng = np.random.default_rng(100 + seed)
        Xtr, ytr, ftr = make(150, rng)
        Xte, yte, _ = make(5000, rng)
        A, la, ha = train(Xtr, ytr, 0.0, seed, snaps=snaps if seed == 0 else ())
        B, lb, hb = train(Xtr, ytr, 0.5, seed, snaps=snaps if seed == 0 else ())
        r = dict(seed=seed, train_nodrop=acc(A, Xtr, ytr), test_nodrop=acc(A, Xte, yte),
                 train_drop=acc(B, Xtr, ytr), test_drop=acc(B, Xte, yte),
                 test_bayes=float((true_rule(Xte) == yte).mean()))
        rows.append(r); print(r)
        if seed == 0:
            np.savez_compressed(OUT / "arrays.npz", Xtr=Xtr, ytr=ytr, ftr=ftr,
                                **{f"A{k}": v for k, v in ha.items()}, **{f"B{k}": v for k, v in hb.items()},
                                la=np.array(la), lb=np.array(lb),
                                true=true_rule(np.stack([g.ravel() for g in np.meshgrid(np.linspace(-1, 1, 140), np.linspace(-1, 1, 140))], 1)).reshape(140, 140))
            demo = r
    mean = {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k != "seed"}
    res = dict(demo_seed0=demo, mean_5_seeds=mean, runs=rows, noise=NOISE, n_train=150, n_test=5000)
    (OUT / "results.json").write_text(json.dumps(res, indent=2))
    print("media:", {k: round(v, 3) for k, v in mean.items()})


if __name__ == "__main__":
    main()
