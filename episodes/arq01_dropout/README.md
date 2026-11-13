# ¿Por qué apagar neuronas hace más lista a una red? (metadato interno: arquitecturas, ep. 1)

**Video:** `output/arq01_dropout.mp4`: 1080×1920, 60 fps, 85,6 s, −15,0 LUFS, pico −1 dBFS.
Se verificó lo siguiente:
- No hay saltos de un solo cuadro.
- Los subtítulos van 50 ms antes de la voz.
- El video no tiene títulos ni banners (regla permanente en `CLAUDE.md`).

## Serie propuesta (PDF «Arquitecturas neuronales fundamentales»)

| # | Historia | Conceptos |
|---|---|---|
| 1 | **¿Por qué apagar neuronas hace más lista a una red?** ✅ | Sobreajuste, generalización, dropout |
| 2 | ¿Cómo lee tu número escrito a mano? | MLP con imágenes, softmax, entropía cruzada |
| 3 | ¿Cómo descubre una app que dos productos se parecen? | Variables categóricas, one-hot, embeddings, similitud aprendida |
| 4 | La red que puede dibujar cualquier forma… en teoría | Capa oculta, no linealidad, fronteras, aproximación universal y sus límites |
| 5 | ¿Por qué la red que lee números falla con ropa y tablas? | Sesgo inductivo, límites de los MLP en imágenes y datos tabulares |

## Historia

1. **Hook.** Un estudiante memoriza las pruebas anteriores: saca 10/10 en la práctica y reprueba la real.
2. **La paradoja.** A las redes les pasa lo mismo, y una solución es apagar neuronas al azar.
3. **El problema.** Una red predice si lloverá a partir de la humedad y la presión. Cada día es un punto, y hay días raros.
4. **Sobreajuste.** La red sin dropout dibuja islas alrededor de los días raros. En los días conocidos acierta el 96 %; en los nuevos, el 78 %.
5. **Por qué.** La red es tan flexible que aprende hasta el ruido, y unas neuronas «especialistas» cargan con el resto.
6. **Dropout.** En cada paso se apaga una mitad distinta de las neuronas. Nadie puede depender de otra, como en un equipo donde cualquiera puede faltar.
7. **Resultado.** Al usar la red se encienden todas y la frontera queda simple. En los días conocidos baja de 96 % a 86 %; en los nuevos sube de 78 % a 83 %.
8. **Cierre.** Se trata de entender la materia, no de memorizar las pruebas. La prueba real ahora sale aprobada.

## Experimento (`experiment.py`, datos simulados)

- **Datos.** 300 días de entrenamiento con regla verdadera suave y 15 % de etiquetas invertidas. La prueba usa 5.000 días nuevos con el mismo ruido, así que el techo alcanzable es ≈ 85 %.
- **Modelo.** MLP de 2 → 256 → 256 → 1 con ReLU, Adam (lr = 0,001) y 2.000 pasos de lote completo.
- **Dropout.** Se usa p = 0,5 en ambas capas ocultas, solo al entrenar, con la escala estándar.

| Promedio de 5 semillas | Días conocidos | Días nuevos |
|---|---|---|
| Sin dropout | 95,7 % | 77,5 % |
| Con dropout | 86,2 % | **82,5 %** |

El dropout mejoró los días nuevos en las 5 semillas. Las fronteras del video son las de la semilla 0.

Antes de elegir esta configuración se probó otra, con 150 días y 4.000 pasos: ahí el dropout apenas ayudaba (73 % → 75 %) y ambas fronteras quedaban sobreajustadas. Se documenta porque **el dropout no siempre basta**, y el video no lo presenta como solución universal.

## Publicación

**Título:** ¿Por qué apagar neuronas hace más lista a una IA? 🧠

**Descripción:**
> Un estudiante memoriza todas las pruebas anteriores: 10/10 en la práctica… y reprueba la real. A las redes neuronales les pasa lo mismo.
> La solución suena absurda: apagar neuronas al azar mientras aprende. Lo probamos con una red de verdad, y en días nuevos acertó más.
> (Datos simulados; resultados de un experimento propio, promedio de 5 simulaciones.)
> ¿Tú memorizabas o entendías? 👇
> #DetrásDelAlgoritmo #IA #RedesNeuronales #DeepLearning #Ciencia #Tecnología #AprendeEnTikTok
