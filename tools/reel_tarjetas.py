"""Reels de stheq.ia con el formato de los carruseles (1080×1920, 60 fps).

    python tools/reel_tarjetas.py episodes/<slug>/guion.json --stills   # cuadros de control
    python tools/reel_tarjetas.py episodes/<slug>/guion.json            # MP4 + SRT + guion + portada

Cada reel es una secuencia de «tarjetas», con el diseño de una lámina de carrusel:
- arriba: logo, nombre de la cuenta, fecha y barra de avance segmentada (una barra por tarjeta);
- foto de Wikimedia Commons en blanco y negro, con zoom lento y crédito (autor · licencia);
- categoría, número de tarjeta y titular grande; opcionalmente, un dato grande en rojo;
- voz (marca.VOICE) sintetizada por frase y subtítulos karaoke con palabras clave en rojo.

guion.json:
{
 "slug": "tec01_robot_cirujano", "fecha": "18 NOV 2026", "fuente": "Medio · fecha",
 "portada": ["LÍNEA 1", "LÍNEA 2"], "portada_rojo": [1],
 "tarjetas": [
   {"cat": "MEDICINA", "titular": "...", "img": "img/a.jpg", "foco": [0.5, 0.4], "zoom": 1.0,
    "pie": "Robot quirúrgico da Vinci Xi", "dato": "24 %",
    "frases": [{"t": "Texto con *clave*", "pausa": 0.4, "tono": "Q" | "WOW", "lento": true}]}
 ]
}
"""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path
import skia
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT), str(ROOT / "tools")]
import carrusel as K
from reelforge import config as C, marca as M, subtitles as SUB, audio as AU, render as R
from reelforge.timeline import Timeline, Beat, Ph
from reelforge.draw import paint, color4, font
from reelforge.ease import clamp, prog, out_cubic, out_back, in_out_cubic

W, H = C.W, C.H
X0, X1 = 64, 1016
FG, GRAY, DIM, RED, BG = M.FG, M.GRAY, M.DIM, M.RED, M.BG
FOTO_Y0, FOTO_Y1 = 360, 1040
G = {}                                   # estado del reel (para draw_frame, que debe ser de módulo)
_cache = {}


def foto_card(base, card, zoom_extra=0.0):
    key = (card["img"], round(zoom_extra, 3))
    if key not in _cache:
        if len(_cache) > 64: _cache.clear()
        _cache[key] = K.foto(base / card["img"], W, FOTO_Y1 - FOTO_Y0, card.get("foco", [0.5, 0.5]),
                             card.get("zoom", 1.0) + zoom_extra)
    return _cache[key]


def cabecera(p, fecha, k, n, frac):
    logo = Image.open(K.LOGO); h = 44; w = round(logo.width * h / logo.height)
    if "logo" not in _cache:
        _cache["logo"] = K.skimg(logo.resize((w * 2, h * 2), Image.LANCZOS))
    p.img(_cache["logo"], X0, 256, X0 + w, 256 + h, nearest=False)
    p.text(M.NAME, X0 + w + 18, 288, 26, FG, 0.85, face=C.FONT_BOLD, align="left", tracking=1.5)
    p.text(fecha, X1, 288, 24, FG, 0.7, face=C.FONT_SEMI, align="right", tracking=2)
    # barra de avance segmentada
    gap = 8; sw = (X1 - X0 - gap * (n - 1)) / n
    for i in range(n):
        x = X0 + i * (sw + gap)
        p.rect(x, 322, x + sw, 328, FG, 0.22, radius=3)
        f = 1.0 if i < k else (frac if i == k else 0.0)
        if f > 0: p.rect(x, 322, x + sw * f, 328, FG, 0.95, radius=3)


