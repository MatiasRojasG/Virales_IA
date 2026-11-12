"""reelforge: motor reutilizable para convertir clases en reels educativos animados.

Módulos:
  config     identidad visual (colores, tipografías, formato)
  ease       funciones de easing e interpolación
  draw       primitivas vectoriales sobre skia (texto, nodos, aristas, glow, imágenes)
  mathtex    ecuaciones LaTeX (mathtext de matplotlib) -> trazos vectoriales coloreables
  tts        narración con Edge TTS + marcas de tiempo por palabra
  timeline   guion -> línea de tiempo, cues por palabra, subtítulos y SRT
  subtitles  subtítulos karaoke incrustados
  audio      música procedural, efectos de sonido y mezcla con ducking
  render     render paralelo de cuadros con skia + ffmpeg (H.264)
"""
