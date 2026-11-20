# tec01 · ¿Por qué tu cargador es tan chico? (cargadores de GaN)

Reel de stheq.ia: **motion graphics animados dibujados por código** (`reelforge`), 50 s, 1080×1920, 60 fps, −14,4 LUFS. Sin fotos. Propuesta A del 20-nov-2026 (`propuestas/2026-11-20/`).

## Fuentes
- Infineon (E. Persson, How2Power, 2022): los cargadores flyback de silicio rara vez operan sobre ~65 kHz; el GaN tiene mucha menos carga de salida, lo que permite frecuencias más altas. https://www.how2power.com/newsletters/2208/H2PToday2208_commentary_Infineon.pdf
- Texas Instruments, «GaN: Pushing the limits of power density & efficiency»: conmutación sobre 500 kHz, componentes magnéticos hasta 60 % más pequeños. https://ti.com/technologies/gallium-nitride.html
- Infineon, «What is a GaN charger and how does it work». https://www.infineon.com/product-information/what-is-a-gan-charger-and-how-does-it-work
- USB-IF, USB Power Delivery: el cargador negocia con el celular voltajes de 5 a 20 V.

## Simplificaciones
- «65.000 veces por segundo» es la frecuencia típica de muchos cargadores de silicio (no de todos).
- «Hasta 60 %» se refiere a los componentes magnéticos (transformador/inductores), según TI; no al cargador completo.
- El cargador de GaN de la foto es un ejemplo; no todos los cargadores chicos usan GaN.

## Escenas
1. Dos cargadores de 30 W (uno grande, uno chico) con medida de alturas y «?».
2. Enchufe → onda roja enorme (220 V) → cargador → línea casi plana (5–20 V) → celular que se carga.
3. Interruptor que prende y apaga cada vez más rápido + onda cuadrada → «65.000 / s» (la animación es lenta: representa, no mide).
4. El transformador dentro del cargador se achica al subir la velocidad (control lento → rápido).
5. Chip de silicio que se calienta y bota energía vs chip de GaN frío → «500.000 / s».
6. Transformador «hasta −60 %» y el cargador grande se encoge hasta el chico (empalme con el inicio).

## Texto para publicar
¿Por qué tu cargador nuevo es tan chico? 🔌
Dos cargadores de 30 W, mismo poder… pero uno cabe en la mano. El secreto es el nitruro de galio (GaN): prende y apaga la corriente cientos de miles de veces por segundo sin calentarse tanto, y eso permite piezas mucho más chicas (Texas Instruments, Infineon).
¿Tu cargador es de GaN? Revisa la etiqueta y cuéntanos 👇
Guárdalo para no olvidarlo.
Fuentes: Texas Instruments; Infineon.
#stheqia #tecnologia #cargador #GaN #celulares #electronica #ciencia
