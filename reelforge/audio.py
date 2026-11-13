"""Música instrumental procedural (libre de derechos: se sintetiza aquí),
efectos de sonido sintetizados y mezcla con ducking bajo la voz."""
from __future__ import annotations
import subprocess
import numpy as np

SR = 48000
rng = np.random.default_rng(12)


def _midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x, axis=0)


def _env(n, att, rel):
    e = np.ones(n)
    na, nr = min(n, int(att * SR)), min(n, int(rel * SR))
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e


def music(duration, bpm=96, seed=3, arp_from=0.0, pulse=None, quiet=None):
    """Pad ambiental + bajo + arpegio suave. Progresión Am–F–C–G (estéreo).
    arp_from: segundo en que entra el arpegio (la historia "despega").
    pulse: (t0, t1) tramo con pulso grave suave (clímax).
    quiet: lista de (t0, t1) donde la música baja (respiro / suspenso)."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    out = np.zeros((n, 2))
    beat = 60 / bpm
    bar = 4 * beat
    prog = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 52, 55, 60], [55, 59, 62, 67]]
    nbars = int(np.ceil(duration / bar)) + 1
    for b in range(nbars):
        ch = prog[b % 4]
        i0 = int(b * bar * SR); i1 = min(n, int((b + 1) * bar * SR + 0.8 * SR))
        if i0 >= n: break
        tt = t[i0:i1] - t[i0]
        seg = np.zeros((i1 - i0, 2))
        for k, m in enumerate(ch):
            f = _midi(m)
            for det, pan in ((-0.12, 0.3), (0.12, 0.7)):
                ph = 2 * np.pi * f * (1 + det / 100) * tt + rng.random() * 6
                w = np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.1 * np.sin(3 * ph)
                seg[:, 0] += w * (1 - pan); seg[:, 1] += w * pan
        seg *= _env(len(tt), 0.9, 1.2)[:, None] * 0.035
        # bajo
        fb = _midi(ch[0] - 12)
        bass = np.sin(2 * np.pi * fb * tt) * _env(len(tt), 0.05, 0.8) * 0.08
        seg += bass[:, None]
        out[i0:i1] += seg
    out = _lowpass(out, 1800)
    # arpegio "pluck" en corcheas
    step = beat / 2
    k = int(np.ceil(arp_from / step))
    while k * step < duration:
        b = int(k * step / bar)
        ch = prog[b % 4]
        m = ch[[0, 2, 3, 1, 2, 3, 1, 2][k % 8]] + 12
        i0 = int(k * step * SR); L = int(0.45 * SR)
        if i0 + L > n: break
        tt = np.arange(L) / SR
        pl = np.sin(2 * np.pi * _midi(m) * tt) * np.exp(-tt * 9) * 0.03
        pan = 0.35 + 0.3 * ((k * 3) % 5) / 4
        out[i0:i0 + L, 0] += pl * (1 - pan); out[i0:i0 + L, 1] += pl * pan
        k += 1
    if pulse:
        t0, t1 = pulse
        kb = int(np.ceil(t0 / beat))
        while kb * beat < min(t1, duration):
            i0 = int(kb * beat * SR); L = min(int(0.35 * SR), n - i0)
            tt = np.arange(L) / SR
            f = 55 + 40 * np.exp(-tt * 30)
            y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9) * 0.10
            out[i0:i0 + L] += y[:, None]
            kb += 1
    if quiet:
        g = np.ones(n)
        for q0, q1 in quiet:
            g -= 0.6 * np.clip(np.minimum((t - q0) / 0.6, (q1 - t) / 0.6), 0, 1)
        out *= g[:, None]
    # fade in/out
    out *= _env(n, 1.5, 2.5)[:, None]
    return out.astype(np.float32)


# ---------------- efectos ----------------
def sfx_whoosh(dur=0.45, up=True):
    n = int(dur * SR); x = rng.standard_normal(n)
    from scipy.signal import butter, sosfilt
    out = np.zeros(n)
    hop = 512
    for i in range(0, n, hop):
        fr = i / n
        fc = 300 + 4000 * (fr if up else 1 - fr)
        sos = butter(2, [fc * 0.6, min(fc * 1.6, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        out[i:i + hop] = sosfilt(sos, x[i:i + hop])
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    y = out * env
    return (y / (np.abs(y).max() + 1e-9) * 0.22).astype(np.float32)


def sfx_pop(freq=880, dur=0.12):
    t = np.arange(int(dur * SR)) / SR
    f = freq * (1 + 0.5 * np.exp(-t * 60))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 35)
    return (y * 0.22).astype(np.float32)


def sfx_ding(freq=1320, dur=1.2):
    t = np.arange(int(dur * SR)) / SR
    y = sum(np.sin(2 * np.pi * freq * h * t) * np.exp(-t * (3 + 2 * h)) / h for h in (1, 2.01, 3.03))
    return (y * 0.16).astype(np.float32)


def sfx_riser(dur=1.2):
    t = np.arange(int(dur * SR)) / SR
    f = 200 + 900 * (t / dur) ** 2
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 2
    nz = rng.standard_normal(len(t)) * (t / dur) ** 3 * 0.3
    return ((y * 0.5 + _lowpass(nz, 3000)) * 0.12).astype(np.float32)


def sfx_thump(dur=0.5):
    t = np.arange(int(dur * SR)) / SR
    f = 120 * np.exp(-t * 8) + 40
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    return (y * 0.45).astype(np.float32)


def sfx_tick():
    return sfx_pop(2400, 0.04) * 0.6


def sfx_rewind(dur=0.55):
    """Rebobinado: barrido descendente + 'cinta' que frena."""
    t = np.arange(int(dur * SR)) / SR
    f = 1800 * np.exp(-t * 4) + 120
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25
    y = (sfx_whoosh(dur, up=False)[:len(t)] * 2 + tone * np.exp(-t * 3)) * np.sin(np.pi * t / dur)
    return (y * 0.6).astype(np.float32)


def sfx_swell(dur=1.6):
    t = np.arange(int(dur * SR)) / SR
    y = sum(np.sin(2 * np.pi * _midi(m) * t) for m in (57, 64, 69, 76)) / 4
    env = np.sin(np.pi * t / dur) ** 2
    return (_lowpass(y * env, 2500) * 0.18).astype(np.float32)


SFX = {"rewind": sfx_rewind, "swell": sfx_swell,"whoosh": sfx_whoosh, "whoosh_down": lambda: sfx_whoosh(up=False), "pop": sfx_pop,
       "ding": sfx_ding, "riser": sfx_riser, "thump": sfx_thump, "tick": sfx_tick,
       "pop_low": lambda: sfx_pop(520)}


def mix(voice, duration, cues, music_gain_db=-17, duck_db=-9, out_wav=None, music_kw=None):
    """voice: mono float32; cues: lista de (t, nombre_sfx, ganancia)."""
    n = int(duration * SR)
    v = np.zeros(n, np.float32); v[:min(n, len(voice))] = voice[:n]
    mus = music(duration, **(music_kw or {}))
    # ducking: envolvente de la voz suavizada
    env = np.abs(v)
    win = int(0.25 * SR)
    env = np.convolve(env, np.ones(win) / win, mode="same")
    act = np.clip(env / 0.02, 0, 1)
    act = np.convolve(act, np.ones(win) / win, mode="same")
    g = 10 ** (music_gain_db / 20) * 10 ** (duck_db * act / 20)
    out = mus * g[:, None]
    out += np.repeat(v[:, None], 2, axis=1) * 0.95
    cache = {}
    for t, name, gain in cues:
        if name not in cache: cache[name] = SFX[name]()
        s = cache[name] * gain
        i = int(t * SR)
        if i >= n or i < 0: continue
        L = min(len(s), n - i)
        out[i:i + L] += s[:L, None]
    # normaliza a -1 dBFS pico con limitador suave
    out = np.tanh(out * 1.1) / np.tanh(1.1)
    out *= 0.89 / (np.abs(out).max() + 1e-9)
    if out_wav:
        import wave
        pcm = (np.clip(out, -1, 1) * 32767).astype("<i2")
        with wave.open(str(out_wav), "wb") as w:
            w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
    return out
