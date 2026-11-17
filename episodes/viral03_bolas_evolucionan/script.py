"""Guion — «Nadie les enseñó a sobrevivir» (metadato; no se muestra en el video)

Inspiración (estilo, pedido del usuario): reels «satisfying» de bolas que se multiplican en un
círculo con un engranaje (p. ej. «The gear turns, the balls multiply», ~959 mil me gusta).
Solo se toma el estilo: la mecánica, la historia y el diseño son propios.
Clase: algoritmos genéticos / evolutivos (copiar con mutación + selección).
Simulación real (experiment.py, NumPy, semilla 5): 5 bolas → 160; giro medio 0,10 → 0,78.
"""
from reelforge.timeline import Beat, Ph

EPISODE = {"num": 3, "slug": "viral03_bolas_evolucionan", "title": "Nadie les enseñó a sobrevivir", "tag": ""}
VOICE = "es-MX-JorgeNeural"
RATE = "+19%"
Q = "+5Hz"; SLOW = "-5%"

BEATS = [
    Beat("hook", [
        Ph("Cada vez que una bola toca el engranaje...", pause=0.3),
        Ph("*se copia*.", pause=0.55),
        Ph("Si toca el borde *rosado*... desaparece.", pause=0.6),
    ]),
    Beat("pregunta", [
        Ph("¿Cuáles van a sobrevivir?", pause=0.7, pitch=Q),
    ]),
    Beat("copias", [
        Ph("Fíjate en algo: las copias no son perfectas.", pause=0.35),
        Ph("Cada una nace con un *pequeño cambio*...", pause=0.25),
        Ph("en cuánto *gira* hacia el centro.", pause=0.55, rate=SLOW),
    ]),
    Beat("azar", [
        Ph("Las *violetas* casi no giran.", pause=0.25),
        Ph("Rebotan al azar... y muchas terminan en el rosado.", pause=0.5),
    ]),
    Beat("crece", [
        Ph("Y el borde rosado...", pause=0.35),
        Ph("empieza a *crecer*.", pause=0.7, rate=SLOW),
    ]),
    Beat("ventaja", [
        Ph("Las que giran un poco más vuelven al engranaje... y se copian *más*.", pause=0.3),
        Ph("Y sus copias heredan ese giro.", pause=0.6),
    ]),
    Beat("suspenso", [
        Ph("Generación tras generación...", pause=0.9, rate=SLOW),
    ]),
    Beat("revela", [
        Ph("casi todas son *cyan*.", pause=0.6),
        Ph("Dan vueltas alrededor del engranaje...", pause=0.3),
        Ph("y nadie las programó para eso.", pause=0.9),
    ]),
    Beat("nombre", [
        Ph("Copiar, cambiar un poquito y quedarse con lo que sobrevive...", pause=0.35),
        Ph("eso es un *algoritmo genético*.", pause=0.65, rate=SLOW),
    ]),
    Beat("real", [
        Ph("La NASA usó uno para diseñar una *antena*...", pause=0.3),
        Ph("que terminó en el espacio.", pause=0.7),
    ]),
    Beat("cierre", [
        Ph("¿Cuáles sobrevivieron?", pause=0.45, pitch=Q),
        Ph("Las que aprendieron a *volver*.", pause=0.9, rate=SLOW),
    ]),
]
