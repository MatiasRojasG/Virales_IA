"""Guion de un episodio nuevo. Copia esta carpeta: cp -r episodes/_plantilla episodes/ep02_redes_sin_flechas
Sintaxis: *clave* = cyan en subtítulos · mostrar|pronunciar (guiones bajos = espacios)."""
from reelforge.timeline import Beat

EPISODE = {
    "num": 2,
    "slug": "ep02_redes_sin_flechas",
    "title": "Redes sin flechas",
    "tag": "EP 02 · REDES DE MARKOV",
    "next": "EP 03 · Cuatro estudiantes",
}

BEATS = [
    Beat("hook", "Dos píxeles vecinos tienen el mismo color. ¿Cuál *causa* al otro?"),
    Beat("idea", "Ninguno. La relación es *simétrica*, y por eso necesitamos aristas sin dirección."),
]
