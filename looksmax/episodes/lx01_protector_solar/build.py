"""Construye «Misma edad, distinta piel» (cuenta looksmax).

    python looksmax/episodes/lx01_protector_solar/build.py            # video final
    python looksmax/episodes/lx01_protector_solar/build.py --stills   # solo cuadros de control
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "looksmax"), str(HERE)]

from reelforge.timeline import Timeline
from reelforge import audio as AU, render as R
import scenes
from script import BEATS, EPISODE, VOICE, RATE

BUILD = HERE / "build"
OUT = HERE / "output"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    tl = Timeline(BEATS, BUILD / "tts", voice=VOICE, rate=RATE)
    scenes.setup(tl, None, EPISODE)
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
    R.render_still(scenes.draw_cover, 0.0, OUT / "portada.png")
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
