# Architecture technique et scientifique

```text
CSV officiels
    ↓
Pandas : nettoyage, normalisation, contrôle qualité et réconciliation
    ↓
Analyse exploratoire scientifique (notebook Jupyter)
    ↓
K-Means : log1p → StandardScaler → K-Means → PCA
    ↓
Isolation Forest + règles robustes + sensibilité de contamination
    ↓
Régression : baseline + Ridge + Random Forest + Gradient Boosting
    ↓
Validation KFold + validation GroupKFold par période
    ↓
Artefacts ML et données enrichies
    ↓
SQLite en développement / PostgreSQL en production
    ↓
FastAPI
    ↓
Streamlit
```

## Modules Machine Learning

1. **Clustering exploratoire** : regroupement des infractions selon leurs saisines, victimes, interpellations et résultats. Une transformation `log1p` réduit l'influence des valeurs extrêmes avant standardisation.
2. **Détection d'anomalies** : Isolation Forest et règles robustes. Une analyse de sensibilité documente l'effet du paramètre `contamination`.
3. **Régression expérimentale** : comparaison de quatre modèles avec baseline, KFold 5 plis et validation par période.
4. **Interprétation** : résidus, MAE, RMSE, R² et importance exploratoire par permutation dans le notebook.

## Limites

- seulement 152 observations agrégées ;
- seulement deux années complètes et un semestre ;
- absence de granularité mensuelle ou journalière ;
- absence de localisation ;
- écarts entre certaines lignes détaillées et les totaux officiels ;
- distributions de comptage fortement asymétriques ;
- résultats exploratoires nécessitant une validation métier.
