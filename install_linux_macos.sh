#!/usr/bin/env bash
set -euo pipefail
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
(cd backend && python -m scripts.prepare_all)
(cd backend && pytest -q)
echo "Installation terminée. Utilisez ./run_api.sh puis ./run_frontend.sh dans deux terminaux."
