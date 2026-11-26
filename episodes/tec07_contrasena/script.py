"""Guion — «¿Cuánto tarda alguien en adivinar tu contraseña?» (metadato; no se muestra en el video)

Fuente principal: Hive Systems, «The 2026 Password Table» (14-jul-2026),
https://www.hivesystems.com/blog/are-your-passwords-in-the-green
- Equipo: 16 × RTX 5090 (tarjetas de video de consumo, arrendadas), contra bcrypt con costo 10;
  138.675 intentos por segundo en total.
- Clave de 8 caracteres AL AZAR: solo minúsculas ≈ 2 semanas; mezclando números, mayúsculas, minúsculas y
  símbolos: 132 años (tiempo máximo de fuerza bruta).
- Supone una clave que no está en filtraciones: «Attackers try all common and breached passwords before
  bothering to crack new ones»; «a common, reused, or dictionary-based password can fall instantly».
- Recomienda ir más allá de 8 caracteres y dejar que un gestor de contraseñas genere algo largo y al azar;
  «a long passphrase beats a short, clever-looking one every time».
Aritmética propia: cada carácter multiplica las combinaciones por 26 (minúsculas) o por ≈ 95 (todo el teclado).
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 7, "slug": "tec07_contrasena", "title": "¿Cuánto tarda alguien en adivinar tu contraseña?",
           "tag": "", "fecha": "26 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Tu contraseña tiene *ocho* letras.", pause=0.2),
        Ph("¿Cuánto tarda alguien en *adivinarla*?", pause=0.4, pitch=Q),
    ]),
    Beat("bloqueo", [
        Ph("Probar una por una en la página no sirve:", pause=0.12),
        Ph("al tercer intento, te *bloquea*.", pause=0.3),
    ]),
    Beat("robo", [
        Ph("Por eso roban la *lista completa* de claves de un sitio.", pause=0.2),
        Ph("Viene guardada como *huellas*: códigos revueltos que no se pueden deshacer.", pause=0.35),
    ]),
    Beat("imitar", [
        Ph("Pero sí se pueden *imitar*:", pause=0.2, pitch=WOW),
        Ph("inventan una clave, sacan su huella y comparan.", pause=0.15),
        Ph("¿Coincide?", pause=0.15, pitch=Q),
        Ph("La *encontraron*.", pause=0.35),
    ]),
    Beat("gpu", [
        Ph("Con *tarjetas de video*, prueban más de *cien mil* claves por segundo.", pause=0.4, rate=SLOW),
    ]),
    Beat("cifras", [
        Ph("Una empresa de seguridad lo midió:", pause=0.25),
        Ph("ocho minúsculas al azar...", pause=0.25, rate=SLOW),
        Ph("*dos semanas*.", pause=0.4, rate=SLOW),
        Ph("Ocho caracteres con mayúsculas, números y símbolos...", pause=0.45, rate=SLOW),
        Ph("*132|ciento_treinta_y_dos años*.", pause=0.6, pitch=WOW, rate=SLOW),
    ]),
    Beat("porque", [
        Ph("¿Por qué?", pause=0.2, pitch=Q),
        Ph("Cada carácter extra *multiplica* las opciones:", pause=0.15),
        Ph("por *26|veintiséis* con minúsculas,", pause=0.12, rate=SLOW),
        Ph("por casi *100|cien* con todo el teclado.", pause=0.4, rate=SLOW),
    ]),
    Beat("trampa", [
        Ph("Pero si tu clave es predecible, o ya se filtró,", pause=0.12),
        Ph("la prueban *primero*...", pause=0.2),
        Ph("y cae en *segundos*.", pause=0.55, pitch=WOW),
    ]),
    Beat("cierre", [
        Ph("Entonces, ¿cuánto tarda?", pause=0.2, pitch=Q),
        Ph("Depende menos de lo rara que se vea,", pause=0.15),
        Ph("y más de lo *larga* y *al azar* que sea.", pause=0.5),
    ]),
]
