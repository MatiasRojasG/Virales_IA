# Propuestas stheq.ia · 2026-11-26 (jueves)

**Tendencias:** hoy fallaron las dos fuentes automáticas: `tools/tendencias_decalogo.py` y `tools/tendencias.py` devolvieron HTTP 403 (API de YouTube) y vidIQ no tiene créditos. Se usan las mediciones más recientes del repo (30 días, corridas del 22–24 nov): mediana top 10 por categoría — día a día 2,23 M; autos 1,82 M; robótica 1,23 M; ciberseguridad 0,56 M; energía 0,49 M; medicina 0,24 M (máx. 18,0 M); espacio 0,19 M — y los videos del tema más vistos del 24-nov («I bought every product from AI scam ads», 13,5 M; «Are These People Real or AI?», 44,3 M). Ayer (tec06, Euphoria) fue **videojuegos / día a día**: hoy no se repite. Jueves: no hay carrusel (el último es del 25-nov). Temas ya usados o propuestos se descartan (CAPTCHA, robot cirujano, WhatsApp, deepfakes, estafas con anuncios, etc.). Solo se toma el tema; nunca se copia nada.

## A · CIBERSEGURIDAD — «¿Cuánto tarda alguien en adivinar tu contraseña?» ✅ ELEGIDA
- Tendencia: ciberseguridad y estafas (0,56 M de mediana; «I bought every product from AI scam ads», 13,5 M). La pregunta «¿cuánto tarda un hacker en descifrar mi contraseña?» se repite cada año cuando sale la tabla de Hive Systems.
- Gancho: una clave de 8 letras en pantalla y un contador de intentos que se dispara. ¿Cuánto aguanta?
- Escenas: 1) clave de 8 letras + contador · 2) en la página no se puede: te bloquea al tercer intento · 3) roban la lista completa, guardada como «huellas» (hash) · 4) la huella no se deshace, pero se imita: inventar, sacar huella, comparar · 5) tarjetas de video de videojuegos, más de cien mil intentos por segundo · 6) 8 minúsculas al azar: ~2 semanas · 7) 8 caracteres mezclados: 132 años · 8) por qué: cada carácter multiplica las opciones (×26 / ×≈95) · 9) la trampa: si es predecible o se filtró, cae en segundos · 10) respuesta: importa lo larga y al azar que sea; frase larga o gestor de contraseñas.
- Fuentes: Hive Systems, «The 2026 Password Table» (14-jul-2026; 16 × RTX 5090, bcrypt costo 10, 138.675 intentos/s; 8 minúsculas ≈ 2 semanas; 8 mezclados 132 años; claves comunes, filtradas o reutilizadas «can fall instantly»; recomienda gestor de contraseñas y frase larga) — https://www.hivesystems.com/blog/are-your-passwords-in-the-green ; comunicado PR Newswire 14-jul-2026; Carrier Management 14-jul-2026.
- Puntuación: tracción 8 · gancho 10 · interés general 10 · potencial visual 9 · fuentes 9 = **46**

## B · MEDICINA Y SALUD — «¿Cómo sabe tu reloj cuántas veces late tu corazón?»
- Tendencia: medicina y salud (máx. 18,0 M en 30 días) y relojes inteligentes en día a día.
- Gancho: el reloj no toca tu corazón… y aun así cuenta cada latido.
- Escenas: luz verde que entra en la muñeca · la sangre absorbe verde · con cada latido hay más sangre y vuelve menos luz · la onda que sube y baja = pulso · por qué falla si el reloj está suelto.
- Fuentes: Apple, «Monitor your heart rate with Apple Watch» (support.apple.com/HT204666: LED verdes y fotodiodos, fotopletismografía); Macworld/iMore sobre la explicación de Apple.
- Puntuación: tracción 7 · gancho 9 · interés 9 · visual 9 · fuentes 9 = **43**

## C · ESPACIO — «Tu celular necesita a Einstein para no perderse»
- Tendencia: espacio (0,19 M de mediana), GPS en día a día.
- Gancho: el GPS te ubica a metros… pero sin una corrección de Einstein se equivocaría kilómetros por día.
- Escenas: satélites que mandan la hora · el celular mide cuánto tarda cada señal · los relojes arriba se adelantan ≈ 38 µs por día · eso son ≈ 10 km de error diario · se corrigen desde fábrica.
- Fuentes: Penn State GEOG 862 «The Satellite Clock»; Ashby, «Relativity in the Global Positioning System» (Living Reviews in Relativity); Smithsonian «Time and Navigation».
- Puntuación: tracción 6 · gancho 8 · interés 8 · visual 8 · fuentes 9 = **39**

**Elección:** A (46 puntos): pregunta que todos se hacen sobre algo que usan cada día, mecanismo dibujable (contador de combinaciones que explota, huellas que se comparan) y una fuente medida y fechada (Hive Systems 2026). Cifras de la fuente; la multiplicación ×26 / ×95 es aritmética propia.
