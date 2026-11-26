# Propuestas stheq.ia · 2026-11-26 (jueves)

Flujo automático (CLAUDE.md, desde el 23-nov): 3 ideas, puntaje y se produce la de mayor puntaje. Ayer (tec06) fue **videojuegos / día a día**, así que hoy no se usa esa categoría. Hoy no hay carrusel de noticias (el último fue el 25-nov; toca el 27).

Tendencias (`tools/tendencias_decalogo.py --dias 30`, Shorts en español, mediana del top 10): autos y movilidad 2,28 M · día a día 1,95 M · robótica 1,23 M · energía 0,47 M · ciberseguridad 0,40 M · espacio 0,25 M · medicina 0,24 M · IA aplicada 0,16 M.

## A · AUTOS Y MOVILIDAD — «¿Cómo ve de noche un auto sin conductor?» ✅ ELEGIDA (tec07_lidar)
- Tendencia: «Toyota Built a Self-Driving Car for 5-Year-Olds» (10,5 M), «Self-Driving Car with My Mum» (2,3 M), «Even the Cop Was Confused by This Self-Driving Car» (2,0 M), «O carro continua dirigindo sozinho quando o motorista dorme» (3,2 M).
- Gancho: 2 de la mañana, un auto sin nadie al volante y alguien vestido de negro cruza. ¿Cómo lo ve?
- Escenas: calle de noche desde arriba + lupa con el asiento vacío · visor de cámara casi negro · pulso láser de ida y vuelta · 30 cm por milmillonésima de segundo, 200 milmillonésimas = 30 m · barrido de 360° y nube de puntos (raycasting propio con NumPy) · la persona dibujada con puntos · círculo de 300 m (según Waymo), de día o de noche · lidar + cámaras + radar · cierre: no espera la luz, la lanza y mide el eco.
- Aprende: cómo el lidar mide distancias con el tiempo de vuelo de la luz y arma una imagen 3D sin necesitar luz ambiente.
- Fuentes: Waymo, soporte «A suite of sensors means safer rides, safer roads» (360°, hasta 300 m); Waymo, «The Waymo Driver Handbook: Perception» (oct-2021: millones de pulsos en todas direcciones, todas las condiciones de luz); Waymo, «Meet the 6th-generation Waymo Driver» (ago-2024: 13 cámaras, 4 lidar, 6 radar); velocidad de la luz (cálculo propio).
- Puntaje: tracción 9 · gancho 9 · interés general 8 · potencial visual 10 · fuentes 9 = **45**

## B · ROBÓTICA — «El robot que dispara láser a los salmones»
- Tendencia: «Norway Deploys 2.000 AI Laser Robots to Protect Salmon» (3,5 M).
- Gancho: en Noruega, bajo el agua, un robot dispara un láser a un salmón… para salvarlo. ¿Qué apunta?
- Escenas: jaula de salmones · piojo de mar pegado a la piel · dos cámaras ven pasar al pez · la IA lo detecta y predice su trayectoria · espejos móviles apuntan · pulso verde: el piojo oscuro absorbe, la escama brillante refleja · cuántos equipos hay · advertencia: el Instituto Veterinario noruego registró reportes de cataratas en sitios con láser.
- Fuentes: IEEE Spectrum; Business Norway; Research Council of Norway (Forskningsrådet); Laser Focus World; Instituto Veterinario de Noruega (Fish Health Report).
- Puntaje: tracción 7 · gancho 9 · interés general 7 · potencial visual 9 · fuentes 8 = **40**

## C · ENERGÍA — «Pusieron paneles solares en el desierto… y volvió el pasto»
- Tendencia: «A China cobriu montanhas com painéis solares» (7,9 M).
- Gancho: un desierto, millones de paneles, y unos años después… ovejas pastando debajo. ¿Qué pasó?
- Escenas: suelo seco y viento · sombra de los paneles: menos evaporación y menos viento · el agua de lavado se infiltra · brota pasto · el pasto tapa los paneles · llegan las ovejas · advertencia: no sirve en todos los desiertos.
- Fuentes: China Daily y People's Daily (parque de Talatan, Qinghai; cifras de monitoreo locales); estudio en Environmental Research Letters (2025) citado por medios — por verificar en la fuente.
- Puntaje: tracción 7 · gancho 8 · interés general 7 · potencial visual 7 · fuentes 6 = **35**

**Elección:** A (mayor puntaje; categoría con más vistas en 30 días y mecanismo muy visual que se puede dibujar paso a paso). Solo se toma el tema de las tendencias; no se copia nada.
