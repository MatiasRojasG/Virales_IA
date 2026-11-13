# Serie «Redes de Markov» — plan de episodios

Fuente: clase *Métodos Probabilísticos para el Aprendizaje de Máquinas — Modelos gráficos no dirigidos: factores, redes de Markov e imágenes* (Alfredo Alegría, PUC Chile, EPG4003, 12-nov-2026). 22 diapositivas.

## Mapa conceptual del material

```
Sistemas sin flechas (píxeles, sensores, mallas)
   └─► Grafos NO dirigidos  ≠  redes bayesianas (DAG)
          ├─ Ejemplo 4 estudiantes: A⊥C|{B,D}, B⊥D|{A,C}  → ningún DAG lo codifica
          └─► Factores φ(D): afinidad, no normalizados
                 └─► Conjunta = (1/Z) ∏ φ  ·  Z = Σ (2ⁿ términos) = cuello de botella
                        ├─ Límites de factores por pares: 2n(n−1) vs 2ⁿ−1 → cliques
                        ├─ Separación: todo camino X→Y pasa por Z  ·  manta de Markov
                        └─ Forma de energía: φ = exp(−E) → MAP = minimizar costo, Z se cancela
                               └─► Imágenes: P(y|x) ∝ ∏ φᵢ(yᵢ,xᵢ) ∏ ψᵢⱼ(yᵢ,yⱼ)
                                      └─ Ising: exp{α Σ sᵢuᵢ + β Σ sᵢsⱼ}  ·  ICM
                                             └─ Restauración: 15 % ruido → 2,5 %, OCR 42 % → 94 %
```

## Enfoque de la serie (desde la v3)

**No explicamos la clase: usamos la clase para explicar el mundo.** Cada episodio parte de un
problema cotidiano y llega a las ideas de la clase como consecuencia lógica. Los términos técnicos
se nombran solo después de haber sido entendidos.

| # | Pregunta del mundo real | Ideas de la clase que la responden | Estado |
|---|---|---|---|
| 01 | ¿Cómo limpia tu celular una foto nocturna? | Vecinos simétricos, factores de datos y suavidad, energía ↔ probabilidad, explosión combinatoria, actualización local (ICM), compromiso de β | ✅ `episodes/ep01_foto_nocturna` |
| 02 | ¿Cómo se rescata un documento ilegible para que un lector automático lo entienda? | Etiquetas binarias, modelo de Ising (α, β), ICM, OCR 42 % → 94 % | borrador v2 en `episodes/ep01_restauracion_documento` (hay que adaptarlo al nuevo enfoque y al número 02) |
| 03 | ¿Por qué un rumor entre cuatro amigos no se puede dibujar con flechas? | Ejemplo de 4 estudiantes, A⊥C\|{B,D}, colisionadores, límites de los DAG | pendiente |
| 04 | ¿Cómo «puntúa» una app de citas qué tan compatibles son dos personas? | Factores como afinidad no normalizada, tablas φ, producto de factores | pendiente |
| 05 | ¿Por qué el pronóstico del tiempo no puede revisar todos los futuros posibles? | Constante Z, 2ⁿ términos, cuello de botella, métodos aproximados | pendiente |
| 06 | ¿Por qué tres amigos juntos no son la suma de tres parejas? | Límites de los factores por pares, interacciones de orden 3, cliques | pendiente |
| 07 | ¿Qué necesitas saber de tu vecino para predecir tu cuenta de luz? | Separación, independencia condicional, manta de Markov | pendiente |
| 08 | ¿Por qué los sistemas «buscan» el estado de menor energía? | Forma de energía, MAP = minimizar costo, Z se cancela | pendiente |

---

## Plan original (v1, por orden de la clase; se conserva como referencia)



El episodio 1 abre con el resultado más sorprendente (restauración + OCR) como «tráiler» de la serie;
desde el 2 se construye la teoría en orden, y el 9–10 vuelve al experimento con todo el detalle formal.

