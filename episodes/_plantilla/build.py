"""Build de un episodio nuevo: copiar la carpeta _plantilla y editar script.py y scenes.py.

    python episodes/_plantilla/build.py --stills   # ritmo de la narración + cuadros de control
    python episodes/_plantilla/build.py            # MP4 + SRT + guion + portada + QA
    python episodes/_plantilla/build.py --qa       # solo QA del MP4 existente
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from reelforge.build import main

if __name__ == "__main__":
    main(__file__)
