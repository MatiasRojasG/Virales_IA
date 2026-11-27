"""Guion — «¿Cómo sabe tu celular dónde está el suelo?» (metadato; no se muestra en el video)

Fuentes:
- Android Developers, «Motion sensors»
  (https://developer.android.com/develop/sensors-and-location/sensors/sensors_motion):
  el acelerómetro mide la aceleración «including the force of gravity»; sobre la mesa marca 9,81 m/s²;
  «when the device is in free fall … its accelerometer reads a magnitude of g = 0 m/s²»; el sensor de
  gravedad se usa para saber la orientación del equipo; contador y detector de pasos.
- Analog Devices (familia ADXL35x): «a spring mass system … The mass moves in response to an external
  acceleration»; la capacitancia entre dedos fijos y dedos unidos a la masa cambia al moverse.
- Revisión en Sensors (PMC7411979): todo smartphone actual trae un acelerómetro MEMS de tres ejes.
- Tamaño: los acelerómetros de celular vienen en encapsulados de unos 2 × 2 mm (p. ej. Bosch BMA400).
Simplificaciones: se dibuja una sola pesa por eje; los dedos y resortes reales son de silicio y miden micras.
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 8, "slug": "tec08_acelerometro", "title": "¿Cómo sabe tu celular dónde está el suelo?",
           "tag": "", "fecha": "27 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Giras tu celular... y la pantalla gira contigo.", pause=0.3),
        Ph("Pero no tiene ojos.", pause=0.2),
        Ph("¿Cómo sabe dónde está el *suelo*?", pause=0.55, pitch=Q),
    ]),
    Beat("adentro", [
        Ph("Adentro hay un chip de un par de *milímetros*,", pause=0.15, rate=SLOW),
        Ph("y en él, una pieza que se *mueve*.", pause=0.5, pitch=WOW),
    ]),
    Beat("resortes", [
        Ph("Es una pesita diminuta, colgada de *resortes*.", pause=0.3),
        Ph("La gravedad la tira hacia abajo...", pause=0.2),
        Ph("y los resortes se *estiran* un poquito.", pause=0.4),
    ]),
    Beat("dedos", [
        Ph("Pegados a la pesa hay *dedos* de silicio, frente a otros fijos.", pause=0.25),
        Ph("Si la pesa baja, unos se *acercan* y otros se alejan,", pause=0.15),
        Ph("y la *carga eléctrica* entre ellos cambia.", pause=0.25),
        Ph("Así el chip *mide* cuánto se movió.", pause=0.45),
    ]),
    Beat("ejes", [
        Ph("Hay pesitas para *tres* direcciones.", pause=0.25),
        Ph("Si inclinas el celular, la gravedad tira hacia otro lado...", pause=0.2),
        Ph("se mueve otra pesa,", pause=0.15),
        Ph("y la pantalla *gira*.", pause=0.6, pitch=WOW),
    ]),
    Beat("pasos", [
        Ph("Al caminar, la pesa rebota en cada paso,", pause=0.15),
        Ph("y así puede contar tus *pasos*.", pause=0.45),
    ]),
    Beat("caida", [
        Ph("¿Y si se te cae?", pause=0.3, pitch=Q),
        Ph("Mientras cae, la pesa *flota*...", pause=0.3),
        Ph("y el sensor marca *cero*.", pause=0.6, pitch=WOW, rate=SLOW),
    ]),
    Beat("cierre", [
        Ph("Entonces, ¿cómo sabe dónde está el suelo?", pause=0.2, pitch=Q),
        Ph("Siente hacia dónde *cae* una pesita...", pause=0.2),
        Ph("que cuelga de *resortes*.", pause=0.5),
    ]),
]
