"""Simulación del episodio: probabilidades ILUSTRATIVAS para «un número del 1 al 10»
(el 7 más probable, como en las encuestas a personas) y 200 giros reales de la ruleta
(muestreo con temperatura 1). También: muestreo con temperatura baja y alta, para comparar."""
import json
from pathlib import Path
import numpy as np

OUT = Path(__file__).parent / "build" / "experiment"
P = np.array([0.03, 0.05, 0.12, 0.06, 0.08, 0.05, 0.38, 0.11, 0.07, 0.05])   # ilustrativo


def temp(p, T):
    l = np.log(p) / T; e = np.exp(l - l.max()); return e / e.sum()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(7)
    draws = rng.choice(10, 200, p=P) + 1
    res = {"p": P.tolist(), "draws": draws.tolist(), "counts": np.bincount(draws, minlength=11)[1:].tolist(),
           "p_T05": temp(P, 0.5).tolist(), "p_T2": temp(P, 2.0).tolist()}
    (OUT / "results.json").write_text(json.dumps(res))
    print(res["counts"], "7:", res["counts"][6])


if __name__ == "__main__":
    main()
