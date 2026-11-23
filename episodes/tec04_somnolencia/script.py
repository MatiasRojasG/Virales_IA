"""Guion — «¿Tu auto sabe que te estás durmiendo?» (metadato; no se muestra en el video)

Propuesta A del 23-nov-2026 (propuestas/2026-11-23). Fuentes:
- NHTSA, «Drowsy Driving» (estimación 2017: 91.000 choques reportados por la policía con conductores somnolientos).
- Wierwille et al. (1994) y Dinges et al., FHWA-MCRT-98-006 (FHWA/NHTSA, 1998): PERCLOS = proporción de un
  minuto con los ojos al menos 80 % cerrados; el estudio la encontró la medida de somnolencia más confiable
  de las que probó.
- Euro NCAP (ESV 27, paper 000289): los sistemas directos usan cámaras infrarrojas para observar la cara,
  la mirada y la apertura de los párpados.
- Comisión Europea, «Safer cars, safer roads: new rules take effect» (8-jul-2026): desde el 7-jul-2026 todo
  auto y furgoneta nuevos en la UE deben traer aviso avanzado de distracción del conductor (con cámara).
- Cálculo propio: 100 km/h = 27,8 m/s.
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 4, "slug": "tec04_somnolencia", "title": "¿Tu auto sabe que te estás durmiendo?", "tag": "",
           "fecha": "23 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Llevas horas manejando de noche.", pause=0.25),
        Ph("Los párpados te *pesan*...", pause=0.3),
        Ph("y cierras los ojos *un segundo*.", pause=0.45),
        Ph("¿Tu auto se puede *dar cuenta*?", pause=0.40, pitch=Q),
    ]),
    Beat("segundo", [
        Ph("A cien kilómetros por hora, en ese segundo avanzas casi *28|veintiocho* *metros*...", pause=0.2, rate=SLOW),
        Ph("*sin ver nada*.", pause=0.40),
        Ph("En Estados Unidos estimaron *91.000|noventa_y_un_mil* choques por sueño en un solo año.", pause=0.40, rate=SLOW),
    ]),
    Beat("camara", [
        Ph("Por eso, muchos autos nuevos traen una *cámara* que mira al conductor.", pause=0.25),
        Ph("Pero de noche... ¿cómo te ve?", pause=0.35, pitch=Q),
        Ph("Te ilumina con *luz infrarroja*: invisible para ti, pero no para la cámara.", pause=0.50, pitch=WOW),
    ]),
    Beat("parpados", [
        Ph("Un parpadeo no le importa: es *rápido*.", pause=0.25),
        Ph("Busca párpados que bajan *lento*... y se quedan *cerrados*.", pause=0.35),
        Ph("Cuenta cuánto de cada minuto pasas con los ojos *casi cerrados*.", pause=0.3),
        Ph("Se llama *PERCLOS|pérclos*: una de las medidas más *confiables* del cansancio.", pause=0.45, pitch=WOW),
    ]),
    Beat("alerta", [
        Ph("Si ese tiempo sube, el auto te *avisa*: descansa.", pause=0.35),
        Ph("En Europa, desde *2026|dos_mil_veintiséis*, todo auto nuevo debe traer una cámara que vigila si te *distraes*.", pause=0.45, rate=SLOW),
    ]),
    Beat("cierre", [
        Ph("¿Tu auto sabe que te duermes?", pause=0.25, pitch=Q),
        Ph("No lee tu mente: mira tus *párpados*... y cuenta el *tiempo*.", pause=0.35, pitch=WOW),
        Ph("Porque *un segundo* con los ojos cerrados ya es demasiado.", pause=0.6),
    ]),
]
