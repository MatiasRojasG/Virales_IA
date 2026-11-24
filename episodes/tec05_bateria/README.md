# tec05 · ¿Por qué tu batería dura menos cada año? (pérdida de litio, calor y carga al 100 %)

Reel de stheq.ia: **motion graphics animados dibujados por código** (`reelforge`), 59,8 s, 1080×1920, 60 fps. Sin fotos. Propuesta A del 24-nov-2026 (`propuestas/2026-11-24/`, 45 puntos, elegida de forma automática), categoría **día a día**. Tema inspirado en las tendencias «Essa capinha pode resolver o problema da bateria do iPhone» (2,47 M vistas) y «La batería de Apple en 2030 es un chiste» (2,23 M); no se copia nada.

## Fuentes
- Apple, «Battery Service and Recycling» y soporte «iPhone battery and performance»: los iPhone 15 y posteriores están diseñados para conservar el 80 % de su capacidad original a los 1.000 ciclos de carga completos en condiciones ideales (los modelos anteriores, 500). https://www.apple.com/batteries/service-and-recycling/ · cobertura: Engadget, MacRumors (20-feb-2024).
- Apple soporte 105105, «Charge and maintain your iPhone battery»: zona ideal 16–22 °C; sobre 35 °C el calor puede dañar la capacidad de forma permanente; la carga optimizada reduce el tiempo que el iPhone pasa al 100 %. https://support.apple.com/105105
- Apple soporte 108055, «About Charge Limit and Optimized Battery Charging»: opción «Límite del 80 %» (y límite configurable entre 80 y 100 % en modelos recientes). https://support.apple.com/108055
- Mikheenkova et al., Journal of The Electrochemical Society (2023), y NREL (fy22osti/79499): la pérdida de litio disponible, ligada al crecimiento de la capa SEI en el ánodo, es el principal modo de envejecimiento; la temperatura y un estado de carga alto lo aceleran. https://www.nrel.gov/docs/fy22osti/79499.pdf

## Simplificaciones
- «El litio viaja»: en realidad son iones de litio que pasan entre el ánodo (grafito) y el cátodo; los electrones van por el circuito. La capa roja representa la SEI (interfase sólida del electrolito); no se nombra en el video.
- La pérdida de litio es el mecanismo principal, pero no el único (también se degradan los electrodos y sube la resistencia interna).
- El descenso de 100 % a 80 % en 1.000 cargas se anima de forma lineal solo como ilustración; la curva real no es lineal. El 80 %/1.000 ciclos es el dato de diseño de Apple en condiciones ideales, no una garantía para cualquier uso.
- «Muchos celulares traen una opción para cargar hasta el 80 %»: está en iPhone 15 y posteriores y en varios Android (p. ej. protección de batería de Samsung y Pixel); no en todos.
- Los puntos que quedan atrapados (uno por viaje, «día 1») son un dibujo, no una tasa real.

## Escenas
1. Celular al 4 % y barra del día cortada en la tarde (gancho) → rebobina: nuevo, llega a la noche → «2 años después» se apaga en la tarde → «?».
2. Corte de la batería: los puntos de litio van a la izquierda al cargar y vuelven al usar; el ir y venir es la energía.
3. En cada viaje uno queda atrapado en una capa roja junto a la placa: «atrapado», ya no vuelve.
4. La carcasa de la batería se encoge (contorno original punteado): menos capacidad.
5. Termómetro y batería al 100 % con reloj: la capa crece más rápido.
6. Batería grande: marca del 80 % y contador de 1.000 cargas completas, «en condiciones ideales».
7. Celular con el interruptor «Límite 80 %»: carga y se detiene; «100 %» tachado.
8. Vuelta al corte («día 1, 2…») y al celular enchufado de noche: «¿la dejas cargando toda la noche?».

## Control de calidad
- ffprobe: h264 1080×1920 60 fps, AAC 48 kHz estéreo, 59,83 s. Loudness −14,5 LUFS, pico verdadero −3,0 dBTP.
- Narración: 178 palabras en 59,8 s (≈ 3,0 palabras/s), cifras con `rate=SLOW`, preguntas con `pitch=Q`. Subtítulos alineados por palabra (sin Whisper). No pude escuchar el audio: se verificó con métricas.

## Texto para publicar
**YouTube (título):** ¿Por qué tu batería dura menos cada año? 🔋 #shorts

**Texto:**
Tu celular nuevo llegaba a la noche… y dos años después no llega ni a la tarde. ¿Qué le pasó? 🔋

En cada carga, un poquito de litio queda atrapado en una capa dentro de la batería y deja de trabajar. El calor y pasar muchas horas al 100 % aceleran ese desgaste. Apple diseña los iPhone 15 y posteriores para conservar el 80 % de su capacidad tras 1.000 cargas completas (en condiciones ideales).

¿Tú la dejas cargando toda la noche? 👇
Guárdalo para no olvidarlo.

Fuentes: Apple (Battery Service, soporte «Charge and maintain your iPhone battery» y «Charge Limit»); NREL; Mikheenkova et al., J. Electrochem. Soc. (2023).
Animación original de stheq.ia (sin fotos).

#stheqia #bateria #celular #tecnologia #iphone #android #litio #datoscuriosos
