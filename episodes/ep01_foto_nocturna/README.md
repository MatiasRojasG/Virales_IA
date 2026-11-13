# EP 01 — ¿Cómo limpia tu celular una foto nocturna? · Detrás del Algoritmo

**Video:** `output/ep01_foto_nocturna.mp4`: 1080×1920, 60 fps, H.264 + AAC 48 kHz, **82,4 s**, −14,8 LUFS, pico −1 dBFS.
Se verificó lo siguiente:
- No hay saltos de un solo cuadro.
- Los subtítulos van 60 ms antes de la voz.
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

## Storyboard

| t (s) | Bloque | Lo que ocurre en pantalla |
|---|---|---|
| 0–8,5 | Hook | Celular, disparo con destello y foto granulada. La versión limpia se revela con un barrido y luego se rebobina; queda un «?». |
| 8,5–16,6 | Luz | La cámara entra al muro. Caen gotas de luz en cada punto, con su conteo (0, 1, 5, 8…), y el muro parejo queda moteado. |
| 16,6–21,6 | Difícil | Spotlight sobre un punto con 8 gotas: «¿brillo real?» / «¿ruido?». |
| 21,6–27,3 | Vecinos | El foco se abre a 8 vecinos y el punto adopta el promedio (8 → 2,9). Una onda aplica el promedio a toda la foto. |
| 27,3–32,8 | Exceso | El muro queda limpio, pero el letrero queda borroso y aparece «ILEGIBLE». |
| 32,8–51,6 | Resortes | Una fila del letrero se convierte en cuentas con resortes. Primero se aplana; luego los resortes entre objetos distintos se sueltan (rosado) y los bordes vuelven. Se ven la barra de tensión y la de probabilidad. |
| 51,6–65,6 | Cálculo | 1 punto equivale a 256 brillos; se cuentan 12 000 000 puntos; fotos posibles vs. átomos. La foto se limpia pasada a pasada. |
| 65,6–77,4 | Revelación | Retícula «RED DE MARKOV». Se vuelve al celular con un deslizador antes/después y la aclaración en pantalla. |
| 77,4–82,4 | Puente | El documento ilegible y «Próximo: el documento ilegible». |
