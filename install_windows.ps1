$ErrorActionPreference = "Stop"
python -m venv .venv
& .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
Push-Location backend
python -m scripts.prepare_all
pytest -q
Pop-Location
Write-Host "Installation terminée. Lancez run_api_windows.ps1 puis run_streamlit_windows.ps1 dans deux terminaux."
