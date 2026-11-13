# ¿Cómo adivina tu teclado la palabra que viene? (metadato interno: modelos de lenguaje, ep. 1)

**Video (v3, corto):** `output/lm01_teclado.mp4`: 1080×1920, 60 fps, **80,5 s**, −14,6 LUFS. Voz a +14 % (2,97 palabras/s al hablar). Sin títulos ni banners.
**Versión larga (v2, 159 s):** `output/lm01_teclado_largo_159s.mp4`, con la tabla de embeddings y la predicción detallada. Sirve de base si se quiere una segunda parte.

**v3:**
- Se mantiene lo esencial: embedding = lugar aprendido = vector (casa en (3, 2) → 16 números de «café»).
- Se lee comparando direcciones (café–té 0,998; café–perro 0,21).
- El teclado junta «me tomé un» y sugiere lo que apunta hacia el mismo lado.
- Se quitaron la tabla y el interruptor que elige la fila, y la escena de conflicto aparte. Se condensaron las frases de contexto.

**Ritmo (regla de narración cinematográfica):**
- Voz a +12 %, más pausada que la de los episodios anteriores: 2,88 palabras/s al hablar y 2,45 palabras/s con las pausas.
- Pausas de 0,2 a 1,0 s (media 0,55 s). 15 pausas de ≥ 0,6 s, ubicadas antes y después de las revelaciones.
- Sin saltos ni pantallas vacías (medido cuadro a cuadro). Subtítulos 60 ms antes de la voz.

## v2: explicación del embedding paso a paso

Después de «ese lugar se llama embedding», cada pregunta abre la siguiente:

1. **¿Qué es ese lugar?**
   - Un **vector**: en el mapa de tu ciudad, la casa está en (3, 2) = 3 al este y 2 al norte. Una lista de números que dice dónde está algo.
   - El de «café» tiene **16 números reales**: −0,5 −2,0 −1,4 1,2 2,2 …
   - Nadie los elige: el juego los ajusta (se ve cómo se acomodan). El mapa los aplana a 2.
2. **¿Dónde viven?** En la **tabla de embeddings**, una fila por palabra (valores reales). El interruptor de «café» (one-hot) **elige su fila**, que es la idea de la clase «one-hot × matriz = elegir una fila».
3. **¿Cómo se lee un vector?** No número por número (se tacha), sino **comparando hacia dónde apunta**.
   - Flechas con los ángulos reales: el ángulo sale del coseno entre vectores.
   - En la escala de 0 a 1, café–té da **0,998** y café–perro **0,21**.
4. **¿Cómo adivina el teclado?**
   - Junta (promedia) los vectores reales de «me», «tomé» y «un».
   - Calcula un **puntaje** con cada palabra: mate 9,7 · té 9,6 · café 9,5 · perro 2,8 · pan 0,3 · parque −0,2.
   - Lo convierte en **probabilidades**: mate 19 % · té 18 % · café 16 % · resto ≈ 0 %. El resto se reparte entre chocolate y jugo.
   - En pantalla se aclara que el modelo usa un segundo vector por palabra para esta comparación (los vectores de salida).

## Serie propuesta (PDF «Modelos de lenguaje»)

| # | Historia | Conceptos |
|---|---|---|
| 1 | **¿Cómo adivina tu teclado la palabra que viene?** ✅ | Palabras como símbolos (one-hot), contexto, juego de predecir la palabra, embeddings y vecindades de significado |
| 2 | «El perro muerde al hombre» ≠ «el hombre muerde al perro» | Promediar palabras pierde el orden, codificador recurrente |
| 3 | ¿Cómo traduce 5 palabras en 7? | Encoder-decoder (seq2seq), vector de contexto |
| 4 | ¿Por qué un traductor se enreda con frases largas? | Cuello de botella del vector de contexto, exposure bias, greedy y beam search: el camino al Transformer |

## Arco emocional

| Etapa | Momento |
|---|---|
| Curiosidad | El teclado sugiere café, té y mate |
| Expectativa | ¿Cómo sabe? |
| Conflicto | Para el computador, «café» es un símbolo: un interruptor en una fila de miles. Café↔té = café↔perro |
| Intuición | Tú lo sabes porque aparecen rodeados de las mismas palabras: «dime con quién andas…» |
| Suspenso | El juego: miles de frases, adivinar la siguiente, palabras con un lugar al azar que se corrige con cada error |
| Revelación | Las palabras se ordenan solas en barrios: bebidas, animales, comidas, lugares |
| Comprensión | Ese lugar se llama embedding (16 números reales de «café») |
| Satisfacción | De vuelta al teclado: «no sabe qué es el café; sabe con qué palabras anda» |

## Experimento (`experiment.py`)

- **Corpus.** 6.000 frases de juguete generadas con 20 plantillas: 69 palabras, sin errores de género (verificado).
- **Modelo.** Modelo de lenguaje neuronal simple, como en la clase:
  - Las 3 palabras anteriores pasan por la matriz de embeddings (one-hot × matriz = una fila).
  - Se promedian y el resultado entra a un softmax sobre el vocabulario.
  - Pérdida: log-verosimilitud negativa. Entrenamiento con Adam en 30 épocas.
- **Resultados reales:**
  - Vecinos de «café»: mate, jugo, chocolate, té. Vecinos de «perro»: pájaro, caballo, conejo, gato.
  - Para «me tomé un ___», el modelo sugiere chocolate, mate, té, jugo y café (las 5 bebidas, como el teclado del video).
- **Cómo se dibuja el mapa.**
  - Es la PCA real de los embeddings en 13 instantáneas del entrenamiento, cada una normalizada a su escala.
  - Dentro de cada barrio, las palabras se separan en un pequeño anillo para que las etiquetas se lean.
- **En pantalla:** «Modelo propio con frases de ejemplo · los teclados reales usan modelos mucho más grandes».

## Publicación

**Título:** ¿Cómo adivina tu teclado la palabra que viene? ⌨️

**Descripción:**
> Escribes «me tomé un»… y tu teclado ya sugiere café, té, mate. ¿Cómo sabe?
> Para un computador, una palabra no significa nada. Pero si juega millones de veces a adivinar la siguiente palabra, algo sorprendente pasa: las palabras se ordenan solas por significado.
> Entrenamos un modelo pequeño para mostrarlo ☕
> ¿Cuál es la sugerencia más rara que te ha hecho tu teclado? 👇
> (Modelo propio con frases de ejemplo; los teclados reales usan modelos mucho más grandes.)
> #DetrásDelAlgoritmo #IA #ModelosDeLenguaje #InteligenciaArtificial #Tecnología #Ciencia #AprendeEnTikTok
