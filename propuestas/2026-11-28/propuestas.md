# Propuestas stheq.ia · 2026-11-28 (sábado)

**Tendencias:** hoy fallaron otra vez las fuentes automáticas: `tools/tendencias_decalogo.py` y `tools/tendencias.py` devolvieron HTTP 403 (API de YouTube) y vidIQ no tiene créditos (se renuevan el 16-dic). Se usan las mediciones más recientes del repo (30 días, corridas del 22–24 nov): mediana top 10 por categoría — día a día 2,23 M; autos y movilidad 1,82 M; robótica 1,23 M; ciberseguridad 0,56 M; energía 0,49 M; medicina 0,24 M (máx. 18,0 M); espacio 0,19 M. Ayer (tec08, carga inalámbrica) fue **día a día**: hoy no se repite. Carrusel: el último es del 27-nov → hoy no toca (próximo el 29). Solo se toma el tema; nunca se copia nada.

## A · AUTOS Y MOVILIDAD — «¿Cómo sabe tu auto que vas a chocar… antes que tú?» (frenado automático de emergencia) ✅ PRODUCIDA COMO RESERVA (tec09_frenado_automatico)
- Tendencia: autos y movilidad es la segunda categoría con más vistas (1,82 M de mediana); el lidar (tec07) mostró cómo «ve» un auto, pero no cómo decide frenar.
- Gancho: el auto de adelante frena de golpe, tú miras el celular… y tu auto frena solo. ¿Cómo supo?
- Escenas: 1) auto que se acerca a otro que frena; aparece la alerta · 2) ¿qué tiene que saber? distancia y a qué velocidad se acercan · 3) el sensor delantero (muchas veces radar o cámara) manda una señal que rebota · 4) con dos medidas seguidas: la distancia se achica → velocidad de acercamiento · 5) la cuenta clave: distancia ÷ velocidad = segundos para el choque (ej. 30 m a 50 km/h ≈ 2,2 s) · 6) reloj que baja: primero avisa · 7) si no frenas, frena él; si frenas débil, completa la fuerza · 8) resultado: IIHS, −50 % choques por alcance y −56 % con heridos · 9) límites: lluvia, niebla, curvas; no reemplaza al conductor · 10) respuesta y empalme.
- Fuentes: IIHS (J. Cicchino, «Front crash prevention slashes police-reported rear-end crashes», ene-2016, actualizado; y «Autobrake is good, but it could be better», feb-2019): frenado automático −50 % choques por alcance, −56 % con lesionados; NHTSA, «Driver Assistance Technologies» (CIB frena si el conductor no lo hace; DBS complementa si frena poco); Transport Canada, «Automatic emergency braking» (mod. 19-feb-2026): avisa primero, puede no evitar el choque, limitaciones con lluvia, nieve, niebla, noche o curvas.
- Puntuación: tracción 9 · gancho 9 · interés general 9 · potencial visual 9 · fuentes 10 = **46**

## B · MEDICINA Y SALUD — «¿Cómo ve una resonancia dentro de tu cuerpo sin abrirte?»
- Tendencia: medicina y salud (máx. 18,0 M en 30 días).
- Gancho: te acuestas en un tubo que hace ruido… y sale una foto de tu rodilla por dentro. Sin rayos X.
- Escenas: protones como brújulas diminutas · el imán gigante los alinea · un pulso de radio los tumba · al volver emiten señal · cada tejido vuelve a distinto ritmo → contraste · por qué suena tan fuerte.
- Fuentes: NIH / NIBIB, «Magnetic Resonance Imaging (MRI)».
- Puntuación: tracción 7 · gancho 8 · interés 8 · visual 9 · fuentes 9 = **41**

## C · ESPACIO — «¿Cómo aterriza de pie un cohete?»
- Tendencia: espacio (0,19 M de mediana, pero los aterrizajes y capturas de cohetes se viralizan).
- Gancho: un cohete de 40 m cae desde el espacio… y se para solo sobre una plataforma en el mar.
- Escenas: vuelta de la primera etapa · aletas de rejilla que guían · encendido de frenado · patas · el cálculo de cuándo encender.
- Fuentes: SpaceX (Falcon 9, páginas oficiales), NASA.
- Puntuación: tracción 6 · gancho 9 · interés 8 · visual 9 · fuentes 8 = **40**

**Elección:** A (46 puntos): categoría con mucha tracción, algo que ya traen muchos autos nuevos y que casi nadie sabe cómo decide, mecanismo dibujable (eco, distancia que se achica, reloj de segundos para el choque) y fuentes de primer nivel (IIHS, NHTSA, Transport Canada). El ejemplo numérico (30 m a 50 km/h) es un cálculo propio de física simple, no una cifra de la fuente.

**Nota:** otra ejecución paralela de hoy ya programó en Metricool el reel `tec09_ia_te_da_la_razon` (Instagram 10:00, YouTube 16:00; ver `propuestas_ia.md`). Para no publicar dos reels el mismo día, `tec09_frenado_automatico` queda listo y sin publicar, como reserva (MP4, SRT, portada y README con el texto para publicar).
