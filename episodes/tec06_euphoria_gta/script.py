"""Guion — «¿Cómo sabe caer un personaje de GTA?» (metadato; no se muestra en el video)

Encargo del usuario del 24-nov-2026 (propuestas/encargos/euphoria_gta6.md). Fuentes:
- Euphoria (NaturalMotion): simulación completa del personaje 3D (cuerpo, músculos y sistema nervioso motor);
  en vez de animaciones predefinidas, las acciones y reacciones se sintetizan en tiempo real y son distintas cada
  vez (Wikipedia, «Euphoria (software)»). GTA IV (2008) fue el primer juego de Rockstar con Euphoria; luego
  Red Dead Redemption y Max Payne 3; está integrado en el motor RAGE.
- Origen: Torsten Reil simulaba sistemas nerviosos humanos en su doctorado en Zoología en Oxford para entender
  cómo controlan el movimiento; fundó NaturalMotion en 2001 (Departamento de Biología, Universidad de Oxford;
  Oxford University Innovation).
- GTA VI (salió el 19-nov-2026): según Rockstar (Aaron Garbut a The New York Times, 27-ago-2026), sus personajes
  no jugables tienen más de 600.000 animaciones, frente a 55.000 en GTA V y 300.000 en RDR2 (GamesRadar, TechRadar).
- Rockstar no ha detallado cuánto cambió Euphoria en GTA VI: no se afirma nada al respecto.
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 6, "slug": "tec06_euphoria_gta", "title": "¿Cómo sabe caer un personaje de GTA?", "tag": "",
           "fecha": "25 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Empujas a un personaje de videojuego...", pause=0.2),
        Ph("y en vez de caer como un muñeco, *estira los brazos* y da un paso.", pause=0.3),
        Ph("¿Cómo *sabe* qué hacer?", pause=0.45, pitch=Q),
    ]),
    Beat("grabado", [
        Ph("Antes, las caídas se *grababan* una vez...", pause=0.2),
        Ph("y se repetían *siempre iguales*.", pause=0.35),
    ]),
    Beat("trapo", [
        Ph("La otra opción: soltar el cuerpo y dejar que caiga solo.", pause=0.2),
        Ph("Pero cae como un *muñeco de trapo*.", pause=0.45, pitch=WOW),
    ]),
    Beat("oxford", [
        Ph("En Oxford, el investigador *Torsten|Tórsten Reil|Rail* estudiaba cómo el *sistema nervioso* controla el movimiento.", pause=0.4),
    ]),
    Beat("idea", [
        Ph("Su idea: un cuerpo virtual con *músculos*...", pause=0.2),
        Ph("y un pequeño *cerebro* que los mueve.", pause=0.3),
        Ph("Si lo empujan, *calcula* en el momento dónde poner el pie para no caerse.", pause=0.5, pitch=WOW),
    ]),
    Beat("nombre", [
        Ph("Esa técnica se llama *Euphoria*,", pause=0.2),
        Ph("y Rockstar la usa desde *GTA|ge_te_a IV|cuatro*, en *2008|dos_mil_ocho*.", pause=0.3, rate=SLOW),
        Ph("Por eso no hay *dos caídas iguales*.", pause=0.45),
    ]),
    Beat("gta6", [
        Ph("Según Rockstar, los peatones de GTA|ge_te_a VI|seis tienen además más de *600.000|seiscientas_mil* animaciones,", pause=0.2, rate=SLOW),
        Ph("*diez veces* más que en GTA|ge_te_a V|cinco.", pause=0.4, rate=SLOW),
    ]),
    Beat("cierre", [
        Ph("Pero ante un empujón, el personaje no *recuerda* una caída:", pause=0.25),
        Ph("la *calcula*... como un cuerpo que no quiere caerse.", pause=0.6, pitch=WOW),
    ]),
]
