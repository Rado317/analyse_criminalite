# Index du code source complet

## Front-end Streamlit
- `streamlit_app.py` — point d'entrée de déploiement.
- `frontend/app.py` — interface complète : filtres, tableau de bord, clustering, anomalies, qualité des données, estimation ML et page À propos.

## Back-end FastAPI
- `backend/api/main.py` — API REST, endpoints statistiques, qualité, modèles, anomalies, clusters et prédiction.

## Data Science / Machine Learning
- `backend/src/data_cleaning.py` — nettoyage, normalisation, variables dérivées, contrôle qualité et réconciliation.
- `backend/src/clustering.py` — transformation `log1p`, standardisation, K-Means, silhouette et PCA.
- `backend/src/anomaly_detection.py` — Isolation Forest, règles robustes, niveaux et analyse de sensibilité.
- `backend/src/train.py` — baseline, Ridge, Random Forest, Gradient Boosting, KFold, GroupKFold, métriques, résidus et importance par permutation.

## Base de données
- `backend/src/database.py` — moteur SQLAlchemy SQLite/PostgreSQL.
- `backend/src/models.py` — modèle ORM.
- `backend/src/schemas.py` — schémas Pydantic.
- `backend/scripts/init_db.py` — initialisation de la base.

## Orchestration
- `backend/scripts/prepare_artifacts.py` — reconstruit les artefacts analytiques.
- `backend/scripts/prepare_all.py` — prépare données, modèles et base.

## Tests
- `backend/tests/test_cleaning.py`
- `backend/tests/test_clustering.py`
- `backend/tests/test_anomalies.py`
- `backend/tests/test_training.py`
- `backend/tests/test_api.py`

## Déploiement
- `render.yaml` — FastAPI + PostgreSQL sur Render (rootDir: backend).
- `backend/Dockerfile.api` — image backend.
- `Dockerfile.frontend` — image Streamlit.
- `docker-compose.yml` — stack locale complète PostgreSQL + API + Streamlit.
- `.streamlit/config.toml` — configuration Streamlit.
- `.streamlit/secrets.toml.example` — exemple de secret `API_URL`.
