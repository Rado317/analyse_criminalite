.PHONY: install prepare artifacts db api frontend test all podman docker clean

install:
	python -m pip install -r backend/requirements.txt

prepare:
	cd backend && python -m src.data_cleaning

artifacts:
	cd backend && python -m scripts.prepare_artifacts

db:
	cd backend && python -m scripts.init_db --force

all:
	cd backend && python -m scripts.prepare_all

api:
	cd backend && uvicorn api.main:app --reload

frontend:
	streamlit run streamlit_app.py

test:
	cd backend && pytest -q

podman:
	podman-compose up --build

docker:
	docker compose up --build

clean:
	rm -f backend/data/criminalite.db backend/data/processed/*.csv backend/data/processed/*.json backend/artifacts/*
