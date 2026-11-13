"""Detrás del Algoritmo — EP01: ¿Por qué tu banco bloqueó tu café?

Ejemplo hipotético simplificado para enseñar Bayes.
No representa estadísticas reales de un banco.

Cuentas del ejemplo (exactas): 100 compras, 1 fraude, 99 normales.
El detector marca el fraude y se equivoca con 4 normales → 5 alertas → 1 de 5 = 20 %.
Antes de la alerta: 1 de 100 (tasa base). Después: 1 de 5.
"""

from reelforge.timeline import Beat, Ph

EPISODE = {
    "num": 1,
    "slug": "inc01_compra_bloqueada",
    "title": "¿Por qué tu banco bloqueó tu café?",
    "tag": "DETRÁS DEL ALGORITMO · EP 01",
}

Q = "+5Hz"

BEATS = [
    Beat("hook", [
        Ph("Estás de vacaciones. Entras a una cafetería, pides un café...", pause=0.2),
        Ph("pero cuando intentas pagar, tu banco *bloquea* la tarjeta.", pause=0.5),
        Ph("¿Por qué cree que alguien te está *robando*?", pause=0.5, pitch=Q),
    ]),

    Beat("contexto", [
        Ph("Tu banco utiliza sistemas que buscan compras *sospechosas*.", pause=0.2),
        Ph("Por ejemplo, pagar de repente en *otro país* puede parecer extraño.", pause=0.3),
        Ph("Pero una compra sospechosa no significa que sea un *fraude*.", pause=0.5),
    ]),

    Beat("ejemplo", [
        Ph("Imagina que tenemos *cien compras*.", pause=0.3),
        Ph("Noventa y nueve son normales. Y solo *una* es fraudulenta.", pause=0.5),
        Ph("Eso significa que el fraude es muy poco *frecuente*.", pause=0.4),
    ]),

    Beat("detector", [
        Ph("Ahora imaginemos un detector que identifica correctamente ese fraude...", pause=0.2),
        Ph("pero también se equivoca con *cuatro* compras normales.", pause=0.5),
        Ph("En total, marca *cinco* compras como sospechosas.", pause=0.4),
    ]),

    Beat("descubrimiento", [
        Ph("Aquí viene lo interesante.", pause=0.3),
        Ph("De esas cinco compras sospechosas, solo *una* era realmente un fraude.", pause=0.5),
        Ph("Es decir, apenas el *veinte por ciento*.", pause=0.6),
    ]),

    Beat("explicacion", [
        Ph("¿Cómo puede pasar esto?", pause=0.2, pitch=Q),
        Ph("Porque el fraude es tan poco común que incluso unos pocos errores generan muchas *falsas alertas*.", pause=0.5),
        Ph("Y aquí aparece una idea fundamental de la probabilidad.", pause=0.4),
    ]),

    Beat("bayes", [
        Ph("Se llama *regla de Bayes*.", pause=0.3),
        Ph("Y nos ayuda a responder una pregunta:", pause=0.2),
        Ph("Si una compra fue marcada como sospechosa, ¿qué probabilidad hay de que realmente sea un fraude?", pause=0.5, pitch=Q),
        Ph("Para responder, combinamos dos cosas:", pause=0.2),
        Ph("Qué tan *frecuente* es el fraude normalmente...", pause=0.2),
        Ph("y qué tan *confiable* es nuestro detector.", pause=0.4),
    ]),

    Beat("tasa_base", [
        Ph("La primera tiene un nombre: *tasa base*.", pause=0.3),
        Ph("Es simplemente la probabilidad que teníamos *antes* de recibir la alerta.", pause=0.4),
        Ph("En nuestro ejemplo, era una compra fraudulenta de cada cien.", pause=0.4),
        Ph("Después de la alerta, esa probabilidad cambia: ahora es *una de cada cinco*.", pause=0.5),
    ]),

    Beat("cierre", [
        Ph("Por eso, una alerta no es una *prueba* de fraude.", pause=0.3),
        Ph("Es una nueva *pista* que debemos interpretar considerando qué tan raro era el fraude desde el principio.", pause=0.4),
        Ph("Y eso es exactamente lo que nos permite hacer *Bayes*.", pause=0.6),
    ]),
]
