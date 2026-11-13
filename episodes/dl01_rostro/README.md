# Deep Learning · EP 01 — ¿Cómo sabe tu celular que eres tú?

**Video (v2):** `output/dl01_rostro.mp4`: 1080×1920, 60 fps, H.264 + AAC, **116 s**, −14,5 LUFS, pico −1 dBFS.
Se verificó lo siguiente:
- No hay saltos de un solo cuadro.
- Los subtítulos van 60 ms antes de la voz.
- El 95 % de la voz cae dentro de las palabras marcadas.

| Archivo | Contenido |
|---|---|
| `output/dl01_rostro.mp4` · `.srt` · `guion_narrado.txt` · `portada.png` | Entregables |
| `script.py` | Guion por frases, con la cadena causal documentada |
| `scenes.py` | Animaciones |
| `experiment.py` | Rostros sintéticos y red neuronal entrenada desde cero con NumPy |

## v2: la red neuronal, paso a paso

Se reemplazó la explicación rápida de «neurona y capas» por cuatro pasos que responden qué entra, qué hace y qué sale:

1. **¿Qué le entra a una neurona?** Un pedacito de la imagen. Son 9 puntos reales de la cara, junto al ojo, con su número de luz: 0,6 0,7 0,7 / 0,1 0,2 1,0 / 0,1 0,4 0,9.
2. **Pesos.** Cada punto tiene un peso: +1 significa «aquí quiero luz», −1 «aquí quiero oscuridad» y 0 «no me importa».
3. **Multiplica y suma.** Se ven los 9 productos.
   - Junto al ojo la suma da **1,8**: sale un solo número y la neurona se **enciende**.
   - En la mejilla pareja, con todos los puntos en 0,5, da **0,0** y queda **apagada**.
4. **Barrido.** Como esos pesos buscan «oscuro → claro», es decir, un borde, al recorrer toda la cara la neurona se enciende en los bordes. Se ve cómo se va pintando el mapa.
5. **Capas.** Una capa es un grupo de neuronas, cada una con pesos distintos (vertical, horizontal, diagonales).
   - **Capa 1.** Recibe la luz de la imagen y entrega 4 **mapas** de bordes.
   - **Capa 2.** Esos mapas **entran** a ella; en pantalla se ven pulsos viajando de una capa a la otra. Sus neuronas combinan bordes y entregan mapas de partes (ojo, nariz, boca).
   - **Capa 3.** Entrega la **huella**: los 32 números reales que la red entrenada produce para esa foto.
   - El repaso «de luz, a bordes, a partes, a huella» ilumina cada fila en orden.

Los pesos de los pasos 2 a 4 son de ejemplo, para que las cuentas se entiendan. La fila de capas está rotulada como ilustración de lo que suelen aprender. La huella y el entrenamiento son reales.

## Serie propuesta (resumen «Fundamentos de Deep Learning»)

| # | Título | Problema cotidiano | Conceptos |
|---|---|---|---|
| 01 | **¿Cómo sabe tu celular que eres tú?** ✅ | Te cambias el look y el celular igual se desbloquea | Píxeles como números, límite de las reglas a mano (feature engineering), neurona (pesos, suma, activación), capas jerárquicas, pérdida y descenso de gradiente |
| 02 | ¿Por qué una sola neurona no basta? | El interruptor de escalera (la luz se prende solo si los interruptores están distintos) | Frontera lineal, XOR, capa oculta, no linealidad, MLP |
| 03 | ¿Cómo aprende una IA de sus errores? | Aprender a encestar | Pérdida, parámetros, descenso de gradiente, sesgo inductivo |
| 04 | De píxeles a objetos | Distinguir un perro de un gato nunca visto | Representaciones aprendidas, composición de funciones, jerarquías |
| 05 | ¿Por qué la IA tardó décadas en despegar? | Ideas antiguas, explosión reciente | Algoritmos, grandes datos, GPUs |

El resumen no desarrolla el aprendizaje no supervisado ni por refuerzo, ni las redes convolucionales, recurrentes o Transformers. Por eso no se incluyen.

## Experimento real (`experiment.py`)

- **Datos.** 8 personas sintéticas, cada una con su geometría facial. Las variaciones no cambian la identidad: peinado, lentes, luz, expresión y desplazamiento.
  - Entrenamiento: 1.760 fotos de 32×32.
  - Prueba: 240 fotos.
  - Una combinación de look (persona 0 con chasquilla y lentes) se reservó y nunca se usó para entrenar.
- **Por qué comparar píxeles falla:**
  - La foto nueva de la persona 0 cambia el **79 %** de los puntos respecto de su foto base. La de otra persona cambia el **48 %**.
  - Diferencia media de brillo: 0,139 frente a 0,073.
  - El vecino más cercano por píxeles es la persona 6, es decir, se equivoca.
- **Red.** Perceptrón multicapa de 1.024 → 128 → 32 («huella») → 8, con activaciones ReLU y 135.592 parámetros. Se entrenó con entropía cruzada y Adam (descenso de gradiente), en 60 épocas.
  - La curva del video es la pérdida real por paso.
- **Resultado:**
  - Exactitud de 100 % en las 240 fotos de prueba. Las caras sintéticas son mucho más fáciles que las reales.
  - La foto nueva, nunca vista, se clasifica como la persona 0 y su vecino más cercano por huella también es la persona 0.
  - El mapa de puntos es la proyección PCA real de los píxeles y de las huellas de las fotos de prueba.
- **Ilustraciones (rotuladas así):**
  - La neurona de bordes usa pesos de ejemplo (−1, 0, +1), no pesos aprendidos.
  - La fila «bordes → partes» muestra la jerarquía típica que el material describe con matiz: ocurre frecuentemente, no siempre.

## Validación

1. **¿Interesa sin saber de IA?** Sí: el desbloqueo facial es cotidiano.
2. **¿El problema va antes que la solución?** Sí: números → comparar falla → reglas se rompen → recién entonces la neurona.
3. **¿Cada concepto tiene razón de existir?** Sí:
   - la neurona, para dejar que la máquina descubra qué mirar;
   - las capas, para pasar de bordes a una cara;
   - el aprendizaje, para responder quién elige los pesos.
4. **¿Se entiende sin conocimientos previos?** Sí. Peso es importancia, error es lo que se mide y el descenso de gradiente es bajar un cerro a ciegas.
5. **¿Hay continuidad?** Sí: la misma cara recorre todo el video.
6. **¿El resultado responde al inicio?** Sí: «Aprendió qué mirar».
7. **¿Es correcto?** Las cifras salen del experimento y se presentan como «en este ejemplo». En pantalla se aclara que es una simulación con rostros sintéticos y que los sistemas reales usan sensores y redes de cada fabricante.

## Publicación

**Título:** ¿Cómo sabe tu celular que eres tú? 📱

**Descripción:**
> Te cortas el pelo, te pones lentes… y tu celular igual se desbloquea. Pero para él, tu cara es solo una grilla de números, y con otra luz casi todos cambian.
> Entonces, ¿cómo sabe que eres tú? Entrenamos una red neuronal desde cero para mostrarlo: no memoriza tu foto, aprende qué mirar.
> (Simulación con rostros sintéticos; cada fabricante usa sus propios sensores y redes.)
> ¿Qué otra cosa de tu celular quieres entender? 👇
> #DetrásDelAlgoritmo #DeepLearning #RedesNeuronales #IA #Tecnología #Ciencia #AprendeEnTikTok
