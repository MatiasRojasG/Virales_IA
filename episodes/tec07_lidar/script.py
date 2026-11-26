"""Guion — «¿Cómo ve de noche un auto sin conductor?» (metadato; no se muestra en el video)

Propuesta A del 26-nov-2026 (propuestas/2026-11-26), elegida automáticamente por puntaje. Fuentes:
- Waymo, soporte «A suite of sensors means safer rides, safer roads»: el lidar mide tamaño y distancia de los
  objetos en 360° alrededor del vehículo y hasta 300 m.
- Waymo, «The Waymo Driver Handbook: Perception» (oct 2021): sensores lidar alrededor del vehículo envían millones
  de pulsos láser en todas direcciones y miden cuánto tardan en rebotar; nubes de puntos hasta 300 m en todas
  las condiciones de luz.
- Waymo, «Meet the 6th-generation Waymo Driver» (ago 2024): 13 cámaras, 4 lidar y 6 radar.
- Física: c ≈ 299.792 km/s → 29,98 cm por nanosegundo. 30 m ida y vuelta = 60 m → 200 ns (cálculo propio).
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 7, "slug": "tec07_lidar", "title": "¿Cómo ve de noche un auto sin conductor?", "tag": "",
           "fecha": "26 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Dos de la mañana. Un auto avanza por la calle...", pause=0.25),
        Ph("y no hay *nadie* al volante.", pause=0.35),
        Ph("Alguien vestido de negro cruza.", pause=0.25),
        Ph("¿Cómo lo *ve*?", pause=0.5, pitch=Q),
    ]),
    Beat("oscuro", [
        Ph("Una cámara, de noche, ve casi lo mismo que tú:", pause=0.15),
        Ph("*muy poco*.", pause=0.45),
    ]),
    Beat("pulso", [
        Ph("Por eso el auto *trae su propia luz*.", pause=0.3, pitch=WOW),
        Ph("Lanza un pulso de *láser*, invisible para tus ojos...", pause=0.2),
        Ph("y mide cuánto tarda en *volver*.", pause=0.45),
    ]),
    Beat("tiempo", [
        Ph("La luz avanza unos *30|treinta* *centímetros* en una milmillonésima de segundo.", pause=0.3, rate=SLOW),
        Ph("Si el rebote vuelve en *200|doscientas* milmillonésimas...", pause=0.2, rate=SLOW),
        Ph("la persona está a *30|treinta* *metros*.", pause=0.5, rate=SLOW, pitch=WOW),
    ]),
    Beat("nube", [
        Ph("Ahora repite eso *millones* de veces, en todas direcciones.", pause=0.25),
        Ph("Cada rebote es un *punto*...", pause=0.3),
        Ph("y los puntos, juntos, dibujan la *forma* de una persona.", pause=0.35, pitch=WOW),
        Ph("Eso es el *lidar*.", pause=0.6),
    ]),
    Beat("dato", [
        Ph("Según Waymo, la empresa de robotaxis, su lidar mide *todo alrededor* del auto...", pause=0.2, rate=SLOW),
        Ph("hasta unos *300|trescientos* *metros*. De día... o de noche.", pause=0.4, rate=SLOW),
    ]),
    Beat("equipo", [
        Ph("Y no trabaja solo: lo combina con *cámaras* y *radar*.", pause=0.45),
    ]),
    Beat("cierre", [
        Ph("¿Cómo ve en la oscuridad, sin nadie al volante?", pause=0.25, pitch=Q),
        Ph("No espera la luz: la *lanza*... y mide el *eco*.", pause=0.4, pitch=WOW),
        Ph("¿Tú te subirías a uno?", pause=0.4, pitch=Q),
    ]),
]
