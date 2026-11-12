"""Render de cuadros con skia en paralelo y codificación H.264 con ffmpeg."""
from __future__ import annotations
import os, subprocess, multiprocessing as mp
from pathlib import Path
from . import config as C
from .draw import P, frame_surface


def _worker(args):
    draw_fn, i0, i1, out, fps, crf = args
    arr, surf = frame_surface()
    cv = surf.getCanvas()
    p = P(cv)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
           "-s", f"{C.W}x{C.H}", "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-tune", "animation", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(i0, i1):
        draw_fn(p, i / fps)
        surf.flushAndSubmit() if hasattr(surf, "flushAndSubmit") else None
        proc.stdin.write(arr.tobytes())
    proc.stdin.close(); proc.wait()
    return out


def render_video(draw_fn, duration, out_mp4, audio_wav, workdir, fps=C.FPS, workers=None, crf=17):
    """draw_fn(P, t) dibuja el cuadro en el tiempo t. Debe ser picklable (función de módulo)."""
    workdir = Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
    nframes = int(round(duration * fps))
    workers = workers or max(1, os.cpu_count() or 1)
    step = (nframes + workers - 1) // workers
    jobs = [(draw_fn, k, min(nframes, k + step), workdir / f"part_{j:02}.mp4", fps, crf)
            for j, k in enumerate(range(0, nframes, step))]
    ctx = mp.get_context("fork")
    with ctx.Pool(len(jobs)) as pool:
        parts = pool.map(_worker, jobs)
    lst = workdir / "parts.txt"
    lst.write_text("".join(f"file '{Path(p).resolve()}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
                    "-i", str(audio_wav), "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", "-shortest", str(out_mp4)], check=True)
    return out_mp4


def render_still(draw_fn, t, out_png):
    import numpy as np
    from PIL import Image
    arr, surf = frame_surface()
    draw_fn(P(surf.getCanvas()), t)
    Image.fromarray(arr[..., :3].copy()).save(out_png)
    return out_png
