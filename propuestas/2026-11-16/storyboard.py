"""Storyboard (fotogramas clave) de las 3 propuestas del día. Uso: python propuestas/2026-11-16/storyboard.py"""
import json, math, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from reelforge import config as C
from reelforge.draw import P, frame_surface, paint, vignette, font
from PIL import Image, ImageDraw

AM = (1.0, 0.72, 0.3); GR = (0.55, 0.6, 0.72)


def sub(p, txt):
    p.text(txt, 540, 1410, 58, C.WHITE, 1, face=C.FONT_XBOLD)


def person(p, x, y, s=1.0, col=GR, a=1.0):
    p.circle(x, y - 40 * s, 28 * s, col, a); p.rect(x - 38 * s, y - 6 * s, x + 38 * s, y + 60 * s, col, a, radius=30 * s)


def paper(p, x, y, txt_lines=5, a=1.0, w=260, h=330):
    p.rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, C.PAPER, a, radius=14)
    for k in range(txt_lines):
        p.line(x - w / 2 + 30, y - h / 2 + 50 + k * 48, x + w / 2 - 30 - (60 if k == txt_lines - 1 else 0), y - h / 2 + 50 + k * 48, (0.7, 0.73, 0.8), a, w=10)


# ---------------------------------------------------------------- A · el profe con IA
def A1(p):
    paper(p, 540, 820)
    p.rect(300, 1010, 780, 1110, C.PINK, 1, radius=30)
    p.text("⚠ 98 % escrito por IA", 540, 1075, 44, C.WHITE, 1, face=C.FONT_BLACK)
    person(p, 540, 560, 1.3, C.VIOLET)
    sub(p, "El detector dice que la hizo una IA…")


def A2(p):
    paper(p, 400, 820, w=220, h=280); person(p, 760, 820, 1.6)
    p.text("…", 760, 650, 90, C.WHITE, 1, face=C.FONT_BLACK)
    p.text("✓ la escribiste tú", 400, 1030, 40, C.CYAN, 1, face=C.FONT_BOLD)
    sub(p, "Pero la escribiste tú.")


def A3(p):
    for k in range(30):
        r, c = divmod(k, 6); x, y = 200 + c * 136, 620 + r * 140
        person(p, x, y, 0.7, C.VIOLET if k in (3, 14, 22) else GR)
    p.text("30 estudiantes · 3 usaron IA", 540, 540, 40, C.WHITE, 1, face=C.FONT_BOLD)
    sub(p, "Imagina un curso de treinta…")


def A4(p):
    for k in range(30):
        r, c = divmod(k, 6); x, y = 200 + c * 136, 620 + r * 140
        hot = k in (3, 14, 22); alarm = k in (3, 14, 22, 8, 19, 27)
        person(p, x, y, 0.7, C.VIOLET if hot else GR)
        if alarm: p.circle(x, y - 10, 62, C.PINK, 1, stroke=6)
    p.text("6 alarmas", 540, 540, 60, C.PINK, 1, face=C.FONT_BLACK)
    sub(p, "El detector marca a seis…")


def A5(p):
    for k, ok in enumerate([1, 1, 1, 0, 0, 0]):
        x = 140 + k * 160
        person(p, x, 820, 0.9, C.VIOLET if ok else GR)
        p.text("IA" if ok else "inocente", x, 960, 30, C.VIOLET if ok else C.PINK, 1, face=C.FONT_BOLD)
    p.text("la mitad era inocente", 540, 620, 64, C.CYAN, 1, face=C.FONT_BLACK)
    sub(p, "…y la mitad era inocente.")


# ---------------------------------------------------------------- B · pregunta trampa
def B1(p):
    p.rect(110, 560, 970, 1260, (0.08, 0.10, 0.16), 1, radius=40)
    p.rect(330, 620, 930, 720, C.VIOLET, 1, radius=50); p.text("¿Cuántas R tiene «ferrocarril»?", 630, 685, 34, C.WHITE, 1, face=C.FONT_SEMI)
    p.rect(150, 780, 560, 880, (0.16, 0.18, 0.26), 1, radius=50); p.text("Tiene 3 R.", 355, 845, 40, C.WHITE, 1, face=C.FONT_SEMI)
    p.text("✗", 620, 860, 90, C.PINK, 1, face=C.FONT_BLACK)
    sub(p, "La IA que escribe ensayos… falla esto.")


