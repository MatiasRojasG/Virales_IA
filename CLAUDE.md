# ReelForge · stheq.ia — reglas permanentes

**Una sola cuenta: stheq.ia** (antes «Detrás del Algoritmo»). Publica todos los videos: IA y tecnología, ciencia cotidiana y cuidado personal basado en evidencia (lo que antes era «looksmax»). Los episodios publicados antes de esta regla quedan como están.

Las instrucciones nuevas complementan estas. Ante contradicciones, prima la instrucción explícita más reciente.

## Enfoque narrativo
- No explicar la clase: usar sus conceptos para explicar el mundo real. El PDF es fuente de conocimiento, no guion. Se ignora lo administrativo (fechas, evaluaciones, profesores, instituciones).
- Una historia y un problema por video. Arco: situación cotidiana → problema → por qué es difícil → intuición → descubrimiento → solución → resultado.
- El porqué va antes del cómo. Cada frase responde a la pregunta que dejó la anterior.
- Ningún término técnico, cifra ni fórmula sin contexto. El nombre técnico se dice después de entender la idea.
- Sin lenguaje de profesor («hoy aprenderemos», «en esta clase»), sin definiciones iniciales ni enumeraciones académicas.
- No inventar estadísticas ni exagerar capacidades. **Sin notas al pie ni aclaraciones técnicas en pantalla** (nada de «simulación propia», «ejemplo ilustrativo»): la honestidad va en la narración (p. ej. «imagina…», «en este ejemplo…», «muchas veces» en vez de «siempre») y en el README del episodio.
- Preferir simulaciones/experimentos reales ejecutados en el repo (NumPy) y distinguir resultados propios de los de la fuente.
- El cierre responde la pregunta del inicio. Idealmente, el último cuadro empalma con el primero (loop).

## Flujo diario automático (YouTube Shorts + Instagram Reels de stheq.ia)
**El usuario solo elige el tema; todo lo demás es automático.** Una tarea programada lo dispara cada mañana.
1. **Tendencias:** `python tools/tendencias_decalogo.py --dias 30` compara categorías de hábitos (verse mejor, piel, pelo, ejercicio, dormir, estudiar, alimentación, mente, productividad) por mediana de vistas de Shorts en español. Se puede complementar con `python tools/tendencias.py --dias 30 --amplio --min-vistas 300000 --n 45` cuando un decálogo de IA calce (p. ej., «10 usos de la IA para estudiar»).
2. **3 ideas de decálogo:**
   - de categorías distintas, con preferencia por las de mayor mediana;
   - sin repetir temas de `episodes/` ni de `propuestas/`;
   - solo con reglas que tengan respaldo.
3. **Propuestas:** en `propuestas/<fecha>/` van `propuestas.md` (por idea: tendencia con vistas, gancho y las 10 reglas con su fuente) y `storyboard_A/B/C.png` (5 fotogramas con el estilo de marca). Se envían al usuario y se pregunta «¿Cuál produzco: A, B o C?». **Sin elección no se publica nada.**
4. **Producción** con la plantilla `episodes/dec01_glow_up/`, la validación obligatoria y el control de calidad de abajo. Duración de 50–80 s. Commit y push.
5. **Publicación en Metricool** (marca stheticIA, `blogId 8154202`, zona America/Santiago, Instagram y YouTube conectados):
   - **Media:** `https://raw.githubusercontent.com/MatiasRojasG/Virales_IA/<SHA del commit>/episodes/<slug>/output/<slug>.mp4` (repo público; con el SHA el enlace no cambia). La portada `output/portada.png` va como `videoThumbnailUrl` solo en Instagram.
   - **Horario:** `getBestTimeToPostByNetwork` para youtube e instagram (hoy). Se elige la mejor hora de cada red que esté ≥ 30 min en el futuro y antes de las 22:00, **a ≥ 1 h de cualquier otra publicación ya programada** (revisar con `getScheduledPosts`).
   - **Dos publicaciones**, cada una a su mejor hora:
     - **YouTube:** `type "short"`, título ≤ 90 caracteres con `#shorts`, `category "HOWTO_STYLE"`, `madeForKids false`, 5–7 tags.
     - **Instagram:** `type "REEL"`, `showReelOnFeed true`.
   - **Texto:** gancho, «todas con respaldo científico», pregunta para comentarios, «Guárdalo», y 6–8 hashtags con `#stheqia`. Sin aclaraciones técnicas; las fuentes van en el README.
