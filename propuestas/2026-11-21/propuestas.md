# Propuestas stheq.ia · 2026-11-21 (sábado)

Tendencias: `tools/tendencias_decalogo.py --dias 30` (mediana top 10: día a día 2,33 M; autos y movilidad 1,76 M; robótica 1,30 M; energía 0,49 M; ciberseguridad 0,43 M; medicina 0,24 M; espacio 0,19 M; IA aplicada 0,16 M, máx. 4,0 M) y `tools/tendencias.py --amplio` (top IA: «Are These People Real or AI?», 41,2 M). Ayer (tec01, cargador GaN) fue **día a día**: hoy no se repite. Robótica y ciberseguridad ya se propusieron ayer (NEO, deepfake de Arup), así que se eligen otras categorías. Sábado: no hay carrusel de noticias. Solo se toma el tema; nunca se copia nada.

Storyboards (`storyboard_A/B/C.png`, script `storyboard.py`): bocetos con el estilo de los reels animados (reelforge, negro/blanco/rojo).

## A · ENERGÍA — «Hay sol, tienes paneles… y te quedas sin luz igual»
- Tendencia: «Si se va la luz, tus paneles solares también se apagan, aunque haya sol» (3,29 M vistas).
- Gancho: se corta la luz en el barrio a mediodía. Tienes paneles y pleno sol. ¿Por qué tu casa queda a oscuras?
- Tarjetas:
  1. **Sol, paneles… y sin luz** — Se cortó la luz en tu barrio. Tus paneles siguen recibiendo sol. ¿Por qué tu casa quedó a oscuras igual?
  2. **Tu casa no está sola** — La mayoría de los paneles de casa están conectados a la red: lo que sobra viaja por los mismos cables del barrio.
  3. **Alguien sube al poste** — En un corte, técnicos trabajan en esos cables. Si tus paneles siguieran inyectando energía, el cable «muerto» estaría vivo y podría electrocutarlos.
  4. **El inversor escucha a la red** — La caja que convierte la energía de los paneles vigila el voltaje y la frecuencia de la red (50 veces por segundo en Chile). Si desaparecen, se desconecta. Dato: **en ≤ 2 s** (IEEE 1547 / UL 1741).
  5. **Se llama «anti-isla»** — Evita que tu casa quede como una isla con energía en medio del apagón.
  6. **¿Y si quiero luz?** — Con una batería y un equipo que primero separa tu casa de la red, sí: te alimenta sin mandar energía al cable. Respuesta al gancho.
- Fuentes: IEEE Std 1547-2018 (desconexión ante isla no intencional en ≤ 2 s), explicado en NREL, «IEEE 1547-2018 unintentional islanding primer» (https://www.nrel.gov/docs/fy22osti/77782.pdf); UL 1741 (norma de ensayo de inversores, complementa a IEEE 1547); Penn State AE 868, «Interconnection Codes and Technical Issues» (https://courses.ems.psu.edu/ae868/book/export/html/970).

## B · IA APLICADA — «¿Cuál de estas caras es real?»
- Tendencia: «Are These People Real or AI?» (41,2 M vistas) y «POV: esos videos de frutas con IA» (9,6 M).
- Gancho: dos caras. Una existe; la otra la inventó una IA. ¿Cuál es cuál?
- Tarjetas:
  1. **¿Cuál es real?** — Una de estas personas existe. La otra nunca nació. ¿Puedes notarlo?
  2. **El experimento** — Investigadoras de Lancaster y Berkeley mostraron caras reales y hechas con IA a **315 personas** (128 caras cada una).
  3. **Como lanzar una moneda** — Acertaron el **48,2 %** de las veces: igual que adivinar al azar (50 %).
  4. **Dos IAs que compiten** — Una dibuja caras; otra intenta pillar las falsas. Tras millones de rondas, la que dibuja aprende a no dejar pistas (red generativa antagónica, GAN).
  5. **Y les creemos más** — Otro grupo (223 personas) calificó las caras falsas como **7,7 % más confiables**.
  6. **Entonces, ¿cómo te defiendes?** — No mires solo la cara: revisa quién lo publica y de dónde viene. Vuelta a las dos caras.
- Fuentes: Nightingale, S. J. y Farid, H. (2022), «AI-synthesized faces are indistinguishable from real faces and more trustworthy», PNAS 119(8) e2120481119 (https://pmc.ncbi.nlm.nih.gov/articles/PMC8872790); Scientific American (feb-2022); Lancaster University (nota de prensa). Aclaración honesta: no todas las caras falsas son indistinguibles; el estudio usa StyleGAN2 (2022).

## C · AUTOS Y MOVILIDAD — «El auto eléctrico que recarga frenando»
- Tendencia: «Lo que cambia al manejar un eléctrico en la ciudad» (2,29 M) y «Mi primera vez manejando un híbrido enchufable» (2,54 M).
- Gancho: cada vez que frenas en un semáforo, la energía del auto se va en calor. ¿Y si se pudiera guardar?
- Tarjetas:
  1. **Frenar = calor** — Las pastillas aprietan el disco y toda esa energía de movimiento se va en calor.
  2. **Un motor que gira** — En un eléctrico, la batería empuja corriente al motor y el motor mueve las ruedas.
  3. **Al revés** — Al soltar el acelerador, las ruedas hacen girar el motor: ahora es un generador y frena el auto.
  4. **La energía vuelve** — Esa corriente recarga la batería. Rinde más en la ciudad (muchas frenadas) que en carretera.
  5. **Pero no reemplaza a los frenos** — Para frenadas fuertes y para detenerse del todo siguen los frenos normales; eso sí, se gastan menos.
  6. **Frena… y recarga** — Respuesta al gancho: sí, una parte se recupera.
- Fuentes: U.S. DOE, fueleconomy.gov, «Where the Energy Goes: Electric Cars» (https://fueleconomy.gov/feg/atv-ev.shtml) y animación de frenado regenerativo (https://afdc.energy.gov/fueleconomy/animations/hybrids/hybrid/hybridbraking.html).
