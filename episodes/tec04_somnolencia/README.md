# tec04 · ¿Tu auto sabe que te estás durmiendo? (cámaras de monitoreo del conductor y PERCLOS)

Reel de stheq.ia: **motion graphics animados dibujados por código** (`reelforge`), ≈ 60 s, 1080×1920, 60 fps. Sin fotos. Propuesta A del 23-nov-2026 (`propuestas/2026-11-23/`), categoría autos y movilidad. Tema inspirado en las tendencias «Toyota Built a Self-Driving Car for 5-Year-Olds» (9,95 M vistas) y «O carro continua dirigindo sozinho quando o motorista dorme» (2,7 M); no se copia nada.

## Fuentes
- NHTSA, «Drowsy Driving»: estimación de 91.000 choques reportados por la policía con conductores somnolientos en 2017 (≈ 50.000 heridos y casi 800 muertes); la propia NHTSA advierte que es una subestimación. https://www.nhtsa.gov/risky-driving/drowsy-driving
- Dinges, Mallis, Maislin y Powell, «PERCLOS: A Valid Psychophysiological Measure of Alertness As Assessed by Psychomotor Vigilance», FHWA-MCRT-98-006 (FHWA/NHTSA, 1998), basado en Wierwille et al. (1994): PERCLOS = proporción de un minuto con los ojos al menos 80 % cerrados; fue la medida más confiable de las que se probaron. https://rosap.ntl.bts.gov/view/dot/113
- Euro NCAP, ESV 27 (paper 000289): los sistemas directos usan cámaras infrarrojas para observar la cara, la mirada y la apertura de los párpados. https://cdn.euroncap.com/media/77182/27esv-000289.pdf
- Comisión Europea, «Safer cars, safer roads: new rules take effect» (8-jul-2026): desde el 7-jul-2026 todo auto y furgoneta nuevos en la UE deben traer aviso avanzado de distracción del conductor (Reglamento (UE) 2019/2144 y Reglamento Delegado (UE) 2023/2590). https://commission.europa.eu/news-and-media/news/safer-cars-safer-roads-new-rules-take-effect-2026-07-08_en
- Cálculo propio: 100 km/h ÷ 3,6 = 27,8 m por segundo («casi 28 metros»).

## Simplificaciones
- «Muchos autos nuevos»: no todos tienen cámara; algunos avisos de cansancio estiman la somnolencia por cómo se mueve el volante.
- La norma europea de 2026 obliga a detectar **distracción** con cámara; el aviso de somnolencia existe desde la fase anterior del reglamento y puede funcionar sin cámara. La narración dice «una cámara que vigila si te distraes».
- El 30 % de las barras es un ejemplo dibujado, no un umbral real; cada fabricante usa sus propios umbrales y combina PERCLOS con otras señales (mirada, cabeza, duración de los parpadeos).
- Las cifras de choques son de EE. UU. (2017) y se dicen como estimación.

## Escenas
1. Un ojo cansado sobre una carretera de noche: el párpado baja y todo se oscurece. «?».
2. Vista desde arriba: en un segundo con los ojos cerrados, el auto avanza 28 m y se desvía. 91.000 choques por sueño en un año (EE. UU.).
3. Cara del conductor y cámara en el volante; a oscuras la cara desaparece; la luz infrarroja la hace visible para la cámara.
4. Primer plano del ojo: un parpadeo rápido no cuenta; un párpado que baja lento y se queda cerrado, sí. Barras de un minuto → PERCLOS.
5. Medidor que sube y alerta. Estrellas de la UE: julio 2026, todo auto nuevo con cámara de distracción.
6. Vuelta al ojo sobre la carretera: «mira tus párpados y cuenta el tiempo»; el párpado vuelve a pesar (empalme con el inicio).

## Control de calidad
- ffprobe: h264 1080×1920 60 fps, AAC 48 kHz estéreo, 59,6 s. Volumen −14,5 LUFS, pico −3,1 dBFS.
- Hoja de cuadros cada 3 s revisada: sin solapamientos ni cuadros vacíos; todo entre y≈480 y 1300. La regla de 28 m llega a 28 cuando la voz lo dice; el contador de 91.000 sube mientras se habla de EE. UU.
- Ritmo: ≈ 175 palabras, 3,35 palabras/s al hablar, con pausas diseñadas. No escuché el audio: verificado con métricas.
- Cifras contra la fuente: 91.000 (NHTSA, 2017), 80 % de cierre y «una de las medidas más confiables» (FHWA 1998), julio 2026 (Comisión Europea), 28 m (100 km/h ÷ 3,6).

## Texto para publicar
¿Tu auto se puede dar cuenta de que te estás quedando dormido? 😴🚗
Muchos autos nuevos traen una cámara con luz infrarroja que mira tus párpados, también de noche. No le importa un parpadeo: cuenta cuánto de cada minuto pasas con los ojos casi cerrados (PERCLOS, una de las medidas más confiables según estudios para la autoridad de carreteras de EE. UU.). Si sube, te avisa que descanses. En Europa, desde julio de 2026, todo auto nuevo debe traer una cámara que detecta distracciones.
¿Tu auto tiene este aviso? Cuéntanos 👇
Guárdalo para no olvidarlo.
Fuentes: NHTSA, «Drowsy Driving»; FHWA/NHTSA, «PERCLOS» (1998); Comisión Europea (jul-2026); Euro NCAP.
#stheqia #tecnologia #autos #seguridadvial #conduccion #inteligenciaartificial #sueño
