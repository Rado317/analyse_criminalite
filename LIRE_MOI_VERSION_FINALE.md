# VERSION FINALE — PROJET DE MÉMOIRE

## Plateforme d'analyse de la criminalité urbaine

Cette archive rassemble la version finale rectifiée du projet : code source, données, traitements Data Science / Machine Learning, API REST FastAPI, interface Streamlit, base de données, notebooks scientifiques, tests, documentation d'installation, configuration Docker/Render et images d'interface.

## Architecture

```text
Utilisateur
   ↓
Streamlit (front-end)
   ↓ HTTP/REST
FastAPI (back-end)
   ↓
SQLAlchemy → SQLite local / PostgreSQL production
   ↓
Données + modèles ML sérialisés
```

## Traitements scientifiques inclus

- nettoyage et contrôle de qualité ;
- réconciliation détail / totaux officiels ;
- EDA approfondie ;
- K-Means avec transformation `log1p` et standardisation ;
- PCA ;
- Isolation Forest et analyse de sensibilité ;
- régression avec DummyRegressor, Ridge, Random Forest et Gradient Boosting ;
- KFold 5 plis ;
- GroupKFold par période ;
- MAE, RMSE et R² ;
- résidus et importance exploratoire des variables.

## Installation rapide

### Windows PowerShell

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install_windows.ps1
```

Puis ouvrir deux PowerShell :

```powershell
.\run_api_windows.ps1
```

```powershell
.\run_streamlit_windows.ps1
```

### Linux / macOS

```bash
chmod +x install_linux_macos.sh run_api.sh run_frontend.sh
./install_linux_macos.sh
```

Puis dans deux terminaux :

```bash
./run_api.sh
```

```bash
./run_frontend.sh
```

## URLs locales

- Streamlit : `http://127.0.0.1:8501`
- FastAPI : `http://127.0.0.1:8000`
- Swagger : `http://127.0.0.1:8000/docs`
- Health check : `http://127.0.0.1:8000/health`

## Déploiement

- Backend FastAPI + PostgreSQL : `render.yaml`
- Frontend : Streamlit Community Cloud
- Point d'entrée Streamlit : `streamlit_app.py`
- Secret Streamlit à définir :

```toml
API_URL = "https://VOTRE-API-RENDER.onrender.com"
```

Lire `docs/INSTALLATION_DEPLOIEMENT_STREAMLIT.md` pour toutes les étapes.

## Images

Les illustrations de l'interface sont dans :

```text
docs/images/interfaces/
```

## Vérification

La version finale contient 5 tests Pytest couvrant nettoyage, clustering, anomalies, entraînement et API.
