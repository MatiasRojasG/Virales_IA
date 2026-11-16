# El robot que se cayó una y otra vez (opción C, propuestas 16-nov)

**Video:** `output/viral02_robot_aprende.mp4`: 1080×1920, 60 fps, **46,9 s**, −15,0 LUFS, pico −1 dBFS. Subtítulos 60 ms antes de la voz. Sin saltos ni pantallas vacías.

- **Inspiración:** «NVIDIA's Cute AI Ducks Can Do Somersaults» (7,4 M) y «When Jensen asks for a somersault» (5,3 M).
- **Clase:** aprender de los errores (pérdida y descenso de gradiente).
- **Simulación real** (`experiment.py`):
  - El robot salta con dos parámetros: fuerza y ángulo.
  - El error es la distancia mínima de su trayectoria al punto de aterrizaje.
  - Se ajusta con descenso de gradiente numérico.
  - Primer aterrizaje en la plataforma: **intento 21** (es el número que dice la narración).
- **Voz:** `es-MX-JorgeNeural` a +20 %, 2,9 palabras/s.
- **Lo simplificado, solo aquí y no en pantalla:** los robots reales aprenden con muchos más parámetros y otras técnicas, en simulaciones de millones de intentos. La narración lo dice sin cifras («millones de perillas», «en una simulación»).

**Texto para publicar:**
> Este robot se cayó 20 veces… y nadie le enseñó a saltar 🤖
> Así aprende una inteligencia artificial: equivocarse, medir el error y ajustar un poquito.
> ¿Cuántas veces te caíste tú antes de aprender algo? 👇
> #DetrásDelAlgoritmo #IA #InteligenciaArtificial #Robots #RedesNeuronales #Ciencia #AprendeEnTikTok
