"""Guion — «¿Por qué tu banco bloqueó tu café?» · Detrás del Algoritmo · Incertidumbre EP 01

Clase base: EPG4003, 22-oct (diap. 3 «riesgo y fraude», diap. 8-9 Bayes y tasa base, diap. 12-13
independencia condicional). Números del ejemplo: los de la diap. 9 (1 %, 99 %, 5 %), presentados
SIEMPRE como ejemplo ilustrativo, nunca como estadística real de un banco.

Cadena causal:
  hook        te bloquean una compra legítima en un viaje
  intuicion   el detector atrapa 99 de cada 100 fraudes → «si me marcó, casi seguro era fraude» (≈ 95-99 %)
  dificultad  falta un dato que nadie pregunta: ¿qué tan común es el fraude?
  simulacion  1.000 compras, 10 fraudes; alarmas: 10 reales + ~49 falsas
  descubrir   de 59 alarmas, solo 10 eran fraude → 1 de cada 6 (≈ 17 %)
  porque      el grupo normal es enorme: un error chico sobre muchos > aciertos sobre pocos
  bayes       recién aquí: la regla de Bayes como «alarmas que son fraude / todas las alarmas»
  solucion    sumar evidencia: el 17 % es el nuevo punto de partida; una 2.ª señal que falle
              por su cuenta (independencia condicional) lleva a ≈ 80 %
  usos        exámenes médicos, alarmas de fábrica (misma cuenta)
  cierre      responde el hook y vuelve al primer cuadro
"""
from reelforge.timeline import Beat, Ph

EPISODE = {
    "num": 1,
    "slug": "inc01_compra_bloqueada",
    "title": "¿Por qué tu banco bloqueó tu café?",
    "tag": "DETRÁS DEL ALGORITMO · INCERTIDUMBRE 01",
}

Q = "+5Hz"
SLOW = "-4%"

BEATS = [
    Beat("hook", [
        Ph("Estás de viaje, pagas un café...", pause=0.12),
        Ph("y tu banco *bloquea* la tarjeta.", pause=0.45),
        Ph("¿Cómo pudo equivocarse un sistema tan sofisticado?", pause=0.5, pitch=Q),
    ]),
    Beat("intuicion", [
        Ph("Imagina un detector que atrapa *99 de cada 100* fraudes...", pause=0.1),
        Ph("y que solo se equivoca con *5 de cada 100* compras normales.", pause=0.35),
        Ph("Si te marcó a ti, parece obvio: casi seguro era *fraude*.", pause=0.45),
    ]),
    Beat("dificultad", [
        Ph("Pero falta un dato que casi nadie pregunta:", pause=0.15),
        Ph("¿qué tan *común* es el fraude?", pause=0.5, pitch=Q),
    ]),
    Beat("simulacion", [
        Ph("Pensemos en *mil compras*, y supongamos que solo *diez* son fraude.", pause=0.35),
        Ph("El detector atrapa a las diez.", pause=0.3),
        Ph("Pero de las novecientas noventa normales, se equivoca con cinco de cada cien:", pause=0.1),
        Ph("unas *49* también hacen sonar la alarma.", pause=0.5),
    ]),
    Beat("descubrir", [
        Ph("Ahora mira solo las *alarmas*.", pause=0.35),
        Ph("De cincuenta y nueve, apenas diez eran fraude.", pause=0.2),
        Ph("*Una de cada seis*.", pause=0.55, rate=SLOW),
    ]),
    Beat("porque", [
        Ph("El detector no es malo: las compras normales son *muchísimas* más,", pause=0.1),
        Ph("y un error pequeño sobre un grupo enorme suma más alarmas que el fraude real.", pause=0.45),
    ]),
    Beat("bayes", [
        Ph("Esa cuenta tiene nombre: *regla de Bayes*.", pause=0.3),
        Ph("Arriba, las alarmas que sí son fraude. Abajo, *todas* las alarmas.", pause=0.35),
        Ph("Y el dato que lo cambia todo es la *tasa base*: qué tan raro es el fraude desde el principio.", pause=0.5),
    ]),
    Beat("solucion", [
        Ph("¿Entonces cómo se decide bien? *Sumando evidencia*.", pause=0.3),
        Ph("Ese uno de cada seis es el nuevo punto de partida.", pause=0.25),
        Ph("Si una segunda señal, que se equivoca por su cuenta, también suena...", pause=0.12),
        Ph("la probabilidad salta a cerca de *ocho de cada diez*.", pause=0.5),
    ]),
    Beat("usos", [
        Ph("La misma cuenta explica por qué un *examen médico* positivo no siempre significa estar enfermo...", pause=0.1),
        Ph("y por qué las *alarmas* de una fábrica suenan tanto en falso.", pause=0.45),
    ]),
    Beat("cierre", [
        Ph("Así que si un día te bloquean un café en el extranjero:", pause=0.15),
        Ph("no es que el detector sea malo.", pause=0.15),
        Ph("Es que el fraude es *raro*.", pause=0.3, rate=SLOW),
    ]),
]
