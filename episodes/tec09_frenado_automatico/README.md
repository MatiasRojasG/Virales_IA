# tec09 · ¿Cómo supo tu auto que ibas a chocar? (frenado automático de emergencia)

Reel animado (motion graphics por código), 57,9 s, 1080×1920, 60 fps. Categoría: **autos y movilidad**. Elegido en `propuestas/2026-11-28/propuestas.md` (46 puntos).

## Fuentes
- **IIHS, Jessica Cicchino, «Front crash prevention slashes police-reported rear-end crashes»** (ene-2016, actualizado con más datos): https://www.iihs.org/news/detail/front-crash-prevention-slashes-police-reported-rear-end-crashes — «automatic emergency braking reduced rear-end crashes by 50 percent and reduced rear-end crashes that caused injuries by 56 percent».
- **IIHS, «Autobrake is good, but it could be better»** (feb-2019): https://www.iihs.org/news/detail/autobrake-is-good-but-it-could-be-better — repite −50 % choques por alcance y −56 % con heridos; menos eficaz en giros, con camiones o motos, con nieve o hielo y a alta velocidad.
- **NHTSA, «Driver Assistance Technologies»**: https://www.nhtsa.gov/vehicle-safety/driver-assistance-technologies — CIB frena si el conductor no frena; DBS «supplements the driver's braking» si frena poco.
- **Transport Canada, «Automatic emergency braking»** (mod. 19-feb-2026): https://tc.canada.ca/en/road-transportation/driver-assistance-technologies/collision-intervention/automatic-emergency-braking — usa sensores; si no reaccionas a la alerta puede frenar; puede no evitar el choque; puede no funcionar con lluvia intensa, nieve, niebla, sol fuerte, de noche o en curvas; no reemplaza tu atención.
- **Cálculo propio** (física simple, no de la fuente): 50 km/h = 13,9 m/s; 30 m ÷ 13,9 m/s ≈ 2,2 s.

## Escenas
1. Gancho: el auto de adelante con luces de freno, tú mirando el celular; la distancia se achica y tu auto frena solo; «?».
2. Retroceso: corchete «distancia» y flecha «rapidez».
3. El sensor delantero («radar») lanza ondas que rebotan en el otro auto y vuelven.
4. Mide otra vez: el corchete se achica (fantasma del anterior y flecha roja).
5. La cuenta: distancia ÷ rapidez = segundos para chocar.
6. Ejemplo: 30 m ÷ 50 km/h ≈ 2,2 s.
7. Cuenta regresiva: aviso (triángulo), frena él (✓) y barra de fuerza de freno que el auto completa.
8. Barras: choques por alcance sin y con frenado automático, −50 % (IIHS · EE. UU.).
9. Lluvia y niebla: las ondas se dispersan, ✕; «tú» y el celular tachado.
10. Cierre: se repite y frena antes; el último cuadro vuelve al estado del cuadro 0 (empalme).

## Simplificaciones
- «Muchas veces un radar»: según el modelo, el sensor puede ser radar, cámara o ambos; las fuentes oficiales hablan de «sensores».
- La «rapidez» es la de acercamiento (diferencia de velocidades). El tiempo para el choque se explica con la cuenta básica distancia ÷ rapidez; los sistemas reales usan además frenado, aceleraciones y otros datos.
- La cuenta regresiva (1,5 s al avisar, 0,8 s al frenar) es ilustrativa; cada fabricante usa sus propios umbrales.
- −50 % es el resultado del IIHS con datos de choques reportados a la policía en EE. UU. (no de todos los países ni de todos los tipos de choque).
- Distancias y autos no están a escala.

## Control de calidad
- ffprobe: h264 1080×1920 60 fps, AAC 48 kHz, 57,9 s. −14,5 LUFS, pico −2,2 dBTP.
- Ritmo: ≈ 135 palabras en 57,9 s (≈ 3,3 palabras/s al hablar). No puedo escuchar el audio: verificado con métricas.

## Texto para publicar
¿Cómo supo tu auto que ibas a chocar? 🚗💥
Un sensor adelante lanza una señal que rebota en el auto de adelante: así mide la distancia y qué tan rápido se acercan. Divide una por la otra y obtiene los segundos que faltan para el choque. Primero te avisa; si no reaccionas, frena solo. Según el IIHS (EE. UU.), los autos con frenado automático tienen la mitad de choques por alcance. Ojo: con lluvia, niebla o en curvas puede fallar, y el que maneja sigues siendo tú.
¿Tu auto lo tiene? 👇
Guárdalo para no olvidarlo.
Fuentes: IIHS (Cicchino, 2016 y 2019); NHTSA, «Driver Assistance Technologies»; Transport Canada, «Automatic emergency braking».
#stheqia #autos #seguridadvial #tecnologia #frenadoautomatico #ciencia #autonomos