| # | Título de trabajo | Concepto central (diapositivas) | Hook (primeros 2 s) | Visual clave | Estado |
|---|---|---|---|---|---|
| 01 | El documento ilegible | Restauración con red de Markov: vecinos, α/β, ICM, OCR (3, 14–18) | «15 % de los píxeles invertidos» sobre el documento con ruido | Zoom a píxeles, malla → grafo, balance α vs β, iteraciones | ✅ renderizado |
| 02 | Redes sin flechas | Sistemas simétricos; dirigido vs no dirigido (4) | Dos píxeles con una flecha que se tacha: «¿quién causa a quién?» | Tres paneles (imagen, sensores, malla) → aristas simétricas | guion pendiente |
| 03 | Cuatro estudiantes y un malentendido | Ejemplo A-B-C-D; A⊥C\|{B,D}; ningún DAG sirve; colisionadores (5–6) | «Este problema no cabe en ninguna red bayesiana» | Ciclo A-B-C-D; intento de orientar y colisionador que *abre* el camino | guion pendiente |
| 04 | Factores: medir la compatibilidad | Factor φ: Val(D)→ℝ₊, afinidad, no normalizado; tablas φ₁…φ₄ (7–8) | «Este número no es una probabilidad… y está bien» | Tablas que se transforman en barras de afinidad por pareja | guion pendiente |
| 05 | La constante Z | Producto de factores, Z = 7 201 840, 2ⁿ términos (9) | «Para normalizar 4 variables sumo 16 términos; para 300, más que átomos en el universo» | Árbol de 16 configuraciones → explosión 2ⁿ | guion pendiente |
| 06 | Lo que los pares no ven | 4·C(n,2) = 2n(n−1) vs 2ⁿ−1 (180 vs 1023); interacciones de orden 3; cliques (10) | «180 parámetros contra 1023» | Contador de parámetros + triángulo que necesita factor propio | guion pendiente |
| 07 | Separación: cortar el grafo | X⊥Y\|Z si todo camino pasa por Z; no hay colisionadores (11) | «En estas redes, observar siempre bloquea» | Caminos animados que se apagan al llegar a nodos observados | guion pendiente |
| 08 | Manta de Markov y energía | Manta = vecinos; ∏ φ_c sobre cliques; φ = exp(−E); MAP = min energía; Z se cancela (11–12) | «Para predecir un nodo, basta mirar a sus vecinos» | Paisaje de energía 3D; bola que cae al mínimo | guion pendiente |
| 09 | Ising: α contra β | Etiquetado de imágenes, término de datos/suavidad, Ising con sᵢ = 2yᵢ−1, efecto de β, ICM (13–15) | «Un solo número decide si ves ruido o una mancha» | Barrido de β en vivo (simulación) + ICM paso a paso | guion pendiente |
| 10 | Del código al OCR | Implementación (R → Python), vecinos(), 30 pasadas, resultados, bordes, OCR (16–18) | «30 líneas de código, del 42 % al 94 %» | Código que se escribe + mapas de error + comparación de texto OCR | guion pendiente |

> Nota técnica para el EP 09: con 4 vecinos la suma Σsⱼ ∈ {−4,−2,0,2,4}; por eso, con la regla
> simultánea de la clase, cualquier β > α/2 ≈ 0,43 da exactamente el mismo resultado (lo verificamos:
> β = 0,6; 1,2; 2,5; 5 → mismo error 2,6 %). Para mostrar «β grande borra detalles» hará falta una
> vecindad de 8 o más píxeles o una versión con probabilidades (muestreo de Gibbs). Esto se explicará
> como hallazgo propio, sin atribuirlo a la clase.

## Hilo conductor entre episodios

Cada cierre adelanta la pregunta del episodio siguiente (01→02: «¿por qué aquí no sirven las flechas?»;
02→03: «¿hay independencias que ningún DAG puede expresar?»; … 08→09: «¿y si los nodos son píxeles?»).
