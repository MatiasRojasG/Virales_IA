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
    "tag": "DETRÁS DEL ALGORITMO · EP 01",
    "next": "",
}

Q = "+5Hz"
SLOW = "-4%"

BEATS = [
    # Primer segundo: la imagen con ruido ya está en pantalla con un titular.
    Beat("hook", [
        Ph("Tu cámara vio *esto*.", pause=0.3),
        Ph("Pero tu celular te mostró *esto*.", pause=0.4),
        Ph("¿De dónde sacó lo que la cámara *no vio*?", pause=0.5, pitch=Q),
    ]),
    Beat("luz", [
        Ph("De noche, a cada punto del sensor le llegan apenas unas *gotas de luz*...", pause=0.1),
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
    # Los resortes: primero UNA bolita, cada resorte por separado; después la fila entera.
    Beat("bolita", [
        Ph("Imagina cada punto como una *bolita*: mientras más arriba, más brillante.", pause=0.35),
        Ph("Un resorte la amarra a lo que *midió la cámara*: si se aleja, la tira de vuelta.", pause=0.4),
        Ph("Otros resortes la unen a sus *vecinos*: si es distinta a ellos, la acercan.", pause=0.4),
        Ph("La bolita se queda donde las dos fuerzas se *equilibran*.", pause=0.5),
    ]),
    Beat("resortes", [
        Ph("En una fila del letrero, si todos los resortes tiran igual, los bordes se *aplanan*.", pause=0.35),
        Ph("Pero si un vecino es demasiado distinto, seguro es otro objeto:", pause=0.1),
        Ph("ese resorte *se suelta*... y las letras vuelven.", pause=0.45),
        Ph("La foto con menos *tensión* total es la explicación *más probable* de lo que vio la cámara.", pause=0.5),
    ]),
    Beat("calculo", [
        Ph("¿Y por qué no calcularla de una vez?", pause=0.3, pitch=Q),
        Ph("Con cientos de brillos por punto y *doce millones* de puntos, hay más fotos posibles que *átomos en el universo*.", pause=0.4),
        Ph("Así que cada punto se acomoda mirando a sus vecinos...", pause=0.1),
        Ph("y *repetimos*.", pause=0.5),
    ]),
    # La idea completa: nombre, fórmula y su relación con los resortes.
    Beat("formula", [
        Ph("Puntos que se influyen sin que ninguno mande: eso es una *red de Markov*.", pause=0.35),
        Ph("Y los resortes tienen fórmula:", pause=0.25),
        Ph("el de la cámara mide cuánto te alejas de lo *observado*;", pause=0.1),
        Ph("los de los vecinos, cuánto te *diferencias* de ellos.", pause=0.3),
        Ph("Su suma es la *energía*... y mientras menor la energía, más probable la foto.", pause=2.2),
    ]),
    Beat("usos", [
        Ph("La misma idea rescata *documentos* escaneados, delimita *tumores* en resonancias...", pause=0.1),
        Ph("y clasifica *bosques* y ciudades en imágenes satelitales.", pause=0.5),
    ]),
    # Cierre que responde la pregunta del inicio y empalma con el primer cuadro.
    Beat("cierre", [
        Ph("Así que ahora ya sabes de dónde sacó tu celular lo que la cámara no vio...", pause=0.15),
        Ph("de sus *vecinos*.", pause=0.3, rate=SLOW),
    ]),
]
