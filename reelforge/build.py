"""Build común de episodios. El `build.py` de cada episodio solo llama a `main(__file__)`.

    python episodes/<slug>/build.py --stills   # ritmo de la narración + cuadros de control + hoja
    python episodes/<slug>/build.py            # MP4 + SRT + guion + portada + QA
    python episodes/<slug>/build.py --qa       # solo QA del MP4 ya renderizado

El episodio aporta `script.py` (EPISODE, BEATS y opcionalmente VOICE, RATE) y `scenes.py`
(setup, draw_frame, draw_cover, sfx_cues, music_kw, CHUNKS). Si tiene `experiment.py`, se ejecuta
una vez y su resultado (`build/experiment/sim.json` o lo que devuelva `load()`) llega a `scenes.setup`.
"""
from __future__ import annotations
import argparse, importlib, json, subprocess, sys, time
from pathlib import Path

from . import audio as AU, render as R, tts as TTS, qa as QA
from .timeline import Timeline

LUFS, TP = -15.0, -1.5


def loudnorm(src, dst, I=LUFS, TP=TP):
    """Normaliza a I LUFS en dos pasadas con pico verdadero ≤ TP dBTP."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"loudnorm=I={I}:TP={TP}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    f = (f"loudnorm=I={I}:TP={TP}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(src), "-af", f, "-ar", "48000", str(dst)], check=True)


def rhythm_report(tl):
    """Palabras por segundo y mapa de pausas por bloque (validación de narración antes del render)."""
    lines, tot_w, tot_s = [], 0, 0.0
    for b in tl.beats:
        speech = sum(len(sg) for _, sg in b.segments) / tl.sr
        nw = len(b.tokens)
        pauses = [round(b.segments[i + 1][0] - (b.segments[i][0] + len(b.segments[i][1]) / tl.sr), 2)
                  for i in range(len(b.segments) - 1)]
        pauses.append(round(b.start + b.dur - (b.segments[-1][0] + len(b.segments[-1][1]) / tl.sr), 2))
        wps = nw / max(speech, 1e-3); tot_w += nw; tot_s += speech
        flag = "  ⚠ rápido" if wps > 3.2 else ""
        lines.append(f"  {b.id:<14} {b.start:5.1f}s  {nw:3d} pal  {wps:4.2f} pal/s  pausas {pauses}{flag}")
    print("Ritmo de la narración:")
    print("\n".join(lines))
    print(f"  total: {tot_w} palabras, {tot_w / max(tot_s, 1e-3):.2f} pal/s hablando, {tl.duration:.1f} s de video")


def contact_sheet(items, out_png, w=270, h=480, cols=6):
    from PIL import Image, ImageDraw
    rows = (len(items) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * (h + 24)), (40, 40, 40))
    for i, (pth, lab) in enumerate(items):
        im = Image.open(pth).resize((w, h)); x, y = (i % cols) * w, (i // cols) * (h + 24)
        sheet.paste(im, (x, y + 24)); ImageDraw.Draw(sheet).text((x + 4, y + 4), lab, fill=(255, 255, 255))
    sheet.save(out_png)


def _load_data(here, build):
    if not (here / "experiment.py").exists():
        return {}
    exp = importlib.import_module("experiment")
    if hasattr(exp, "load"):
        return exp.load()
    sim = build / "experiment" / "sim.json"
    if not sim.exists():
        exp.main()
    return json.loads(sim.read_text()) if sim.exists() else {}


def main(build_file, crf=18):
    here = Path(build_file).resolve().parent
    sys.path[:0] = [str(here)]
    ap = argparse.ArgumentParser()
    ap.add_argument("--stills", action="store_true", help="ritmo + cuadros de control (rápido)")
    ap.add_argument("--qa", action="store_true", help="solo control de calidad del MP4 existente")
    ap.add_argument("--workers", type=int, default=None)
    args = ap.parse_args()

    script = importlib.import_module("script"); scenes = importlib.import_module("scenes")
    build, out = here / "build", here / "output"
    out.mkdir(parents=True, exist_ok=True)
    EP = script.EPISODE; slug = EP["slug"]
    tl = Timeline(script.BEATS, build / "tts", voice=getattr(script, "VOICE", TTS.VOICE),
                  rate=getattr(script, "RATE", TTS.RATE))
    scenes.setup(tl, _load_data(here, build), EP)
    print(f"duración: {tl.duration:.2f} s")
    mp4 = out / f"{slug}.mp4"

    if args.qa:
        sys.exit(0 if QA.run(mp4, tl, scenes.CHUNKS, build / "qa") else 1)

    if args.stills:
        rhythm_report(tl)
        sd = build / "stills"; sd.mkdir(parents=True, exist_ok=True)
        for f in sd.glob("*.png"): f.unlink()
        items = []
        for b in tl.beats:
            for frac in (0.15, 0.5, 0.85):
                tt = b.start + frac * b.dur
                pth = sd / f"{b.id}_{int(frac * 100)}.png"
                R.render_still(scenes.draw_frame, tt, pth); items.append((pth, f"{b.id} {tt:.1f}s"))
        for tt, nm in ((0.0, "first"), (tl.duration - 1 / 60, "last")):
            R.render_still(scenes.draw_frame, tt, sd / f"_{nm}.png")
        R.render_still(scenes.draw_cover, 0.0, sd / "_portada.png")
        contact_sheet(items, sd / "hoja.png")
        print("stills en", sd, "(hoja.png, _first/_last para el loop, _portada)")
        return

    raw, wav = build / "mix_raw.wav", build / "mix.wav"
    AU.mix(tl.voice_track(), tl.duration, scenes.sfx_cues(tl), out_wav=raw, music_kw=scenes.music_kw(tl))
    loudnorm(raw, wav)
    (out / f"{slug}.srt").write_text(tl.srt(scenes.CHUNKS), encoding="utf-8")
    (out / "guion_narrado.txt").write_text(tl.script_text(), encoding="utf-8")
    R.render_still(scenes.draw_cover, 0.0, out / "portada.png")
    t0 = time.time()
    R.render_video(scenes.draw_frame, tl.duration, mp4, wav, build / "parts", workers=args.workers, crf=crf)
    print(f"render {time.time() - t0:.1f} s → {mp4}")
    QA.run(mp4, tl, scenes.CHUNKS, build / "qa")
