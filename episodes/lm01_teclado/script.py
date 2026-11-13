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
        Ph("Escribes: «me tomé un»...", pause=0.5),
        Ph("y tu teclado ya sugiere: *café*, *té*, *mate*.", pause=0.6),
        Ph("¿Cómo sabe?", pause=0.7, pitch=Q),
    ]),
    Beat("simbolos", [
        Ph("Para un computador, una palabra es solo un símbolo: un *interruptor* encendido en una fila de miles.", pause=0.35),
        Ph("Café y té son tan distintos...", pause=0.15, rate=SLOW),
        Ph("como café y *perro*.", pause=0.6, rate=SLOW),
    ]),
    Beat("intuicion", [
        Ph("Pero café y té aparecen *rodeados* de las mismas palabras: *tomé*, *pedí*, *caliente*.", pause=0.4),
        Ph("Dime con quién andas...", pause=0.2, rate=SLOW),
        Ph("y te diré quién eres.", pause=0.7, rate=SLOW),
    ]),
    Beat("juego", [
        Ph("Así que le damos a la máquina miles de frases, y un *juego*: adivinar la palabra siguiente.", pause=0.35),
        Ph("Cada palabra recibe un *lugar* en un mapa, al azar... y con cada error, se mueve un poco.", pause=0.5),
    ]),
    Beat("revelacion", [
        Ph("Después de miles de intentos...", pause=0.8, rate=SLOW),
        Ph("las palabras se *ordenan* solas.", pause=0.5),
        Ph("Bebidas. Animales. Comidas. Lugares.", pause=0.7),
    ]),
    Beat("nombre", [
        Ph("Ese lugar se llama *embedding*.", pause=0.4),
    ]),
    Beat("vector", [
        Ph("Y es un *vector*: una lista de números que dice dónde está algo.", pause=0.3),
        Ph("Como tu casa en un mapa: tres al este... dos al norte.", pause=0.45),
        Ph("Café tiene *dieciséis* números, y nadie los eligió: los ajustó el juego.", pause=0.5),
    ]),
    Beat("leer", [
        Ph("¿Cómo se leen? *Comparando* hacia dónde apuntan.", pause=0.3, pitch=Q),
        Ph("Café y té, casi en la misma *dirección*...", pause=0.2),
        Ph("café y perro, no.", pause=0.6),
    ]),
    Beat("prediccion", [
        Ph("Tu teclado junta los vectores de «me tomé un»...", pause=0.25),
        Ph("y sugiere las palabras que apuntan hacia el mismo *lado*.", pause=0.6),
    ]),
    Beat("cierre", [
        Ph("No sabe qué es el café.", pause=0.35),
        Ph("Sabe con qué palabras *anda*.", pause=0.6, rate=SLOW),
    ]),
]