6. **Confirmación:** se programa un aviso 10 min después de cada publicación. Al llegar, `getScheduledPosts` (`extendedRange true`) debe mostrar PUBLISHED, y se envían los enlaces. Si falló, se explica en 1–2 frases y qué hacer.
- Nunca copiar videos ajenos: solo el tema.

## Formato decálogo (serie de stheq.ia)
- Decálogos prácticos: cómo cuidarse, estudiar, verse mejor, hacer ejercicio, dormir, etc. El tema se elige por tendencia (`tools/tendencias_decalogo.py`).
- **Excepción al arco de «una historia»:** el gancho es una pregunta con promesa («¿Quieres… sin…?») y la cifra («diez reglas»); luego vienen 10 reglas de 4–8 s, y el cierre responde la pregunta del gancho, con un llamado a guardar.
- **Cada regla:** número hablado («Uno:»), la acción y una frase de respaldo («en un estudio…», «recomienda la OMS…»).
- **Solo reglas con respaldo:** fuentes en el README; las simplificaciones se dicen en la narración o en el README.
- **Visual por regla:** número grande arriba, ícono blanco animado que reacciona a la palabra clave, etiqueta corta y una fila de 10 puntos de avance. Cada regla entra por la derecha y sale por la izquierda.
- **Plantilla:** `episodes/dec01_glow_up/`.

## Carrusel de noticias de IA y tecnología (Instagram, lunes, miércoles y viernes)
- **Publicación directa, sin aprobación previa:** por eso la verificación es estricta.
- **Primero la hora, después las noticias.** Se elige la hora de publicación (ver «Publicación») y la ventana de noticias son **solo las 24 h previas a esa hora**. Cada noticia debe tener fecha y hora de publicación dentro de esa ventana; se anota en `noticias.json` (`"publicada": "2026-11-18 07:30 UTC"`).
- **Sin repetir:** se descarta cualquier noticia (o continuación sin un hecho nuevo) que ya aparezca en `carruseles/*/noticias.json`. Una actualización solo entra si trae un hecho nuevo de las últimas 24 h, y se cuenta ese hecho.
- **Selección:** 3–5 noticias de IA o tecnología de interés general. Si en 24 h solo hay 2 sólidas, el carrusel lleva 2. Si hay menos de 2, ese día **no se publica** y se avisa al usuario.
  - Cada una se verifica en la fuente original (comunicado, filing, blog oficial, discurso) o en al menos un medio de primer nivel (Reuters, AP, Bloomberg, CNBC, NPR, The Verge, etc.).
  - Si no hay confirmación sólida, la noticia no entra.
- **Tono:** nada de rumores, acusaciones sobre la vida privada de personas ni cifras sin fuente. Si una empresa no dio un motivo, se dice así.
- **Fotos** solo de Wikimedia Commons con licencia libre (`python tools/commons.py buscar|bajar`), con crédito en la lámina y en la descripción.
  - Nada de fotos de agencias o medios (derechos de autor).
  - La foto debe representar la noticia sin inducir a error. Ejemplo: no usar una pantalla con el anuncio de otra empresa.
  - Si aparece una persona, el campo `pie` dice quién es.
- **Diseño:** `carruseles/<fecha>_noticias/noticias.json` y luego `python tools/carrusel.py <json>`. El kicker de la portada es «NOTICIAS DE IA · ÚLTIMAS 24 H» y el título no dice «esta semana».
  - Salida: 1080×1350, portada, una lámina por noticia y cierre con el logo.
  - Cada lámina lleva el logo y el nombre de la cuenta, la fecha, la foto en blanco y negro, el número, la categoría, el titular, el texto, «Por qué importa» y la fuente.
  - Revisar `hoja.png` y cada lámina con Read: sin cortes, solapamientos ni faltas.