def tarjeta(p, base, card, k, n, lt, dur, a=1.0, dx=0.0):
    """Dibuja la tarjeta k en su tiempo local lt (s) de duración dur."""
    if a <= 0: return
    with p.layer(a):
        # foto con zoom lento (Ken Burns) en pasos pequeños para cachear
        z = round(0.06 * clamp(lt / max(dur, 0.1)), 2)
        p.img(foto_card(base, card, z), 0, FOTO_Y0, W, FOTO_Y1, nearest=False)
        K.degradado(p, FOTO_Y0, FOTO_Y0 + 160, 1.0, 0.0)
        K.degradado(p, FOTO_Y1 - 320, FOTO_Y1 + 2, 0.0, 1.0)
        cr = K.credito(base / card["img"])
        if card.get("pie"): cr = card["pie"] + "  ·  " + cr
        if cr: p.text(cr, X1, FOTO_Y1 - 22, 18, FG, 0.5, face=C.FONT_MED, align="right")
        # dato grande sobre la foto
        if card.get("dato"):
            ad = prog(lt, 0.35, 0.8)
            if ad > 0:
                s = 0.8 + 0.2 * out_back(clamp((lt - 0.35) / 0.5))
                fs = 210
                wd = font(fs, C.FONT_BLACK).measureText(card["dato"])
                if wd > 900: fs = fs * 900 / wd                      # el dato siempre cabe en pantalla
                with p.transform(0, 0, s, cx=W / 2, cy=760):
                    p.text(card["dato"], W / 2, 760 + fs * 0.35, fs, RED, ad, face=C.FONT_BLACK, glow=0.6, shadow=True)
        with p.transform(dx, 0):
            y = 1112
            ai = prog(lt, 0.0, 0.4)
            p.text(f"{k + 1:02d}", X0, y, 40, RED, ai, face=C.FONT_BLACK, align="left")
            with p.layer(ai):
                K.pill(p, card["cat"], X0 + 78, y - 2, FG)
            tl = K.wrap(card["titular"], 64, C.FONT_BLACK, X1 - X0)
            if len(tl) > 2: tl = K.wrap(card["titular"], 54, C.FONT_BLACK, X1 - X0)
            ts = 64 if len(tl) <= 2 else 54
            yy = y + 22
            for j, ln in enumerate(tl[:3]):
                aj = prog(lt, 0.1 + 0.08 * j, 0.5 + 0.08 * j)
                yy += ts * 1.08
                p.text(ln, X0 - 2 + 30 * (1 - out_cubic(aj)), yy - ts * 0.15, ts, FG, aj, face=C.FONT_BLACK, align="left")


def draw_frame(p, t):
    p.c.clear(color4(BG))
    cards, base, beats = G["cards"], G["base"], G["beats"]
    n = len(cards)
    k = max(i for i, b in enumerate(beats) if t >= b.start - 0.001) if t >= beats[0].start else 0
    b = beats[k]; lt = t - b.start
    frac = clamp(lt / max(b.dur, 0.1))
    # transición: la tarjeta anterior se desvanece hacia la izquierda en 0,35 s
    tr = 0.35
    if k > 0 and lt < tr:
        u = in_out_cubic(lt / tr)
        pb = beats[k - 1]
        tarjeta(p, base, cards[k - 1], k - 1, n, t - pb.start, pb.dur, a=1 - u, dx=-60 * u)
        tarjeta(p, base, cards[k], k, n, lt, b.dur, a=u, dx=60 * (1 - u))
    else:
        tarjeta(p, base, cards[k], k, n, lt, b.dur)
    if k == n - 1 and G.get("fuente"):
        p.text("Fuente: " + G["fuente"], X0, FOTO_Y0 + 48, 22, FG, 0.85 * prog(lt, 0.6, 1.0), face=C.FONT_SEMI, align="left", shadow=True)
    M.vignette(p, 0.35)
    cabecera(p, G["fecha"], k, n, frac)
    M.sub_band(p)
    SUB.draw(p, G["chunks"], t, **M.SUB_COLORS)


