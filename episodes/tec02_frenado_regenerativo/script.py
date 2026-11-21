"""Guion — «¿Y si frenar recargara tu auto?» (metadato; no se muestra en el video)

Propuesta C del 21-nov-2026 (propuestas/2026-11-21). Fuentes: U.S. DOE, fueleconomy.gov, «Where the Energy
Goes: Electric Cars» (en ciudad, ciclo EPA FTP-75, la energía neta devuelta por frenado regenerativo
equivale a ≈ 32 % de la energía tomada de la red; en carretera la ventaja es pequeña) y animación DOE/AFDC
de frenado regenerativo (el motor se invierte y las ruedas lo hacen girar como generador).
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 2, "slug": "tec02_frenado_regenerativo", "title": "¿Y si frenar recargara tu auto?", "tag": "",
           "fecha": "21 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Cada vez que frenas en un semáforo...", pause=0.2),
        Ph("tu auto *pierde energía*.", pause=0.35),
        Ph("Las pastillas aprietan el disco,", pause=0.15),
        Ph("y todo ese impulso se va en *calor*.", pause=0.45),
        Ph("¿Y si se pudiera *guardar*?", pause=0.75, pitch=Q),
    ]),
    Beat("motor", [
        Ph("En un auto eléctrico, la *batería* manda corriente al *motor*,", pause=0.2),
        Ph("y el motor hace girar las ruedas.", pause=0.45),
    ]),
    Beat("reves", [
        Ph("Pero cuando sueltas el acelerador...", pause=0.45),
        Ph("ahora son las *ruedas* las que hacen girar al motor.", pause=0.35),
        Ph("Y un motor que alguien más hace girar...", pause=0.3),
        Ph("se convierte en *generador*.", pause=0.75, pitch=WOW),
    ]),
    Beat("vuelve", [
        Ph("Esa corriente vuelve a la *batería*,", pause=0.2),
        Ph("y el esfuerzo de generarla *frena el auto*.", pause=0.45),
        Ph("Se llama *frenado regenerativo*.", pause=0.65, pitch=WOW),
    ]),
    Beat("dato", [
        Ph("Funciona mejor en la *ciudad*, donde frenas todo el rato.", pause=0.35),
        Ph("Según el Departamento de Energía de Estados Unidos,", pause=0.15, rate=SLOW),
        Ph("ahí lo recuperado equivale a cerca de un *32%|treinta_y_dos_por_ciento*", pause=0.15, rate=SLOW),
        Ph("de la energía que el auto saca del enchufe.", pause=0.5, rate=SLOW),
        Ph("En carretera casi no frenas... y recupera *mucho menos*.", pause=0.5),
    ]),
    Beat("cierre", [
        Ph("Los frenos de siempre siguen ahí para frenar fuerte,", pause=0.2),
        Ph("pero se gastan menos.", pause=0.45),
        Ph("Entonces, ¿la energía de ese semáforo?", pause=0.35, pitch=Q),
        Ph("Una parte... *vuelve a la batería*.", pause=1.0, pitch=WOW),
    ]),
]
