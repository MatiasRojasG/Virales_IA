# Incertidumbre · EP 01 — ¿Por qué tu banco bloqueó tu café?

**Video:** `output/inc01_compra_bloqueada.mp4`: 1080×1920, 60 fps, H.264 + AAC, **90,7 s**, −15,2 LUFS, pico −1 dBFS.
Se verificó lo siguiente:
- No hay saltos de un solo cuadro.
- Los subtítulos van 60 ms antes de la voz.
- El 95 % de la voz cae dentro de las palabras marcadas.
- El último cuadro empalma con el primero.

Clase base: *Incertidumbre, independencia condicional y el lenguaje de los grafos* (EPG4003, 22-oct).

## Serie propuesta

| # | Título | Hook | Concepto que lo resuelve |
|---|---|---|---|
| 01 | **¿Por qué tu banco bloqueó tu café?** ✅ | «Compra bloqueada» en pleno viaje | Probabilidad condicional, Bayes, tasa base, falsas alarmas, sumar evidencia |
| 02 | La alarma que se dispara sola | Sonó la alarma y no hubo ruido eléctrico | Observar el efecto común vuelve dependientes a sus causas |
| 03 | ¿Llovió o fue el aspersor? | Pasto mojado en una ciudad seca | Independencia condicional vs. independencia |
| 04 | Helados y ahogados | Las dos cifras suben juntas | Asociación ≠ causalidad; correlación cero ≠ independencia |
| 05 | ¿Cuánto vas a esperar el bus? | Dos paraderos con la misma espera promedio | Variable aleatoria, esperanza, varianza |
| 06 | El médico que no necesita saber la estación | 63 números contra 17 | Conjunta, marginal y condicional; factorización con un DAG |
| 07 | El mapa de qué informa a qué | Una planta con cientos de sensores | Grafos dirigidos y no dirigidos, caminos, cliques |

## Cadena causal del EP 01

| Pregunta que deja la escena | Respuesta | Concepto |
|---|---|---|
| ¿Cómo se equivocó un sistema tan sofisticado? | Un detector que atrapa 99 de cada 100 fraudes y se equivoca con 5 de cada 100 compras normales: «si me marcó, casi seguro era fraude» | Sensibilidad y tasa de falsos positivos |
| ¿Y qué falta? | ¿Qué tan común es el fraude? | Probabilidad a priori |
| ¿Cómo se ve con números? | 1.000 compras y 10 fraudes. Suenan las 10 y unas 49 normales | Probabilidad total |
| ¿Cuántas alarmas son reales? | 10 de 59: una de cada seis | P(fraude ∣ alarma) ≈ 16,7 % |
| ¿Por qué? | Un error pequeño sobre un grupo enorme supera a los aciertos sobre un grupo chico | Tasa base |
| ¿Tiene nombre? | Regla de Bayes, armada con los mismos puntos (arriba los fraudes, abajo todas las alarmas) | P(A∣B) = P(B∣A)P(A)/P(B) |
| ¿Cómo se decide bien? | Sumando evidencia: el 1/6 es el nuevo punto de partida y una segunda señal lleva a ≈ 80 % | Actualización bayesiana con independencia condicional |
| ¿Dónde más? | Exámenes médicos y alarmas de fábrica | Mismo cálculo (diap. 9) |
| Cierre | «No es que el detector sea malo. Es que el fraude es raro.» | Responde el hook |

## Validación (antes de renderizar)

1. **¿Interesa sin estudiar IA?** Sí. A casi todos les han bloqueado o alertado una compra.
2. **¿El problema va antes que la explicación?** Sí. Bayes aparece recién a los 49 s.
3. **¿Cada concepto surge por una necesidad narrativa?** Sí:
   - La tasa base aparece cuando la intuición falla.
   - Bayes aparece al nombrar la cuenta ya hecha.
   - La segunda señal aparece cuando hay que decidir mejor.
4. **¿Las ideas se conectan sin saltos?** Sí. Ver la tabla anterior.
5. **¿La imagen muestra lo que dice la voz?** Sí:
   - Los 1.000 puntos son las compras.
   - Las alarmas son anillos sobre esos mismos puntos.
   - La fracción de Bayes se arma moviendo esos puntos.
   - El medidor de arriba registra la respuesta: «casi seguro», luego 1/6 y luego ≈ 8/10.
6. **¿La conclusión resuelve la pregunta inicial?** Sí. El cierre vuelve al celular bloqueado.
7. **¿Se mantiene la precisión?** Sí:
   - **Números de la diapositiva 9.**
     - P(fraude) = 0,01, P(alarma ∣ fraude) = 0,99 y P(alarma ∣ normal) = 0,05.
     - De ahí, P(alarma) = 0,0594 y P(fraude ∣ alarma) = 0,1667.
     - En pantalla se rotulan como **«Ejemplo ilustrativo con números redondos (no son datos de un banco real)»**.
   - **Valores esperados en los puntos.** Las 49 alarmas falsas son 49,5 en valor esperado. Las 2,5 que vuelven a sonar se dibujan como 2 puntos llenos y 1 a media opacidad.
   - **Segunda señal.** El ≈ 80 % (79,8 %) supone que ambas señales se equivocan de forma independiente, condicionado al tipo de compra. Eso se dice en pantalla y prepara el EP 03.

## Publicación

**Título:** ¿Por qué tu banco bloqueó tu café? ☕💳

**Descripción:**
> Estás de viaje, pagas un café… y tu tarjeta queda bloqueada. ¿Cómo se equivoca un sistema que «acierta casi siempre»?
> La respuesta está en un dato que casi nadie pregunta: qué tan raro es el fraude. Con mil compras lo ves en segundos… y de paso entiendes la regla de Bayes sin una sola fórmula al principio.
> ¿Te ha pasado? Cuéntame en los comentarios 👇
> (Ejemplo ilustrativo con números redondos; no describe a un banco en particular.)
> #DetrásDelAlgoritmo #Probabilidad #Bayes #Matemáticas #Ciencia #Finanzas #IA #AprendeEnTikTok

**Portada:** `output/portada.png`
