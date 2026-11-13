"""Guion — «¿Cómo adivina tu teclado la palabra que viene?» (metadato; no se muestra en el video)

Arco emocional: curiosidad (el teclado adivina) → expectativa (¿cómo?) → conflicto (para el
computador las palabras son símbolos sin relación) → intuición (tú lo sabes por las palabras que
las rodean) → suspenso (el juego de adivinar, el mapa al azar que se mueve) → revelación (las
palabras se ordenan solas) → comprensión (embedding = lugar aprendido) → satisfacción (vuelve
al teclado: no sabe qué es el café, sabe con qué palabras anda).

Experimento real (experiment.py): corpus de juguete de 6.000 frases, modelo de lenguaje neuronal
que adivina la palabra siguiente a partir de las 3 anteriores, embeddings de 16 números.
"""
from reelforge.timeline import Beat, Ph

EPISODE = {
    "num": 1,
    "slug": "lm01_teclado",
    "title": "¿Cómo adivina tu teclado la palabra que viene?",
    "tag": "",
}

Q = "+5Hz"
SLOW = "-6%"

BEATS = [
    Beat("hook", [
        Ph("Escribes: «me tomé un»...", pause=0.6),
        Ph("y antes de que termines, tu teclado ya sugiere: *café*, *té*, *mate*.", pause=0.7),
        Ph("¿Cómo sabe qué palabra viene?", pause=0.9, pitch=Q),
    ]),
    Beat("simbolos", [
        Ph("Para un computador, una palabra no significa nada.", pause=0.35),
        Ph("Es solo un *símbolo*: un interruptor encendido, en una fila de miles.", pause=0.45),
        Ph("Así, *café* y *té* son tan distintos entre sí...", pause=0.2, rate=SLOW),
        Ph("como *café* y *perro*.", pause=0.7, rate=SLOW),
    ]),
    Beat("conflicto", [
        Ph("Y si no sabe qué palabras se parecen...", pause=0.2),
        Ph("no tiene cómo *adivinar*.", pause=0.7),
    ]),
    Beat("intuicion", [
        Ph("Pero piensa cómo lo sabes tú.", pause=0.45),
        Ph("Café y té aparecen rodeados de las mismas palabras:", pause=0.25),
        Ph("*tomé*, *pedí*, *caliente*.", pause=0.6, rate=SLOW),
        Ph("Dime con quién andas...", pause=0.25, rate=SLOW),
        Ph("y te diré quién eres.", pause=0.9, rate=SLOW),
    ]),
    Beat("juego", [
        Ph("Esa es la idea.", pause=0.4),
        Ph("Le damos a la máquina miles de frases, y le proponemos un *juego*:", pause=0.25),
        Ph("mirar las palabras anteriores... y adivinar la siguiente.", pause=0.6),
        Ph("Cada palabra recibe un *lugar* en un mapa. Al principio, al azar.", pause=0.5),
        Ph("Y cada vez que se equivoca, mueve un poco esos lugares, para acertar mejor la próxima vez.", pause=0.5),
    ]),
    Beat("revelacion", [
        Ph("Después de miles de intentos...", pause=0.9, rate=SLOW),
        Ph("las palabras se *ordenan* solas.", pause=0.7),
        Ph("Las bebidas, juntas. Los animales, juntos. Las comidas. Los lugares.", pause=0.8),
        Ph("Nadie le dijo qué era un animal.", pause=0.3),
        Ph("Lo descubrió por las palabras que lo rodean.", pause=1.0),
    ]),
    Beat("nombre", [
        Ph("Ese lugar aprendido se llama *embedding*.", pause=0.6),
    ]),
    Beat("cierre", [
        Ph("Entonces, cuando escribes «me tomé un»...", pause=0.5),
        Ph("el modelo busca qué palabras suelen ir ahí, y todas viven en el mismo barrio.", pause=0.6),
        Ph("Tu teclado no sabe qué es el café.", pause=0.4),
        Ph("Sabe con qué palabras *anda*.", pause=0.6, rate=SLOW),
    ]),
]
