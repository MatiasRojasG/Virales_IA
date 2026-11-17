"""Control de calidad automático después del render (ver «Control de calidad» en CLAUDE.md).

Mide sobre el MP4 final:
  - formato: 1080×1920, 60 fps, H.264 yuv420p, AAC 48 kHz;
  - sonoridad: −16 a −14 LUFS integrados y pico verdadero ≤ −1 dBTP;
  - sincronía: desfase entre cada bloque de subtítulos y el inicio real de la voz (< 100 ms);
  - saltos aislados: cuadros cuya diferencia con el anterior es mucho mayor que la de sus vecinos;
  - loop: diferencia entre el primer y el último cuadro (informativo).
Escribe `build/qa/qa.json` y la hoja `build/qa/hoja_video.png`, y devuelve True si todo pasa.
"""
from __future__ import annotations
import json, re, subprocess
from pathlib import Path
import numpy as np

from . import config as C

LUFS_RANGE = (-16.0, -14.0)
TP_MAX = -1.0
SUB_MAX_MS = 100
QA_W, QA_H = 90, 160          # resolución de análisis de cuadros


def probe(mp4):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate:format=duration",
                          "-of", "json", str(mp4)], capture_output=True, text=True, check=True).stdout
    j = json.loads(out)
    v = next(s for s in j["streams"] if s["codec_type"] == "video")
    a = next((s for s in j["streams"] if s["codec_type"] == "audio"), {})
    num, den = map(int, v["r_frame_rate"].split("/"))
    return {"width": v["width"], "height": v["height"], "fps": num / den, "vcodec": v["codec_name"],
            "pix_fmt": v.get("pix_fmt"), "acodec": a.get("codec_name"), "sample_rate": int(a.get("sample_rate", 0)),
            "duration": float(j["format"]["duration"])}


def loudness(mp4):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(mp4), "-af", "ebur128=peak=true",
                          "-f", "null", "-"], capture_output=True, text=True).stderr
    summ = err[err.rfind("Summary:"):]
    i = float(re.search(r"I:\s+(-?[\d.]+) LUFS", summ).group(1))
    tp = float(re.search(r"Peak:\s+(-?[\d.]+|-inf) dBFS", summ).group(1))
    return {"lufs": i, "true_peak_dbtp": tp}


def frame_diffs(mp4):
    """Diferencia media absoluta (0–255) entre cuadros consecutivos, en gris a baja resolución."""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-vf", f"scale={QA_W}:{QA_H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True, check=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, QA_H, QA_W).astype(np.float32)
    return fr, np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))


def isolated_jumps(d, fps, min_abs=6.0, ratio=4.0):
    """Un salto aislado: un cuadro cambia mucho y sus vecinos casi nada (corte sin transición, parpadeo)."""
    out = []
    for i in range(1, len(d) - 1):
        nb = max(d[i - 1], d[i + 1], 0.3)
        if d[i] >= min_abs and d[i] >= ratio * nb:
            out.append({"t": round((i + 1) / fps, 3), "diff": round(float(d[i]), 2), "vecinos": round(float(nb), 2)})
    return out


def subtitle_offsets(tl, chunks, thresh_db=-35.0, win=0.010):
    """Desfase (ms) entre el inicio de cada bloque de subtítulos y el inicio de la voz en ese bloque.
    Positivo = el subtítulo aparece después de la voz."""
    v = tl.voice_track(); sr = tl.sr; hop = int(win * sr)
    env = np.sqrt(np.convolve(v ** 2, np.ones(hop) / hop, "same") + 1e-12)
    thr = 10 ** (thresh_db / 20) * max(env.max(), 1e-6)
    loud = env > thr
    gap = int(0.08 * sr)               # silencio mínimo antes de un arranque medible
    prev_end = {id(tk): (tl.tokens[i - 1].end if i else 0.0) for i, tk in enumerate(tl.tokens)}
    res = []
    for c in chunks:
        tk0 = c["tokens"][0]
        a, b = int(max(0, tk0.start - 0.25, prev_end.get(id(tk0), 0.0) + 0.02) * sr), int(min(tk0.end, tk0.start + 0.25) * sr)
        onset = None
        for i in np.flatnonzero(np.diff(loud[a:b].astype(np.int8)) == 1) + a + 1:
            if not loud[max(0, i - gap):i].any():
                onset = i / sr; break
        if onset is None:              # el bloque empieza en medio de habla continua: no medible por energía
            continue
        res.append({"t": round(c["start"], 3), "texto": " ".join(t.display for t in c["tokens"]),
                    "ms": round((c["start"] - onset) * 1000)})
    return res


