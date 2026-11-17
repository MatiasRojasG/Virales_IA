"""Guion — «Glow up: 10 reglas con ciencia» (metadato; no se muestra en el video)

Tendencia (YouTube Shorts, últimos 30 días, búsquedas en español): «glow up / verse mejor» es el
tema de hábitos con más vistas (mediana del top 10 ≈ 2,4 M; p. ej. «everything I did in korea for
24HRS to glow up», 5,4 M). Solo se toma el tema.
Fuentes por regla en el README (Axelsson 2010, Hughes 2013, Whitehead 2012, OMS 2020,
Okada 2013, AAD, estudios sobre sonrisa y atractivo).
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 1, "slug": "dec01_glow_up", "title": "Glow up: 10 reglas con ciencia", "tag": "decálogo"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("¿Quieres verte mejor... sin filtros, sin cirugías y sin gastar una fortuna?", pause=0.45, pitch=Q),
        Ph("Estas son *diez reglas* que sí tienen respaldo científico.", pause=0.55, pitch=WOW),
    ]),
    Beat("r1", [
        Ph("*Uno:* duerme siete horas o más.", pause=0.25),
        Ph("En un estudio, las mismas personas, tras una noche sin dormir, se vieron más cansadas y *menos atractivas*.", pause=0.5),
    ]),
    Beat("r2", [
        Ph("*Dos:* protector solar, cada mañana.", pause=0.25),
        Ph("Quienes lo usaron a diario por cuatro años y medio mostraron *menos envejecimiento* en la piel.", pause=0.5, rate=SLOW),
    ]),
    Beat("r3", [
        Ph("*Tres:* más frutas y verduras.", pause=0.25),
        Ph("En seis semanas cambian levemente el tono de tu piel... y otros te ven más *saludable*.", pause=0.5),
    ]),
    Beat("r4", [
        Ph("*Cuatro:* muévete.", pause=0.2),
        Ph("Ciento cincuenta minutos a la semana, y *fuerza* dos días: eso recomienda la OMS.", pause=0.5, rate=SLOW),
    ]),
    Beat("r5", [
        Ph("*Cinco:* no fumes.", pause=0.2),
        Ph("En estudios con gemelos, el que fumaba solía verse *mayor*.", pause=0.5, pitch=WOW),
    ]),
    Beat("r6", [
        Ph("*Seis:* lava tu cara con un limpiador suave.", pause=0.2),
        Ph("Frotar fuerte *irrita* más de lo que limpia.", pause=0.45),
    ]),
    Beat("r7", [
        Ph("*Siete:* hidrata tu piel justo después de lavarla.", pause=0.45),
    ]),
    Beat("r8", [
        Ph("*Ocho:* no revientes tus granos.", pause=0.2),
        Ph("Pueden quedar *manchas* o cicatrices.", pause=0.45),
    ]),
    Beat("r9", [
        Ph("*Nueve:* sonríe.", pause=0.25),
        Ph("Una cara que sonríe se percibe más *atractiva*.", pause=0.5, pitch=WOW),
    ]),
    Beat("r10", [
        Ph("*Diez:* sé constante.", pause=0.25),
        Ph("Nada de esto se nota en un día...", pause=0.3),
        Ph("se nota en *semanas*.", pause=0.55, pitch=WOW),
    ]),
    Beat("cierre", [
        Ph("¿Verte mejor sin filtros?", pause=0.3, pitch=Q),
        Ph("Se puede... y casi todo es *gratis*.", pause=0.4, pitch=WOW),
        Ph("Guárdalo y empieza hoy, por una.", pause=0.6),
    ]),
]
