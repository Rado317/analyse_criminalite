# Installation et déploiement complet — Streamlit + FastAPI

Ce projet utilise l'architecture suivante :

```text
Navigateur utilisateur
        ↓
Streamlit Community Cloud
        ↓ API_URL
FastAPI (Render)
        ↓
PostgreSQL (Render)
```

- **Streamlit** est l'interface web principale visible par l'utilisateur.
- **FastAPI** fournit l'API REST et les endpoints utilisés par Streamlit.
- **SQLite** est utilisé facilement en local.
- **PostgreSQL** est prévu pour le déploiement du backend.

Le fichier principal recommandé pour Streamlit Community Cloud est :

```text
streamlit_app.py
```

Il charge l'application réelle située dans `frontend/app.py`.

---

## 1. Prérequis

Installer :

- Python 3.12 recommandé ;
- Git ;
- un compte GitHub ;
- un compte Streamlit Community Cloud ;
- un compte Render si le backend FastAPI est déployé séparément.

Vérifier Python :

```bash
python --version
```

ou :

```bash
python3 --version
```

Vérifier Git :

```bash
git --version
```

---

# PARTIE A — INSTALLATION LOCALE

## 2. Décompresser et entrer dans le projet

### Linux / macOS

```bash
unzip Projet_Memoire_Criminalite_VERSION_FINALE_Streamlit.zip
cd criminalite_intelligente_v2
```

### Windows PowerShell

```powershell
Expand-Archive .\Projet_Memoire_Criminalite_VERSION_FINALE_Streamlit.zip -DestinationPath .
cd .\criminalite_intelligente_v2
```

---

## 3. Créer l'environnement virtuel

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloque l'activation :

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

---

## 4. Installer les dépendances

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

Vérification rapide :

```bash
python -c "import streamlit, fastapi, sklearn, pandas; print('Installation OK')"
```

---

## 5. Préparer les données, modèles et base locale

Commande recommandée :

```bash
cd backend
python -m scripts.prepare_all
```

Cette commande exécute :

```text
Nettoyage
→ Réconciliation des données
→ Clustering K-Means
→ Détection d'anomalies
→ Comparaison et entraînement des modèles de régression
→ Création / mise à jour de la base SQLite
```

Pour ne reconstruire que les artefacts Data Science (depuis `backend/`) :

```bash
python -m scripts.prepare_artifacts
```

Pour recréer seulement la base (depuis `backend/`) :

```bash
python -m scripts.init_db --force
```

---

## 6. Exécuter les tests

```bash
cd backend
pytest -q
```

La version rectifiée a été préparée avec les tests automatisés du projet.

---

# PARTIE B — LANCEMENT LOCAL

## 7. Terminal 1 : lancer FastAPI

### Linux / macOS / Windows avec environnement activé

```bash
cd backend
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Ouvrir :

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/health
```

La page `/docs` correspond à Swagger, utile pour tester l'API REST.

---

## 8. Terminal 2 : lancer Streamlit

Activer de nouveau `.venv` (depuis la racine du projet), puis :

```bash
streamlit run streamlit_app.py
```

ou directement :

```bash
streamlit run frontend/app.py
```

Ouvrir :

```text
http://127.0.0.1:8501
```

Par défaut Streamlit contacte :

```text
http://localhost:8000
```

---

## 9. Définir manuellement l'API locale si nécessaire

### Linux / macOS

```bash
export API_URL=http://127.0.0.1:8000
streamlit run streamlit_app.py
```

### Windows PowerShell

```powershell
$env:API_URL="http://127.0.0.1:8000"
streamlit run streamlit_app.py
```

---

# PARTIE C — GITHUB

## 10. Créer le dépôt Git local

Depuis la racine `criminalite_intelligente_v2` :

```bash
git init
git add .
git commit -m "Version rectifiee evaluation scientifique 2"
git branch -M main
```

Créer ensuite un dépôt vide sur GitHub, puis remplacer l'URL ci-dessous :

```bash
git remote add origin https://github.com/VOTRE_UTILISATEUR/VOTRE_DEPOT.git
git push -u origin main
```

Pour les prochaines modifications :

```bash
git add .
git commit -m "Mise a jour du projet"
git push
```

Ne pas envoyer de secrets personnels dans GitHub.

---

# PARTIE D — DÉPLOYER LE BACKEND FASTAPI SUR RENDER

## 11. Fichier déjà fourni

Le projet contient :

```text
render.yaml
```

Ce Blueprint définit :

- le service web FastAPI ;
- une base PostgreSQL ;
- `DATABASE_URL` ;
- le health check `/health`.

Le backend est construit avec :

```bash
pip install -r requirements.txt && python -m scripts.prepare_artifacts
```

Il démarre avec :

