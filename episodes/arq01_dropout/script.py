"""Guion — «¿Por qué apagar neuronas hace más lista a una red?» (metadato; no se muestra en el video)

Cadena causal:
  hook        el estudiante que memoriza las pruebas: perfecto en la práctica, mal en la real
  puente      a las redes neuronales les pasa lo mismo; una solución: apagar neuronas al azar (paradoja)
  datos       una red predice si llueve con humedad y presión; cada punto = un día (simulado);
              algunos días son raros (llovió sin aviso)
  memoriza    una red grande acierta todos los días conocidos dibujando islas alrededor de cada
              día raro → con días nuevos acierta menos → «sobreajuste»
  porque      es tan flexible que aprende hasta el ruido; algunas neuronas se especializan en
              casos puntuales y las demás se apoyan en ellas
  dropout     en cada paso de entrenamiento se apaga al azar la mitad → nadie puede depender de
              otra → cada una aprende algo útil (equipo donde cualquiera puede faltar) → «dropout»
  resultado   al usar la red se encienden todas; frontera más simple; algo peor en lo conocido,
              mejor en lo nuevo (experimento propio, varias semillas)
  cierre      no se trata de memorizar las pruebas, sino de entender la materia (vuelve al hook)
"""
from reelforge.timeline import Beat, Ph

EPISODE = {
    "num": 1,
    "slug": "arq01_dropout",
    "title": "¿Por qué apagar neuronas hace más lista a una red?",
    "tag": "",          # sin banners ni títulos dentro del video (regla permanente)
}

Q = "+5Hz"
SLOW = "-4%"

BEATS = [
    Beat("hook", [
        Ph("Un estudiante se aprende de memoria todas las pruebas anteriores.", pause=0.25),
        Ph("En la práctica, saca nota *perfecta*.", pause=0.3),
        Ph("En la prueba real... *reprueba*.", pause=0.5),
    ]),
    Beat("puente", [
        Ph("A las redes neuronales les pasa exactamente lo mismo.", pause=0.2),
        Ph("Y una de las soluciones suena absurda: *apagar* neuronas al azar.", pause=0.5),
    ]),
    Beat("datos", [
        Ph("Pongamos a una red a predecir si va a *llover*, mirando la humedad y la presión del aire.", pause=0.25),
        Ph("Cada punto es un día del pasado: celeste si llovió, violeta si no.", pause=0.25),
        Ph("Pero hay días *raros*: llovió cuando nada lo anunciaba.", pause=0.45),
    ]),
    Beat("memoriza", [
        Ph("Una red grande puede acertar *casi todos* los días que ya vio.", pause=0.15),
        Ph("¿Cómo? Dibujando *islas* alrededor de cada día raro: los memoriza.", pause=0.35),
        Ph("Pero cuando llegan días *nuevos*, se equivoca más.", pause=0.3),
        Ph("Casi perfecta en la práctica, peor en la prueba real. Se llama *sobreajuste*.", pause=0.5),
    ]),
    Beat("porque", [
        Ph("¿Por qué pasa?", pause=0.2, pitch=Q),
        Ph("Porque la red es tan flexible que puede aprender hasta el *ruido*.", pause=0.25),
        Ph("Algunas neuronas se especializan en recordar casos puntuales... y las demás se *apoyan* en ellas.", pause=0.45),
    ]),
    Beat("dropout", [
        Ph("La idea: mientras entrena, en cada paso, *apagamos* al azar la mitad de las neuronas.", pause=0.3),
        Ph("Ninguna puede contar con que otra esté ahí...", pause=0.1),
        Ph("así que cada una tiene que aprender algo *útil* por sí misma.", pause=0.3),
        Ph("Como un equipo donde cualquiera puede faltar: todos tienen que entender el trabajo.", pause=0.3),
        Ph("Se llama *dropout*.", pause=0.5, rate=SLOW),
    ]),
    Beat("resultado", [
        Ph("Al usar la red, se encienden todas.", pause=0.2),
        Ph("Y la frontera queda más *simple*: ya no persigue a cada día raro.", pause=0.3),
        Ph("Acierta un poco menos en los días conocidos... pero *más* en los días nuevos.", pause=0.5),
    ]),
    Beat("cierre", [
        Ph("Igual que con el estudiante:", pause=0.15),
        Ph("no se trata de memorizar las pruebas... sino de *entender* la materia.", pause=0.3, rate=SLOW),
    ]),
]
