"""Guion — «¿Por qué la IA siempre dice 7?» (metadato; no se muestra en el video)

Origen del tema: tendencias de YouTube de la semana (tools/tendencias.py): «Esto pasa si le
pides un número a la IA». Base de clase: modelos de lenguaje (predecir la palabra siguiente,
probabilidades/softmax, estrategia de decodificación: elegir siempre la más probable vs. muestrear).

Cadena: hook (la IA dice 7) → también las personas → la IA no piensa el número, predice la
palabra siguiente a partir de textos humanos → reparte probabilidades (ilustrativas) → si toma
siempre la más probable: siempre 7 → por eso se usa una ruleta (muestreo) + perilla «temperatura»
→ aun así el 7 gana más seguido (simulación real de 200 giros) → no lo eligió: lo heredó de nosotros.
"""
from reelforge.timeline import Beat, Ph

EPISODE = {"num": 1, "slug": "viral01_numero7", "title": "¿Por qué la IA siempre dice 7?", "tag": ""}
VOICE = "en-US-AndrewMultilingualNeural"      # voz enérgica estilo «narrador de IA» (habla español)
RATE = "+20%"
Q = "+4Hz"; SLOW = "-6%"

BEATS = [
    Beat("hook", [
        Ph("Pídele a una IA|i_a un número del uno al diez.", pause=0.35),
        Ph("Muchas veces responde... *siete*.", pause=0.5),
        Ph("¿Coincidencia?", pause=0.6, pitch=Q),
    ]),
    Beat("humanos", [
        Ph("Pregúntale lo mismo a la gente, y pasa algo parecido:", pause=0.15),
        Ph("el siete también es el *favorito*.", pause=0.5),
    ]),
    Beat("predice", [
        Ph("Y no es casualidad. Una IA|i_a de texto no *piensa* un número.", pause=0.3),
        Ph("Adivina qué palabra viene, después de leer millones de textos escritos... por *personas*.", pause=0.5),
    ]),
    Beat("probas", [
        Ph("Para cada número calcula una *probabilidad*...", pause=0.3),
        Ph("y el siete parte con *ventaja*.", pause=0.5),
    ]),
    Beat("greedy", [
        Ph("Si siempre eligiera el más probable, diría siete... *siempre*.", pause=0.5),
    ]),
    Beat("ruleta", [
        Ph("Por eso muchos modelos giran una *ruleta*: cada número ocupa un pedazo según su probabilidad.", pause=0.3),
        Ph("Una perilla llamada *temperatura* decide cuánto se arriesga.", pause=0.4),
        Ph("Giremos doscientas veces.", pause=0.5),
    ]),
    Beat("resultado", [
        Ph("Hay sorpresas... pero el siete sigue *ganando*.", pause=0.6),
    ]),
    Beat("cierre", [
        Ph("La IA|i_a no eligió el siete.", pause=0.35),
        Ph("Lo *heredó*... de nosotros.", pause=0.7, rate=SLOW),
    ]),
]
