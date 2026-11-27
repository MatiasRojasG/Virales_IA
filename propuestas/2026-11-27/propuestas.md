# Propuestas stheq.ia · 2026-11-27 (viernes)

**Tendencias:** hoy fallaron de nuevo las fuentes automáticas: `tools/tendencias_decalogo.py` y `tools/tendencias.py` devolvieron HTTP 403 (API de YouTube) y vidIQ no tiene créditos. Se usan las mediciones más recientes del repo (30 días, corridas del 22–24 nov): mediana top 10 por categoría — día a día 2,23 M; autos 1,82 M; robótica 1,23 M; ciberseguridad 0,56 M; energía 0,49 M; medicina 0,24 M (máx. 18,0 M); espacio 0,19 M. Ayer se produjeron **ciberseguridad** (tec07_contrasena) y **autos y movilidad** (tec07_lidar): hoy no se repiten. Viernes: sí hay carrusel de noticias (último el 25-nov) → `carruseles/2026-11-27_noticias/`, Instagram 10:00. Solo se toma el tema; nunca se copia nada.

## A · DÍA A DÍA — «¿Cómo pasa la energía por el aire?» (carga inalámbrica) ✅ ELEGIDA
- Tendencia: día a día es la categoría con más vistas (2,23 M de mediana); la batería y los cargadores del celular ya rindieron (tec01, tec05).
- Gancho: dejas el celular sobre una base, sin cable, y empieza a cargar. ¿Cómo cruza la energía el aire?
- Escenas: 1) celular cae sobre la base y aparece el rayo de carga · 2) rayos X: una bobina abajo y otra arriba, sin tocarse · 3) la corriente necesita un camino de metal; aquí hay aire · 4) un imán que entra y sale de una bobina hace saltar la aguja · 5) en la base no se mueve nada: la corriente cambia de sentido y el campo crece, se apaga y se invierte · 6) las líneas del campo cruzan y empujan corriente en la bobina del celular: inducción magnética · 7) celular corrido: el campo se escapa; los imanes de Qi2 lo centran · 8) el celular le avisa a la base cuando la batería está llena · 9) una moneda encima se calienta; el estándar define cómo detectarla · 10) respuesta y empalme.
- Fuentes: Wireless Power Consortium, «How Qi works» (corriente alterna en la bobina transmisora → campo magnético → voltaje en la receptora; el teléfono manda señales de control para apagar el transmisor cuando la batería está llena); Belkin, «What is Qi2» (Magnetic Power Profile, imanes de alineación basados en MagSafe; eficiencia que varía con la alineación en Qi estándar); IEC 63563-7:2025 / Qi v2.0 parte 7, «Foreign Object Detection» (evitar calentar objetos metálicos como monedas o llaves en el campo del transmisor).
- Puntuación: tracción 9 · gancho 9 · interés general 9 · potencial visual 10 · fuentes 8 = **45**

## B · MEDICINA Y SALUD — «¿Cómo sabe tu reloj cuántas veces late tu corazón?»
- Tendencia: medicina y salud (máx. 18,0 M en 30 días) y relojes inteligentes.
- Gancho: el reloj no toca tu corazón… y aun así cuenta cada latido.
- Escenas: luz verde que entra en la muñeca · la sangre absorbe verde · con cada latido vuelve menos luz · la onda que sube y baja = pulso · por qué falla si el reloj está suelto.
- Fuentes: Apple, «Monitor your heart rate with Apple Watch» (support.apple.com/HT204666: LED verdes y fotodiodos, fotopletismografía).
- Puntuación: tracción 7 · gancho 9 · interés 9 · visual 9 · fuentes 9 = **43**

## C · ROBÓTICA — «¿Cómo se mantiene de pie un robot humanoide?»
- Tendencia: robótica (1,23 M de mediana; robots humanoides en lanzamientos de noviembre, p. ej. XPENG IRON).
- Gancho: lo empujas… y no se cae. ¿Cómo?
- Escenas: robot de pie · centro de masa sobre los pies · empujón: el centro se sale · paso de recuperación · sensores de inclinación y motores que corrigen cientos de veces por segundo.
- Fuentes: literatura de control de equilibrio (punto de momento cero, Vukobratović); comunicados de fabricantes. Riesgo: se parece al reel de equilibrio de tec06 (Euphoria).
- Puntuación: tracción 8 · gancho 8 · interés 8 · visual 8 · fuentes 7 = **39**

**Elección:** A (45 puntos): la categoría con más vistas, algo que mucha gente usa sin saber cómo funciona y un mecanismo muy visual (bobinas, líneas de campo que van y vienen, imanes que centran). Las afirmaciones salen del Wireless Power Consortium, del estándar Qi (FOD) y de la ficha de Qi2; no se usan cifras que no estén en las fuentes.
