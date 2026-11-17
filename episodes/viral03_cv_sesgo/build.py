"""Construye «La IA que descartaba currículums de mujeres».

    python episodes/viral03_cv_sesgo/build.py            # video final
    python episodes/viral03_cv_sesgo/build.py --stills   # solo cuadros de control
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
import scenes
from script import BEATS, EPISODE, VOICE, RATE

BUILD = HERE / "build"
OUT = HERE / "output"


def load_data():
    return {}


def loudnorm(src, dst, I=-15.0, TP=-1.5):
    """Normaliza a -15 LUFS (dos pasadas) con pico verdadero <= -1,5 dBTP."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    f = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", f, "-ar", "48000", str(dst)], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true")
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_data()
    tl = Timeline(BEATS, BUILD / "tts", voice=VOICE, rate=RATE)
    scenes.setup(tl, data, EPISODE)
    print(f"duración: {tl.duration:.2f} s")

    if args.stills:
        sd = BUILD / "stills"; sd.mkdir(parents=True, exist_ok=True)
        for f in sd.glob("*.png"): f.unlink()
        ims = []
        for b in BEATS:
            for frac in (0.15, 0.5, 0.85):
                tt = b.start + frac * b.dur
                pth = sd / f"{b.id}_{int(frac*100)}.png"
                R.render_still(scenes.draw_frame, tt, pth); ims.append((pth, f"{b.id} {tt:.1f}s"))
        for tt, nm in ((0.0, "first"), (tl.duration - 1 / 60, "last")):
            R.render_still(scenes.draw_frame, tt, sd / f"_{nm}.png")
        from PIL import Image, ImageDraw
        w, h = 270, 480; cols = 6; rows = (len(ims) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * w, rows * (h + 24)), (40, 40, 40))
        for i, (pth, lab) in enumerate(ims):
            im = Image.open(pth).resize((w, h)); x, y = (i % cols) * w, (i // cols) * (h + 24)
            sheet.paste(im, (x, y + 24)); ImageDraw.Draw(sheet).text((x + 4, y + 4), lab, fill=(255, 255, 255))
        sheet.save(sd / "hoja.png")
        print("stills en", sd); return

    slug = EPISODE["slug"]
    # audio
    wav = BUILD / "mix.wav"
    raw = BUILD / "mix_raw.wav"
    AU.mix(tl.voice_track(), tl.duration, scenes.sfx_cues(tl), out_wav=raw, music_kw=scenes.music_kw(tl))
    loudnorm(raw, wav)
    # subtítulos y guion
    (OUT / f"{slug}.srt").write_text(tl.srt(scenes.CHUNKS), encoding="utf-8")
    (OUT / "guion_narrado.txt").write_text(tl.script_text(), encoding="utf-8")
    # portada (cuadro del hook con el resultado)
    R.render_still(scenes.draw_cover, 0.0, OUT / "portada.png")
    # video
    t0 = time.time()
    mp4 = OUT / f"{slug}.mp4"
    R.render_video(scenes.draw_frame, tl.duration, mp4, wav, BUILD / "parts", workers=args.workers, crf=18)
    print(f"render {time.time() - t0:.1f} s ->", mp4)
    info = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                           "stream=codec_name,width,height,r_frame_rate,sample_rate,channels:format=duration",
                           "-of", "compact", str(mp4)], capture_output=True, text=True).stdout
    print(info)


if __name__ == "__main__":
    main()