def B2(p):
    word = "FERROCARRIL"
    for k, ch in enumerate(word):
        x = 120 + k * 80
        p.rect(x, 780, x + 70, 880, C.CYAN if ch == "R" else (0.2, 0.22, 0.3), 1, radius=12)
        p.text(ch, x + 35, 850, 52, C.BG if ch == "R" else C.WHITE, 1, face=C.FONT_BLACK)
    p.text("tú ves 11 letras · 4 son R", 540, 700, 44, C.WHITE, 1, face=C.FONT_BOLD)
    sub(p, "Tú ves letras.")


def B3(p):
    for k, (part, col) in enumerate([("ferro", C.VIOLET), ("carr", C.CYAN), ("il", AM)]):
        x = 260 + k * 290
        p.rect(x - 120, 760, x + 120, 900, col, 1, radius=26)
        p.text(part, x, 852, 58, C.BG, 1, face=C.FONT_BLACK)
    p.text("la IA ve pedazos", 540, 680, 52, C.WHITE, 1, face=C.FONT_BLACK)
    sub(p, "La IA ve pedazos de palabras…")


def B4(p):
    for k, (part, col) in enumerate([("ferro", C.VIOLET), ("carr", C.CYAN), ("il", AM)]):
        x = 260 + k * 290
        p.text(part, x, 680, 40, col, 1, face=C.FONT_BOLD)
        rng = np.random.default_rng(k)
        for j in range(6):
            v = rng.uniform(-1, 1); y = 740 + j * 70
            p.rect(x - 90, y, x + 90, y + 56, col, 0.35 + 0.6 * abs(v), radius=10)
            p.text(f"{v:+.2f}".replace(".", ","), x, y + 40, 30, C.WHITE, 1, face=C.FONT_BOLD)
    sub(p, "…convertidos en números.")


def B5(p):
    p.rect(110, 600, 970, 1150, (0.08, 0.10, 0.16), 1, radius=40)
    p.text("deletréala primero:", 540, 700, 40, C.GRAY, 1, face=C.FONT_MED)
    p.text("F-E-R-R-O-C-A-R-R-I-L", 540, 820, 56, C.WHITE, 1, face=C.FONT_BLACK)
    p.text("4 R ✓", 540, 980, 90, C.CYAN, 1, face=C.FONT_BLACK)
    sub(p, "Truco: pídele que la deletree.")


# ---------------------------------------------------------------- C · el robot que se cayó mil veces
SIM = json.load(open(HERE / "sim_salto.json"))


def robot(p, x, y, s=1.0, col=C.CYAN, a=1.0):
    p.rect(x - 34 * s, y - 70 * s, x + 34 * s, y - 10 * s, col, a, radius=20 * s)
    p.circle(x - 12 * s, y - 46 * s, 7 * s, C.BG, a); p.circle(x + 12 * s, y - 46 * s, 7 * s, C.BG, a)
    p.line(x - 18 * s, y - 10 * s, x - 22 * s, y + 20 * s, col, a, w=8 * s); p.line(x + 18 * s, y - 10 * s, x + 22 * s, y + 20 * s, col, a, w=8 * s)


def scene_jump(p, ks, cols):
    X0, Y0, S = 140, 1150, 120
    p.rect(X0 + 6 * S - 60, Y0 - 2 * S, X0 + 6 * S + 120, Y0 - 2 * S + 30, C.WHITE, 1, radius=8)
    p.line(60, Y0 + 20, 1020, Y0 + 20, C.DIM, 1, w=6)
    for k, col in zip(ks, cols):
        v, ang = SIM["hist"][k]
        t = np.linspace(0, 3, 80); x = v * np.cos(ang) * t; y = v * np.sin(ang) * t - 4.9 * t * t
        pts = [(X0 + xx * S, Y0 - yy * S) for xx, yy in zip(x, y) if yy > -0.2 and xx < 7.2]
        for (a1, b1), (a2, b2) in zip(pts, pts[1:]): p.line(a1, b1, a2, b2, col, 0.9, w=5)
    robot(p, X0, Y0)


