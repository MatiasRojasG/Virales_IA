"""Construye «La foto nocturna» (EP 01).

    python episodes/ep01_foto_nocturna/build.py            # video final
    python episodes/ep01_foto_nocturna/build.py --stills   # solo cuadros de control
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path[:0] = [str(ROOT), str(HERE)]

from reelforge.timeline import Timeline
from reelforge import audio as AU, render as R
import experiment, scenes
from script import BEATS, EPISODE

BUILD = HERE / "build"
OUT = HERE / "output"


def load_data():
    exp = BUILD / "experiment"
    if not (exp / "arrays.npz").exists():      # determinista: se regenera si falta
        experiment.main()
    z = np.load(exp / "arrays.npz")
    d = {k: z[k] for k in z.files}
    d["res"] = json.loads((exp / "results.json").read_text())
    # documento restaurado (mosaico «dónde más se usa»)
    doc = HERE.parent / "ep01_restauracion_documento" / "build" / "experiment" / "arrays.npz"
    if doc.exists():
        zd = np.load(doc)
        for key, arr in (("doc_noisy", zd["obs"]), ("doc_clean", zd["hist"][-1])):
            g = np.where(arr[..., None] == 1, [11, 16, 32], [233, 238, 247]).astype(np.uint8)
            d[key] = np.dstack([g, np.full(arr.shape, 255, np.uint8)])
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_data()
    tl = Timeline(BEATS, BUILD / "tts")
    scenes.setup(tl, data, EPISODE)
    print(f"duración: {tl.duration:.2f} s")

    if args.stills:
        sd = BUILD / "stills"; sd.mkdir(parents=True, exist_ok=True)
        for f in sd.glob("*.png"): f.unlink()
        for b in BEATS:
            for frac in (0.2, 0.5, 0.8):
                tt = b.start + frac * b.dur
                R.render_still(scenes.draw_frame, tt, sd / f"{b.id}_{int(frac*100)}.png")
        print("stills en", sd); return

    slug = EPISODE["slug"]
    # audio
    wav = BUILD / "mix.wav"
    AU.mix(tl.voice_track(), tl.duration, scenes.sfx_cues(tl), out_wav=wav, music_kw=scenes.music_kw(tl))
    # subtítulos y guion
    (OUT / f"{slug}.srt").write_text(tl.srt(scenes.CHUNKS), encoding="utf-8")
    (OUT / "guion_narrado.txt").write_text(tl.script_text(), encoding="utf-8")
    # portada (cuadro del hook con el resultado)
    R.render_still(scenes.draw_cover, 3.0, OUT / "portada.png")
    # video
    t0 = time.time()
    mp4 = OUT / f"{slug}.mp4"
    R.render_video(scenes.draw_frame, tl.duration, mp4, wav, BUILD / "parts", workers=args.workers)
    print(f"render {time.time() - t0:.1f} s ->", mp4)
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                           "stream=codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration",
                           "-of", "compact", str(mp4)], capture_output=True, text=True).stdout
    print(info)


if __name__ == "__main__":
    main()
