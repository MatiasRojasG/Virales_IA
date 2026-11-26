# tec07 · ¿Cómo ve de noche un auto sin conductor? (lidar: tiempo de vuelo de la luz y nube de puntos)

Reel de stheq.ia: **motion graphics animados dibujados por código** (`reelforge`), 59,8 s, 1080×1920, 60 fps. Sin fotos. Propuesta A del 26-nov-2026 (`propuestas/2026-11-26/`, 45 puntos, elegida de forma automática), categoría **autos y movilidad**. Tema inspirado en las tendencias «Toyota Built a Self-Driving Car for 5-Year-Olds» (10,5 M vistas) y «Self-Driving Car with My Mum» (2,3 M); no se copia nada.

## Fuentes
- Waymo, soporte «A suite of sensors means safer rides, safer roads»: el lidar mide tamaño y distancia de los objetos en 360° alrededor del vehículo y hasta 300 m. https://support.google.com/waymo/answer/9190838
- Waymo, «The Waymo Driver Handbook: Perception» (oct-2021): sensores lidar alrededor del vehículo envían millones de pulsos láser en todas direcciones y miden cuánto tardan en rebotar; nubes de puntos hasta 300 m en todas las condiciones de luz. https://waymo.com/blog/2021/10/the-waymo-driver-handbook-perception
- Waymo, «Meet the 6th-generation Waymo Driver» (ago-2024): 13 cámaras, 4 lidar y 6 radar (más receptores de audio). https://waymo.com/blog/2024/08/meet-the-6th-generation-waymo-driver/
- Física (cálculo propio): la luz recorre 29,98 cm por nanosegundo (c = 299.792 km/s). A 30 m, ida y vuelta = 60 m → 200 ns.

## Simulación propia
- La nube de puntos de la calle es un **raycasting real hecho con NumPy** (`scenes.raycast`): 2.160 rayos desde el techo del auto contra los edificios, autos estacionados, árboles y personas dibujados; cada rayo deja el punto de rebote más cercano (con un ruido de ±4 cm). Los anillos grises sobre el asfalto imitan los haces inclinados hacia abajo de un lidar giratorio (radios elegidos a mano).
- La persona dibujada con filas de puntos es una silueta propia muestreada en 22 líneas de escaneo; no son datos de un lidar real.

## Simplificaciones
- La escena está en 2D vista desde arriba; un lidar real mide en 3D con decenas o cientos de haces a distintas alturas.
- Las personas están exageradas de tamaño para que se vean; las distancias de la calle (30 m hasta el cruce) son coherentes con la cota.
- «Millones de veces»: Waymo habla de millones de pulsos en todas direcciones; el ritmo exacto depende del sensor y no se cita.
- El alcance de 300 m es el máximo que declara Waymo, no una garantía para cualquier objeto. «De día o de noche»: el lidar no depende de la luz ambiente, aunque la lluvia densa o la niebla pueden afectarlo (por eso se combina con cámaras y radar).
- No se afirma que el lidar sea infalible ni que estos autos no tengan incidentes.

## Escenas
1. Calle de noche desde arriba: el auto avanza; lupa sobre el asiento vacío y el volante («nadie»); una persona oscura cruza; «?».
2. Visor de cámara: imagen casi negra con ruido, la silueta apenas se distingue: «muy poco».
3. El lidar del techo se ilumina y lanza un pulso rojo que llega a la persona y vuelve.
4. Recuadro «30 cm en 1 milmillonésima de segundo»; contador 0 → 200 «ida y vuelta»; cota «30 m».
5. Barrido de 360° que acelera; los rebotes dibujan edificios, autos, árboles, anillos en el asfalto y a la persona en rojo; «cada rebote es un punto».
6. Zoom a la persona: filas de puntos dibujan su forma; «LIDAR».
7. Vista lejana: círculo de 300 m alrededor del auto («según Waymo»), sol → luna sin que cambien los puntos.
8. Lidar + cámaras + radar convergen en el auto.
9. Vuelta a la calle: la persona rodeada de puntos, un último pulso y su eco; los puntos se apagan y queda la calle del inicio (empalme).

## Control de calidad
- ffprobe: h264 1080×1920 60 fps, AAC 48 kHz estéreo, 59,78 s. Loudness −14,5 LUFS (LRA 2,4 LU), pico verdadero −2,8 dBTP.
- Hoja de cuadros cada 3 s revisada: sin solapamientos; contenido entre y≈480 y 1300 (el cruce peatonal queda en el borde superior); subtítulos en la banda inferior.
- Narración: 177 palabras en 59,8 s (≈ 3,0 palabras/s), cifras con `rate=SLOW`, preguntas con `pitch=Q`, revelaciones con `pitch=WOW`. Subtítulos alineados por palabra (sin Whisper). No pude escuchar el audio: se verificó con métricas.
- Cifras: 30 cm/ns y 200 ns ↔ 30 m (cálculo propio con c); 300 m y 360° (Waymo).

## Texto para publicar
**YouTube (título):** ¿Cómo ve de noche un auto sin conductor? 🚗 #shorts

**Texto:**
Dos de la mañana. Un auto sin nadie al volante… y alguien vestido de negro cruza. ¿Cómo lo ve? 🚗🌙

No espera la luz: la lanza. El lidar dispara pulsos de láser y mide cuánto tardan en volver. La luz avanza unos 30 cm en una milmillonésima de segundo, así que si el rebote vuelve en 200 milmillonésimas, la persona está a 30 metros. Millones de rebotes forman una imagen en 3D. Según Waymo, su lidar mide 360° alrededor del auto y hasta unos 300 metros, de día o de noche, y lo combina con cámaras y radar.

¿Tú te subirías a uno? 👇
Guárdalo para no olvidarlo.

Fuentes: Waymo (soporte «A suite of sensors…», blog «The Waymo Driver Handbook: Perception», 2021, y «Meet the 6th-generation Waymo Driver», 2024).
Animación original de stheq.ia (sin fotos).

#stheqia #autonomo #lidar #robotaxi #waymo #tecnologia #autos #datoscuriosos
