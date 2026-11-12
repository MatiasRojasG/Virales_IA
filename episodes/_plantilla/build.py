"""Build genérico: python episodes/<carpeta>/build.py [--stills]"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE.parent.parent), str(HERE)]
from reelforge.timeline import Timeline
from reelforge import audio as AU, render as R
import scenes
from script import BEATS, EPISODE

BUILD, OUT = HERE / "build", HERE / "output"


def load_data():
    """Si el episodio tiene experiment.py, cárgalo aquí y devuelve sus datos."""
    return {}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--stills", action="store_true")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    tl = Timeline(BEATS, BUILD / "tts")
    scenes.setup(tl, load_data(), EPISODE)
    print(f"duración: {tl.duration:.2f} s")
    if args.stills:
        sd = BUILD / "stills"; sd.mkdir(parents=True, exist_ok=True)
        for b in BEATS:
            R.render_still(scenes.draw_frame, b.start + 0.7 * b.dur, sd / f"{b.id}.png")
        return
    slug = EPISODE["slug"]
    wav = BUILD / "mix.wav"
    AU.mix(tl.voice_track(), tl.duration, scenes.sfx_cues(tl), out_wav=wav)
    (OUT / f"{slug}.srt").write_text(tl.srt(scenes.CHUNKS), encoding="utf-8")
    (OUT / "guion_narrado.txt").write_text(tl.script_text(), encoding="utf-8")
    R.render_still(scenes.draw_cover, 1.0, OUT / "portada.png")
    R.render_video(scenes.draw_frame, tl.duration, OUT / f"{slug}.mp4", wav, BUILD / "parts")
    print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(OUT / f"{slug}.mp4")], capture_output=True, text=True).stdout)


if __name__ == "__main__":
    main()
