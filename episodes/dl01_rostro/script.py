"""Guion — «¿Cómo sabe tu celular que eres tú?» · Detrás del Algoritmo · Deep Learning EP 01

Cadena causal (cada bloque responde la pregunta que deja el anterior):
  hook        cambias de look y el celular igual te reconoce → ¿cómo sabe que eres tú?
  pixeles     ¿qué ve el celular? → una grilla de números (luz en cada punto)
  dificil     ¿y por qué no comparar esos números? → cambian casi todos con otra luz/peinado;
              en este ejemplo, tu foto nueva se parece menos a ti que otra persona (medido)
  reglas      ¿y si escribimos reglas? → medidas a mano se rompen (feature engineering)
  neurona     ¿entonces? → que la máquina aprenda qué mirar; la pieza: una neurona
              (pesos, suma, se enciende) → con ciertos pesos, detecta bordes
  capas       ¿y una cara? → capas: bordes → partes → «huella» del rostro (deep learning)
  aprender    ¿quién elige los pesos? → nadie: se aprenden con ejemplos, error y ajuste
              (pérdida + descenso de gradiente, el cerro a ciegas) — curva real
  resultado   ¿funciona? → las huellas se ordenan por persona; la foto nueva cae en tu grupo
  cierre      tu celular no memoriza tu foto: aprendió qué mirar (vuelve al hook)

Experimento real (experiment.py): 8 personas sintéticas, red de 3 capas entrenada desde cero.
"""
from reelforge.timeline import Beat, Ph

EPISODE = {
    "num": 1,
    "slug": "dl01_rostro",
    "title": "¿Cómo sabe tu celular que eres tú?",
    "tag": "DETRÁS DEL ALGORITMO · DEEP LEARNING",
}

Q = "+5Hz"
SLOW = "-4%"

BEATS = [
    Beat("hook", [
        Ph("Te cortas el pelo, te pones lentes...", pause=0.15),
        Ph("y tu celular igual se *desbloquea*.", pause=0.4),
        Ph("¿Cómo sabe que eres *tú*?", pause=0.5, pitch=Q),
    ]),
    Beat("pixeles", [
        Ph("Para el celular, tu cara no es una cara:", pause=0.1),
        Ph("es una grilla de *números*. Cuánta luz llegó a cada punto.", pause=0.45),
    ]),
    Beat("dificil", [
        Ph("Y basta cambiar la luz o el peinado para que casi *todos* esos números cambien.", pause=0.3),
        Ph("En este ejemplo, tu foto nueva se parece menos a ti...", pause=0.1),
        Ph("que la foto de *otra persona*.", pause=0.5),
    ]),
    Beat("reglas", [
        Ph("Podríamos escribir *reglas* a mano: medir los ojos, la nariz, la boca...", pause=0.15),
        Ph("pero con sombras, ángulos y lentes, las reglas se *rompen*.", pause=0.5),
    ]),
    Beat("neurona", [
        Ph("La salida fue otra: dejar que la máquina *descubra* qué mirar.", pause=0.3),
        Ph("Su pieza básica es una *neurona artificial*:", pause=0.1),
        Ph("multiplica cada punto por un *peso*, suma todo, y se *enciende* si el resultado es alto.", pause=0.3),
        Ph("Con los pesos adecuados, esta neurona se enciende con los *bordes*.", pause=0.45),
    ]),
    Beat("capas", [
        Ph("Si apilas *capas* de neuronas, las siguientes combinan bordes en partes: un ojo, una nariz...", pause=0.12),
        Ph("y las últimas, en una especie de *huella* de tu rostro.", pause=0.3),
        Ph("Muchas capas: por eso se llama aprendizaje *profundo*.", pause=0.45),
    ]),
    Beat("aprender", [
        Ph("¿Y quién elige todos esos pesos? *Nadie*. Se aprenden.", pause=0.3),
        Ph("Le mostramos miles de fotos. Cada vez que confunde a dos personas, medimos el *error*...", pause=0.1),
        Ph("y movemos cada peso un poquito en la dirección que lo *reduce*.", pause=0.25),
        Ph("Como bajar un cerro a ciegas, paso a paso.", pause=0.45),
    ]),
    Beat("resultado", [
        Ph("Al final, las huellas se *ordenan* por persona, aunque cambie la luz o el peinado.", pause=0.3),
        Ph("Y tu foto nueva cae justo en *tu* grupo.", pause=0.5),
    ]),
    Beat("cierre", [
        Ph("Así que tu celular no memoriza una foto tuya.", pause=0.2),
        Ph("Aprendió *qué mirar*.", pause=0.3, rate=SLOW),
    ]),
]
