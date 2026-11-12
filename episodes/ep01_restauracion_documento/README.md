# EP 01 — El documento ilegible

**Archivo final:** `output/ep01_restauracion_documento.mp4` · 1080×1920 · 30 fps · H.264 + AAC 48 kHz estéreo · 89,97 s · −15,3 LUFS integrados, pico −1 dBFS.

| Archivo | Contenido |
|---|---|
| `output/ep01_restauracion_documento.mp4` | Video final con subtítulos incrustados |
| `output/ep01_restauracion_documento.srt` | Subtítulos (sincronizados por palabra con la voz) |
| `output/guion_narrado.txt` | Guion tal como se narró, con tiempos por bloque |
| `output/portada.png` | Portada 1080×1920 |
| `script.py` | Guion editable (palabras clave, pronunciación) |
| `scenes.py` | Animaciones (una función por escena, sincronizadas con palabras) |
| `experiment.py` | Recreación del experimento: ruido 15 %, ICM, OCR |
| `build.py` | Construye todo: `python episodes/ep01_restauracion_documento/build.py` |

## Publicación

**Título:** ¿Se puede leer lo ilegible? Redes de Markov en 90 segundos

**Descripción:**
> Un escáner invirtió el 15 % de los píxeles de este documento y el OCR no pudo leerlo. La solución no fue un modelo gigante: fue escuchar a los píxeles vecinos.
> Cada píxel combina dos voces: lo que vio el sensor (α) y lo que dicen sus cuatro vecinos (β). Eso es una red de Markov (grafo no dirigido) y el método ICM.
> 📊 En la clase: error 15 % → 2,5 %, OCR 42 % → 94 % de caracteres.
> 🐍 Mi recreación en Python (otra tipografía y otro ruido): error 14,9 % → 2,6 %, OCR 0 % → 91 %.
> Episodio 1 de la serie de Modelos Gráficos Probabilísticos · Magíster en IA.
> #IA #MachineLearning #RedesDeMarkov #Probabilidad #VisionPorComputador #OCR #Matematicas #DivulgacionCientifica

**Portada:** `output/portada.png` — documento partido en dos (mitad con ruido / mitad restaurada, divisor cyan), titular «¿SE PUEDE LEER LO ILEGIBLE?», chips «15 % DE RUIDO» / «RESTAURADO». Texto centrado y fuera de las zonas que tapa la interfaz.

## Resultados: clase vs. recreación propia

| Métrica | Clase (diap. 17–18, código R) | Mi ejecución (Python, `experiment.py`) |
|---|---|---|
| Píxeles invertidos | 15 % | 14,9 % (semilla 7, NumPy) |
| Error tras restaurar | 2,5 % | 2,6 % |
| OCR sobre escaneo con ruido | 42 % de caracteres (rescata solo la última línea) | 0 % (Tesseract no devuelve texto útil) |
| OCR sobre la restauración | 94 % | 90,5 % |
| Parámetros | α = ½·ln(0,85/0,15) ≈ 0,87, β = 1,2, 30 pasadas | idénticos |

Diferencias explicables: otra tipografía (Liberation Serif 42 px), otro generador aleatorio y otra
métrica de OCR (1 − distancia de Levenshtein / largo del texto). La diapositiva 3 dice que el lector «no
devuelve ni una sola palabra», mientras que la 18 reporta el 42 %; el video cita el 42 % y lo atribuye a la clase.

La regla se aplica a todos los píxeles **a la vez** (igual que el código R de la clase); ICM clásico
actualiza los píxeles de a uno. Por eso el video dice «es la idea de ICM».

## Storyboard

| t (s) | Bloque | Visual | Sonido |
|---|---|---|---|
| 0–8 | Hook | Documento con ruido desde el cuadro 0, contador 0→15 %, barrido rosado del OCR que falla, barrido cyan que revela la restauración | golpe grave + subida + campanilla |
| 8–16 | Problema | Zoom continuo (escala logarítmica) hasta ver píxeles; se marcan los invertidos (tinta→papel rosado, papel→tinta violeta); un cursor «?» salta sin poder decidir | whoosh, pops |
| 16–23 | Idea | Malla 7×7 sintética; pares vecinos unidos en violeta; punto aislado con sus 4 vecinos resaltados | pops |
| 23–33 | Grafo | Cuadrados → nodos; flecha causal tachada; aristas en onda desde el centro; capa observada en cyan | subida |
| 33–42 | Dos voces | Nodo central, 4 vecinos (β) y sensor (α); ecuación h_i = α u_i + β Σ s_j se construye y se ilumina por término | pops |
| 42–52 | Ejemplo | +0,87 vs −4,8 en una barra de balance; el nodo se voltea a papel | campanilla |
| 52–62 | Iterar | Documento real pasada a pasada con barrido, contador de error y curva de error | ticks por pasada |
| 62–70 | Resultado clase | Barras 15 → 2,5 % y 42 → 94 % | campanilla |
| 70–76 | Recreación | Deslizador antes/después, contadores 2,6 % y 0 → 91 % | campanilla |
| 76–81 | Bordes | Zoom a la restauración con errores residuales en rosado | pop |
| 81–90 | Cierre | Aplicaciones (documentos, resonancias, satélites) → adelanto: DAG de 4 nodos con «?» y «EP 02 · Redes sin flechas» | subida |
