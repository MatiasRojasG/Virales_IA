# Virales_IA — Detrás del Algoritmo

Clases de IA convertidas en reels educativos.

Sistema reutilizable que transforma una clase (PDF) en videos verticales animados (1080×1920, 60 fps, H.264)
con narración neuronal en español latinoamericano, subtítulos karaoke sincronizados por palabra, ecuaciones
vectoriales, simulaciones reales en Python, música procedural libre de derechos y efectos de sonido.

**Enfoque:** no explicamos la clase; usamos la clase para explicar el mundo (ver `docs/plan_serie.md`).

**Flujo diario:** tendencias de YouTube → 3 propuestas con storyboard en `propuestas/<fecha>/` → el usuario elige →
reel de 40–60 s → QA automático → publicación. Las reglas completas están en [`CLAUDE.md`](CLAUDE.md).

| Episodio | Tema | Video |
|---|---|---|
| viral01 · ¿Por qué la IA siempre dice 7? | muestreo y probabilidades | [`episodes/viral01_numero7/output/`](episodes/viral01_numero7/output/) |
| viral02 · El robot que se cayó una y otra vez | descenso de gradiente (simulación real) | [`episodes/viral02_robot_aprende/output/`](episodes/viral02_robot_aprende/output/) |
| viral03 · La IA que descartaba currículums de mujeres | sesgo en los datos de entrenamiento | [`episodes/viral03_cv_sesgo/output/`](episodes/viral03_cv_sesgo/output/) |

Episodios anteriores (serie de clases): `ep01_foto_nocturna`, `dl01_rostro`, `arq01_dropout`, `lm01_teclado`, `inc01_compra_bloqueada`.

## Uso

```bash
sudo apt-get install -y ffmpeg libegl1 libgl1          # (+ tesseract-ocr tesseract-ocr-spa solo para ep01)
pip install -r requirements.txt

python tools/tendencias.py --dias 30 --amplio --min-vistas 300000 --n 45   # temas virales de IA (YouTube API)

python episodes/viral03_cv_sesgo/build.py --stills   # ritmo de la narración + cuadros de control (segundos)
python episodes/viral03_cv_sesgo/build.py            # MP4 + SRT + guion + portada + QA (≈1–2 min)
python episodes/viral03_cv_sesgo/build.py --qa       # solo el control de calidad
```

Un episodio nuevo: copiar `episodes/viral03_cv_sesgo` (o `_plantilla`), editar `script.py` (guion por bloques) y
`scenes.py` (dibujo por bloque). El `build.py` de cada episodio solo llama a `reelforge.build.main(__file__)`.

### Control de calidad automático (`reelforge/qa.py`)

| Medida | Criterio |
|---|---|
| Formato | 1080×1920, 60 fps, H.264 yuv420p, AAC 48 kHz |
| Sonoridad | −16 a −14 LUFS, pico verdadero ≤ −1 dBTP (el build normaliza a −15 LUFS en dos pasadas) |
| Sincronía | desfase subtítulo–voz < 100 ms, medido en cada arranque de voz tras un silencio |
| Saltos aislados | ningún cuadro que cambie ≥ 4× más que sus vecinos (aparición sin fundido, parpadeo) |
| Loop | diferencia media entre el primer y el último cuadro (informativa) |

Resultado en `build/qa/qa.json` y `build/qa/hoja_video.png`.

### Entorno cloud (Claude Code)
El entorno `virales_ia` instala ffmpeg, skia y edge-tts, permite `speech.platform.bing.com` e inyecta la clave
de la API de YouTube. `reelforge/tts.py` le da a edge-tts la CA del proxy (edge-tts ignora `SSL_CERT_FILE`).

## Arquitectura (`reelforge/`)

```
script.py (Beats con texto)  ──► tts.py: Edge TTS es-MX + marcas de tiempo por palabra (caché)
                                  │
                                  ▼
                           timeline.py: línea de tiempo, cues T(beat, "palabra"), bloques de subtítulos, SRT
                                  │
scenes.py: draw(P, t) ◄───────────┤  (animaciones sincronizadas a palabras exactas)
   │  draw.py (skia): nodos, aristas, glow, texto, imágenes, cámara
   │  mathtex.py: LaTeX (mathtext) → trazos vectoriales coloreables por término
   │  subtitles.py: karaoke, palabras clave en cyan, zona segura
   ▼
render.py: procesos en paralelo → ffmpeg H.264  ◄── audio.py: música procedural + SFX + ducking
   │
build.py: loudnorm −15 LUFS, SRT, portada, hoja de cuadros  ──►  qa.py: formato, LUFS, sincronía, saltos, loop
```

Decisiones técnicas:
- **skia en vez de Manim**: no hay LaTeX en el entorno y skia dibuja ~3 ms/cuadro con antialiasing, glow y
  tipografía Inter; las ecuaciones se obtienen del mathtext de matplotlib como trazos vectoriales.
- **Edge TTS** (gratuito) con voz `es-MX-JorgeNeural`, sintetizada **frase por frase** (`Ph` en `timeline.py`):
  se recortan los silencios del TTS y se insertan pausas diseñadas; cada frase puede llevar su propio ritmo y tono. Entrega
  marcas de tiempo por palabra, así que no hace falta Whisper para sincronizar subtítulos ni animaciones.
  Las voces quedan en caché en `build/tts/`, por lo que re-renderizar no requiere red.
- **Música y efectos sintetizados** con NumPy: sin problemas de licencia.
- Tipografías incluidas en `assets/fonts` (Inter, JetBrains Mono, Liberation Serif — licencia OFL).

## Identidad visual
Fondo `#090D18` · texto blanco · cyan `#00D9FF` (destacados) · violeta `#9B5CFF` (conexiones / vecinos) ·
rosado `#FF4D8D` solo para errores. Acabado: viñeta, profundidad de campo (desenfoque a ¼ de resolución) y cámara con zoom geométrico. Zonas seguras: contenido entre y ≈ 480 y 1300, subtítulos en y ≈ 1390,
margen derecho libre para los botones de la plataforma.
