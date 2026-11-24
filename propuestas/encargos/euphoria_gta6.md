# Encargo del usuario (24-nov-2026): próximo reel sobre Euphoria y los movimientos de GTA VI

Pedido explícito de Mati: «quiero que el próximo reel hable de eso» (Euphoria y cómo se mueven los personajes de GTA VI).
La tarea diaria del 25-nov-2026 produce ESTE tema como reel (tec06_euphoria_gta), en vez de elegir entre 3 ideas.

## Idea
- Gancho (cuadro 0): un personaje recibe un empujón y, en vez de caer como un muñeco de trapo, estira los brazos y trata de no caerse. ¿Cómo «sabe» qué hacer?
- Arco: animaciones grabadas (siempre iguales) → muñeco de trapo (ragdoll: cae sin vida) → Euphoria: cuerpo con músculos simulados y un «sistema nervioso» que intenta mantener el equilibrio y protegerse, en tiempo real → por eso no hay dos caídas iguales → origen: investigación en la Universidad de Oxford (Torsten Reil), NaturalMotion → Rockstar lo usa desde GTA IV (2008), RDR, Max Payne 3, GTA V, RDR2 → GTA VI (salió el 19-nov-2026): además, ~600.000 animaciones para los peatones (vs. ~55.000 en GTA V), según reportaje (revista Edge, ago-2026, citado por PC Gamer/GamesRadar/TechRadar).
- Respuesta final: el personaje no «sabe» la caída de memoria: la calcula en el momento, como un cuerpo que quiere no caerse.
- Animación: monigote articulado dibujado por código (simulación física simple en NumPy: péndulo invertido / equilibrio con controlador), comparación lado a lado ragdoll vs. controlado.

## Cuidado (honestidad)
- Rockstar no ha detallado oficialmente cuánto cambió Euphoria en GTA VI: no afirmar mejoras concretas. Decir «Rockstar usa esta tecnología desde GTA IV» y lo de 600.000 animaciones «según un reportaje».
- Verificar cada dato antes de usarlo. No usar imágenes, logos, personajes ni capturas de GTA (derechos): solo monigotes propios. No nombrar personajes del juego.

## Fuentes a verificar
- https://en.wikipedia.org/wiki/Euphoria_(software)
- https://innovation.ox.ac.uk/?p=9022 (Oxford University Innovation, NaturalMotion)
- https://russellgroup.ac.uk/policy/case-studies/developing-ground-breaking-software-for-the-gaming-industry
- https://users.sussex.ac.uk/~philh/pubs/reilhusbandsIEEE.pdf (Reil & Husbands, redes neuronales evolucionadas para caminar bípedo)
- https://wccftech.com/rockstar-euphoria-evolved-rdr2/ (Rockstar: Euphoria evolucionado en RDR2)
- https://www.pcgamer.com/games/grand-theft-auto/gta-6s-npcs-have-about-600-000-animations-as-well-as-personality-traits-that-take-demographic-and-professional-variables-into-account/
- https://www.gamesradar.com/games/grand-theft-auto/gta-6s-hand-crafted-npcs-have-over-600-000-animations-compared-to-only-55-000-animations-in-gta-5/
- https://www.fox10tv.com/2026/10/16/gta-6-locks-nov-19-release-date-after-delays/
