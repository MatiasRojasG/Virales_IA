"""Guion — «Misma edad, distinta piel» (metadato; no se muestra en el video)

Inspiración (propuestas 2026-11-17, opción A): reel de skincare con retinal (246 K vistas) y la
página de la AAD sobre looksmaxxing que recomienda volver a lo básico.
Evidencia: Hughes MCB, Williams GM, Baker P, Green AC. «Sunscreen and prevention of skin aging:
a randomized trial». Annals of Internal Medicine 2013;158:781-790. Ensayo de Nambour (Australia):
903 adultos menores de 55 años, 4,5 años; protector diario de amplio espectro vs uso a discreción.
Se midió el envejecimiento con moldes de silicona del dorso de la mano. El grupo diario no mostró
aumento detectable del envejecimiento y tuvo un 24 % menos de probabilidad de mostrarlo.
"""
from reelforge.timeline import Beat, Ph

EPISODE = {"num": 1, "slug": "lx01_protector_solar", "title": "Misma edad, distinta piel", "tag": ""}
VOICE = "es-MX-JorgeNeural"
RATE = "+15%"
Q = "+5Hz"; SLOW = "-4%"; SLOWER = "-8%"

BEATS = [
    Beat("hook", [
        Ph("Mira la piel de tu brazo, por dentro...", pause=0.35),
        Ph("y la del *dorso* de tu mano.", pause=0.45),
        Ph("Tienen *exactamente* la misma edad.", pause=0.5),
        Ph("¿Entonces por qué una se ve más *vieja*?", pause=0.75, pitch=Q),
    ]),
    Beat("sol", [
        Ph("La diferencia no son los años...", pause=0.55),
        Ph("es cuánto *sol* ha recibido cada una.", pause=0.6, rate=SLOW),
    ]),
    Beat("colageno", [
        Ph("La luz *ultravioleta* entra en la piel", pause=0.2),
        Ph("y rompe de a poco el *colágeno*, la red que la mantiene firme.", pause=0.45),
        Ph("Y ese daño se *acumula*, año tras año.", pause=0.6),
    ]),
    Beat("duda", [
        Ph("Pero si tarda años en verse...", pause=0.3),
        Ph("¿cómo sabes si protegerte sirve de algo?", pause=0.8, pitch=Q),
    ]),
    Beat("estudio", [
        Ph("En Australia lo probaron con *903|novecientas_tres* personas.", pause=0.4, rate=SLOW),
        Ph("La mitad usó protector *todos los días*.", pause=0.25),
        Ph("La otra mitad, solo cuando quería.", pause=0.45),
        Ph("Y durante *cuatro años y medio*, midieron la piel... del dorso de sus manos.", pause=0.8, rate=SLOW),
    ]),
    Beat("resultado", [
        Ph("En el grupo diario, la piel *casi no envejeció*.", pause=0.5),
        Ph("Tenían un *24%|veinticuatro_por_ciento* menos de probabilidad de mostrar envejecimiento.", pause=1.0, rate=SLOWER),
    ]),
    Beat("rutina", [
        Ph("La clave no es un protector caro.", pause=0.3),
        Ph("Es usarlo *cada mañana*,", pause=0.2),
        Ph("aunque esté nublado,", pause=0.2),
        Ph("en la cara, el cuello... y las manos.", pause=0.6),
    ]),
    Beat("cierre", [
        Ph("Esa diferencia entre tu brazo y tu mano...", pause=0.3),
        Ph("no la hicieron los años.", pause=0.5),
        Ph("La hizo el *sol*.", pause=0.6),
    ]),
]
