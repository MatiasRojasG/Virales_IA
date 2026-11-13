"""Guion — «¿Cómo sabe tu celular que eres tú?» · Detrás del Algoritmo · Deep Learning EP 01

Cadena causal (cada bloque responde la pregunta que deja el anterior):
  hook        cambias de look y el celular igual te reconoce → ¿cómo sabe que eres tú?
  pixeles     ¿qué ve el celular? → una grilla de números (luz en cada punto)
  dificil     ¿y por qué no comparar esos números? → cambian casi todos con otra luz/peinado;
              en este ejemplo, tu foto nueva se parece menos a ti que otra persona (medido)
  reglas      ¿y si escribimos reglas? → medidas a mano se rompen (feature engineering)
  neurona     ¿entonces? → que la máquina aprenda qué mirar; la pieza: una neurona. ¿qué le entra?
              → un pedacito de imagen (números de luz)
  pesos       ¿qué hace con ellos? → cada punto tiene un peso (+ quiero luz, − quiero oscuridad)
  suma        → multiplica y suma → sale UN número; alto = se enciende; zona pareja ≈ 0
  barrido     ejemplo: pesos − 0 + = busca un borde → recorriendo la cara, se enciende en los bordes
  capas       capa = grupo de neuronas → salen MAPAS → esos mapas ENTRAN a la capa siguiente →
              bordes → partes → huella (aprendizaje profundo)
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
        Ph("Y basta cambiar la luz o el peinado para que casi *todos* esos números cambien.", pause=0.25),
        Ph("Tanto, que en este ejemplo tu foto nueva se parece más a *otra persona*.", pause=0.45),
    ]),
    Beat("reglas", [
        Ph("Podríamos escribir *reglas*: medir ojos, nariz y boca...", pause=0.1),
        Ph("pero con sombras y lentes, se *rompen*.", pause=0.45),
    ]),
    # La neurona, paso a paso: qué entra, qué hace, qué sale.
    Beat("neurona", [
        Ph("La salida: que la máquina *descubra* qué mirar, usando neuronas artificiales.", pause=0.25),
        Ph("¿Qué le entra a una neurona?", pause=0.15, pitch=Q),
        Ph("Un pedacito de la imagen: unos pocos puntos, cada uno con su número de *luz*.", pause=0.4),
    ]),
    Beat("pesos", [
        Ph("A cada punto le da un *peso*: cuánto le importa.", pause=0.2),
        Ph("Peso positivo: «aquí quiero *luz*». Negativo: «aquí quiero *oscuridad*».", pause=0.4),
    ]),
    Beat("suma", [
        Ph("Multiplica cada punto por su peso, y *suma* todo.", pause=0.25),
        Ph("Sale un *solo número*: qué tanto ese pedacito se parece a lo que busca.", pause=0.2),
        Ph("Alto: se *enciende*. En una zona pareja: casi cero, apagada.", pause=0.45),
    ]),
    Beat("barrido", [
        Ph("Esta neurona quiere oscuridad a la izquierda y luz a la derecha: busca un *borde*.", pause=0.2),
        Ph("Si la pasamos por toda la cara, se enciende justo en los bordes.", pause=0.4),
    ]),
    # Las capas: lo que sale de una es lo que entra a la siguiente.
    Beat("capas", [
        Ph("Una *capa* es un grupo de neuronas, cada una buscando algo distinto.", pause=0.2),
        Ph("Lo que sale ya no es una foto: son *mapas* de dónde se encendió cada una.", pause=0.3),
        Ph("Y esos mapas *entran* a la capa siguiente,", pause=0.1),
        Ph("cuyas neuronas combinan bordes y encuentran *partes*: un ojo, una nariz, una boca.", pause=0.3),
        Ph("La última junta las partes en una lista de números: una *huella* de tu rostro.", pause=0.3),
        Ph("De luz, a bordes, a partes, a huella: por eso se llama aprendizaje *profundo*.", pause=0.45),
    ]),
    Beat("aprender", [
        Ph("¿Y quién elige los pesos? *Nadie*. Se aprenden.", pause=0.25),
        Ph("Le mostramos miles de fotos. Cuando confunde a dos personas, medimos el *error*...", pause=0.1),
        Ph("y movemos cada peso un poquito para *reducirlo*.", pause=0.2),
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
