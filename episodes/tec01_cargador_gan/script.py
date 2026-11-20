"""Guion — «¿Por qué tu cargador es tan chico?» (metadato; no se muestra en el video)

Propuesta A del 20-nov-2026 (propuestas/2026-11-20). Fuentes: Infineon (E. Persson, How2Power 2022:
los flyback de silicio rara vez pasan de ~65 kHz; el GaN tiene mucha menos carga de salida y permite
frecuencias más altas) y Texas Instruments («GaN: pushing the limits…»: > 500 kHz, componentes
magnéticos hasta 60 % más pequeños). USB Power Delivery: 5 a 20 V.
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 1, "slug": "tec01_cargador_gan", "title": "¿Por qué tu cargador es tan chico?", "tag": "",
           "fecha": "20 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Estos dos cargadores entregan *lo mismo*:", pause=0.2),
        Ph("*30|treinta* watts.", pause=0.45, rate=SLOW),
        Ph("Pero uno es *mucho más chico*.", pause=0.3),
        Ph("¿Cómo lo hace?", pause=0.7, pitch=Q),
    ]),
    Beat("enchufe", [
        Ph("El enchufe de tu casa entrega *220|doscientos_veinte* volts.", pause=0.35, rate=SLOW),
        Ph("Tu celular necesita entre *5|cinco* y *20|veinte*.", pause=0.25, rate=SLOW),
        Ph("El cargador tiene que *bajarlos*.", pause=0.5),
    ]),
    Beat("chip", [
        Ph("Para eso, un chip *prende y apaga* la corriente...", pause=0.2),
        Ph("miles de veces por segundo.", pause=0.35),
        Ph("En muchos cargadores, unas *65.000|sesenta_y_cinco_mil* veces.", pause=0.6, rate=SLOW),
    ]),
    Beat("truco", [
        Ph("Y aquí está el truco...", pause=0.45),
        Ph("mientras *más rápido* prende y apaga,", pause=0.2),
        Ph("más chica puede ser la pieza más grande de adentro:", pause=0.25),
        Ph("el *transformador*.", pause=0.6, pitch=WOW),
    ]),
    Beat("gan", [
        Ph("Pero el *silicio*, si va muy rápido, se calienta.", pause=0.45),
        Ph("El *nitruro de galio* pierde mucho menos energía en cada cambio...", pause=0.3, pitch=WOW),
        Ph("y puede pasar las *500.000|quinientas_mil* veces por segundo.", pause=0.6, rate=SLOW),
    ]),
    Beat("cierre", [
        Ph("Según Texas Instruments, eso achica esas piezas hasta un *60%|sesenta_por_ciento*.", pause=0.45, rate=SLOW),
        Ph("Por eso tu cargador nuevo...", pause=0.25),
        Ph("*cabe en la mano*.", pause=0.9, pitch=WOW),
    ]),
]
