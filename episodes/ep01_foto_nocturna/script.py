"""Guion — «La foto nocturna» · Detrás del Algoritmo · EP 01

Enfoque: no se explica la clase; la clase explica algo del mundo.
Pregunta motora: ¿cómo puede una foto de noche salir limpia si a la cámara le faltó luz?

Cadena causal (cada bloque responde a la pregunta que deja el anterior):
  hook        foto granulada → el celular la entrega limpia → ¿de dónde sacó lo que no vio?
  luz         ¿por qué salen granos?  → pocos fotones, al azar (simulación)
  dificil     ¿y no se puede corregir cada punto? → solo, es imposible saber
  vecinos     ¿entonces?  → lo que está al lado suele parecerse
  exceso      ¿basta con promediar? → no: se borran los bordes
  resortes    ¿cómo equilibrar? → resortes hacia la cámara y hacia los vecinos;
              el que une objetos distintos se suelta; mínima tensión = foto más probable
  calculo     ¿por qué no calcularla directo? → demasiadas combinaciones → ajuste local repetido
  revelacion  resultado + nombre del concepto (recién aquí) + aclaración honesta
  puente      la misma idea, otro problema (próximo episodio)

Conceptos de la clase que aparecen (sin nombrarlos como clase):
  relaciones simétricas sin causa (red no dirigida), factores de compatibilidad
  (datos y suavidad), producto de factores ↔ energía (P ∝ e^(−E): menor tensión = más probable),
  explosión combinatoria (2ⁿ, por qué no se calcula todo), actualización local iterada (ICM),
  compromiso de β (poco: ruido; mucho: se pierden detalles) y la manta de Markov
  (cada punto solo necesita a sus vecinos).
"""
from reelforge.timeline import Beat, Ph

EPISODE = {
    "num": 1,
    "slug": "ep01_foto_nocturna",
    "title": "¿Cómo limpia tu celular una foto nocturna?",
    "tag": "DETRÁS DEL ALGORITMO · EP 01",
    "next": "Próximo: el documento ilegible",
}

Q = "+5Hz"
SLOW = "-4%"

BEATS = [
    Beat("hook", [
        Ph("Tomas una foto de noche...", pause=0.15),
        Ph("y sale así: llena de *granitos*.", pause=0.4),
        Ph("Pero tu celular te muestra *esta*.", pause=0.45),
        Ph("¿De dónde sacó lo que la cámara *no vio*?", pause=0.55, pitch=Q),
    ]),
    Beat("luz", [
        Ph("Con poca luz, a cada punto del sensor le llegan apenas unas *gotas de luz*...", pause=0.1),
        Ph("y al azar.", pause=0.35, rate=SLOW),
        Ph("Por eso, un muro parejo sale *moteado*.", pause=0.45),
    ]),
    Beat("dificil", [
        Ph("Y mirando un solo punto, no hay cómo saber si brilla de verdad...", pause=0.12),
        Ph("o es puro *ruido*.", pause=0.45),
    ]),
    Beat("vecinos", [
        Ph("Pero lo que está al lado suele *parecerse*.", pause=0.25),
        Ph("Así que cada punto puede corregirse mirando a sus *vecinos*.", pause=0.45),
    ]),
    Beat("exceso", [
        Ph("Aunque, si solo promedias, también se borran los *bordes*...", pause=0.1),
        Ph("y el letrero se vuelve *ilegible*.", pause=0.5),
    ]),
    Beat("resortes", [
        Ph("Imagina cada punto atado con *resortes*:", pause=0.15),
        Ph("uno lo tira hacia lo que vio la *cámara*, y otros hacia sus *vecinos*.", pause=0.35),
        Ph("Si un vecino es demasiado distinto, seguro es otro objeto:", pause=0.1),
        Ph("ese resorte *se suelta*.", pause=0.4),
        Ph("Cada punto se queda donde la *tensión* es mínima...", pause=0.12),
        Ph("y esa foto, la de menor tensión, es la explicación *más probable* de lo que vio la cámara.", pause=0.5),
    ]),
    Beat("calculo", [
        Ph("¿Y por qué no calcularla de una vez?", pause=0.3, pitch=Q),
        Ph("Cada punto puede tomar cientos de brillos, y una foto tiene *doce millones* de puntos:", pause=0.1),
        Ph("hay más fotos posibles que *átomos en el universo*.", pause=0.4),
        Ph("Así que cada punto se acomoda mirando solo a sus vecinos...", pause=0.1),
        Ph("y *repetimos*.", pause=0.5),
    ]),
    Beat("revelacion", [
        Ph("Puntos que se influyen sin que ninguno mande: eso es una *red de Markov*.", pause=0.35),
        Ph("Tu celular usa versiones mucho más sofisticadas, pero la idea de fondo es esta:", pause=0.12),
        Ph("un punto se entiende mejor... mirando a su *alrededor*.", pause=0.5, rate=SLOW),
    ]),
    Beat("puente", [
        Ph("Con la misma idea se rescata un *documento ilegible*.", pause=0.2),
        Ph("Eso, en el próximo.", pause=0.2),
    ]),
]
