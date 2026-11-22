"""Guion — «¿Por qué no se rompe la pantalla?» (metadato; no se muestra en el video)

Propuesta A del 22-nov-2026 (propuestas/2026-11-22). Fuentes: Corning, «How It Works: Strengthening Glass»
(el vidrio se rompe por defectos de su superficie que crecen cuando esta queda en tensión; en un baño de sal
fundida, iones de potasio reemplazan a los de sodio; al ser más grandes dejan la superficie en compresión;
analogía de cambiar bolas de pool por pelotas de tenis en el triángulo) y Corning Gorilla Glass, «A look
behind Corning Gorilla Glass» (baño de sal fundida a ≈ 400 °C).
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 3, "slug": "tec03_vidrio_celular", "title": "¿Por qué no se rompe la pantalla?", "tag": "",
           "fecha": "22 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Un martillo... contra la *pantalla* de un celular.", pause=0.3),
        Ph("Es *vidrio*, igual que una ventana.", pause=0.25),
        Ph("Y una ventana se haría *trizas*.", pause=0.35),
        Ph("¿Por qué esta *aguanta*?", pause=0.7, pitch=Q),
    ]),
    Beat("grieta", [
        Ph("Todo vidrio tiene en su superficie *grietas diminutas*.", pause=0.3),
        Ph("Cuando un golpe lo *dobla*, una de sus caras se *estira*...", pause=0.2),
        Ph("y la grieta se *abre*... y avanza.", pause=0.45),
        Ph("El vidrio se rompe *desde la superficie*.", pause=0.5),
    ]),
    Beat("bano", [
        Ph("Entonces, hay que *proteger la superficie*.", pause=0.35),
        Ph("Muchas pantallas pasan por un baño de *sal derretida*,", pause=0.15),
        Ph("a unos *400|cuatrocientos* grados.", pause=0.4, rate=SLOW),
        Ph("átomos pequeños de *sodio* salen del vidrio...", pause=0.15),
        Ph("y entran átomos más grandes de *potasio*.", pause=0.6, pitch=WOW),
    ]),
    Beat("aprieta", [
        Ph("Imagina un triángulo de pool lleno de bolas...", pause=0.2),
        Ph("y cambias cada bola por una *pelota de tenis*.", pause=0.3),
        Ph("No caben... y quedan *apretadas*.", pause=0.45),
        Ph("Eso le pasa a la superficie del vidrio: queda *comprimida*.", pause=0.65, pitch=WOW),
    ]),
    Beat("cierre", [
        Ph("Ahora, para que una grieta se abra,", pause=0.15),
        Ph("primero tiene que vencer *ese apretón*.", pause=0.45),
        Ph("Se llama *vidrio templado químicamente*.", pause=0.5),
        Ph("¿Es irrompible?", pause=0.3, pitch=Q),
        Ph("No: una mala caída lo puede romper igual.", pause=0.45),
        Ph("Pero cuando tu celular *aguanta un golpe*...", pause=0.2),
        Ph("es porque su superficie *está apretada*.", pause=0.8, pitch=WOW),
    ]),
]
