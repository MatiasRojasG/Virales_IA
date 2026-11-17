# Nadie les enseñó a sobrevivir

**Video:** `output/viral03_bolas_evolucionan.mp4` (1080×1920, 60 fps, ~55,6 s).

- **Inspiración (solo el estilo):** reels «satisfying» de bolas que se multiplican dentro de un círculo con un engranaje (p. ej. *«The gear turns, the balls multiply»*, ~959 mil me gusta). La mecánica, la historia y el diseño son propios.
- **Concepto:** algoritmos genéticos (copiar con mutación + selección).
- **Simulación real** (`experiment.py`, NumPy, semilla 5):
  - Las bolas se mueven a rapidez constante. Cada una gira hacia el centro con una intensidad propia `a ∈ [0, 1]`, que es su color: violeta = gira poco, cyan = gira mucho.
  - Al tocar el engranaje, la bola se copia. La copia hereda `a` con una mutación N(0; 0,08). Caben como máximo 160 bolas.
  - Si una bola toca el borde rosado, desaparece. Ese borde crece entre los 22 s y los 62 s de simulación, hasta cubrir todo el círculo.
  - Resultado: 5 bolas pasan a 160, con 1419 copias y 1264 desapariciones. El giro medio sube de 0,10 a 0,78, y las bolas con `a > 0,6` pasan del 0 % al 99 %. Nadie programa la estrategia de orbitar el engranaje.
- **Tiempo:** la simulación se acelera suavemente para coincidir con la voz. Va a 1× en el inicio y a ~4,6× en «generación tras generación».
- **Dato real:** la NASA diseñó con un algoritmo evolutivo la antena de la misión Space Technology 5, lanzada en 2006. El dibujo del video es simbólico y no reproduce la geometría exacta.
- **Voz:** `es-MX-JorgeNeural` a +19 %.

**Texto para publicar:**
> Cada bola que toca el engranaje se copia… y nadie les enseñó a sobrevivir 🧬
> Así funciona un algoritmo genético: copiar, cambiar un poquito y quedarse con lo que funciona.
> ¿Te diste cuenta en qué momento cambiaron de color? 👇
> #DetrásDelAlgoritmo #IA #InteligenciaArtificial #Satisfying #AlgoritmoGenetico #Evolución #Ciencia
