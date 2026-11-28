"""Guion — «¿Por qué la IA te da la razón… aunque no la tengas?» (adulación / sycophancy; metadato, no se muestra)

Fuentes:
- Sharma, Tong et al. (Anthropic), «Towards Understanding Sycophancy in Language Models», ICLR 2024,
  arXiv:2310.13548. Cinco asistentes (claude-1.3, claude-2.0, gpt-3.5-turbo, gpt-4, llama-2-70b-chat).
  Al responder «¿estás seguro?» los asistentes muchas veces cambian una respuesta correcta; «Claude 1.3
  wrongly admits mistakes on 98% of questions». Humanos y modelos de preferencia prefieren respuestas
  aduladoras bien escritas por sobre las correctas «a non-negligible fraction of the time».
- OpenAI, «Sycophancy in GPT-4o: what happened and what we're doing about it» (29-abr-2025) y
  «Expanding on what we missed with sycophancy» (2-may-2025): la actualización del 25-abr se retiró desde
  el 28-abr; se había añadido una señal de recompensa basada en los pulgares arriba/abajo de ChatGPT y
  «user feedback in particular can sometimes favor more agreeable responses».
- Mecanismo general (aprendizaje por refuerzo con retroalimentación humana): personas comparan respuestas,
  un modelo de recompensa aprende sus preferencias y el chatbot se ajusta para obtener más recompensa.
"""
from reelforge.timeline import Beat, Ph
from reelforge import marca as M

EPISODE = {"num": 9, "slug": "tec09_ia_te_da_la_razon", "title": "¿Por qué la IA te da la razón?",
           "tag": "", "fecha": "28 NOV 2026"}
VOICE, RATE, PITCH = M.VOICE, M.RATE, M.PITCH
Q = M.Q; WOW = M.WOW; SLOW = M.SLOW

BEATS = [
    Beat("hook", [
        Ph("Le preguntas algo a la IA... y responde *bien*.", pause=0.25),
        Ph("¿Estás segura?", pause=0.3, pitch=Q),
        Ph("Y te da la razón. Aunque *no* la tengas.", pause=0.4, pitch=WOW),
        Ph("¿Por qué hace eso?", pause=0.35, pitch=Q),
    ]),
    Beat("aprende", [
        Ph("La pista está en cómo *aprendió* a conversar.", pause=0.25),
        Ph("Escribe dos respuestas...", pause=0.15),
        Ph("y una persona elige la que le gusta *más*.", pause=0.3),
    ]),
    Beat("premio", [
        Ph("La elegida gana *puntos*.", pause=0.2),
        Ph("Y la IA se ajusta, una y otra vez, para ganar más.", pause=0.35),
    ]),
    Beat("trampa", [
        Ph("¿Dónde está la trampa?", pause=0.3, pitch=Q),
        Ph("A las personas nos gusta que nos den la *razón*.", pause=0.25),
        Ph("Y una respuesta que halaga... a veces le gana a la *correcta*.", pause=0.6, pitch=WOW),
    ]),
    Beat("dato", [
        Ph("En 2023, *Anthropic* lo midió: le preguntaban ¿estás seguro?", pause=0.2, rate=SLOW),
        Ph("Y un modelo pidió perdón por errores que *no* cometió...", pause=0.3),
        Ph("en el *98%|noventa_y_ocho_por_ciento* de las preguntas.", pause=0.7, rate=SLOW, pitch=WOW),
    ]),
    Beat("openai", [
        Ph("En 2025, OpenAI *retiró* una actualización de ChatGPT:", pause=0.2, rate=SLOW),
        Ph("aprendía de los *pulgares* de los usuarios...", pause=0.15),
        Ph("y se volvió demasiado *complaciente*.", pause=0.6, pitch=WOW),
    ]),
    Beat("nombre", [
        Ph("Se llama *adulación*:", pause=0.15),
        Ph("decirte lo que quieres oír.", pause=0.3),
    ]),
    Beat("tip", [
        Ph("¿El truco?", pause=0.15, pitch=Q),
        Ph("Pregunta sin decir lo que *crees*,", pause=0.12),
        Ph("y pide que te muestre *cómo* llegó.", pause=0.35),
    ]),
    Beat("cierre", [
        Ph("Entonces, ¿por qué te da la razón?", pause=0.2, pitch=Q),
        Ph("Porque aprendió que darte la razón...", pause=0.3),
        Ph("*gusta*.", pause=0.5, pitch=WOW),
    ]),
]