def draw_cover(p, t=0.0):
    p.c.clear(color4(BG))
    card = G["cards"][0]
    p.img(foto_card(G["base"], card), 0, FOTO_Y0, W, FOTO_Y1, nearest=False)
    K.degradado(p, FOTO_Y0, FOTO_Y0 + 160, 1.0, 0.0)
    K.degradado(p, FOTO_Y1 - 380, FOTO_Y1 + 2, 0.0, 1.0)
    cabecera(p, G["fecha"], 0, len(G["cards"]), 0.0)
    y = 1150
    for i, ln in enumerate(G.get("portada", [card["titular"]])):
        p.text(ln, X0 - 4, y, 96, RED if i in G.get("portada_rojo", []) else FG, 1, face=C.FONT_BLACK, align="left")
        y += 104


def beats_de(spec):
    beats = []
    for i, card in enumerate(spec["tarjetas"]):
        phs = []
        for f in card["frases"]:
            tono = {"Q": M.Q, "WOW": M.WOW}.get(f.get("tono"))
            phs.append(Ph(f["t"], pause=f.get("pausa", 0.3), pitch=tono, rate=M.SLOW if f.get("lento") else None))
        beats.append(Beat(f"t{i:02d}", phs))
    return beats


def sfx(beats, cards):
    cues = [(0.0, "swell", 0.3)]
    for b, c in zip(beats[1:], cards[1:]):
        cues.append((max(0, b.start - 0.15), "whoosh", 0.35))
    for b, c in zip(beats, cards):
        if c.get("dato"): cues += [(b.start + 0.35, "pop", 0.45)]
    return cues


def loudnorm(mp4, I=-14.5, TP=-1.0):
    f = f"loudnorm=I={I}:TP={TP}:LRA=11"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-af", f + ":print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
    f2 = (f + f":measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    tmp = mp4.with_suffix(".tmp.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(mp4), "-c:v", "copy", "-af", f2, "-ar", "48000",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(tmp)], check=True)
    tmp.replace(mp4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("guion"); ap.add_argument("--stills", action="store_true"); ap.add_argument("--workers", type=int)
    a = ap.parse_args()
    js = Path(a.guion).resolve(); base = js.parent
    spec = json.loads(js.read_text())
    build, out = base / "build", base / "output"; out.mkdir(parents=True, exist_ok=True)
    beats = beats_de(spec)
    tl = Timeline(beats, build / "tts", voice=M.VOICE, rate=M.RATE, pitch=M.PITCH)
    G.update(cards=spec["tarjetas"], base=base, beats=beats, fecha=spec["fecha"], fuente=spec.get("fuente"),
             portada=spec.get("portada"), portada_rojo=spec.get("portada_rojo", []),
             chunks=tl.chunks(SUB.measure, max_words=4))
    print(f"duración: {tl.duration:.2f} s")
    if a.stills:
        sd = build / "stills"; sd.mkdir(parents=True, exist_ok=True)
        for f in sd.glob("*.png"): f.unlink()
        for b in beats:
            for fr in (0.15, 0.6):
                R.render_still(draw_frame, b.start + fr * b.dur, sd / f"{b.id}_{int(fr * 100)}.png")
        R.render_still(draw_cover, 0, sd / "portada.png")
        print("stills en", sd); return
    slug = spec["slug"]
    wav = build / "mix.wav"
    AU.mix(tl.voice_track(), tl.duration, sfx(beats, spec["tarjetas"]), out_wav=wav,
           music_kw={"arp_from": beats[1].start if len(beats) > 1 else 0.0})
    (out / f"{slug}.srt").write_text(tl.srt(G["chunks"]), encoding="utf-8")
    (out / "guion_narrado.txt").write_text(tl.script_text(), encoding="utf-8")
    R.render_still(draw_cover, 0.0, out / "portada.png")
    t0 = time.time(); mp4 = out / f"{slug}.mp4"
    R.render_video(draw_frame, tl.duration, mp4, wav, build / "parts", workers=a.workers)
    loudnorm(mp4)
    print(f"render {time.time() - t0:.1f} s ->", mp4)


if __name__ == "__main__":
    main()