```bash
python -m scripts.init_db --force && uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

## 12. Déploiement Render

1. Envoyer le projet sur GitHub.
2. Dans Render, créer un **Blueprint** depuis le dépôt.
3. Render lit le fichier `render.yaml` placé à la racine (il pointe vers `rootDir: backend`).
4. Lancer le déploiement.
5. Attendre que le service `criminalite-api` soit disponible.
6. Copier son URL publique.

Exemple :

```text
https://criminalite-api-xxxx.onrender.com
```

Tester ensuite :

```text
https://criminalite-api-xxxx.onrender.com/health
```

et :

```text
https://criminalite-api-xxxx.onrender.com/docs
```

Conserver cette URL : elle sera utilisée dans Streamlit.

---

# PARTIE E — DÉPLOYER L'INTERFACE SUR STREAMLIT COMMUNITY CLOUD

## 13. Fichier principal Streamlit

Utiliser :

```text
streamlit_app.py
```

Le projet conserve également l'application réelle dans :

```text
frontend/app.py
```

## 14. Paramètres Streamlit Community Cloud

Dans la création de l'application :

```text
Repository : VOTRE_UTILISATEUR/VOTRE_DEPOT
Branch     : main
Main file  : streamlit_app.py
```

Dans **Advanced settings**, choisir de préférence la même version de Python que celle utilisée pour le projet, par exemple Python 3.12.

Dans les **Secrets**, saisir :

```toml
API_URL = "https://criminalite-api-xxxx.onrender.com"
```

Remplacer l'adresse par la véritable URL Render du backend.

Puis cliquer sur **Deploy**.

Streamlit Community Cloud installe automatiquement les dépendances déclarées dans le `requirements.txt` du dépôt.

---

# PARTIE F — VÉRIFICATIONS APRÈS DÉPLOIEMENT

## 15. Vérifier le backend

Dans le navigateur :

```text
https://VOTRE-API/health
```

Résultat attendu de forme :

```json
{
  "status": "ok",
  "lignes_en_base": 152
}
```

Puis vérifier Swagger :

```text
https://VOTRE-API/docs
```

---

## 16. Vérifier Streamlit

Ouvrir l'URL fournie par Streamlit Community Cloud.

Vérifier les onglets :

```text
Tableau de bord
Clustering
Anomalies
Qualité des données
Estimation ML
À propos
```

Dans la barre latérale, l'adresse affichée après `API :` doit être l'URL du backend Render, et non `localhost`.

---

# PARTIE G — COMMANDES UTILES

## 17. Tout préparer

```bash
cd backend
python -m scripts.prepare_all
```

## 18. Seulement les modèles et traitements

```bash
cd backend
python -m scripts.prepare_artifacts
```

## 19. Base SQLite

```bash
cd backend
python -m scripts.init_db --force
```

## 20. Backend FastAPI

```bash
cd backend
uvicorn api.main:app --reload
```

## 21. Frontend Streamlit

```bash
streamlit run streamlit_app.py
```

## 22. Tests

```bash
cd backend
pytest -q
```

## 23. Jupyter Notebook

Si Jupyter est installé :

```bash
jupyter notebook backend/notebooks/Analyse_scientifique_criminalite_Jupyter.ipynb
```

S'il n'est pas installé :

```bash
pip install notebook
jupyter notebook backend/notebooks/Analyse_scientifique_criminalite_Jupyter.ipynb
```

## 24. Docker Compose — alternative locale

```bash
docker compose up --build
```

Puis :

```text
Streamlit : http://127.0.0.1:8501
FastAPI   : http://127.0.0.1:8000/docs
```

Arrêt :

```bash
docker compose down
```

---

# PARTIE H — ORDRE CONSEILLÉ POUR LA SOUTENANCE

Pour une démonstration locale :

```bash
# 1. Activer l'environnement
source .venv/bin/activate

# 2. Vérifier les tests
cd backend && pytest -q

# 3. Lancer l'API dans un premier terminal
cd backend && uvicorn api.main:app --reload

# 4. Lancer Streamlit dans un deuxième terminal (depuis la racine)
cd .. && streamlit run streamlit_app.py
```

Puis montrer :

1. le tableau de bord Streamlit ;
2. l'EDA dans le notebook ;
3. le clustering ;
4. les anomalies ;
5. les métriques des modèles ;
6. `/docs` de FastAPI ;
7. la qualité et la réconciliation des données.

---

# Résumé du déploiement

```text
1. pip install -r backend/requirements.txt
2. cd backend && python -m scripts.prepare_all
3. cd backend && pytest -q
4. git push sur GitHub
5. Render → déployer render.yaml (rootDir: backend) → récupérer URL FastAPI
6. Streamlit Community Cloud → main file: streamlit_app.py
7. Secret Streamlit : API_URL = "URL_FASTAPI_RENDER"
8. Deploy
```
