"""Guion — «El robot que se cayó una y otra vez» (metadato; no se muestra en el video)

Inspiración (tendencias, 30 días): «NVIDIA's Cute AI Ducks Can Do Somersaults» (7,4 M) y
«When Jensen asks for a somersault, the AI duck delivers» (5,3 M).
Clase: aprender de los errores — función de pérdida y descenso de gradiente (fundamentos de DL).
Simulación real (experiment.py): primer aterrizaje en la plataforma en el intento 21.
"""
from reelforge.timeline import Beat, Ph

EPISODE = {"num": 2, "slug": "viral02_robot_aprende", "title": "El robot que se cayó una y otra vez", "tag": ""}
VOICE = "es-MX-JorgeNeural"
RATE = "+20%"
Q = "+5Hz"; SLOW = "-6%"

BEATS = [
    Beat("hook", [
        Ph("Este robot quiere subir a esa plataforma...", pause=0.5),
        Ph("y se *cae*.", pause=0.6),
        Ph("Otra vez.", pause=0.55),
        Ph("Y otra vez.", pause=0.6),
    ]),
    Beat("pregunta", [
        Ph("Nadie le enseñó a saltar.", pause=0.3),
        Ph("¿Entonces cómo *aprende*?", pause=0.6, pitch=Q),
    ]),
    Beat("pista", [
        Ph("Cada caída deja una *pista*: cuánto le faltó... y hacia dónde.", pause=0.5),
    ]),
    Beat("perillas", [
        Ph("Con esa pista mueve dos perillas, *fuerza* y *ángulo*...", pause=0.2),
        Ph("solo un *poquito*.", pause=0.5, rate=SLOW),
    ]),
    Beat("repetir", [
        Ph("Salta. Mide el error. Ajusta.", pause=0.3),
        Ph("Una y otra vez...", pause=0.3),
        Ph("y el error *baja*.", pause=0.6),
    ]),
    Beat("logra", [
        Ph("Hasta que, en el intento veintiuno...", pause=0.8, rate=SLOW),
        Ph("*lo logra*.", pause=1.0),
    ]),
    Beat("redes", [
        Ph("Así aprenden también las *redes neuronales*:", pause=0.25),
        Ph("medir el error, ajustar un poquito... y repetir.", pause=0.45),
        Ph("Solo que en vez de dos perillas... tienen *millones*.", pause=0.6),
    ]),
    Beat("cierre", [
        Ph("Los robots que ves haciendo piruetas se cayeron muchísimas veces antes...", pause=0.2),
        Ph("solo que en una *simulación*.", pause=0.6, rate=SLOW),
    ]),
]
