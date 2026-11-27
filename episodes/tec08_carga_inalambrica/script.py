"""Guion — «¿Cómo pasa la energía por el aire?» (carga inalámbrica; metadato, no se muestra en el video)

Fuentes:
- Wireless Power Consortium, «How Qi works»
  https://www.wirelesspowerconsortium.com/knowledge-base/magnetic-induction/how-qi-works/
  «An alternating current in the transmitter coil generates a magnetic field which induces a voltage in the
  receiver coil.» «the phone must be able to shut down the transmitter when the battery is full. The phone,
  therefore, needs to send control signals to the charging station.»
- Belkin, «What is Qi2 wireless charging» https://www.belkin.com/us/clp-what-is-qi2-wireless-charging-blog.html
  Magnetic Power Profile (basado en MagSafe): imanes que alinean el teléfono; en Qi estándar la eficiencia
  «varies based on alignment».
- IEC 63563-7:2025 (Qi v2.0, parte 7: Foreign Object Detection): métodos para que la transferencia ocurra
  «without heating metal objects in the magnetic field of a Power Transmitter» (monedas, llaves).
- Física básica (ley de Faraday): un campo magnético que cambia dentro de una bobina induce corriente.
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 8, "slug": "tec08_carga_inalambrica", "title": "¿Cómo pasa la energía por el aire?",
           "tag": "", "fecha": "27 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Dejas el celular *encima*... y se carga.", pause=0.25),
        Ph("Sin cable. ¿Cómo pasa la energía por el *aire*?", pause=0.45, pitch=Q),
    ]),
    Beat("dentro", [
        Ph("Adentro hay dos *bobinas* de cobre:", pause=0.15),
        Ph("una en la base y otra en el celular.", pause=0.2),
        Ph("Y no se *tocan*.", pause=0.35),
    ]),
    Beat("problema", [
        Ph("Pero la corriente necesita un camino de *metal*.", pause=0.2),
        Ph("Aquí hay aire. ¿Entonces?", pause=0.5, pitch=Q),
    ]),
    Beat("iman", [
        Ph("La pista está en un *imán*.", pause=0.2),
        Ph("Si lo acercas y lo alejas de una bobina...", pause=0.3),
        Ph("aparece *corriente*.", pause=0.6, pitch=WOW),
    ]),
    Beat("truco", [
        Ph("En la base no se mueve nada.", pause=0.15),
        Ph("Pero su corriente cambia de sentido, sin parar.", pause=0.2, rate=SLOW),
        Ph("Y su campo magnético crece, se apaga y se *invierte*:", pause=0.2),
        Ph("un imán que se mueve... *sin moverse*.", pause=0.45, pitch=WOW),
    ]),
    Beat("induccion", [
        Ph("Ese campo cruza el aire, atraviesa la bobina del celular...", pause=0.15),
        Ph("y ahí crea *corriente*.", pause=0.25),
        Ph("Se llama *inducción magnética*.", pause=0.6, pitch=WOW),
    ]),
    Beat("centrar", [
        Ph("¿Y por qué a veces carga *lento*?", pause=0.2, pitch=Q),
        Ph("Si queda corrido, parte del campo no pasa por la bobina.", pause=0.2),
        Ph("Por eso los cargadores nuevos traen *imanes* que lo centran.", pause=0.35),
    ]),
    Beat("habla", [
        Ph("Y el celular le *avisa* a la base cuando la batería se llena,", pause=0.12),
        Ph("para que se apague.", pause=0.35),
    ]),
    Beat("cierre", [
        Ph("Entonces, ¿cómo cruza el aire?", pause=0.2, pitch=Q),
        Ph("Como un campo magnético que va y viene...", pause=0.15),
        Ph("que tu celular vuelve a convertir en *corriente*.", pause=0.6),
    ]),
]
