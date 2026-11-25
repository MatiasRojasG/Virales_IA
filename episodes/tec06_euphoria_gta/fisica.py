"""Simulaciones propias (NumPy) para el reel de Euphoria. No reproducen Euphoria: son modelos de juguete.

- `sim_control`: péndulo invertido lineal (centro de masa a altura fija) con un «cerebro» mínimo: si el punto de
  captura (x + v/ω) sale de la base de apoyo, da un paso hacia él. Es la idea clásica de equilibrio por pasos
  (Pratt et al., «Capture Point», 2006), no el algoritmo de NaturalMotion.
- `sim_trapo`: cuerpo rígido que pivota sobre los pies sin control (θ'' = g/l·sen θ): cae como muñeco de trapo.
Unidades: metros y segundos. x hacia la derecha (dirección del empujón).
"""
from __future__ import annotations
import math
import numpy as np

G = 9.81
Z = 0.95                     # altura del centro de masa
W = math.sqrt(G / Z)         # ω del péndulo invertido lineal
DT = 1 / 240
TS = 0.30                    # duración de un paso
REACT = 0.06                 # tiempo de reacción del «cerebro»
FOOT = 0.07                  # medio largo de pie (zona donde puede ir el apoyo)
MAXSTEP = 0.62


def sim_control(dv, T=5.0, half=0.12):
    """Devuelve dict de arrays muestreados cada DT desde el empujón (t=0)."""
    n = int(T / DT) + 1
    x, v = 0.0, dv
    feet = [-half, half]; lift = [0.0, 0.0]
    stepping = None            # (pie, desde, hasta, t0)
    t_need = None
    out = {k: np.zeros(n) for k in ("x", "v", "p", "fl", "fr", "ll", "lr", "cp", "tgt", "tgt_a")}
    tgt, tgt_a = 0.0, 0.0
    for i in range(n):
        t = i * DT
        cp = x + v / W
        if stepping is None:
            lo, hi = min(feet) - FOOT, max(feet) + FOOT
            out_sup = cp > hi + 0.01 or cp < lo - 0.01
            settle = abs(v) < 0.03 and abs(feet[0] - feet[1]) > 0.42
            if out_sup or settle:
                if t_need is None: t_need = t
                if t - t_need >= REACT:
                    if out_sup:
                        sgn = 1 if v > 0 else -1
                        sw = int(np.argmin(feet)) if sgn > 0 else int(np.argmax(feet))
                        st = 1 - sw
                        target = cp + 0.06 * sgn
                        target = feet[st] + sgn * min(abs(target - feet[st]), MAXSTEP)
                    else:   # junta los pies: el de atrás avanza
                        sw = int(np.argmin(feet)); st = 1 - sw
                        target = feet[st] - 2 * half; sgn = 0
                    stepping = [sw, feet[sw], target, t, sgn if out_sup else 0]; tgt = target; t_need = None
            else:
                t_need = None
            if stepping is None:
                p = min(max(cp, lo), hi)
        if stepping is not None:
            sw, a0, a1, t0, sg = stepping
            u = min(1.0, (t - t0) / TS)
            st = 1 - sw
            if sg != 0 and u < 0.85:    # replanifica: punto de captura previsto al aterrizar
                pst = min(max(cp, feet[st] - FOOT), feet[st] + FOOT)
                cpp = pst + (cp - pst) * math.exp(W * TS * (1 - u))
                a1 = feet[st] + sg * min(max(0.12, sg * (cpp + 0.05 * sg - feet[st])), MAXSTEP)
                stepping[2] = a1; tgt = a1
            e = 0.5 - 0.5 * math.cos(math.pi * u)
            feet[sw] = a0 + (a1 - a0) * e
            lift[sw] = 0.13 * math.sin(math.pi * u) * min(1.0, abs(a1 - a0) / 0.2 + 0.3)
            st = 1 - sw
            p = min(max(cp, feet[st] - FOOT), feet[st] + FOOT)
            tgt_a = 1.0
            if u >= 1.0:
                lift[sw] = 0.0; stepping = None
        else:
            tgt_a = max(0.0, tgt_a - DT * 1.5)
        acc = W * W * (x - p) - 0.25 * v * (abs(v) < 0.2)
        v += acc * DT; x += v * DT
        for k, val in (("x", x), ("v", v), ("p", p), ("fl", feet[0]), ("fr", feet[1]), ("ll", lift[0]),
                       ("lr", lift[1]), ("cp", cp), ("tgt", tgt), ("tgt_a", tgt_a)):
            out[k][i] = val
    return out


def sim_trapo(dv, T=4.0, L=1.0):
    """Ángulo del cuerpo (0 = de pie, π/2 = en el suelo) sin control."""
    n = int(T / DT) + 1
    th, om = 0.0, dv / L
    ths = np.zeros(n); oms = np.zeros(n)
    lim = math.pi / 2 - 0.04
    for i in range(n):
        al = G / L * math.sin(th) - 0.05 * om
        om += al * DT; th += om * DT
        if th > lim:
            th = lim; om = -0.18 * om if om > 0.3 else 0.0
        ths[i] = th; oms[i] = om
    return {"th": ths, "om": oms}


def sample(sim, key, ts):
    """Interpola sim[key] en el tiempo de simulación ts (antes de 0: valor inicial)."""
    arr = sim[key]
    if ts <= 0: return float(arr[0]) if key not in ("v", "om") else 0.0
    f = ts / DT
    i = int(f)
    if i >= len(arr) - 1: return float(arr[-1])
    u = f - i
    return float(arr[i] * (1 - u) + arr[i + 1] * u)


if __name__ == "__main__":
    for dv in (0.6, 0.9, 1.2, 1.6):
        s = sim_control(dv)
        steps = int(np.sum(np.abs(np.diff(s["fl"])) + np.abs(np.diff(s["fr"])) > 0) and 0)
        # contar pasos = flancos de subida de lift
        lifts = (s["ll"] > 0) | (s["lr"] > 0)
        n = int(np.sum(np.diff(lifts.astype(int)) == 1))
        print(f"dv={dv}: pasos={n}, x final={s['x'][-1]:.2f}, v final={s['v'][-1]:.3f}, pies={s['fl'][-1]:.2f},{s['fr'][-1]:.2f}")
        first = np.argmax(lifts) * DT; print("   primer paso a", round(first, 3), "s")
    r = sim_trapo(0.6); i = int(np.argmax(r["th"] > 1.5)); print("trapo: al suelo a", round(i * DT, 2), "s")
