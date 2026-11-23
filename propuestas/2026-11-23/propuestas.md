# Propuestas stheq.ia · 2026-11-23 (lunes)

Tendencias: `tools/tendencias_decalogo.py --dias 30` (mediana top 10: autos y movilidad 2,22 M; robótica 2,22 M; día a día 2,19 M; ciberseguridad 0,67 M; energía 0,49 M; medicina 0,24 M; espacio 0,20 M; IA aplicada 0,17 M) y `tools/tendencias.py --amplio` (top: «Are These People Real or AI?», 43,3 M; «I bought every product from AI scam ads», 13,5 M). Ayer (tec03, vidrio del celular) fue **día a día**: hoy no se repite. Lunes: hay carrusel de noticias (`carruseles/2026-11-23_noticias/`). Solo se toma el tema; nunca se copia nada.

Storyboards (`storyboard_A/B/C.png`, script `storyboard.py`): bocetos con el estilo de los reels animados (reelforge, negro/blanco/rojo).

## A · AUTOS Y MOVILIDAD — «¿Cómo sabe tu auto que te estás quedando dormido?»
- Tendencia: «Toyota Built a Self-Driving Car for 5-Year-Olds» (9,95 M) y «O carro continua dirigindo sozinho quando o motorista dorme» (2,70 M).
- Gancho: de noche, en la carretera, los párpados pesan… ¿Cómo puede saberlo el auto antes que tú?
- Tarjetas:
  1. **¿Y si te duermes manejando?** — Un microsueño de pocos segundos basta para salirte de la pista. ¿Cómo puede notarlo un auto?
  2. **Una cámara que ve en la oscuridad** — Muchos autos nuevos llevan una cámara frente al conductor con luz infrarroja: invisible para ti, pero le permite ver tus ojos de noche.
  3. **Mide cuánto se cierran tus párpados** — No le importa un parpadeo: busca ojos que se cierran lento y se quedan cerrados.
  4. **El tiempo con los ojos cerrados** — Una medida clásica es el **PERCLOS**: qué parte de un minuto pasas con los ojos al menos **80 %** cerrados. Los estudios para la autoridad de carreteras de EE. UU. la consideraron de las más confiables.
  5. **Te avisa antes** — Si el número sube, suena una alerta y te sugiere descansar. En la Unión Europea, desde julio de **2026**, todo auto nuevo debe traer una cámara que avise si el conductor se distrae.
  6. **Respuesta al gancho** — El auto no lee tu mente: mira tus párpados y cuenta el tiempo.
- Fuentes: Wierwille et al. / Dinges et al., FHWA-MCRT-98-006, «PERCLOS: A Valid Psychophysiological Measure of Alertness» (FHWA/NHTSA, 1998) (https://rosap.ntl.bts.gov/view/dot/113); Comisión Europea, «Safer cars, safer roads: new rules take effect» (8-jul-2026) (https://commission.europa.eu/news-and-media/news/safer-cars-safer-roads-new-rules-take-effect-2026-07-08_en); Reglamento (UE) 2019/2144 y Reglamento Delegado (UE) 2023/2590 (ADDW). Aclaración: hay sistemas que no usan cámara y estiman el cansancio por cómo mueves el volante; los umbrales cambian por fabricante.

## B · ROBÓTICA — «¿Cómo toma un robot un huevo sin romperlo?»
- Tendencia: «IShowSpeed Asked a Humanoid Robot a Question…» (6,7 M) y «Robot Dish Wash» (2,4 M).
- Gancho: una mano robótica puede levantar kilos… y aun así un huevo es su peor pesadilla. ¿Cómo sabe cuándo dejar de apretar?
- Tarjetas:
  1. **¿Cómo no aplastar un huevo?** — Un robot sin tacto aprieta hasta donde le dijeron. Si se pasa, crac.
  2. **Tu dedo siente la presión** — Tu yema tiene miles de receptores que avisan cuánto aprietas y si algo se resbala.
  3. **Una yema de gel con una cámara** — Algunos sensores táctiles usan una capa de gel blando con una cámara detrás: al tocar algo, el gel se hunde y la cámara ve la forma y la fuerza.
  4. **Siente fuerzas mínimas** — El sensor Digit 360 (Meta y GelSight, 2024) detecta fuerzas de apenas **1 milinewton**. Así el robot aprieta… y se detiene a tiempo.
  5. **Firme, pero sin romperlo** — Respuesta al gancho: el robot no adivina, siente. Todavía es tecnología de laboratorio en muchos casos.
- Fuentes: Meta AI, «Advancing embodied AI through progress in touch perception» (31-oct-2024) (https://ai.meta.com/blog/fair-robotics-open-source/); GelSight y Meta AI, nota de prensa (Business Wire, 31-oct-2024) (https://www.businesswire.com/news/home/20241031980322/en/GelSight-and-Meta-AI-Introduce-Digit-360-Tactile-Sensor/); The Robot Report (https://www.therobotreport.com/gelsight-meta-ai-release-digit-360-tactile-sensor-for-robotic-fingers/). Aclaración: es un sensor de investigación; muchos robots comerciales aún usan sensores de fuerza más simples.

## C · CIBERSEGURIDAD — «El código de WhatsApp que no pediste»
- Tendencia: «I bought every product from AI scam ads» (13,5 M) y «Beware of Deepfake Fraud — ICICI Bank» (8,6 M).
- Gancho: te llega un SMS con un código de WhatsApp. Segundos después, un amigo te escribe: «uy, te lo mandé por error, ¿me lo reenvías?».
- Tarjetas:
  1. **Un código que no pediste** — Llega solo y alguien te pide que lo reenvíes.
  2. **Ese código abre tu cuenta** — WhatsApp lo manda para comprobar que el número es tuyo al instalarlo en un teléfono. Quien lo tenga puede abrir tu cuenta en el suyo.
  3. **Tu WhatsApp pasa a otro teléfono** — Y desde ahí pueden escribir a tus contactos pidiendo plata (muchas veces, usando la cuenta de un amigo ya robada).
  4. **Un segundo candado** — La verificación en dos pasos pide una clave tuya además del código: sin ella no pueden registrar tu número.
  5. **El código no se comparte** — Respuesta al gancho: ese mensaje no es un error; es el intento de robo.
- Fuentes: WhatsApp, «About two-step verification» (https://faq.whatsapp.com/general/26000021) y página de seguridad (https://www.whatsapp.com/security); Bitdefender, «Received a WhatsApp verification code without requesting it?» (https://www.bitdefender.com/en-us/blog/hotforsecurity/received-a-whatsapp-verification-code-without-requesting-it-beware-you-might-be-about-to-have-your-account-stolen). Aclaración: WhatsApp está cambiando el PIN de 6 dígitos por una clave más larga en algunas cuentas.
