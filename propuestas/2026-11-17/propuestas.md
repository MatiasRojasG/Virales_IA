# Propuestas del 17-nov-2026

Fuentes de tendencia: vidIQ (outliers Instagram/TikTok en español, últimas 48 h; 20 videos revisados) y noticias de IA (aiweekly.co, 14-nov). `tools/tendencias.py` no pudo consultar la API de YouTube (403 desde el entorno) y vidIQ trending no tenía créditos.
Estilo: blanco y negro, alto contraste, Inter grande. Storyboards: `storyboard_A/B/C.png`.

---

## A · «La IA no arregla tu foto: la inventa» (~50 s)

- **Inspiración:** reel de Instagram «¿Tienes fotos pixeladas? No las borres» (ChatGPT las pasa a 4K), 474,7 K vistas en 2 días (29× la mediana del creador).
- **Concepto:** súper-resolución generativa: la IA no recupera píxeles perdidos, genera la cara *más probable* según lo que vio al entrenar.
- **Caso real:** PULSE (Duke, 2020): una foto pixelada de Barack Obama devolvía la cara de un hombre blanco (The Verge, 2020).
- **Qué aprende el espectador:** una foto «mejorada» por IA no es evidencia; los detalles nuevos son inventados.

| Bloque | Narración | Imagen |
|---|---|---|
| Hook | «¿Esta cara es real… o la inventó una IA?» | Cara pixelada de 16 px |
| Promesa | «Hoy cualquier app convierte una foto pixelada en 4K.» | Bloques que se suavizan en una cara nítida |
| Problema | «Pero en esos cuadrados no queda información: muchas caras distintas se ven igual de pixeladas.» | La misma miniatura → 3 caras distintas |
| Intuición | «La IA no recupera la tuya: dibuja la más probable según las fotos con que aprendió.» | Mosaico de caras de entrenamiento que se funden |
| Caso | «En 2020, PULSE recibió una foto pixelada de Obama… y devolvió a un hombre blanco.» | 2020 · PULSE (siluetas, sin fotos reales) |
| Consecuencia | «Por eso una foto “mejorada” no sirve como prueba.» | Lupa sobre detalle inventado |
| Cierre loop | «Entonces… ¿esta cara es real?» | Vuelve a la cara pixelada |

---

## B · «¿Por qué se nota cuando lo escribió una IA?» (~50 s)

- **Inspiración:** reel de Instagram «Se nota cuando algo lo escribió la IA, ¿no? Se siente raro», 178,4 K vistas (387× la mediana); en Brasil, «Cómo humanizar textos en Claude», 236 K (IG) + 130 K (TikTok).
- **Concepto:** modelos de lenguaje que predicen la siguiente palabra y tienden a elegir las más probables → texto «promedio».
- **Dato real:** el uso de «delve» en resúmenes de PubMed se disparó desde 2023 (Kobak et al., *Science Advances*, 2025).
- **Qué aprende:** por qué el texto de IA suena genérico y cómo reconocerlo.

| Bloque | Narración | Imagen |
|---|---|---|
| Hook | «Lo lees… y sabes que lo escribió una IA. ¿Por qué se nota?» | Párrafo genérico |
| Mecanismo | «La IA escribe palabra por palabra, eligiendo la que más probable viene.» | Barras de probabilidad |
| Efecto | «Lo seguro gana siempre: suena al promedio de millones de textos.» | Grilla de puntos iguales |
| Dato | «Una palabra en inglés, “delve”, se disparó en artículos científicos tras ChatGPT.» | Curva que sube |
| Cierre loop | «Entonces… ¿se nota?» | Vuelve al párrafo |

---

## C · «La IA que descartaba currículums de mujeres» (~55 s)

- **Inspiración:** TikTok «Llevaba dos meses buscando empleo… nadie la llamaba» (@unitel.bo), 511 K vistas en 2 días.
- **Concepto:** sesgo en los datos de entrenamiento: un modelo aprende patrones del pasado, incluidos los injustos.
- **Caso real:** Amazon entrenó (2014–2017) un sistema con 10 años de CV, mayoritariamente de hombres; penalizaba la palabra «women's» y lo abandonó (Reuters, 2018).
- **Qué aprende:** la IA no inventa el sesgo: lo copia de los datos.

| Bloque | Narración | Imagen |
|---|---|---|
| Hook | «¿Y si tu currículum nunca lo leyó una persona?» | CV tachado |
| Contexto | «En 2014, Amazon creó una IA para elegir a los mejores candidatos.» | Pila de CV |
| Datos | «La entrenó con los currículums de diez años… casi todos de hombres.» | CV que se agrupan |
| Revelación | «Aprendió que “mujer” era mala señal: bajaba el puntaje de “capitana del club de ajedrez femenino”.» | Palabra resaltada, puntaje cae |
| Final | «Amazon la abandonó. La IA no inventó el sesgo: lo copió.» | Texto grande |
| Cierre loop | «Entonces… ¿quién leyó tu CV?» | Vuelve al CV |
