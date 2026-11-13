# EP 01 — ¿Cómo limpia tu celular una foto nocturna? · Detrás del Algoritmo

**Video:** `output/ep01_foto_nocturna.mp4`: 1080×1920, 60 fps, H.264 + AAC 48 kHz, **105,8 s**, −14,0 LUFS, pico −1 dBFS.
Se verificó lo siguiente:
- No hay saltos de un solo cuadro.
- Los subtítulos van 50 ms antes de la voz.
- El último cuadro empalma con el primero (loop).
- El 95 % de la voz cae dentro de las palabras marcadas.

| Archivo | Contenido |
|---|---|
| `output/ep01_foto_nocturna.mp4` | Video final |
| `output/ep01_foto_nocturna.srt` | Subtítulos |
| `output/guion_narrado.txt` | Guion con tiempos |
| `output/portada.png` | Portada |
| `script.py` | Guion por frases y cadena causal documentada |
| `scenes.py` | Toma continua: celular → muro → punto → vecinos → resortes → combinaciones → pasadas |
| `experiment.py` | Escena nocturna, simulación de fotones y restauración con campo de Markov |

## v5: reglas de ritmo y más contraste visual

- **Duración y ritmo:** 84,4 s (antes 105,8). Voz a +10 % (3,2 palabras/s al hablar), con pausas largas en las revelaciones. Sin títulos ni etiquetas superiores: el titular del inicio pasó a ser un rótulo sobre la imagen («lo que vio la cámara» / «lo que te mostró el celular»).
- **Más ruido.** El sensor recibe **6 fotones** por punto blanco (antes 12): el grano se nota mucho más.
- **Más nitidez:**
  - La restauración usa un vecindario de 5×5 con peso gaussiano: misma energía, con más vecinos.
  - Los resortes se sueltan según una guía con mediana de 3×3, para que un punto aislado no se proteja a sí mismo.
  - Parámetros: β = 3, δ = 0,08 y 20 pasadas. PSNR: foto con ruido 14,4 dB → restaurada **23,0 dB**.
- **Guion condensado:**
  - Se quitó la cuenta de «más fotos que átomos».
  - Las pasadas quedan en una frase: «cada punto se acomoda así, mirando a sus vecinos… y repetimos».
  - La fórmula se resume en una línea: la tensión de los resortes se llama energía; mientras menor, más probable la foto.
- **Nuevo punto protagonista:** fila 566, columna 19. Recibió 6 gotas mientras su vecindario promedia 1.

## Enfoque

No se explica la clase. La clase explica algo del mundo: **¿cómo puede una foto de noche salir limpia si a la cámara le faltó luz?**

| Pregunta que se abre | Respuesta en la historia | Idea de la clase detrás |
|---|---|---|
| ¿De dónde sacó el celular lo que la cámara no vio? | *(open loop: se responde al final)* | — |
| ¿Por qué salen granos? | A cada punto le llegan pocas «gotas de luz», al azar (simulación de fotones con conteos reales) | Observación ruidosa xᵢ |
| ¿Y no se puede arreglar cada punto? | Solo, es imposible saber si brilla de verdad | Un clasificador por píxel falla (diap. 13) |
| ¿Entonces? | Lo que está al lado suele parecerse | Relaciones simétricas, sin causa: red no dirigida (diap. 3–4) |
| ¿Basta con promediar? | No: el letrero se vuelve ilegible | β grande borra detalles finos (diap. 15) |
| ¿Cómo equilibrar? | Resortes hacia la cámara y hacia los vecinos; el que une objetos distintos se suelta | Factores de compatibilidad: datos (φᵢ) y suavidad (ψᵢⱼ) (diap. 7, 14) |
| ¿Cuál es la mejor foto? | La de menor tensión total, que es la más probable | Forma de energía P ∝ e^(−E) (diap. 12) |
| ¿Por qué no calcularla directo? | Hay más fotos posibles que átomos en el universo | Explosión combinatoria (2ⁿ, diap. 9) |
| ¿Cómo se hace entonces? | Cada punto se acomoda mirando solo a sus vecinos, y se repite | Manta de Markov (diap. 11) e ICM (diap. 15) |
| ¿Cómo se llama esto? | Red de Markov (nombrada recién al final) | — |

