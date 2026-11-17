"""Simulación real (NumPy): bolas que se copian al tocar un engranaje giratorio y desaparecen
al tocar el borde rosado. Cada copia hereda el «giro hacia el centro» (a ∈ [0, 1]) de su madre
con una pequeña mutación. Nadie programa la estrategia: la selección la hace aparecer.

Guarda posiciones por cuadro (60 por segundo de simulación), nacimientos y muertes."""
import json
from pathlib import Path
import numpy as np

OUT = Path(__file__).parent / "build" / "experiment"
CX, CY, R = 540.0, 885.0, 405.0        # arena (px)
RB, RG = 15.0, 78.0                    # radio de bola y del engranaje
V, K = 340.0, 2.4                      # rapidez (px/s) y giro máximo hacia el centro (rad/s)
DANGER = np.pi / 2                     # centro del borde rosado (abajo)
W0, W1, T1, T2 = 58.0, 180.0, 22.0, 62.0  # su semiancho (°) crece de W0 a W1 entre T1 y T2 (s)


def half_width(t):
    u = np.clip((t - T1) / (T2 - T1), 0, 1)
    return np.radians(W0 + (W1 - W0) * u * u * (3 - 2 * u))
CAP, SIGMA, COOL = 160, 0.08, 0.55
FPS, SUB, TMAX = 60, 4, 80.0
GEAR_W = 1.1                            # rad/s


def run(seed):
    rng = np.random.default_rng(seed)
    n0 = 5
    ang = rng.uniform(0, 2 * np.pi, n0); rr = rng.uniform(160, 300, n0)
    pos = np.c_[CX + rr * np.cos(ang), CY + rr * np.sin(ang)]
    th = ang + np.pi + rng.uniform(-0.25, 0.25, n0)          # salen hacia el engranaje
    vel = V * np.c_[np.cos(th), np.sin(th)]
    a = rng.uniform(0.0, 0.2, n0)
    ids = list(range(n0)); nid = n0
    cool = np.zeros(n0)
    births, deaths = [], []
    traits = {i: float(a[i]) for i in range(n0)}
    frames = []
    dt = 1 / FPS / SUB
    for f in range(int(TMAX * FPS)):
        for s in range(SUB):
            t = (f * SUB + s) * dt
            d = pos - [CX, CY]; dist = np.hypot(d[:, 0], d[:, 1]) + 1e-9
            # giro hacia el centro (rapidez constante)
            cur = np.arctan2(vel[:, 1], vel[:, 0]); want = np.arctan2(-d[:, 1], -d[:, 0])
            dlt = (want - cur + np.pi) % (2 * np.pi) - np.pi
            cur = cur + np.clip(dlt, -a * K * dt, a * K * dt)
            vel = V * np.c_[np.cos(cur), np.sin(cur)]
            pos = pos + vel * dt; cool -= dt
            d = pos - [CX, CY]; dist = np.hypot(d[:, 0], d[:, 1]) + 1e-9; nrm = d / dist[:, None]
            # engranaje: rebote + copia
            hit = dist < RG + RB
            for i in np.where(hit)[0]:
                vn = vel[i] @ nrm[i]
                if vn < 0: vel[i] = vel[i] - 2 * vn * nrm[i]
                tang = np.array([-nrm[i, 1], nrm[i, 0]])
                vel[i] = vel[i] + tang * GEAR_W * RG * 0.8
                vel[i] *= V / np.linalg.norm(vel[i])
                pos[i] = [CX, CY] + nrm[i] * (RG + RB + 0.5)
                if cool[i] <= 0 and len(ids) < CAP:
                    ca = float(np.clip(a[i] + rng.normal(0, SIGMA), 0, 1))
                    rot = rng.choice([-1, 1]) * rng.uniform(0.35, 0.7)
                    c, s_ = np.cos(rot), np.sin(rot)
                    v2 = np.array([c * vel[i, 0] - s_ * vel[i, 1], s_ * vel[i, 0] + c * vel[i, 1]])
                    pos = np.vstack([pos, pos[i]]); vel = np.vstack([vel, v2]); a = np.append(a, ca)
                    cool = np.append(cool, COOL); cool[i] = COOL
                    births.append([f, ids[i], nid, float(pos[i, 0]), float(pos[i, 1]), ca])
                    traits[nid] = ca; ids.append(nid); nid += 1
            # borde
            d = pos - [CX, CY]; dist = np.hypot(d[:, 0], d[:, 1]) + 1e-9; nrm = d / dist[:, None]
            out = dist > R - RB
            kill = []
            for i in np.where(out)[0]:
                phi = np.arctan2(d[i, 1], d[i, 0])
                if abs((phi - DANGER + np.pi) % (2 * np.pi) - np.pi) < half_width(t):
                    kill.append(i); deaths.append([f, ids[i], float(pos[i, 0]), float(pos[i, 1]), float(a[i])])
                else:
                    vn = vel[i] @ nrm[i]
                    if vn > 0: vel[i] = vel[i] - 2 * vn * nrm[i]
                    pos[i] = [CX, CY] + nrm[i] * (R - RB - 0.5)
            if kill:
                keep = np.ones(len(ids), bool); keep[kill] = False
                pos, vel, a, cool = pos[keep], vel[keep], a[keep], cool[keep]
                ids = [x for x, k in zip(ids, keep) if k]
            if not ids: return None
        frames.append((list(ids), pos.copy()))
    return frames, births, deaths, traits, nid


def stats(res):
    frames, births, deaths, traits, nid = res
    out = []
    for f in range(0, len(frames), FPS * 5):
        ids, _ = frames[f]; tr = np.array([traits[i] for i in ids])
        out.append((f // FPS, len(ids), round(float(tr.mean()), 2), round(float((tr > 0.6).mean()), 2)))
    out.append(('min', min(len(fr[0]) for fr in frames[FPS*20:])))
    return out


def main(seed=None):
    OUT.mkdir(parents=True, exist_ok=True)
    res = run(seed if seed is not None else SEED)
    frames, births, deaths, traits, nid = res
    P = np.full((len(frames), nid, 2), np.nan, np.float32)
    for f, (ids, pos) in enumerate(frames): P[f, ids] = pos
    tr = np.array([traits[i] for i in range(nid)], np.float32)
    np.savez_compressed(OUT / "sim.npz", P=P, traits=tr, births=np.array(births, np.float32),
                        deaths=np.array(deaths, np.float32))
    st = stats(res)
    meta = {"seed": SEED, "fps": FPS, "n_total": nid, "n_births": len(births), "n_deaths": len(deaths),
            "first_birth_s": births[0][0] / FPS, "first_death_s": deaths[0][0] / FPS if deaths else None,
            "stats_every_5s": st,
            "per_second": [[f // FPS, int(np.isfinite(P[f, :, 0]).sum()),
                            round(float(np.nanmean(np.where(np.isfinite(P[f, :, 0]), tr, np.nan))), 3),
                            round(float(np.nansum(np.where(np.isfinite(P[f, :, 0]), tr > 0.6, 0)) /
                                        max(1, np.isfinite(P[f, :, 0]).sum())), 3)]
                           for f in range(0, len(P), FPS)]}
    (OUT / "sim.json").write_text(json.dumps(meta, indent=1))
    return meta


SEED = 5
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "scan":
        for sd in range(12):
            r = run(sd)
            if r is None: print(sd, "extinta"); continue
            print(sd, "births0", r[1][0][0] / FPS, "death0", r[2][0][0] / FPS if r[2] else None, stats(r)[::2], stats(r)[-1])
    else:
        print(json.dumps(main(), indent=1))
