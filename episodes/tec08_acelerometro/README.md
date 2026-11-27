# tec08 · ¿Cómo sabe tu celular dónde está el suelo?

Reel animado (motion graphics por código), 54,7 s, 1080×1920, 60 fps. Categoría: **día a día**. Propuesto en `propuestas/2026-11-27/propuestas_acelerometro.md` (45 puntos).

**Estado: RESERVA, no publicado.** Se produjo en una ejecución paralela del 27-nov; ese día ya se publicaba otro reel. Para usarlo otro día: cambiar `fecha` en `script.py` y correr `python episodes/tec08_acelerometro/build.py`.

## Fuentes
- **Android Developers, «Motion sensors»**: https://developer.android.com/develop/sensors-and-location/sensors/sensors_motion — el acelerómetro mide la aceleración «including the force of gravity»; quieto sobre la mesa marca 9,81 m/s²; «when the device is in free fall … its accelerometer reads a magnitude of g = 0 m/s²»; el sensor de gravedad sirve para conocer la orientación del equipo; existen sensores de contador y detector de pasos.
- **Analog Devices** (familia ADXL35x, artículo «Managing Stress and Strain to Get the Best Performance in High Precision Tilt/Angle Sensing»): sistema masa-resorte; la masa se mueve con la aceleración y cambia la capacitancia entre dedos fijos y dedos unidos a la masa.
- Revisión en *Sensors* (PMC7411979): los smartphones actuales traen un acelerómetro MEMS de tres ejes.
- Tamaño: los acelerómetros de celular vienen en encapsulados de unos 2 × 2 mm (p. ej. Bosch BMA400, 2,0 × 2,0 × 0,95 mm).

## Escenas
1. Gancho: el celular gira a horizontal y la imagen se endereza; «no tiene ojos»; aparece el suelo y una flecha roja.
2. Zoom al chip (≈ 2 mm) que se transforma en el acelerómetro por dentro.
3. Pesa colgada de resortes; la gravedad la baja y los resortes se estiran.
4. Dedos móviles entre dedos fijos: al bajar la pesa los espacios cambian, saltan chispas y se llena un medidor de señal.
5. Rayos X del celular: una pesa por eje; al inclinarlo, la gravedad pasa al otro eje y la pantalla gira.
6. Caminar: la pesa rebota, una onda marca cada paso y sube un contador.
7. Caída: la pesa flota al centro y la señal baja a 0.
8. Cierre: la pesa con su flecha y vuelta al celular del inicio (empalme).

## Simplificaciones
- Se dibuja una sola pesa por eje y se exagera su desplazamiento; en los chips reales todo mide micras y es de silicio.
- «Carga eléctrica entre los dedos» = capacitancia; no se nombra el término.
- La onda de pasos, el contador y el medidor son ilustrativos (no son datos medidos).
- Hay acelerómetros con otras arquitecturas (una sola masa para varios ejes, etc.).

## Control de calidad
- ffprobe: h264 1080×1920 60 fps, AAC 48 kHz, 54,7 s. −14,5 LUFS, pico −1,7 dBFS.
- Hoja de cuadros cada 3 s y transiciones revisadas (se corrigió un doble celular entre «gira» y «caminar»).
- Ritmo: 193 palabras en 54,7 s. No puedo escuchar el audio: verificado con métricas.

## Texto para publicar (si se usa)
¿Cómo sabe tu celular dónde está el suelo? 📱⬇️

Adentro hay un chip de un par de milímetros con una pesita diminuta colgada de resortes. La gravedad la tira hacia abajo, unos dedos de silicio se acercan y la señal eléctrica cambia. Por eso gira la pantalla, cuenta tus pasos… y en caída libre marca cero (Android Developers).

¿Tienes activada la rotación automática? 👇
Guárdalo para no olvidarlo.

Fuentes: Android Developers, «Motion sensors»; Analog Devices (acelerómetros ADXL35x).

#stheqia #tecnologia #celular #sensores #ciencia #fisica #android #curiosidades
