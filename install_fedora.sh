#!/usr/bin/env bash
set -euo pipefail

sudo dnf install -y python3 python3-pip python3-devel gcc
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
(cd backend && python -m scripts.prepare_all)

echo "Installation terminée."
echo "Backend : ./run_api.sh"
echo "Frontend : ./run_frontend.sh"
