# ReelForge · Detrás del Algoritmo — reglas permanentes

Las instrucciones nuevas complementan estas. Ante contradicciones, prima la instrucción explícita más reciente.

## Enfoque narrativo
- No explicar la clase: usar sus conceptos para explicar el mundo real. El PDF es fuente de conocimiento, no guion. Se ignora lo administrativo (fechas, evaluaciones, profesores, instituciones).
- Una historia y un problema por video. Arco: situación cotidiana → problema → por qué es difícil → intuición → descubrimiento → solución → resultado.
- El porqué va antes del cómo. Cada frase responde a la pregunta que dejó la anterior.
- Ningún término técnico, cifra ni fórmula sin contexto. El nombre técnico se dice después de entender la idea.
- Sin lenguaje de profesor («hoy aprenderemos», «en esta clase»), sin definiciones iniciales ni enumeraciones académicas.
- No inventar estadísticas ni exagerar capacidades. Los ejemplos hipotéticos se rotulan en pantalla («ejemplo ilustrativo», «simulación propia», «datos simulados»).
- Preferir simulaciones/experimentos reales ejecutados en el repo (NumPy) y distinguir resultados propios de los de la fuente.
- El cierre responde la pregunta del inicio. Idealmente, el último cuadro empalma con el primero (loop).

## Retención
- El hook está en el cuadro 0: problema visual inmediato, sin intro ni pantalla de presentación.
- Curiosidad progresiva, preguntas abiertas y un payoff satisfactorio. Una idea visual principal por escena.
- Duración: 50–90 s sugerido, ajustable a la historia. Si no cabe, dividir en episodios.

## Restricciones visuales permanentes
- **Nunca** mostrar dentro del video títulos, números de episodio, encabezados, nombres de unidades ni banners/etiquetas superiores. Títulos y numeración quedan solo como metadatos (`EPISODE` en `script.py`, README).
- Comenzar directamente con la historia.
- Texto en pantalla solo cuando ayuda a comprender (cifras explicadas, rótulos de simulación, etiquetas de diagramas).
- Subtítulos y elementos importantes dentro de las zonas seguras (`reelforge/config.py`). Contenido entre y≈480 y 1300. Subtítulos en y≈1390. Notas al pie en y≈1290–1305.

## Identidad
- 1080×1920, 9:16, 60 fps, H.264 + AAC 48 kHz.
- Colores: fondo #090D18, cyan #00D9FF, violeta #9B5CFF, blanco #F5F7FA. Rosado #FF4D8D solo para errores/alertas.
- Tipografía Inter (en `assets/fonts`). Motion graphics minimalistas, easing, morphing, continuidad espacial, viñeta y profundidad de campo.

## Voz, subtítulos y audio
- Edge TTS `es-MX-JorgeNeural` a +18 %, sintetizado por frase (`Ph`): silencios recortados, pausas diseñadas, `pitch="+5Hz"` en preguntas y `rate="-4%"` en énfasis.
- Subtítulos karaoke de hasta 4 palabras, con palabras clave `*así*` en cyan y alineación por palabra (sin Whisper).
- Música procedural (`reelforge/audio.py`) con `music_kw` (arpegio desde el descubrimiento, pulso en el clímax, silencio en el suspenso). SFX discretos.

## Pipeline (no duplicar componentes)
- Motor: `reelforge/` (draw, ease, mathtex, tts, timeline, subtitles, audio, render).
- Cada episodio va en `episodes/<slug>/` con `script.py` (EPISODE + BEATS), `scenes.py` (setup, draw_frame, draw_cover, sfx_cues, music_kw), `build.py`, opcionalmente `experiment.py`, y `README.md`. Plantilla: copiar un episodio reciente y modificar solo lo necesario.
- Comandos: `python episodes/<slug>/build.py --stills` (cuadros de control) y `python episodes/<slug>/build.py` (MP4 + SRT + guion + portada).

## Validación obligatoria (antes de renderizar)
1. ¿Interesa a alguien sin conocimientos de IA?
2. ¿El problema aparece antes de la solución?
3. ¿Cada concepto surge por una necesidad narrativa?
4. ¿Se entiende sin conocimientos previos y sin saltos?
5. ¿Las animaciones muestran lo que dice la voz y tienen continuidad?
6. ¿El cierre responde la pregunta inicial?
7. ¿Es científicamente correcto, con aclaraciones visibles?

## Control de calidad después del render
- Hoja de cuadros clave sin solapamientos, sin «saltos aislados» (diferencia entre cuadros), desfase subtítulos–voz < 100 ms, −14 a −16 LUFS y pico −1 dBFS.
- Commit y push a la rama de trabajo. Entregar MP4, SRT, guion, portada y código.

## Narrativa y ritmo cinematográfico (regla permanente)
- **Contexto antes del problema.** Ningún dato, porcentaje, fórmula o término sin explicación previa. Cada frase nace de la anterior. El espectador siempre sabe qué ocurre, por qué importa y qué intentamos descubrir. Sin saltos ni cambios repentinos de tema.
- **Escribir para ser escuchado.**
  - Usar comas, preguntas, «…» y silencios intencionales. Alternar frases cortas y largas.
  - Nunca recitar números ni explicaciones complejas rápido (frases con cifras van con `rate` más lento).
  - Pausas orientativas (`Ph.pause`), adaptadas al ritmo y sin aplicarlas mecánicamente:

    | Momento | Pausa |
    |---|---|
    | Coma | 0,15–0,3 s |
    | Fin de idea | 0,3–0,5 s |
    | Antes de una revelación | 0,5–0,9 s |
    | Después de un descubrimiento | 0,6–1,2 s |

- **Arco emocional.** Curiosidad → expectativa → conflicto → suspenso → revelación → comprensión → satisfacción.
  - Pequeñas preguntas que se resuelven de a poco, con anticipación antes de cada resultado.
  - Sin suspenso artificial, exagerado ni repetido. El descubrimiento debe sentirse merecido y lógico.
- **Sincronía.**
  - La animación sigue a la voz y no revela una respuesta antes de que la narración la prepare.
  - En las pausas importantes, mantener movimiento visual con significado.
  - Transiciones, música y SFX caen sobre las revelaciones.
  - Dar tiempo para observar antes de avanzar. El montaje se ajusta a la voz, no al revés.
- **Validación antes del render final.**
  - Revisar la narración completa: ritmo en palabras por segundo, mapa de pausas y que no suene apresurada.
  - Comprobar el contexto de cada concepto y que cada pausa aporte comprensión o emoción.
  - Eliminar redundancias y suspenso forzado.
  - Límite práctico: no puedo escuchar el audio. Lo verifico con métricas (pausas, velocidad, cobertura) y se lo indico al usuario.
- **Principio.** No explicar mucha información rápido: que el espectador sienta curiosidad, descubra algo y lo comprenda.
