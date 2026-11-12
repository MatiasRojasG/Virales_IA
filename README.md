# Virales_IA — clases de IA convertidas en reels educativos

Sistema reutilizable que transforma una clase (PDF) en videos verticales animados (1080×1920, 30 fps, H.264)
con narración neuronal en español de Chile, subtítulos karaoke sincronizados por palabra, ecuaciones
vectoriales, simulaciones reales en Python, música procedural libre de derechos y efectos de sonido.

**Serie actual:** Modelos gráficos no dirigidos / Redes de Markov (EPG4003, 12-nov-2026) — ver [`docs/plan_serie.md`](docs/plan_serie.md).

| Episodio | Estado | Video |
|---|---|---|
| 01 · El documento ilegible | ✅ | [`episodes/ep01_restauracion_documento/output/`](episodes/ep01_restauracion_documento/) |
| 02–10 | guion pendiente | — |

## Uso

```bash
sudo apt-get install -y ffmpeg libegl1 libgl1 tesseract-ocr tesseract-ocr-spa
pip install -r requirements.txt

python episodes/ep01_restauracion_documento/build.py --stills   # cuadros de control (rápido)
python episodes/ep01_restauracion_documento/build.py            # MP4 + SRT + guion + portada
```

Un episodio nuevo: `cp -r episodes/_plantilla episodes/ep02_redes_sin_flechas`, editar `script.py`
(guion) y `scenes.py` (una función de dibujo por bloque), y ejecutar su `build.py`.

## Arquitectura (`reelforge/`)

```
script.py (Beats con texto)  ──► tts.py: Edge TTS es-CL + marcas de tiempo por palabra (caché)
                                  │
                                  ▼
                           timeline.py: línea de tiempo, cues T(beat, "palabra"), bloques de subtítulos, SRT
                                  │
scenes.py: draw(P, t) ◄───────────┤  (animaciones sincronizadas a palabras exactas)
   │  draw.py (skia): nodos, aristas, glow, texto, imágenes, cámara
   │  mathtex.py: LaTeX (mathtext) → trazos vectoriales coloreables por término
   │  subtitles.py: karaoke, palabras clave en cyan, zona segura
   ▼
render.py: 4 procesos en paralelo → ffmpeg H.264  ◄── audio.py: música procedural + SFX + ducking
```

Decisiones técnicas:
- **skia en vez de Manim**: no hay LaTeX en el entorno y skia dibuja ~3 ms/cuadro con antialiasing, glow y
  tipografía Inter; las ecuaciones se obtienen del mathtext de matplotlib como trazos vectoriales.
- **Edge TTS** (gratuito) con voz `es-CL-LorenzoNeural` (alternativa: `es-CL-CatalinaNeural`). Entrega
  marcas de tiempo por palabra, así que no hace falta Whisper para sincronizar subtítulos ni animaciones.
  Las voces quedan en caché en `build/tts/`, por lo que re-renderizar no requiere red.
- **Música y efectos sintetizados** con NumPy: sin problemas de licencia.
- Tipografías incluidas en `assets/fonts` (Inter, JetBrains Mono, Liberation Serif — licencia OFL).

## Identidad visual
Fondo `#090D18` · texto blanco · cyan `#00D9FF` (destacados) · violeta `#9B6BFF` (conexiones / vecinos) ·
rosado `#FF4D8D` solo para errores. Zonas seguras: contenido entre y = 240 y 1300, subtítulos en y ≈ 1390,
margen derecho libre para los botones de la plataforma.