## Validación del guion (antes de renderizar)

| Pregunta | Respuesta |
|---|---|
| ¿Alguien sin conocimientos de IA entiende el problema? | Sí. Todos han sacado una foto granulada de noche. |
| ¿Cada frase responde a una pregunta que la historia acaba de generar? | Sí. Ver la tabla anterior; cada bloque cierra la pregunta del anterior y abre la siguiente. |
| ¿Se entiende por qué se necesita cada concepto? | Los vecinos, porque un punto solo no basta. El equilibrio, porque promediar borra el letrero. Los resortes que se sueltan, porque el letrero tiene bordes. El ajuste local, porque no se pueden probar todas las fotos. |
| ¿El espectador puede relacionarlo con su vida? | Su celular, sus fotos nocturnas y su propia forma de mirar alrededor. |
| ¿Sería interesante sin mencionar la IA? | Sí. «Red de Markov» aparece una vez, al final, como nombre de algo ya entendido. |
| ¿Cifras sin contexto? | No. «15 %» y «42 → 94 %» desaparecieron. Cada número sale de algo visible: las gotas contadas en cada punto, 256 brillos por punto, 12 millones de puntos y, de ahí, la comparación con los átomos. |

## Precisión y aclaraciones

- **Es una ilustración.** El video lo dice en pantalla: «los celulares reales combinan varias tomas y redes neuronales». La idea de fondo, que un punto se corrige con su vecindario, sí es la misma.
- **Escena y foto son simuladas.** La escena nocturna es sintética. El ruido es de Poisson sobre el brillo, con 12 fotones para el blanco puro, más algo de ruido de color y de lectura del sensor.
- **El modelo de restauración.** Es un campo aleatorio de Markov con 4 vecinos:
  - Energía: E(x) = Σ(xᵢ − yᵢ)² + β Σ ρ(xᵢ − xⱼ), con β = 4.
  - ρ es lorentziana con δ = 0,1: en un resorte, el peso baja cuando los vecinos son muy distintos.
  - Hace 15 pasadas de actualización local simultánea, igual que el código de la clase.
  - «Solo promediar» usa ρ cuadrática con β = 60 y 120 pasadas.
- **Calidad medida (PSNR, más es mejor):**

  | Imagen | PSNR |
  |---|---|
  | Foto con ruido | 17,1 dB |
  | Solo promediar | 18,6 dB |
  | Restaurada | 26,5 dB |

- **Lo que va más allá de la clase.** La clase trabaja etiquetas binarias con el modelo de Ising. Aquí el brillo es continuo y el resorte robusto «que se suelta» es una elección de factor de vecinos ψᵢⱼ. La estructura es la misma: factores de datos y de suavidad, energía y actualización local.
- **Cifras:**
  - 256 niveles por canal de 8 bits.
  - 12 MP es un tamaño típico de sensor.
  - 256^12 000 000 ≈ 10^28 898 880 fotos posibles, frente a unos 10^80 átomos en el universo observable.
- **Los resortes muestran una fila real del letrero.** Es la fila 438, x = 108–141, tomada de la foto con ruido. Se simulan dos fases:
  1. Todos los resortes iguales: la fila se aplana.
  2. Resortes robustos: los bordes de las letras se recuperan.

## Publicación

**Título:** ¿Cómo limpia tu celular una foto de noche?

