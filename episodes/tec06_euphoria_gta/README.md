# tec06 · ¿Cómo sabe caer un personaje de GTA? (Euphoria y la física de los personajes)

Reel de stheq.ia: **motion graphics animados dibujados por código** (`reelforge`), 54,3 s, 1080×1920, 60 fps. Sin fotos, sin capturas, logos ni personajes del juego: solo monigotes propios. **Encargo del usuario** (24-nov-2026, `propuestas/encargos/euphoria_gta6.md`), categoría **día a día / videojuegos**. Tema de tendencia por el lanzamiento de GTA VI (19-nov-2026).

## Fuentes
- Euphoria (NaturalMotion): simulación completa del personaje 3D (cuerpo, músculos y sistema nervioso motor); en vez de animaciones predefinidas, las reacciones se sintetizan en tiempo real y son distintas cada vez, incluso al repetir la misma escena. GTA IV (2008) fue el primer juego de Rockstar con Euphoria; después, Red Dead Redemption y Max Payne 3; está integrado en el motor RAGE. https://en.wikipedia.org/wiki/Euphoria_(software)
- Origen: Torsten Reil simulaba sistemas nerviosos humanos en su doctorado en el Departamento de Zoología de Oxford para entender cómo controlan el movimiento; fundó NaturalMotion en 2001. Departamento de Biología, Universidad de Oxford: https://www.biology.ox.ac.uk/node/2151801 · Oxford University Innovation: https://innovation.ox.ac.uk/?p=9022
- GTA VI: según Rockstar (Aaron Garbut a The New York Times, 27-ago-2026), sus personajes no jugables tienen más de 600.000 animaciones, frente a 55.000 en GTA V y 300.000 en Red Dead Redemption 2. GamesRadar (27-ago-2026): https://www.gamesradar.com/games/grand-theft-auto/gta-6s-hand-crafted-npcs-have-over-600-000-animations-compared-to-only-55-000-animations-in-gta-5/ · TechRadar (28-ago-2026).
- Fecha de lanzamiento de GTA VI, 19-nov-2026: FOX10 (16-oct-2026) y TechRadar.
- Equilibrio por pasos (punto de captura): Pratt, Carff, Drakunov y Goswami, «Capture Point: A Step toward Humanoid Push Recovery», IEEE-RAS Humanoids 2006. Se usa solo para la simulación propia.

## Experimento propio (`fisica.py`, NumPy)
- **Con control:** péndulo invertido lineal (centro de masa a 0,95 m) con un «cerebro» mínimo: si el punto de captura (x + v/ω) sale de la base de apoyo, da un paso hacia él, replanificando durante el paso. Con empujones de 0,55 / 1,0 / 1,4 m/s recupera el equilibrio con 0 / 2 / 3 pasos; con 1,6 m/s no alcanza y cae. Esas tres respuestas son las de «no hay dos caídas iguales».
- **Sin control (muñeco de trapo):** cuerpo rígido que pivota sobre los pies (θ'' = g/l·sen θ): llega al suelo en ≈ 0,9 s.
- La caída «grabada» es la misma curva en 8 cuadros clave rígidos, repetida igual tres veces.
- Estas simulaciones son modelos de juguete para mostrar la idea: **no** son el algoritmo de NaturalMotion ni de Rockstar.

## Simplificaciones y honestidad
- Rockstar no ha detallado cuánto cambió Euphoria en GTA VI: el video no afirma nada sobre eso. Dice que Rockstar la usa desde GTA IV y que, además, GTA VI tiene más de 600.000 animaciones «según Rockstar».
- «Diez veces más»: 600.000 / 55.000 ≈ 10,9 (más de diez veces).
- Las animaciones grabadas y la física se combinan en los juegos; el video lo dice («además»).
- Los «músculos» rojos y el «cerebro» son una representación; Euphoria simula músculos y control motor, no un cerebro real.
- Algunas escenas usan cámara lenta (tiempo de simulación estirado) para que el paso coincida con la voz.

## Escenas
1. Flecha roja que empuja al monigote; un fantasma gris cae como muñeco mientras el blanco estira los brazos y da un paso → «?».
2. Tira de película con la caída grabada; tres monigotes repiten la misma caída a la vez (×1, ×2, ×3).
3. Muñeco de trapo: empujón y caída sin control.
4. «Universidad de Oxford», «Torsten Reil» y una red de neuronas que se enciende sobre el cuerpo.
5. Músculos rojos y «cerebro» en la cabeza; empujón; en el suelo aparece el punto donde pisar y el pie aterriza ahí.
6. «EUPHORIA», línea de tiempo desde GTA IV (2008) → tres empujones distintos, tres reacciones distintas.
7. Barras 55.000 (GTA V) vs. 600.000 (GTA VI), «×10».
8. Cierre: la tira de cuadros se tacha, el punto aparece, recupera el equilibrio; la flecha vuelve a entrar (empalme con el inicio).

## Control de calidad
- ffprobe: h264 1080×1920 60 fps, AAC 48 kHz estéreo, 54,28 s. Loudness −14,5 LUFS, pico verdadero −2,2 dBTP.
- Sin saltos aislados entre cuadros (diferencia máxima media 3,9/255). Hoja de cuadros cada 3 s revisada.
- Narración: 157 palabras en 54,3 s (≈ 2,9 palabras/s), cifras con `rate=SLOW`, pregunta con `pitch=Q`. Subtítulos alineados por palabra (sin Whisper). No pude escuchar el audio: se verificó con métricas.

## Texto para publicar
**YouTube (título):** ¿Cómo sabe caer un personaje de GTA? 🎮 #shorts

**Texto:**
Empujas a un personaje de GTA… y en vez de caer como un muñeco, estira los brazos y da un paso. ¿Cómo sabe qué hacer? 🎮

La técnica se llama Euphoria: nació de una investigación en la Universidad de Oxford (Torsten Reil, NaturalMotion) y simula un cuerpo con músculos y un control que calcula en el momento cómo no caerse. Rockstar la usa desde GTA IV (2008). Y según Rockstar, los peatones de GTA VI tienen además más de 600.000 animaciones, más de diez veces que GTA V.

¿Cuál es la caída más absurda que has visto en un juego? 👇
Guárdalo para no olvidarlo.

Fuentes: NaturalMotion / Universidad de Oxford; Rockstar vía The New York Times (ago-2026), GamesRadar y TechRadar.
Animación original de stheq.ia.

#stheqia #gta6 #gtavi #videojuegos #fisica #tecnologia #rockstargames #gamedev
