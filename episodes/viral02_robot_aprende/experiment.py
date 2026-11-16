"""Simulación real: un robot aprende a saltar a una plataforma ajustando dos «perillas»
(fuerza v y ángulo) con descenso de gradiente sobre su error (distancia al punto de aterrizaje).
Para cada intento se guarda la trayectoria hasta que toca el suelo o la plataforma."""
import json
from pathlib import Path
import numpy as np

OUT = Path(__file__).parent / "build" / "experiment"
G, TX, TY = 9.8, 6.0, 2.0              # plataforma: borde en x≈5.6–6.6 m, altura 2 m
PX0, PX1 = 5.5, 6.7


def tray(v, ang, dt=0.01):
    x, y, vx, vy = 0.0, 0.0, v * np.cos(ang), v * np.sin(ang)
    pts = [(x, y)]
    while True:
        x += vx * dt; vy -= G * dt; y += vy * dt
        if PX0 <= x <= PX1 and vy < 0 and y <= TY and pts[-1][1] >= TY:
            pts.append((x, TY)); return pts, "plataforma"
        if PX0 <= x <= PX1 and y < TY and pts[-1][1] < TY and pts[-1][0] < PX0:
            pts.append((x, y)); return pts, "choca"
        if y <= 0:
            pts.append((x, 0.0)); return pts, "suelo"
        pts.append((x, y))
        if x > 9: return pts, "lejos"


def loss(p):
    v, ang = p; t = np.linspace(0, 3, 600)
    x = v * np.cos(ang) * t; y = v * np.sin(ang) * t - G * t * t / 2
    return float(np.min((x - TX) ** 2 + (y - TY) ** 2))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    p = np.array([5.0, 0.35]); hist = [p.copy()]
    for _ in range(60):
        g = np.array([(loss(p + e) - loss(p - e)) / 2e-3 for e in np.eye(2) * 1e-3])
        p = p - np.array([0.08, 0.004]) * g; hist.append(p.copy())
    att = []
    for q in hist:
        pts, res = tray(*q)
        att.append({"v": float(q[0]), "ang": float(q[1]), "loss": loss(q), "res": res,
                    "pts": [[round(a, 3), round(b, 3)] for a, b in pts[::3]] + [[round(pts[-1][0], 3), round(pts[-1][1], 3)]]})
    json.dump({"attempts": att}, open(OUT / "sim.json", "w"))
    print("primer intento:", att[0]["res"], "| último:", att[-1]["res"], "| errores:", [round(a["loss"], 2) for a in att[::10]])
    print("primer éxito en intento:", next((k for k, a in enumerate(att) if a["res"] == "plataforma"), None))


if __name__ == "__main__":
    main()
