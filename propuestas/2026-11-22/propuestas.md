# Propuestas stheq.ia · 2026-11-22 (domingo)

Tendencias: `tools/tendencias_decalogo.py --dias 30` (mediana top 10: robótica 2,16 M; día a día 2,15 M; autos y movilidad 1,78 M; ciberseguridad 0,65 M; energía 0,49 M; medicina 0,25 M; espacio 0,19 M; IA aplicada 0,15 M) y `tools/tendencias.py --amplio` (top: «Are These People Real or AI?», 42,3 M; «I bought every product from AI scam ads», 13,0 M). Ayer (tec02, frenado regenerativo) fue **autos y movilidad**: hoy no se repite. Domingo: no hay carrusel de noticias. Solo se toma el tema; nunca se copia nada.

Storyboards (`storyboard_A/B/C.png`, script `storyboard.py`): bocetos con el estilo de los reels animados (reelforge, negro/blanco/rojo).

## A · DÍA A DÍA — «¿Por qué la pantalla de tu celular aguanta tanto?»
- Tendencia: «Cuando puedes usar tu celular como martillo 💀» (17,8 M vistas).
- Gancho: un celular contra un martillo. El vidrio común se haría trizas. ¿Por qué este no?
- Tarjetas:
  1. **¿Por qué no se rompe?** — Es vidrio, como el de una ventana. Pero lo golpeas y aguanta. ¿Qué tiene de distinto?
  2. **El vidrio se rompe desde una grieta** — Su superficie tiene grietas diminutas. Cuando algo la estira, la grieta se abre… y avanza.
  3. **Un baño de sal fundida** — Muchas pantallas pasan por un baño de sal a **≈ 400 °C**. Ahí, átomos pequeños de sodio salen del vidrio y entran átomos más grandes de potasio.
  4. **La superficie se aprieta** — Los átomos grandes quedan apretados, como cambiar bolas de pool por pelotas de tenis en el mismo triángulo. La superficie queda comprimida.
  5. **Aprieta las grietas** — Para abrir una grieta, primero hay que vencer ese apretón. Se llama intercambio iónico (vidrio químicamente templado).
  6. **¿Irrompible?** — No: un golpe fuerte o una caída mala lo rompen igual. Respuesta al gancho: aguanta más porque su superficie está comprimida.
- Fuentes: Corning, «How It Works: Strengthening Glass» (https://www.corning.com/worldwide/en/innovation/the-glass-age/science-of-glass/how-it-works-strengthening-glass.html: baño de sal fundida, potasio reemplaza sodio, superficie en compresión, analogía de bolas de pool y pelotas de tenis); Corning Gorilla Glass, «A look behind Corning Gorilla Glass» (https://www.corning.com/gorillaglass/worldwide/en/a-look-behind-corning-gorilla-glass.html: baño ≈ 400 °C).

## B · ROBÓTICA — «¿Cómo sabe tu robot aspiradora dónde está?»
- Tendencia: «Momentos divertidos de robots» (5,3 M) y «¡Llegó un robot inteligente y los pibes lo dominaron!» (4,8 M).
- Gancho: el robot nunca vio tu casa. Lo enciendes… y limpia en franjas ordenadas sin perderse. ¿Cómo sabe dónde está?
- Tarjetas:
  1. **¿Cómo sabe dónde está?** — No tiene GPS dentro de la casa ni conoce tus muebles.
  2. **Un láser que gira** — En muchos modelos, la torrecita de arriba gira **unas 6 veces por segundo** disparando un láser y midiendo la distancia a lo que tiene alrededor.
  3. **Cada rebote, un punto** — Son miles de mediciones por segundo: puntos que dibujan paredes y muebles.
  4. **Mapa y ubicación a la vez** — Mientras se mueve, compara lo que ve con el mapa que lleva hecho para saber dónde está, y con eso corrige el mapa. Se llama SLAM (localización y mapeo simultáneos).
  5. **Por eso limpia en franjas** — Con el mapa sabe qué ya pasó y qué falta. Respuesta al gancho.
- Fuentes: Wyze, soporte «LIDAR sensor» (≈ 6 vueltas/s y 2016 mediciones por vuelta) (https://support.wyze.com/hc/en-us/articles/360050548112-LIDAR-sensor); Dreame, «LiDAR Navigation in Robot Vacuums: How It Works» (≈ 5 vueltas/s) (https://www.dreametech.com/blogs/blog/lidar-navigation-robot-vacuum); TechRadar, «How do robot vacuums navigate?» (SLAM) (https://www.techradar.com/home/robot-vacuums/how-do-robot-vacuums-navigate). Aclaración: no todos los robots usan láser (algunos usan cámara, vSLAM); la cifra de vueltas varía por modelo.

## C · CIBERSEGURIDAD — «El anuncio perfecto… y el paquete que nunca llega»
- Tendencia: «I bought every product from AI scam ads» (13,0 M) e «I Bought AI Scam Products» (7,4 M).
- Gancho: ves un anuncio perfecto, 80 % de descuento. Pagas. Pasan las semanas… y nada. ¿Qué pasó?
- Tarjetas:
  1. **¿Y nunca llegó?** — El anuncio se veía real: fotos lindas, video, oferta increíble.
  2. **Muchas estafas empiezan en redes** — En EE. UU., casi **30 %** de quienes perdieron plata en una estafa dijo que empezó en redes sociales: **US$ 2.100 millones** en 2025 (FTC).
  3. **La más común: comprar** — Más de **4 de cada 10** de esas víctimas compró algo que vio en un anuncio. La mayoría pagó por cosas que nunca llegaron; otras recibieron falsificaciones.
  4. **Sitios que imitan a una marca** — Muchos anuncios llevan a tiendas desconocidas o a copias de marcas famosas con descuentos enormes.
  5. **Antes de pagar** — Revisa la dirección del sitio, busca el nombre de la tienda con «estafa» o «opiniones» y desconfía de los descuentos imposibles. Respuesta al gancho.
- Fuentes: FTC, Data Spotlight «Reported losses to scams on social media are eight times higher than in 2020» (abr-2026) (https://www.ftc.gov/news-events/data-visualizations/data-spotlight/2026/04/reported-losses-scams-social-media-eight-times-higher-2020); FTC, nota de prensa (abr-2026) (https://www.ftc.gov/news-events/news/press-releases/2026/04/new-ftc-data-show-people-have-lost-billions-social-media-scams); TechCrunch (27-abr-2026). Aclaración: son datos reportados en EE. UU.; la FTC advierte que la mayoría de las estafas no se reporta.
