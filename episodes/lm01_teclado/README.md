# ¿Cómo adivina tu teclado la palabra que viene? (metadato interno: modelos de lenguaje, ep. 1)

**Video:** `output/lm01_teclado.mp4`: 1080×1920, 60 fps, 93,6 s, −14,6 LUFS, pico −1 dBFS. Sin títulos ni banners.

**Ritmo (regla de narración cinematográfica):**
- Voz a +12 %, más pausada que la de los episodios anteriores: 2,88 palabras/s al hablar y 2,45 palabras/s con las pausas.
- Pausas de 0,2 a 1,0 s (media 0,55 s). 15 pausas de ≥ 0,6 s, ubicadas antes y después de las revelaciones.
- Sin saltos ni pantallas vacías (medido cuadro a cuadro). Subtítulos 60 ms antes de la voz.

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
