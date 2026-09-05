"""Point d'entrée simplifié pour Streamlit Community Cloud.

L'interface principale reste dans frontend/app.py afin de conserver
une architecture propre et séparée du backend FastAPI.
"""
from pathlib import Path
import runpy

APP_PATH = Path(__file__).resolve().parent / "frontend" / "app.py"
runpy.run_path(str(APP_PATH), run_name="__main__")
