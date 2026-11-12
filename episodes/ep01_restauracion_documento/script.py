"""Guion narrado del Episodio 1 — "El documento ilegible".

Sintaxis: *clave* = resaltado cyan · mostrar|pronunciar (guiones bajos = espacios).
Cada beat es un bloque de narración; las escenas se sincronizan con sus palabras.
"""
from reelforge.timeline import Beat

EPISODE = {
    "num": 1,
    "slug": "ep01_restauracion_documento",
    "title": "El documento ilegible",
    "tag": "EP 01 · REDES DE MARKOV",
    "next": "EP 02 · Redes sin flechas",
}

BEATS = [
    Beat("hook",
         "Al escanear este documento, el *15%|quince_por_ciento* de sus píxeles se invirtió. "
         "Ningún lector automático puede leerlo... pero *una sola idea* lo arregla.",
         pause=0.3),
    Beat("problema",
         "El escáner cambió píxeles al azar: tinta por papel, y papel por tinta. "
         "Mirando *píxel a píxel*, no hay cómo saber cuál está mal.",
         pause=0.25),
    Beat("idea",
         "Pero los *píxeles vecinos* tienden a compartir color. "
         "Un punto negro aislado, en medio del papel, casi seguro es *ruido*.",
         pause=0.25),
    Beat("grafo",
         "Esa relación no tiene dirección: ningún píxel *causa* al otro. "
         "Así que usamos un *grafo no dirigido*, una *red de Markov*: "
         "cada píxel unido a sus cuatro vecinos, y a lo que vio el escáner.",
         pause=0.25),
    Beat("voces",
         "Cada píxel escucha dos voces: el *sensor*, con peso *α|alfa*, "
         "y sus *vecinos*, con peso *β|beta*. "
         "Si la suma es positiva, es tinta. Si es negativa, papel.",
         pause=0.25),
    Beat("ejemplo",
         "Nuestro punto aislado: el sensor dice tinta, *+0,87|más_cero_coma_ochenta_y_siete*. "
         "Sus cuatro vecinos dicen papel: *−4,8|menos_cuatro_coma_ocho*. "
         "Gana el papel... y el ruido desaparece.",
         pause=0.25),
    Beat("iterar",
         "Aplicamos la regla a todos los píxeles, y repetimos. "
         "Pasada tras pasada, el ruido se disuelve. "
         "Es la idea de *ICM*: modos condicionales iterados.",
         pause=0.3),
    Beat("resultado",
         "En la clase, el error bajó del *15%|quince* al *2,5%|dos_coma_cinco_por_ciento*, "
         "y el lector pasó de reconocer el *42%|cuarenta_y_dos* al *94%|noventa_y_cuatro_por_ciento* de los caracteres.",
         pause=0.25),
    Beat("recreacion",
         "En mi recreación en Python: error de *2,6%|dos_coma_seis_por_ciento*, "
         "y el lector pasó de nada... a un *91%|noventa_y_uno_por_ciento*.",
         pause=0.25),
    Beat("bordes",
         "La mayoría de los errores que quedan están en los *bordes* de las letras, "
         "donde las dos voces compiten.",
         pause=0.25),
    Beat("cierre",
         "La misma idea delimita tumores en resonancias, o clasifica suelos desde satélites. "
         "Próximo episodio: por qué aquí *no sirven* las flechas de una red bayesiana.",
         pause=0.2),
]
