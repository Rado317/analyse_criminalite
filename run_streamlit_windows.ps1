$ErrorActionPreference = "Stop"
& .\.venv\Scripts\Activate.ps1
$env:API_URL="http://127.0.0.1:8000"
streamlit run streamlit_app.py
