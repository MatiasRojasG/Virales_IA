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
  bolita      ¿qué significa "equilibrar"? → una bolita, un resorte a la cámara, resortes a los vecinos
  calculo     ¿por qué no calcularla directo? → demasiadas combinaciones → ajuste local repetido
  formula     nombre del concepto + la fórmula de la clase leída como resortes (energía ↔ probabilidad)
  usos        dónde más se usa (documentos, resonancias, satélites) + aclaración honesta
  cierre      responde la pregunta del inicio y empalma con el primer cuadro (loop)

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
    "tag": "",
    "next": "",
}

Q = "+5Hz"
SLOW = "-4%"

BEATS = [
    Beat("hook", [
        Ph("Tu cámara vio *esto*.", pause=0.45),
        Ph("Pero tu celular te mostró *esto*.", pause=0.6),
        Ph("¿De dónde sacó lo que la cámara *no vio*?", pause=0.8, pitch=Q),
    ]),
    Beat("luz", [
        Ph("De noche, a cada punto del sensor le llegan apenas unas *gotas de luz*...", pause=0.15),
        Ph("y al azar.", pause=0.4, rate=SLOW),
        Ph("Por eso, un muro parejo sale *moteado*.", pause=0.6),
    ]),
    Beat("dificil", [
        Ph("Mirando un solo punto, no hay cómo saber si brilla de verdad...", pause=0.15),
        Ph("o es puro *ruido*.", pause=0.6),
    ]),
    Beat("vecinos", [
        Ph("Pero lo que está al lado suele *parecerse*.", pause=0.35),
        Ph("Así que cada punto puede corregirse mirando a sus *vecinos*.", pause=0.6),
    ]),
    Beat("exceso", [
        Ph("Aunque, si solo promedias, también se borran los *bordes*...", pause=0.15),
        Ph("y el letrero se vuelve *ilegible*.", pause=0.7),
    ]),
    Beat("bolita", [
        Ph("Imagina cada punto como una *bolita*: más arriba, más brillante.", pause=0.35),
        Ph("Un resorte la amarra a lo que *midió la cámara*: si se aleja, la tira de vuelta.", pause=0.35),
        Ph("Otros la unen a sus *vecinos*, y la acercan.", pause=0.3),
        Ph("Se queda donde las fuerzas se *equilibran*.", pause=0.6),
    ]),
    Beat("resortes", [
        Ph("En una fila del letrero, si todos tiran igual, los bordes se *aplanan*.", pause=0.35),
        Ph("Pero si un vecino es muy distinto, es otro objeto:", pause=0.15),
        Ph("ese resorte *se suelta*... y las letras vuelven.", pause=0.7),
    ]),
    Beat("calculo", [
        Ph("Cada punto se acomoda así, mirando a sus vecinos... y repetimos.", pause=0.6),
    ]),
    Beat("formula", [
        Ph("Puntos que se influyen sin que ninguno mande: una *red de Markov*.", pause=0.45),
        Ph("La *tensión* de sus resortes se llama *energía*:", pause=0.2),
        Ph("mientras menor, más *probable* la foto.", pause=0.8, rate=SLOW),
    ]),
    Beat("usos", [
        Ph("La misma idea rescata *documentos*, delimita *tumores* y mapea *bosques* desde satélites.", pause=0.5),
    ]),
    Beat("cierre", [
        Ph("Así que ya sabes de dónde sacó tu celular lo que la cámara no vio...", pause=0.3),
        Ph("de sus *vecinos*.", pause=0.5, rate=SLOW),
    ]),
]
