# tec08 · ¿Cómo pasa la energía por el aire? (carga inalámbrica)

Reel animado (motion graphics por código), 58,7 s, 1080×1920, 60 fps. Categoría: **día a día**. Elegido en `propuestas/2026-11-27/propuestas.md` (45 puntos).

## Fuentes
- **Wireless Power Consortium, «How Qi works»**: https://www.wirelesspowerconsortium.com/knowledge-base/magnetic-induction/how-qi-works/ — «An alternating current in the transmitter coil generates a magnetic field which induces a voltage in the receiver coil»; el teléfono debe poder apagar el transmisor cuando la batería está llena y para eso «needs to send control signals to the charging station».
- **Belkin, «What is Qi2 wireless charging»**: https://www.belkin.com/us/clp-what-is-qi2-wireless-charging-blog.html — Magnetic Power Profile (basado en MagSafe): imanes que alinean el teléfono; en Qi estándar la eficiencia «varies based on alignment».
- **IEC 63563-7:2025 (Qi v2.0, parte 7: Foreign Object Detection)**: https://standards.iteh.ai/catalog/standards/iec/2aebf0ed-d5ee-4986-93cb-af6beec820d2/iec-63563-7-2025 — métodos para transferir energía «without heating metal objects in the magnetic field» (monedas, llaves). Se investigó pero la escena de la moneda se recortó por duración.
- Física básica (ley de Faraday de la inducción): un campo magnético que cambia dentro de una bobina induce corriente; un imán que entra y sale de una bobina mueve la aguja de un medidor.

## Escenas
1. Gancho (vista desde arriba): el celular flota sobre la base, cae al decir «encima», aparece el rayo; el cable se tacha y aparece «?».
2. Corte lateral: base y celular con una bobina de cobre cada una (puntos); línea roja: no se tocan.
3. Un cable de metal une las bobinas por el costado con corriente; se disuelve: «aire» y «?».
4. Bobina con medidor: un imán entra y sale y la aguja salta → «corriente».
5. La corriente de la base cambia de sentido (⊙/⊗); las líneas de campo crecen, se apagan y se invierten; un imán fantasma sube y baja al mismo ritmo.
6. Las líneas llegan a la bobina del celular, aparece corriente hacia la batería: «inducción magnética».
7. El celular se corre: la batería carga «lento»; aparecen imanes y lo centran.
8. Paquetes de aviso del celular a la base; batería al 100 % y el campo se apaga.
9. Cierre: vista desde arriba con ondas que van y vienen; el celular vuelve a flotar (empalme con el cuadro 0).

## Simplificaciones
- El espacio entre las bobinas está exagerado; en la realidad las separan milímetros de carcasa.
- Las líneas de campo son un dibujo cualitativo; la oscilación real es mucho más rápida (se dice «sin parar», sin cifra).
- «Carga lento si queda corrido»: menos acoplamiento → menos potencia útil; la cifra exacta depende del cargador y no se da.
- Los imanes de alineación corresponden a Qi2 / MagSafe; no todos los cargadores los tienen («los cargadores nuevos»).
- El aviso del celular a la base se dibuja como paquetes; el protocolo real (modulación de carga) no se detalla.

## Control de calidad
- ffprobe: h264 1080×1920 60 fps, AAC 48 kHz, 58,7 s. −14,5 LUFS, pico −3,0 dBTP.
- Ritmo: ≈ 150 palabras en 58,7 s. No puedo escuchar el audio: verificado con métricas.

## Texto para publicar
¿Cómo pasa la energía por el aire? ⚡📱
En la base y en tu celular hay dos bobinas de cobre que no se tocan. La corriente de la base cambia de sentido sin parar y crea un campo magnético que va y viene; al atravesar la bobina del celular, crea corriente: inducción magnética (Wireless Power Consortium, estándar Qi). Por eso, si queda corrido, carga más lento, y los cargadores nuevos traen imanes que lo centran.
¿Tú cargas con o sin cable? 👇
Guárdalo para no olvidarlo.
Fuentes: Wireless Power Consortium, «How Qi works»; Belkin, «What is Qi2».
#stheqia #cargainalambrica #tecnologia #celulares #ciencia #fisica #qi2
