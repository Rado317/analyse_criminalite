#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate
cd backend
uvicorn api.main:app --reload
