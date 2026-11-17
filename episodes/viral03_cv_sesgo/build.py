"""Construye «La IA que descartaba currículums de mujeres».

    python episodes/viral03_cv_sesgo/build.py --stills   # ritmo de la narración + cuadros de control
    python episodes/viral03_cv_sesgo/build.py            # MP4 + SRT + guion + portada + QA
    python episodes/viral03_cv_sesgo/build.py --qa       # solo QA del MP4 existente
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from reelforge.build import main

if __name__ == "__main__":
    main(__file__)
