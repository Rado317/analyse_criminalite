# Pipeline scientifique

```text
Données brutes
    ↓
Audit de qualité et réconciliation
    ↓
Nettoyage et normalisation
    ↓
Feature Engineering
    ↓
Analyse exploratoire (EDA)
    ↓
┌───────────────────────────────┬─────────────────────────────┐
│ K-Means + PCA                 │ Isolation Forest            │
│ log1p + standardisation       │ + règles robustes           │
└───────────────────────────────┴─────────────────────────────┘
    ↓
Comparaison des modèles supervisés
Dummy / Ridge / Random Forest / Gradient Boosting
    ↓
Validation KFold + validation par période
    ↓
Interprétation des métriques et résidus
    ↓
Artefacts ML + SQLite/PostgreSQL
    ↓
FastAPI
    ↓
Streamlit
    ↓
Discussion scientifique / limites / validation métier
```

## Règles d'interprétation

- Les corrélations ne prouvent pas une causalité.
- Les importances de variables sont exploratoires.
- Les clusters représentent des ressemblances statistiques, pas un niveau de dangerosité.
- Une anomalie n'est pas automatiquement une erreur.
- La régression est une preuve de concept sur données agrégées.
- L'absence de géolocalisation et de temporalité fine interdit de présenter le système comme une vraie prédiction spatio-temporelle.