**Descripción:**
> Sacas una foto de noche y sale llena de granitos… pero tu celular te muestra otra, limpia. ¿De dónde sacó lo que la cámara no vio?
> La respuesta: cada punto se corrige mirando a sus vecinos, sin borrar los bordes. Atrás hay una idea matemática preciosa: una red de Markov.
> (Ilustración simplificada: los celulares reales combinan varias tomas y redes neuronales.)
> #DetrásDelAlgoritmo #Fotografía #IA #Matemáticas #RedesDeMarkov #Divulgación

**Portada:** `output/portada.png`, con el celular partido en dos (sensor / resultado) y el titular «¿CÓMO LIMPIA TU CELULAR UNA FOTO DE NOCHE?».

## Cambios de la v4

- **Primer segundo.** El video abre ya dentro de la foto con ruido, con el letrero en primer plano y el titular «TU CÁMARA VIO ESTO» presente desde el cuadro 0. En el segundo 3 la limpieza se revela con «TU CELULAR TE MOSTRÓ ESTO».
- **Resortes explicados paso a paso** (bloque «bolita»):
  1. Un punto es una bolita: más arriba, más brillante.
  2. Un resorte cyan la amarra a lo que midió la cámara. Se la aleja y el resorte la devuelve, con una flecha de fuerza.
  3. Aparecen dos vecinos con resortes violeta que la acercan.
  4. La bolita se detiene donde las dos fuerzas se equilibran.

  Recién entonces aparece la fila entera del letrero (aplanado, resortes sueltos y letras que vuelven).
- **Idea completa en lugar de «eso, en el próximo»:**
  - **Red de Markov.**
  - **La fórmula leída como resortes.** E(x) = Σ(xᵢ − yᵢ)² (resorte a la cámara, datos) + β Σ ρ(xᵢ − xⱼ) (resortes entre vecinos, suavidad). La energía es la tensión total, y P(x | y) ∝ e^(−E) significa menos energía, foto más probable. Luego se iguala a la forma de la clase, ∏ φᵢ · ∏ ψᵢⱼ.
  - **Dónde más se usa.** Documentos escaneados (con el documento real restaurado), resonancias y satélites, cada uno limpiándose en vivo con su significado de «punto». La aclaración sobre los celulares queda en pantalla.
- **Cierre en loop.** «Así que ahora ya sabes de dónde sacó tu celular lo que la cámara no vio… de sus vecinos». La cámara vuelve al letrero con ruido y al mismo titular del primer cuadro.

## Storyboard (v4)

| Bloque | Lo que ocurre en pantalla |
|---|---|
| Hook (0–5,9 s) | Letrero con ruido y «TU CÁMARA VIO ESTO» desde el cuadro 0. Barrido cyan con «TU CELULAR TE MOSTRÓ ESTO». La cámara se aleja al celular y aparece un «?», luego se rebobina. |
| Luz | La cámara entra al muro y caen gotas de luz, con su conteo en cada punto. El muro parejo queda moteado. |
| Difícil | Spotlight sobre el punto con 8 gotas: «¿brillo real?» / «¿ruido?». |
| Vecinos | Aparecen los 8 vecinos y el punto toma el promedio (8 → 2,9). Una onda promedia toda la foto. |
| Exceso | El letrero queda «ILEGIBLE». |
| Bolita | Una bolita en el eje de brillo, con su resorte a la cámara (se aleja y vuelve) y sus resortes a los vecinos. Termina en «fuerzas equilibradas». |
| Resortes | Fila real del letrero: primero se aplana, después los resortes se sueltan y vuelven los bordes. Barras de tensión y de probabilidad. |
| Cálculo | 256 brillos × 12 millones de puntos, frente a los átomos del universo. La foto se limpia pasada a pasada. |
| Fórmula | «RED DE MARKOV». Cada término de la energía aparece con su resorte, luego P ∝ e^(−E) y ∏ φ · ∏ ψ. |
| Usos | Documentos, resonancias y satélites limpiándose, más la aclaración sobre los celulares. |
| Cierre | El celular con antes/después. «…de sus vecinos». Se vuelve al letrero con ruido y «TU CÁMARA VIO ESTO» (loop). |