def video_sheet(frames, fps, out_png, n=24, cols=6):
    from PIL import Image, ImageDraw
    idx = np.linspace(0, len(frames) - 1, n).astype(int)
    w, h = QA_W * 2, QA_H * 2
    sheet = Image.new("RGB", (cols * w, ((n + cols - 1) // cols) * (h + 18)), (40, 40, 40))
    for k, i in enumerate(idx):
        im = Image.fromarray(frames[i].astype(np.uint8)).resize((w, h))
        x, y = (k % cols) * w, (k // cols) * (h + 18)
        sheet.paste(im, (x, y + 18)); ImageDraw.Draw(sheet).text((x + 4, y + 3), f"{i / fps:.1f}s", fill=(255, 255, 255))
    sheet.save(out_png)


def run(mp4, tl, chunks, out_dir):
    out_dir = Path(out_dir); out_dir.mkdir(parents=True, exist_ok=True)
    rep, ok = {"archivo": str(mp4)}, {}
    p = rep["formato"] = probe(mp4)
    ok["formato"] = (p["width"], p["height"], round(p["fps"]), p["vcodec"], p["pix_fmt"], p["acodec"],
                     p["sample_rate"]) == (C.W, C.H, C.FPS, "h264", "yuv420p", "aac", 48000)
    L = rep["sonoridad"] = loudness(mp4)
    ok["sonoridad"] = LUFS_RANGE[0] <= L["lufs"] <= LUFS_RANGE[1] and L["true_peak_dbtp"] <= TP_MAX
    offs = subtitle_offsets(tl, chunks)
    ms = np.abs([o["ms"] for o in offs]) if offs else np.zeros(1)
    rep["subtitulos"] = {"bloques": len(offs), "media_abs_ms": round(float(ms.mean())), "max_abs_ms": int(ms.max()),
                         "peores": sorted(offs, key=lambda o: -abs(o["ms"]))[:5]}
    ok["subtitulos"] = int(ms.max()) < SUB_MAX_MS
    frames, d = frame_diffs(mp4)
    jumps = isolated_jumps(d, p["fps"])
    rep["saltos_aislados"] = jumps
    ok["saltos"] = not jumps
    rep["loop_diff_primero_ultimo"] = round(float(np.abs(frames[0] - frames[-1]).mean()), 2)
    video_sheet(frames, p["fps"], out_dir / "hoja_video.png")
    rep["ok"] = ok; rep["aprobado"] = all(ok.values())
    (out_dir / "qa.json").write_text(json.dumps(rep, ensure_ascii=False, indent=1))
    print(f"QA  formato {'✓' if ok['formato'] else '✗'} {p['width']}×{p['height']} {p['fps']:.0f} fps "
          f"{p['vcodec']}/{p['acodec']} {p['sample_rate']} Hz, {p['duration']:.2f} s")
    print(f"QA  sonoridad {'✓' if ok['sonoridad'] else '✗'} {L['lufs']:.1f} LUFS, pico {L['true_peak_dbtp']:.1f} dBTP")
    print(f"QA  subtítulos {'✓' if ok['subtitulos'] else '✗'} desfase medio {rep['subtitulos']['media_abs_ms']} ms, "
          f"máx {rep['subtitulos']['max_abs_ms']} ms")
    print(f"QA  saltos aislados {'✓ ninguno' if not jumps else '✗ ' + ', '.join(str(j['t']) + ' s' for j in jumps[:8])}")
    print(f"QA  loop (dif. primer/último cuadro): {rep['loop_diff_primero_ultimo']}/255")
    print("QA  " + ("APROBADO" if rep["aprobado"] else "REVISAR") + f" → {out_dir / 'qa.json'}")
    return rep["aprobado"]
