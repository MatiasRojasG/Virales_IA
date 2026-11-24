"""Guion — «¿Por qué tu batería dura menos cada año?» (metadato; no se muestra en el video)

Propuesta A del 24-nov-2026 (propuestas/2026-11-24). Fuentes:
- Apple, «Battery Service and Recycling» y soporte «iPhone battery and performance»: los iPhone 15 y posteriores
  están diseñados para conservar el 80 % de su capacidad original a los 1.000 ciclos de carga completos en
  condiciones ideales (500 ciclos en modelos anteriores).
- Apple soporte 105105 «Charge and maintain your iPhone battery»: zona ideal 16–22 °C; sobre 35 °C el calor puede
  dañar la capacidad de forma permanente; la carga optimizada reduce el tiempo que el iPhone pasa al 100 %.
- Apple soporte 108055 «About Charge Limit and Optimized Battery Charging»: opción «Límite del 80 %».
- Mikheenkova et al., J. Electrochem. Soc. (2023) y NREL (fy22osti/79499): la pérdida de litio disponible por el
  crecimiento de la capa SEI es el principal modo de envejecimiento; el calor y un estado de carga alto la aceleran.
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 5, "slug": "tec05_bateria", "title": "¿Por qué tu batería dura menos cada año?", "tag": "",
           "fecha": "24 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Recién comprado, tu celular llegaba a la noche *con batería de sobra*.", pause=0.3),
        Ph("Dos años después... no llega *ni a la tarde*.", pause=0.4),
        Ph("¿Qué le pasó?", pause=0.45, pitch=Q),
    ]),
    Beat("viaje", [
        Ph("Adentro de la batería hay *litio*.", pause=0.25),
        Ph("Cuando cargas, el litio viaja *a un lado*.", pause=0.2),
        Ph("Cuando usas el celular, *vuelve*.", pause=0.25),
        Ph("Ese ir y venir es tu *energía*.", pause=0.45),
    ]),
    Beat("trampa", [
        Ph("Pero en cada viaje...", pause=0.3),
        Ph("un poquito de litio se queda *atrapado*, en una capa delgada.", pause=0.3, pitch=WOW),
        Ph("Y ese litio ya *no vuelve* a trabajar.", pause=0.45),
    ]),
    Beat("encoge", [
        Ph("Menos litio que viaja es *menos carga*.", pause=0.3),
        Ph("Por eso tu batería no muere de golpe:", pause=0.2),
        Ph("se *encoge*, de a poco.", pause=0.5, pitch=WOW),
    ]),
    Beat("calor", [
        Ph("¿Y qué la gasta más rápido?", pause=0.3, pitch=Q),
        Ph("El *calor*...", pause=0.25),
        Ph("y pasar muchas horas *al cien por ciento*.", pause=0.25),
        Ph("Ahí esa capa crece *más rápido*.", pause=0.45),
    ]),
    Beat("dato", [
        Ph("Los iPhone más nuevos están hechos para conservar el *80%|ochenta_por_ciento* de su capacidad...", pause=0.2, rate=SLOW),
        Ph("después de *1.000|mil* cargas completas, en condiciones ideales.", pause=0.45, rate=SLOW),
    ]),
    Beat("limite", [
        Ph("Por eso muchos celulares traen una opción para cargar solo *hasta el 80%|ochenta_por_ciento*: menos horas al cien.", pause=0.45, rate=SLOW),
    ]),
    Beat("cierre", [
        Ph("Tu batería no se echó a perder:", pause=0.25),
        Ph("fue perdiendo *litio* en el camino, un poquito *cada día*.", pause=0.35, pitch=WOW),
        Ph("¿Y tú... la dejas cargando *toda la noche*?", pause=0.6, pitch=Q),
    ]),
]
