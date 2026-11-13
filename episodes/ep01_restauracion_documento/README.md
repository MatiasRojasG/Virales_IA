# EP 01 — ¿Puedes leer esto? · Detrás del Algoritmo (v2)

**Video final:** `output/ep01_restauracion_documento.mp4`: 1080×1920, **60 fps**, H.264 + AAC 48 kHz estéreo, **81,1 s**, −14,3 LUFS integrados, pico −1 dBFS.

| Archivo | Contenido |
|---|---|
| `output/ep01_restauracion_documento.mp4` | Video final con subtítulos incrustados |
| `output/ep01_restauracion_documento.srt` | Subtítulos (alineados palabra a palabra con la voz) |
| `output/guion_narrado.txt` | Guion tal como se narró, con tiempos por bloque |
| `output/portada.png` | Portada 1080×1920 |
| `script.py` | Guion por frases con prosodia (ritmo, tono, pausas) |
| `scenes.py` | Toma continua: cámara, capas conceptuales, balanza, resultados |
| `experiment.py` | Recreación del experimento: ruido 15 %, regla de vecinos, OCR |
| `build.py` | `python episodes/ep01_restauracion_documento/build.py [--stills]` |

## Qué cambió respecto de la v1

| Aspecto | v1 | v2 |
|---|---|---|
| Narrativa | Resumen de la clase en orden técnico | Problema cotidiano → curiosidad → intuición (analogía de la palabra mal escuchada) → descubrimiento → explicación (balanza) → resultado |
| Términos técnicos | «grafo no dirigido», ecuación h = αu + βΣs desde el segundo 30 | «Red de Markov» recién cuando la idea ya se entendió; α y β presentados como «perillas» de confianza; sin ecuaciones |
| Visual | 11 escenas separadas con fundidos | **Una sola toma continua** sobre el documento real: zoom hasta un punto con ruido verdadero (fila 28, col. 16), sus vecinos, la red sobre los píxeles, la balanza que sale de la imagen y la limpieza en ondas desde ese mismo punto |
| Transiciones | Fundido + zoom leve | Cámara con zoom geométrico y easing, foco selectivo (spotlight), profundidad de campo (desenfoque) para cambiar de plano, resortes en la balanza |
| Cuadros por segundo | 30 | 60 |
| Voz | es-CL Lorenzo, un audio por bloque | es-MX Jorge (latinoamericano neutro, de las voces con más rango de entonación medido), **frase por frase**: silencios recortados, pausas diseñadas, tono más alto en preguntas y ritmo más lento en frases de énfasis |
| Retención | Hook informativo | Pregunta directa + titular en el cuadro 0, resultado mostrado y **rebobinado** (open loop), pregunta «¿está bien o mal?» sin respuesta inmediata, cierre con pregunta abierta |
| Música | Pad constante | Dinámica: baja en el momento de suspenso, el arpegio entra con el descubrimiento y un pulso grave acompaña el resultado |
| Duración | 90 s | 81 s |

## Publicación

**Título:** ¿Puedes leer esto? Cómo los píxeles vecinos rescatan un texto

**Descripción:**
> Un escáner invirtió el 15 % de los puntos de este documento y un lector automático ya no lo entiende. La solución: que cada punto le pregunte a sus vecinos.
> Así funciona una red de Markov: una red sin flechas donde cada punto equilibra lo que vio el escáner (α) con lo que dicen sus vecinos (β).
> 📊 Clase: el lector pasó del 42 % al 94 % del texto (puntos mal etiquetados: 15 % → 2,5 %).
> 🐍 Mi recreación en Python (otra tipografía y otro ruido): 0 % → 91 %.
> #DetrásDelAlgoritmo #IA #MachineLearning #RedesDeMarkov #Probabilidad #VisiónPorComputador #OCR #Divulgación

**Portada:** `output/portada.png`, con el titular «¿PUEDES LEER ESTO?», el documento partido en dos (con ruido / restaurado) y la marca.

## Resultados: clase vs. recreación propia

| Métrica | Clase (diap. 17–18, código R) | Mi ejecución (`experiment.py`) |
|---|---|---|
| Puntos invertidos | 15 % | 14,9 % (semilla 7, NumPy) |
| Error tras restaurar | 2,5 % | 2,6 % |
| Lector (OCR) sobre el escaneo | 42 % de los caracteres | 0 % |
| Lector (OCR) sobre la restauración | 94 % | 90,5 % (en el video: 91 %) |
| Parámetros | α = ½·ln(0,85/0,15) ≈ 0,87, β = 1,2, 30 pasadas | idénticos |

La balanza del video usa exactamente esos valores. El escáner aporta 0,87 y los cuatro vecinos aportan 4 × 1,2 = 4,8. Por eso el punto se corrige a papel, que es lo que hace el modelo con ese píxel en la primera pasada.

## Storyboard (v2)

| t (s) | Bloque | Imagen | Sonido |
|---|---|---|---|
| 0–7,5 | Hook | Titular «¿PUEDES LEER ESTO?» y documento con ruido desde el cuadro 0. El lector falla (barrido rosado), la restauración se revela (barrido cyan) y se rebobina | golpe + swell, ticks, campanilla, rebobinado |
| 7,5–14,7 | Problema | Zoom continuo hasta los píxeles; los invertidos se marcan (tinta→papel rosado, papel→tinta violeta) | whoosh, pops |
| 14,7–20,6 | Curiosidad | Spotlight sobre un único punto; «?», «¿tinta?» / «¿mancha?» | música baja (suspenso) |
| 20,6–32,8 | Intuición | El foco se abre a los 8 vecinos y al trazo de la «I». Luego, con profundidad de campo, la burbuja «pl_ya» → «playa» | whoosh, campanilla |
| 32,8–41,4 | Descubrimiento | Aristas desde el punto hacia sus 4 vecinos y la red se expande en onda. Aparecen flechas que se disuelven en aristas simétricas y la tarjeta «RED DE MARKOV» | entra el arpegio, swell |
| 41,4–53,9 | Balanza | Los 5 cuadros salen de la imagen hacia una balanza con resortes (0,87 vs 4,8), el punto se corrige y aparecen las perillas α y β | caídas, campanilla |
| 53,9–60,3 | Todo el documento | La cámara se aleja mientras las pasadas limpian en ondas que nacen del mismo punto; contador de pasadas y error | ticks |
| 60,3–72,2 | Resultado | Deslizador antes/después. Tarjeta de la clase 42 → 94 % y tarjeta de mi recreación 0 → 91 % | pulso grave, campanillas |
| 72,2–81 | Cierre | El documento se vuelve una de tres fichas: resonancias y satélites, que se limpian con la misma regla. Luego, un DAG de 4 nodos con «?» y «Próximo: redes sin flechas» | subida |
