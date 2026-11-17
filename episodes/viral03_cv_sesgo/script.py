"""Guion — «La IA que descartaba currículums de mujeres» (metadato; no se muestra en el video)

Inspiración (vidIQ, 15-nov-2026): TikTok «Llevaba dos meses buscando empleo… nadie la llamaba» (511 K vistas).
Concepto: los modelos aprenden patrones de sus datos de entrenamiento, incluidos los sesgos.
Fuente: Jeffrey Dastin, «Amazon scraps secret AI recruiting tool that showed bias against women», Reuters, 10-oct-2018.
Estructura en loop: abre con la pregunta final y cierra con «Entonces…».
"""
from reelforge.timeline import Beat, Ph

EPISODE = {"num": 3, "slug": "viral03_cv_sesgo", "title": "La IA que descartaba currículums de mujeres", "tag": ""}
VOICE = "es-MX-DaliaNeural"
RATE = "+13%"
PITCH = "-6Hz"
Q = "-2Hz"; SLOW = "+4%"

BEATS = [
    Beat("hook", [
        Ph("¿Quién leyó tu *currículum*?", pause=0.3, pitch=Q),
        Ph("¿Una persona…", pause=0.2, pitch=Q),
        Ph("o una *máquina* que aprendió a descartarte?", pause=0.5, pitch=Q),
    ]),
    Beat("contexto", [
        Ph("En 2014|dos_mil_catorce, Amazon creó una IA para revisar currículums.", pause=0.25),
        Ph("A cada postulante le ponía de una a cinco *estrellas*… como a un producto.", pause=0.45),
    ]),
    Beat("datos", [
        Ph("Para aprender, le mostraron los currículums de *diez años*.", pause=0.3, rate=SLOW),
        Ph("Pero la mayoría… eran de *hombres*.", pause=0.55, rate=SLOW),
    ]),
    Beat("revela", [
        Ph("Y la IA sacó su propia conclusión.", pause=0.35),
        Ph("Si aparecía la palabra *femenino*, como en «capitana del club de ajedrez femenino»…", pause=0.2),
        Ph("le bajaba la nota.", pause=0.6, rate=SLOW),
    ]),
    Beat("porque", [
        Ph("Nadie le pidió discriminar.", pause=0.25),
        Ph("Solo copió el *patrón* de su pasado.", pause=0.5),
    ]),
    Beat("final", [
        Ph("Amazon intentó corregirla, y en 2017|dos_mil_diecisiete la abandonó.", pause=0.3),
        Ph("Sus reclutadores nunca decidieron solo con ella.", pause=0.45),
    ]),
    Beat("ensena", [
        Ph("Una IA aprende de lo que le das.", pause=0.25),
        Ph("Si el pasado fue *injusto*… lo repite. Y más rápido.", pause=0.55),
    ]),
    Beat("cierre", [
        Ph("Entonces…", pause=0.15),
    ]),
]

# voz profunda: pitch base en todas las frases que no definan uno propio
for _b in BEATS:
    for _ph in _b.text:
        _ph.pitch = _ph.pitch or PITCH
