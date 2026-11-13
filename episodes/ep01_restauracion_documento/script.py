"""Guion narrado del Episodio 1 (v2) — «¿Puedes leer esto?» · Detrás del Algoritmo.

Arco: problema cotidiano → curiosidad → intuición → descubrimiento → explicación → resultado.
El porqué va antes del cómo; los términos técnicos ("red de Markov", α, β) aparecen solo
cuando el espectador ya entiende la idea que nombran.

Sintaxis: *clave* = resaltado cyan · mostrar|pronunciar (guiones bajos = espacios).
Cada Ph es una frase con su propia prosodia (rate, pitch) y la pausa que la sigue.
"""
from reelforge.timeline import Beat, Ph

EPISODE = {
    "num": 1,
    "slug": "ep01_restauracion_documento",
    "title": "¿Puedes leer esto?",
    "tag": "DETRÁS DEL ALGORITMO · EP 01",
    "next": "Próximo: redes sin flechas",
}

Q = "+5Hz"        # leve subida de tono para preguntas y sorpresa
SLOW = "-4%"      # frases de énfasis

BEATS = [
    # 1 · HOOK: problema + resultado prometido (open loop)
    Beat("hook", [
        Ph("¿Puedes leer *esto*?", pause=0.45, pitch=Q),
        Ph("Una máquina, tampoco.", pause=0.45),
        Ph("Pero una idea sorprendentemente *simple*...", pause=0.12),
        Ph("lo deja *así*.", pause=0.75, rate=SLOW),
    ]),
    # 2 · PROBLEMA cotidiano
    Beat("problema", [
        Ph("Al escanearlo, el *15%|quince_por_ciento* de los puntos salió *al revés*:", pause=0.15),
        Ph("tinta que se volvió papel...", pause=0.08),
        Ph("y papel que se volvió tinta.", pause=0.5),
    ]),
    # 3 · CURIOSIDAD
    Beat("curiosidad", [
        Ph("Mira *un solo punto*.", pause=0.3, rate=SLOW),
        Ph("¿Está bien, o está mal?", pause=0.35, pitch=Q),
        Ph("Solo, es *imposible* saberlo.", pause=0.45),
    ]),
    # 4 · INTUICIÓN (con analogía)
    Beat("intuicion", [
        Ph("Pero tú lo sabrías al instante, porque miras *alrededor*.", pause=0.3),
        Ph("Un punto negro solito en medio del papel es casi seguro una *mancha*:", pause=0.1),
        Ph("la tinta viene en *trazos*.", pause=0.35),
        Ph("Como adivinar una palabra que no escuchaste bien... por las de *al lado*.", pause=0.45),
    ]),
    # 5 · DESCUBRIMIENTO: recién aquí aparece el nombre técnico
    Beat("descubrimiento", [
        Ph("Esa es la idea: cada punto le pregunta a sus *vecinos*.", pause=0.25),
        Ph("Así se forma una red *sin flechas*, porque nadie manda sobre nadie:", pause=0.12),
        Ph("una *red de Markov*.", pause=0.45, rate=SLOW),
    ]),
    # 6 · EXPLICACIÓN: la balanza
    Beat("balanza", [
        Ph("Pongámoslo en una *balanza*.", pause=0.25),
        Ph("El escáner dice: *negro*.", pause=0.25),
        Ph("Pero cuatro vecinos dicen: *blanco*.", pause=0.3),
        Ph("Ellos pesan más...", pause=0.1),
        Ph("y el punto *se corrige*.", pause=0.4),
        Ph("Cuánto pesa cada voz lo regulan dos perillas: *alfa* y *beta*.", pause=0.45),
    ]),
    # 7 · TODO EL DOCUMENTO
    Beat("iterar", [
        Ph("Hacemos lo mismo con todos los puntos, y *repetimos*.", pause=0.25),
        Ph("Pasada tras pasada, las manchas se *desvanecen*.", pause=0.55),
    ]),
    # 8 · RESULTADO (cierre del open loop)
    Beat("resultado", [
        Ph("¿El resultado?", pause=0.35, pitch=Q),
        Ph("En la clase, el lector automático pasó de entender el *42%|cuarenta_y_dos_por_ciento* del texto...", pause=0.1),
        Ph("al *94*.", pause=0.5, rate=SLOW),
        Ph("En mi recreación en Python: de nada, a un *91%|noventa_y_uno_por_ciento*.", pause=0.45),
    ]),
    # 9 · CIERRE + puente al próximo episodio
    Beat("cierre", [
        Ph("La misma idea delimita *tumores* en resonancias, o mapea *bosques* desde satélites.", pause=0.35),
        Ph("¿Y por qué aquí no sirven las *flechas*?", pause=0.2, pitch=Q),
        Ph("En el próximo episodio.", pause=0.2),
    ]),
]
