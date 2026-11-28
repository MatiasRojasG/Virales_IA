"""Guion — «¿Cómo supo tu auto que ibas a chocar?» (frenado automático de emergencia; metadato, no se muestra)

Fuentes:
- IIHS, J. Cicchino, «Front crash prevention slashes police-reported rear-end crashes» (ene-2016, actualizado):
  https://www.iihs.org/news/detail/front-crash-prevention-slashes-police-reported-rear-end-crashes
  «automatic emergency braking reduced rear-end crashes by 50 percent and reduced rear-end crashes that caused
  injuries by 56 percent». Confirmado en IIHS, «Autobrake is good, but it could be better» (feb-2019):
  https://www.iihs.org/news/detail/autobrake-is-good-but-it-could-be-better
- NHTSA, «Driver Assistance Technologies»: https://www.nhtsa.gov/vehicle-safety/driver-assistance-technologies
  CIB: si el conductor no frena, el sistema frena; DBS: «If the system detects a crash and the driver brakes, but not
  hard enough to avoid the crash, DBS automatically supplements the driver's braking».
- Transport Canada, «Automatic emergency braking» (mod. 19-feb-2026):
  https://tc.canada.ca/en/road-transportation/driver-assistance-technologies/collision-intervention/automatic-emergency-braking
  usa sensores para detectar obstáculos; si no reaccionas a la alerta, puede frenar; puede no evitar el choque;
  puede no funcionar con lluvia intensa, nieve, niebla, sol fuerte, de noche o en curvas; no reemplaza tu atención.
- Cálculo propio (física simple): 30 m ÷ (50 km/h = 13,9 m/s) ≈ 2,2 s para el choque.
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 9, "slug": "tec09_frenado_automatico", "title": "¿Cómo supo tu auto que ibas a chocar?",
           "tag": "", "fecha": "28 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("El auto de adelante frena de golpe...", pause=0.12),
        Ph("y tú vas mirando el *celular*.", pause=0.25),
        Ph("Tu auto frena *solo*.", pause=0.2, pitch=WOW),
        Ph("¿Cómo supo que ibas a *chocar*?", pause=0.45, pitch=Q),
    ]),
    Beat("saber", [
        Ph("Necesita saber dos cosas:", pause=0.15),
        Ph("a qué *distancia* está el otro auto,", pause=0.12),
        Ph("y qué tan rápido se *acercan*.", pause=0.35),
    ]),
    Beat("eco", [
        Ph("Un *sensor* adelante, muchas veces un radar,", pause=0.1),
        Ph("lanza una señal que rebota... y vuelve.", pause=0.15),
        Ph("Por lo que tarda, sabe la *distancia*.", pause=0.3),
    ]),
    Beat("rapidez", [
        Ph("Mide otra vez: si se *achica*, se están acercando.", pause=0.4),
    ]),
    Beat("cuenta", [
        Ph("Y la cuenta clave:", pause=0.2),
        Ph("distancia, dividida por esa rapidez...", pause=0.15, rate=SLOW),
        Ph("da los *segundos* para el choque.", pause=0.55, pitch=WOW),
    ]),
    Beat("ejemplo", [
        Ph("Imagina treinta metros, a cincuenta kilómetros por hora:", pause=0.25, rate=SLOW),
        Ph("poco más de *dos segundos*.", pause=0.55, pitch=WOW),
    ]),
    Beat("actua", [
        Ph("Primero te *avisa*.", pause=0.2),
        Ph("Si no reaccionas... *frena él*.", pause=0.25),
        Ph("Y si frenas suave, pone la *fuerza* que falta.", pause=0.4),
    ]),
    Beat("resultado", [
        Ph("¿Sirve?", pause=0.25, pitch=Q),
        Ph("El instituto IIHS, en Estados Unidos, vio", pause=0.08),
        Ph("que reduce a la *mitad* los choques por alcance.", pause=0.55, rate=SLOW),
    ]),
    Beat("limite", [
        Ph("Con lluvia fuerte, niebla o en curvas, puede *fallar*:", pause=0.2),
        Ph("el que maneja sigues siendo *tú*.", pause=0.4),
    ]),
    Beat("cierre", [
        Ph("¿Cómo supo?", pause=0.15, pitch=Q),
        Ph("Midió, calculó los segundos...", pause=0.12),
        Ph("y frenó *antes que tú*.", pause=0.6),
    ]),
]