- **Publicación:** Metricool `blogId 8154202`, solo Instagram, `instagramData.type "POST"`.
  - Media: las láminas por URL raw con el SHA del commit, en orden. `mediaAltText` con el titular de cada una.
  - Hora: la mejor del día con `getBestTimeToPostByNetwork`, ≥ 30 min en el futuro y a ≥ 1 h de otras publicaciones.
  - Texto: «Lo que pasó en IA en las últimas 24 horas 👇», una línea por noticia, pregunta, «Guarda este post», fuentes con fecha, créditos de fotos y 6–8 hashtags con `#stheqia`.
- **Marca:** logo en `assets/marca/` (`logo_blanco.png` para fondo negro).

## Retención
- El hook está en el cuadro 0: problema visual inmediato, sin intro ni pantalla de presentación.
- Curiosidad progresiva, preguntas abiertas y un payoff satisfactorio. Una idea visual principal por escena.
- Duración: 50–90 s sugerido, ajustable a la historia. Si no cabe, dividir en episodios.

## Restricciones visuales permanentes
- **Única excepción de texto fijo:** el nombre de la página, `stheq.ia`, pequeño y centrado arriba (`marca.title`, y≈300, 30 px, tinta al 72 %), visible todo el video.
- **Nunca** mostrar dentro del video títulos del episodio, números de episodio, encabezados, nombres de unidades ni banners/etiquetas. Títulos y numeración quedan solo como metadatos (`EPISODE` en `script.py`, README).
- Comenzar directamente con la historia.
- Texto en pantalla solo cuando ayuda a comprender (cifras, etiquetas de diagramas). El video es entretenimiento visual: imágenes, figuras y movimientos suaves.
- Subtítulos y elementos importantes dentro de las zonas seguras (`reelforge/config.py`). Contenido entre y≈480 y 1300. Subtítulos en y≈1390.

## Identidad (marca stheq.ia, módulo `reelforge/marca.py`)
- 1080×1920, 9:16, 60 fps, H.264 + AAC 48 kHz.
- **Sobria: fondo negro, letras y animaciones blancas.** Fondo #0A0A0A con halo apenas más claro y grano fino (`marca.background`). Letras, trazos y figuras en blanco #F2F2F2. Grises #9A9A9A / #4A4A4A para lo secundario.
- **Rojo #E03131:** acento mínimo, solo para palabras clave, revelaciones y alertas.
- **Café #6B4A33 y tonos de piel:** solo cuando hace falta. Nada de cyan, violeta ni dorado.
- **Subtítulos:** blancos con palabras clave en rojo (`SUB.draw(..., **marca.SUB_COLORS)`), sobre una banda oscura (`marca.sub_band`).
- Tipografía Inter (en `assets/fonts`). Motion graphics minimalistas, easing, morphing, continuidad espacial y viñeta (`marca.vignette`).

## Voz, subtítulos y audio
- Voz **femenina chilena, grave, ágil y con emoción**: Edge TTS `es-CL-CatalinaNeural` (`marca.VOICE`), `rate="+15%"` (`marca.RATE`) y tono base `pitch="-10Hz"` (`Timeline(..., pitch=marca.PITCH)`). Nunca voces «Multilingual» (acento gringo) ni la colombiana. Se sintetiza frase por frase (`Ph`), con silencios recortados y pausas diseñadas. La emoción sale de variar el tono por frase: preguntas con `pitch=marca.Q` (−3 Hz), revelaciones con `pitch=marca.WOW` (−5 Hz) y cifras o énfasis con `rate=marca.SLOW` (+6 %). Ritmo objetivo: ≈ 3,2–3,5 palabras/s al hablar.
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
