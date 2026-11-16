"""Opción C: un robot aprende a saltar a una plataforma ajustando fuerza y ángulo con descenso de gradiente."""
import json, numpy as np
G, TX, TY = 9.8, 6.0, 2.0          # gravedad, plataforma a 6 m y 2 m de alto

def tray(v, ang, n=60):
    t = np.linspace(0, 3, n); x = v*np.cos(ang)*t; y = v*np.sin(ang)*t - G*t*t/2
    return x, y

def loss(p):
    v, ang = p; x, y = tray(v, ang, 400)
    # distancia mínima de la trayectoria al punto de aterrizaje (cayendo)
    return float(np.min((x-TX)**2 + (y-TY)**2))

p = np.array([5.0, 0.35]); hist = [p.tolist()]; L = [loss(p)]
for it in range(60):
    g = np.array([(loss(p+e)-loss(p-e))/(2*1e-3) for e in np.eye(2)*1e-3])
    p = p - np.array([0.08, 0.004]) * g
    hist.append(p.tolist()); L.append(loss(p))
json.dump({"hist": hist, "loss": L}, open("sim_salto.json", "w"))
print("intentos:", len(hist), "error inicial", round(L[0], 2), "→ final", round(L[-1], 4), "p final", np.round(p, 2))
