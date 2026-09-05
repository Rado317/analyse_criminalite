# Checklist de déploiement final

## Avant GitHub
- [ ] `cd backend && python -m scripts.prepare_all`
- [ ] `pytest -q`
- [ ] vérifier que `.env` n'est pas versionné
- [ ] vérifier que `.streamlit/secrets.toml` n'est pas versionné
- [ ] pousser la racine du projet sur GitHub

## Backend Render
- [ ] créer le Blueprint à partir du `render.yaml`
- [ ] vérifier la création de PostgreSQL
- [ ] vérifier `/health`
- [ ] vérifier `/docs`
- [ ] copier l'URL HTTPS publique de FastAPI

## Frontend Streamlit Community Cloud
- [ ] sélectionner le dépôt GitHub
- [ ] branche `main`
- [ ] main file `streamlit_app.py`
- [ ] configurer le secret `API_URL` avec l'URL Render
- [ ] déployer
- [ ] vérifier les 6 onglets
- [ ] vérifier qu'une estimation ML fonctionne

## Soutenance
- [ ] montrer le tableau de bord
- [ ] montrer la qualité / réconciliation
- [ ] montrer clustering et anomalies
- [ ] montrer la comparaison des modèles
- [ ] montrer Swagger `/docs`
- [ ] rappeler les limites des données et l'absence de prédiction spatio-temporelle réelle
