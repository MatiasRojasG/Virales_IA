# tec07 · ¿Cuánto tarda alguien en adivinar tu contraseña?

Reel animado (motion graphics por código), 55,9 s, 1080×1920, 60 fps. Categoría: **ciberseguridad**. Elegido en `propuestas/2026-11-26/propuestas.md` (46 puntos).

## Fuentes
- **Hive Systems, «The 2026 Password Table»** (14-jul-2026): https://www.hivesystems.com/blog/are-your-passwords-in-the-green — 16 × RTX 5090 arrendadas contra bcrypt (costo 10), 138.675 intentos/s en total; 8 caracteres al azar solo minúsculas ≈ 2 semanas; 8 caracteres al azar con números, mayúsculas, minúsculas y símbolos = 132 años (tiempo máximo de fuerza bruta). Las claves comunes, filtradas o reutilizadas «can fall instantly» (en su prueba, unos 3 s). Recomienda pasar de 8 caracteres y que un gestor genere claves largas y al azar; «a long passphrase beats a short, clever-looking one every time».
- Comunicado PR Newswire y Carrier Management (14-jul-2026), que repiten las cifras.
- **Aritmética propia:** 26⁸ = 208.827.064.576 y 95⁸ = 6.634.204.312.890.625 combinaciones (cada carácter multiplica por 26 o por ≈ 95).

## Escenas
1. Gancho: 8 casillas con puntos; giran como tragamonedas y se dispara un contador de intentos.
2. Inicio de sesión: tres intentos fallidos y candado.
3. Servidor → lista de claves robada; las claves se vuelven «huellas» (hash bcrypt) y la flecha de vuelta se tacha.
4. Máquina de huellas: claves inventadas, huella, comparación con la robada hasta que coincide.
5. Tarjeta de video con ventiladores y contador +100.000 claves/s.
6. Barras de tiempo: 8 minúsculas ≈ 2 semanas; 8 mezclados 132 años (la barra se sale).
7. Casillas que se encienden: ×26 por carácter y luego ×95.
8. Lista de claves filtradas que corre y se detiene en «camila2024».
9. Cierre: la clave «rara» se tacha, frase larga al azar, vuelta a las 8 casillas (empalme).

## Simplificaciones
- «Huella» = hash; se omite la sal (bcrypt sala automáticamente) y el costo.
- Los tiempos son de Hive Systems para claves generadas al azar y sin filtrar, con su equipo; con otro hardware o algoritmo cambian.
- Las claves, nombres y hashes en pantalla son inventados (los hashes no son reales).
- No se presenta la relación entre 2 semanas y 132 años como cociente de combinaciones (Hive no publica cada supuesto); las combinaciones se muestran solo como explicación de por qué crece.

## Control de calidad
- ffprobe: h264 1080×1920 60 fps, AAC 48 kHz, 55,9 s. −14,5 LUFS, pico −2,7 dBTP.
- Ritmo: 152 palabras en 55,9 s (≈ 2,7 pal/s con pausas). No puedo escuchar el audio: verificado con métricas.

## Texto para publicar
¿Cuánto tarda alguien en adivinar tu contraseña? 🔐

No la prueban en la página: roban la lista de claves de un sitio, guardadas como «huellas», y prueban millones de combinaciones con tarjetas de video. Según la tabla 2026 de Hive Systems, 8 minúsculas al azar caen en ≈ 2 semanas; 8 caracteres mezclados, 132 años. Pero si tu clave es predecible o ya se filtró, cae en segundos.

¿Cuántos caracteres tiene la tuya? 👇
Guárdalo para no olvidarlo.

Fuente: Hive Systems, «The 2026 Password Table» (14-jul-2026).
#stheqia #ciberseguridad #contraseñas #seguridadinformatica #tecnologia #hackers #privacidad
