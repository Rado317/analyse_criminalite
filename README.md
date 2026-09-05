# Plateforme intelligente d'analyse des infractions — Version 2

Projet de mémoire basé sur les données détaillées de 2024, 2025 et du premier semestre 2026.
La cartographie a été retirée car les fichiers ne contiennent ni quartier, ni adresse, ni coordonnées géographiques.

## Fonctionnalités

- nettoyage et normalisation automatiques des fichiers CSV ;
- contrôle des valeurs manquantes et réconciliation avec les totaux officiels ;
- tableau de bord statistique par période et catégorie ;
- clustering K-Means des profils d'infractions avec `log1p`, standardisation et visualisation PCA ;
- détection d'anomalies avec Isolation Forest et règles robustes ;
- comparaison de quatre modèles de régression avec KFold et validation par période ;
- API REST FastAPI et documentation Swagger ;
- interface Streamlit ;
- stockage SQLite en développement ou PostgreSQL en production ;
- tests Pytest, conteneurs Docker/Podman et CI GitHub Actions.

## 1. Installation sous Fedora Linux

```bash
sudo dnf install python3 python3-pip python3-devel gcc unzip -y
cd criminalite_intelligente_v2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

## 2. Préparer tout le projet

```bash
cd backend
python -m scripts.prepare_all
```

Cette commande exécute successivement :

```text
nettoyage → clustering → anomalies → modèles ML → base de données
```

## 3. Lancer le backend

```bash
cd backend
uvicorn api.main:app --reload
```

- API : `http://127.0.0.1:8000`
- Swagger : `http://127.0.0.1:8000/docs`

## 4. Lancer le frontend

Dans un second terminal :

```bash
cd criminalite_intelligente_v2
source .venv/bin/activate
streamlit run streamlit_app.py
```

Interface : `http://127.0.0.1:8501`

## 5. Tests

```bash
cd backend
pytest -q
```

## 6. Lancement avec Podman sous Fedora

```bash
sudo dnf install podman podman-compose -y
podman-compose up --build
```

Services :

- frontend : `http://127.0.0.1:8501`
- backend : `http://127.0.0.1:8000/docs`
- PostgreSQL : conteneur interne `db`

## 7. Déploiement

### Backend et PostgreSQL

Le fichier `render.yaml` décrit le backend FastAPI et la base PostgreSQL.
Après avoir envoyé le projet sur GitHub, créez un Blueprint depuis ce fichier.

### Frontend Streamlit

Dans Streamlit Community Cloud :

1. sélectionner le dépôt GitHub ;
2. choisir `streamlit_app.py` comme fichier principal ;
3. ajouter le secret suivant :

```toml
API_URL = "https://adresse-de-votre-api"
```

Ne jamais envoyer `.streamlit/secrets.toml` sur GitHub.

## 8. Structure

```text
criminalite_intelligente_v2/
├── backend/
│   ├── api/main.py
│   ├── src/
│   │   ├── data_cleaning.py
│   │   ├── clustering.py
│   │   ├── anomaly_detection.py
│   │   ├── train.py
│   │   ├── database.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── scripts/
│   │   ├── prepare_artifacts.py
│   │   ├── prepare_all.py
│   │   └── init_db.py
│   ├── data/raw/
│   ├── data/processed/
│   ├── artifacts/
│   ├── notebooks/
│   │   └── Analyse_scientifique_criminalite_Jupyter.ipynb
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile.api
├── frontend/app.py
├── streamlit_app.py
├── docs/
│   ├── corrections_evaluation_scientifique.md
│   └── pipeline_scientifique.md
├── Dockerfile.frontend
├── docker-compose.yml
└── render.yaml
```

## 9. Positionnement scientifique

Le clustering regroupe des profils statistiques ; il ne mesure pas la dangerosité.
Une anomalie indique une observation inhabituelle à vérifier, pas nécessairement une erreur.
La régression est une preuve de concept sur des données agrégées et ne doit pas guider une décision individuelle ou opérationnelle.


## 10. Corrections scientifiques — Évaluation 2

La version rectifiée intègre les recommandations de l'évaluation scientifique :

- problématique recentrée sur l'extraction de connaissances à partir de données agrégées ;
- EDA approfondie dans un notebook Jupyter ;
- contrôle explicite des écarts avec les totaux officiels ;
- clustering rendu plus robuste aux distributions asymétriques grâce à `log1p` ;
- comparaison des modèles avec baseline ;
- double validation : KFold et GroupKFold par période ;
- analyse des résidus et importance exploratoire des variables ;
- sensibilité du nombre d'anomalies au paramètre `contamination` ;
- limites et interprétations scientifiques documentées.

Voir `docs/corrections_evaluation_scientifique.md` et le dossier `notebooks/`.

## 11. Guide complet installation → déploiement Streamlit

Un guide prêt à suivre est maintenant fourni :

```text
docs/INSTALLATION_DEPLOIEMENT_STREAMLIT.md
```

Un aide-mémoire avec uniquement les commandes est également disponible :

```text
COMMANDES_RAPIDES.txt
```

Pour Streamlit Community Cloud, le point d'entrée simplifié est :

```text
streamlit_app.py
```

Architecture de production recommandée :

```text
Streamlit Community Cloud → FastAPI sur Render → PostgreSQL
```

Démarrage local minimal :

```bash
python -m venv .venv
# activer .venv
pip install -r backend/requirements.txt
cd backend
python -m scripts.prepare_all
pytest -q
uvicorn api.main:app --reload
```

Puis, dans un deuxième terminal :

```bash
streamlit run streamlit_app.py
```

## 12. Images de l'interface pour le mémoire

Les aperçus visuels sont disponibles dans :

```text
docs/images/interfaces/
```

Vue d'ensemble : `docs/images/interfaces/interface_overview.png`.

Pour une soutenance finale, compléter si possible ces maquettes par des captures réelles de l'application Streamlit après déploiement.
