# tec02 · ¿Y si frenar recargara tu auto? (frenado regenerativo)

Reel de stheq.ia: **motion graphics animados dibujados por código** (`reelforge`), ≈ 58 s, 1080×1920, 60 fps. Sin fotos. Propuesta C del 21-nov-2026 (`propuestas/2026-11-21/`), categoría autos y movilidad. Tema inspirado en la tendencia «Lo que cambia al manejar un eléctrico en la ciudad» (2,3 M vistas); no se copia nada.

## Fuentes
- U.S. Department of Energy, fueleconomy.gov, «Where the Energy Goes: Electric Cars»: en conducción urbana (ciclo EPA FTP-75), la energía neta devuelta por frenado regenerativo a la batería y luego a la ruta equivale a ≈ 32 % de la energía tomada de la red; en carretera la ventaja es pequeña porque casi no se frena. https://www.fueleconomy.gov/feg/atv-ev.shtml
- U.S. DOE, Vehicle Technologies Office, «Fact #884: All-electric vehicle: where does the energy go?» (3-ago-2015). https://www.energy.gov/node/1139266
- U.S. DOE / AFDC, animación de frenado regenerativo: el motor se invierte y las ruedas lo hacen girar como generador; la electricidad va a la batería y esa fuerza frena el auto. https://afdc.energy.gov/fueleconomy/animations/hybrids/hybrid/hybridbraking.html

## Simplificaciones
- «≈ 32 %» es una estimación del DOE para conducción urbana de un ciclo de prueba; varía según el auto, la forma de manejar, el terreno y la carga de la batería.
- La barra de carretera no tiene cifra: es solo cualitativa («mucho menos»).
- En la animación, la batería, el motor y la rueda se dibujan en línea para mostrar el flujo; en un auto real hay inversor, reductora y control electrónico entre ellos.
- Los frenos de fricción siguen siendo necesarios para frenadas fuertes y para detener el auto del todo.

## Escenas
1. Auto que frena ante un semáforo en rojo: discos rojos y ondas de «CALOR». «?» al decir «guardar».
2. Esquema batería → motor → rueda: cargas blancas van al motor y la rueda gira.
3. Al soltar el acelerador, la rueda empuja al motor (flecha roja) y el motor pasa a «GENERADOR».
4. Las cargas rojas vuelven a la batería, que se llena; arco «frena» sobre la rueda; «frenado regenerativo».
5. Ciudad vs carretera: barra «≈ 32 %» (de la energía del enchufe) vs «mucho menos».
6. Vuelta al semáforo del inicio: ahora la energía de las ruedas viaja a la batería del auto (loop).

## Voz y audio
Edge TTS `es-CL-CatalinaNeural` (+15 %, −10 Hz), preguntas −3 Hz, revelaciones −5 Hz, cifras +6 %. Música procedural y SFX discretos (`reelforge/audio.py`). Normalizado a ≈ −14,5 LUFS, pico −1 dBTP.

## Texto para publicar
Cada vez que frenas, tu auto convierte su impulso en calor… ¿y si se pudiera guardar? 🔋

En un auto eléctrico, al soltar el acelerador las ruedas hacen girar al motor, que se vuelve generador y recarga la batería: es el frenado regenerativo. En ciudad, el Departamento de Energía de EE. UU. estima que lo recuperado equivale a cerca de un 32 % de la energía que el auto saca del enchufe.

¿Manejarías con un solo pedal? 👇
Guárdalo para no olvidarlo.

Fuentes: U.S. Department of Energy (fueleconomy.gov, «Where the Energy Goes: Electric Cars»; Fact #884, 2015).
Animación propia de stheq.ia.

#stheqia #autoelectrico #frenadoregenerativo #electromovilidad #tecnologia #ciencia #autos