def C1(p):
    scene_jump(p, [0], [C.PINK]); robot(p, 520, 1170, 1.0, C.PINK)
    p.text("intento 1", 540, 600, 50, C.PINK, 1, face=C.FONT_BLACK)
    sub(p, "Este robot se cayó… muchas veces.")


def C2(p):
    scene_jump(p, [0, 3, 8, 15], [C.PINK, C.PINK, AM, AM])
    p.text("cada caída = un error medido", 540, 600, 40, C.WHITE, 1, face=C.FONT_BOLD)
    sub(p, "Cada intento fallido deja una pista.")


def C3(p):
    p.text("fuerza", 300, 640, 40, C.WHITE, 1, face=C.FONT_BOLD); p.text("ángulo", 780, 640, 40, C.WHITE, 1, face=C.FONT_BOLD)
    for x, frac in ((300, 0.4), (780, 0.3)):
        p.circle(x, 820, 110, C.BG2, 1); p.circle(x, 820, 110, C.VIOLET, 1, stroke=8)
        a = -math.pi * 1.25 + frac * math.pi * 1.5
        p.line(x, 820, x + 80 * math.cos(a), 820 + 80 * math.sin(a), C.CYAN, 1, w=10)
        p.arrow(x - 60, 980, x + 60, 980, C.CYAN, 1, w=6)
    p.text("girar un poquito hacia donde baja el error", 540, 1100, 34, C.CYAN, 1, face=C.FONT_SEMI)
    sub(p, "Ajusta fuerza y ángulo… un poquito.")


def C4(p):
    L = np.array(SIM["loss"]); x0, x1, y0, y1 = 140, 940, 620, 1150
    p.line(x0, y1, x1, y1, C.DIM, 1, w=4); p.line(x0, y0, x0, y1, C.DIM, 1, w=4)
    pts = [(x0 + (x1 - x0) * k / (len(L) - 1), y1 - (y1 - y0) * l / L.max()) for k, l in enumerate(L)]
    for (a1, b1), (a2, b2) in zip(pts, pts[1:]): p.line(a1, b1, a2, b2, C.CYAN, 1, w=6)
    p.text("error", x0 + 10, y0 - 20, 34, C.WHITE, 1, face=C.FONT_BOLD, align="left")
    p.text("intentos →", x1, y1 + 50, 30, C.GRAY, 1, face=C.FONT_MED, align="right")
    sub(p, "El error baja, intento tras intento.")


def C5(p):
    scene_jump(p, [60], [C.CYAN]); robot(p, 140 + 6 * 120 + 30, 1150 - 2 * 120, 1.0, C.CYAN)
    p.text("¡lo logró!", 540, 600, 70, C.CYAN, 1, face=C.FONT_BLACK)
    sub(p, "Así aprende una red neuronal.")


OPTS = {"A": [A1, A2, A3, A4, A5], "B": [B1, B2, B3, B4, B5], "C": [C1, C2, C3, C4, C5]}


def main():
    w, h = 324, 576
    for name, frames in OPTS.items():
        sheet = Image.new("RGB", (w * 5 + 40, h + 70), (9, 13, 24))
        for j, fn in enumerate(frames):
            arr, surf = frame_surface(); p = P(surf.getCanvas())
            p.background(1.0); fn(p); vignette(p, 0.4)
            im = Image.fromarray(arr[..., :3].copy()).resize((w, h))
            sheet.paste(im, (20 + j * w, 50))
        ImageDraw.Draw(sheet).text((24, 14), f"Opción {name}", fill=(0, 217, 255))
        sheet.save(HERE / f"storyboard_{name}.png")
    print("ok")


if __name__ == "__main__":
    main()
