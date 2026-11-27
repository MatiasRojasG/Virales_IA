# Propuestas stheq.ia · 2026-11-27 (viernes) — ejecución paralela

> Esta ejecución corrió en paralelo con la que eligió la carga inalámbrica (`propuestas.md`). Al detectarlo, NO se publicó nada: el carrusel del día ya estaba programado y el reel del día lo produce la otra ejecución. El reel `episodes/tec08_acelerometro/` queda terminado como **reserva** para otro día (cambiar la fecha de la cabecera en `script.py` y volver a renderizar).

**Tendencias (30 días, `tools/tendencias_decalogo.py` + `tools/tendencias.py`, corridas hoy):** mediana top 10 por categoría — robótica 2,40 M; autos y movilidad 1,87 M; día a día 1,42 M; ciberseguridad 0,62 M; energía 0,47 M (máx. 8,1 M); medicina y salud 0,24 M (máx. 18,7 M); espacio 0,21 M; IA aplicada 0,16 M. Ayer se produjeron **ciberseguridad** (tec07 contraseña) y **movilidad** (lidar): hoy no se repiten. Robótica quedó fuera porque sus temas dibujables ya se usaron o propusieron (robot y huevo, aspiradora, caídas/equilibrio en tec06, robot que aprende en viral02). Solo se toma el tema; nunca se copia nada.

## A · DÍA A DÍA — «¿Cómo sabe tu celular dónde está el suelo?» ✅ PRODUCIDA COMO RESERVA (tec08_acelerometro)
- Tendencia: día a día 1,42 M de mediana (p. ej. «Cómo es usar el Apple Pencil con el iPhone Duo?», 1,8 M; «Herramientas increíbles que no conocías», 3,1 M). El celular por dentro es un tema que siempre engancha.
- Gancho: giras el celular y la pantalla gira con él. No tiene ojos… ¿cómo sabe hacia dónde está el suelo?
- Escenas: 1) celular que gira y la pantalla se acomoda · 2) zoom al chip: una pieza diminuta colgada de resortes · 3) la gravedad la tira hacia abajo, los resortes se estiran · 4) dedos/placas que se acercan y la señal eléctrica cambia (capacitancia) · 5) tres direcciones: al inclinar, la gravedad «se pasa» a otro eje → gira la pantalla · 6) al caminar la pieza rebota en cada paso → cuentapasos · 7) en caída libre la pieza «flota» y marca cero · 8) respuesta: siente el peso de una pieza que cuelga de resortes.
- Fuentes: Android Developers, «Motion sensors» (el acelerómetro mide incluida la gravedad; quieto marca 9,81 m/s²; en caída libre marca 0; usa ~10 veces menos energía que otros sensores de movimiento) — https://developer.android.com/develop/sensors-and-location/sensors/sensors_motion ; Analog Devices, «Managing Stress and Strain… Tilt/Angle Sensing» (sistema masa-resorte; la capacitancia entre dedos fijos y dedos unidos a la masa cambia al moverse) ; revisión en *Sensors* (PMC7411979): todo smartphone actual trae un acelerómetro MEMS de 3 ejes.
- Puntuación: tracción 8 · gancho 9 · interés general 10 · potencial visual 10 · fuentes 8 = **45**

## B · ENERGÍA — «¿Por qué tus paneles rinden menos en el día más caluroso?»
- Tendencia: energía (máx. 8,1 M «A China cobriu montanhas com painéis solares»; 3,8 M sobre paneles y cortes de luz).
- Gancho: más sol, más calor… y el panel produce menos de lo que promete.
- Escenas: luz que suelta electrones · el calor agita el material y baja el voltaje · coeficiente de temperatura (≈ −0,3 a −0,5 % por °C) · por qué se dejan ventilados.
- Fuentes: NREL / U.S. DOE (efecto de la temperatura en módulos FV); fichas técnicas de fabricantes (coeficiente de temperatura de Pmax).
- Puntuación: tracción 7 · gancho 8 · interés 8 · visual 8 · fuentes 9 = **40**

## C · MEDICINA Y SALUD — «¿Cómo sabe tu oxígeno una pinza en el dedo?»
- Tendencia: medicina y salud (máx. 18,7 M).
- Gancho: sin agujas, sin sangre… y en segundos te da tu oxígeno.
- Escenas: luz roja e infrarroja atraviesan el dedo · la sangre con oxígeno absorbe distinto cada color · el latido separa sangre de tejido · límites: dedos fríos, uñas pintadas y menor precisión en pieles oscuras (FDA).
- Fuentes: FDA, comunicaciones de seguridad sobre oxímetros de pulso (2021) y guía 2025; Sjoding et al., *NEJM* (dic-2020).
- Puntuación: tracción 7 · gancho 8 · interés 9 · visual 9 · fuentes 10 = **43**

**Elección:** A (45 puntos): todos usan el celular y casi nadie sabe que adentro hay una pieza que se mueve; el mecanismo es perfecto para animar (masa, resortes, placas, gravedad que cambia de eje) y las fuentes son documentación oficial. La simulación del cuentapasos y de la caída libre en el video es ilustrativa (propia); los hechos vienen de Android Developers y Analog Devices.
