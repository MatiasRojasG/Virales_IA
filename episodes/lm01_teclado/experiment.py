"""Experimento real: embeddings de palabras aprendidos jugando a adivinar la palabra que falta.

Corpus de juguete (frases escritas a partir de plantillas, en español). Modelo de lenguaje
neuronal simple, como en la clase: las 3 palabras ANTERIORES predicen la siguiente (lo que hace
un teclado). Cada palabra pasa por la matriz de embeddings (one-hot × matriz = una fila), se
promedian, y P(w | contexto) = softmax(u_w · promedio). Pérdida: log-verosimilitud negativa.
Se entrena con descenso de gradiente (Adam) y se guardan instantáneas del mapa (PCA 2D).
Al final, se usa el mismo modelo como «teclado»: con «me tomé un», ¿qué palabras sugiere?
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

HERE = Path(__file__).parent
OUT = HERE / "build" / "experiment"
CAT = {
    "bebida": ["café", "té", "jugo", "mate", "chocolate"],
    "animal": ["perro", "gato", "caballo", "conejo", "pájaro"],
    "comida": ["pan", "queso", "arroz", "pollo", "pescado"],
    "lugar": ["parque", "campo", "patio", "cerro", "bosque"],
}
TEMPLATES = [
    "me tomé un {bebida} caliente", "me tomé un {bebida} con leche", "pedí un {bebida} en la cafetería",
    "un {bebida} bien cargado por la mañana", "el {bebida} se enfrió en la mesa", "quiero otro {bebida} por favor",
    "el {animal} corre en el {lugar}", "mi {animal} duerme en el {lugar}", "el {animal} juega con los niños",
    "vimos un {animal} en el {lugar}", "el {animal} come {comida}", "alimenté al {animal} en la mañana",
    "comí {comida} con {bebida}", "compramos {comida} para la cena", "el {comida} está muy rico",
    "cocinamos {comida} en la casa", "almorzamos {comida} en el {lugar}",
    "fuimos al {lugar} el domingo", "caminamos por el {lugar} al atardecer", "el {lugar} estaba lleno de gente",
]


def corpus(n=6000, seed=0):
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        t = TEMPLATES[rng.integers(len(TEMPLATES))]
        s = t
        for k, words in CAT.items():
            while "{" + k + "}" in s:
                s = s.replace("{" + k + "}", words[rng.integers(len(words))], 1)
        out.append(s.split())
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sents = corpus()
    vocab = sorted({w for s in sents for w in s})
    idx = {w: i for i, w in enumerate(vocab)}
    V, d, m = len(vocab), 16, 3
    ctx, tgt = [], []
    for s in sents:
        ids = [idx[w] for w in s]
        for i, c in enumerate(ids):
            if i == 0: continue
            cc = [ids[j] for j in range(max(0, i - m), i)]
            ctx.append(cc + [-1] * (m - len(cc))); tgt.append(c)
    ctx = np.array(ctx); tgt = np.array(tgt)
    rng = np.random.default_rng(1)
    E = rng.normal(0, 0.1, (V, d))           # matriz de embeddings (una fila por palabra)
    U = rng.normal(0, 0.1, (V, d))           # vectores de salida
    params = [E, U]; mo = [np.zeros_like(p) for p in params]; ve = [np.zeros_like(p) for p in params]
    snaps, losses, step = {}, [], 0
    focus = [w for k in CAT.values() for w in k]
    snaps[-1] = E[[idx[w] for w in focus]].copy()
    for ep in range(30):
        perm = rng.permutation(len(tgt)); tot = 0
        for s0 in range(0, len(tgt), 256):
            b = perm[s0:s0 + 256]; C = ctx[b]; y = tgt[b]
            mask = (C >= 0)[..., None]
            h = (E[np.maximum(C, 0)] * mask).sum(1) / mask.sum(1)
            z = h @ U.T; z -= z.max(1, keepdims=True); p = np.exp(z); p /= p.sum(1, keepdims=True)
            tot += -np.log(p[np.arange(len(y)), y] + 1e-9).sum()
            g = p; g[np.arange(len(y)), y] -= 1; g /= len(y)
            gU = g.T @ h; gh = g @ U
            gE = np.zeros_like(E)
            share = gh / mask.sum(1)
            for k in range(C.shape[1]):
                ok = C[:, k] >= 0
                np.add.at(gE, C[ok, k], share[ok])
            step += 1
            if ep == 0 and step in (5, 15, 30, 60):
                snaps[-1 + step / 1000] = E[[idx[w] for w in focus]].copy()
            for i, (pp, gg) in enumerate(zip(params, [gE, gU])):
                mo[i] = 0.9 * mo[i] + 0.1 * gg; ve[i] = 0.999 * ve[i] + 0.001 * gg * gg
                pp -= 0.01 * (mo[i] / (1 - 0.9 ** step)) / (np.sqrt(ve[i] / (1 - 0.999 ** step)) + 1e-8)
        losses.append(tot / len(tgt))
        if ep in (0, 1, 2, 4, 7, 12, 20, 29) or (ep == 0):
            snaps[ep] = E[[idx[w] for w in focus]].copy()
    # PCA común (ejes del modelo final) para que el mapa sea estable
    F = E[[idx[w] for w in focus]]
    mu = F.mean(0); _, _, Vt = np.linalg.svd(F - mu, full_matrices=False)
    proj = lambda X: (X - mu) @ Vt[:2].T
    P = {k: proj(v) for k, v in snaps.items()}
    sc = np.abs(P[29]).max(0)
    P = {k: (v / sc).tolist() for k, v in P.items()}
    # teclado: «me tomé un ___» (solo contexto a la izquierda)
    left = [idx[w] for w in ("me", "tomé", "un")]
    h = E[left].mean(0); z = h @ U.T; pr = np.exp(z - z.max()); pr /= pr.sum()
    top = [(vocab[i], float(pr[i])) for i in np.argsort(-pr)[:5]]
    # vecinos más cercanos (coseno) de «café» y «perro»
    En = E / np.linalg.norm(E, axis=1, keepdims=True)
    nn = {w: [vocab[i] for i in np.argsort(-(En @ En[idx[w]]))[1:5]] for w in ("café", "perro", "pan", "parque")}
    res = dict(vec_cafe=E[idx["café"]].tolist(), vocab_size=V, n_sentences=len(sents), dim=d, window=m, losses=losses, keyboard=top,
               neighbors=nn, focus=focus, cats=[k for k, ws in CAT.items() for _ in ws], snaps=P,
               sim_cafe_te=float(En[idx["café"]] @ En[idx["té"]]), sim_cafe_perro=float(En[idx["café"]] @ En[idx["perro"]]))
    (OUT / "results.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps({k: res[k] for k in ("vocab_size", "keyboard", "neighbors", "sim_cafe_te", "sim_cafe_perro")}, ensure_ascii=False, indent=1))
    print("pérdida:", [round(l, 2) for l in losses[::5]])


if __name__ == "__main__":
    main()
