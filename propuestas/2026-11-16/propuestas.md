# Propuestas del 16-nov-2026

Fuente: `python tools/tendencias.py --dias 30 --amplio --min-vistas 300000` (videos de IA más vistos de los últimos 30 días).
Storyboards: `storyboard_A.png`, `storyboard_B.png`, `storyboard_C.png` (o `storyboard_todas.png`).

---

## A · «El profe te acusa de usar IA» (~50 s)

- **Inspiración:** «Quando o professor também usa IA», 5,6 M de vistas (humor de sala de clases).
- **Clase:** Bayes, tasa base y falsas alarmas.
- **Por qué puede pegar:** todos los estudiantes temen que los acusen injustamente; tiene humor y deja una lección.

| Bloque | Narración | Imagen |
|---|---|---|
| Hook | «Entregas tu tarea… y el detector dice: noventa y ocho por ciento escrita por IA.» | Hoja con sello rosado «98 % IA», profe mirando |
| Giro | «Pero la escribiste tú. Palabra por palabra.» | Alumno con «…», visto bueno «la escribiste tú» |
| Pregunta | «¿Cómo se equivoca algo tan seguro?» | El sello tiembla |
| Contexto | «Imagina un curso de treinta. Solo tres usaron IA.» | Grilla de 30 estudiantes, 3 violeta |
| Detector | «El detector pilla a los tres… pero también marca a tres que no la usaron.» | Anillos rosados sobre 6 estudiantes |
| Revelación | «De seis acusados… la mitad era inocente.» | Los 6 en fila: 3 «IA», 3 «inocente» |
| Explicación | «Cuando casi nadie hace trampa, hasta un detector bueno acusa a muchos inocentes. Eso lo calcula la regla de Bayes.» | Las 27 honestas se iluminan: grupo enorme vs. 3 |
| Cierre | «Así que si el detector te acusa… pide que te pregunten por tu tarea. No por su porcentaje.» | Vuelve la hoja; el sello se cae |

Nota: los números (30, 3, 6) son un ejemplo («imagina…»), no la tasa de error de un detector real.

---

## B · «La pregunta trampa que hace fallar a la IA» (~45 s)

- **Inspiración:** «I Ask The Tricky Questions from ChatGPT», 28,5 M de vistas.
- **Clase:** modelos de lenguaje, vocabulario y embeddings (la IA trabaja con pedazos de texto convertidos en números).
- **Por qué puede pegar:** el espectador puede probarlo en su propio celular y comentar el resultado.

| Bloque | Narración | Imagen |
|---|---|---|
| Hook | «Esta IA escribe ensayos, programa y aprueba exámenes… pero esta pregunta la hace dudar.» | Chat: «¿Cuántas R tiene ferrocarril?» → respuesta dudosa ✗ |
| Pregunta | «¿Por qué fallaría en algo tan fácil?» | Zoom a la palabra |
| Tú | «Tú ves once letras… y cuentas cuatro R.» | Las letras se iluminan; las R en cyan |
| IA | «Pero muchas IA no leen letras: leen pedazos de palabras.» | La palabra se parte en «ferro · carr · il» |
| Números | «Y cada pedazo se convierte en una lista de números. Ahí, las letras ya no están.» | Cada pedazo se transforma en columnas de números |
| Revelación | «Le pides contar algo que nunca vio.» | Los números flotan; un «?» sobre las R |
| Truco | «¿El truco? Pídele que la deletree primero.» | F-E-R-R-O-C-A-R-R-I-L → «4 R ✓» |
| Cierre | «Pruébalo y cuéntame qué te respondió.» | Vuelve al chat inicial |

Nota: cómo se corta cada palabra depende del modelo; el corte «ferro·carr·il» es un ejemplo y la narración lo dice con «pedazos». No se afirma que un modelo específico falle siempre.

---

## C · «El robot que se cayó cientos de veces» (~50 s)

- **Inspiración:** «NVIDIA’s Cute AI Ducks Can Do Somersaults», 7,4 M, y «When Jensen asks for a somersault», 5,3 M.
- **Clase:** aprender de los errores: pérdida y ajuste de parámetros (descenso de gradiente).
- **Por qué puede pegar:** robots tiernos, fracasos graciosos y un logro final satisfactorio.
- **Simulación real** (`sim_salto.py`): un robot ajusta la fuerza y el ángulo de su salto. El error baja de 17,4 a casi 0 en 60 intentos.

| Bloque | Narración | Imagen |
|---|---|---|
| Hook | «Este robot quiere subir a la plataforma… y se cae. Otra vez. Y otra vez.» | Saltos fallidos en rosado, el robot rebota |
| Pregunta | «Nadie le enseña a saltar. ¿Cómo aprende?» | El robot mira la plataforma |
| Error | «Cada caída deja una pista: cuánto le faltó, y hacia dónde.» | Flecha de distancia entre el aterrizaje y la plataforma |
| Ajuste | «Con esa pista mueve dos perillas, fuerza y ángulo… solo un poquito.» | Perillas que giran un poco |
| Repetir | «Intento tras intento, el error baja.» | Trayectorias que se acercan y curva de error que cae |
| Revelación | «Hasta que… lo logra.» | Salto perfecto en cyan, aterrizaje con rebote |
| Explicación | «Así aprenden también las redes neuronales: medir el error, ajustar un poquito y repetir.» | Las perillas se multiplican en miles |
| Cierre | «Los robots que ves haciendo piruetas se cayeron muchísimas veces antes. Solo que en una simulación.» | Vuelve el primer salto, ahora perfecto |

Nota: el robot del video es una simulación simple con dos perillas. Los robots reales aprenden en simulaciones con millones de intentos y técnicas más avanzadas; la narración lo dice sin cifras.
