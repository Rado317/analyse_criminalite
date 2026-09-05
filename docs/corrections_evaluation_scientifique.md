# Corrections intégrées après l'Évaluation 2

## 1. Problématique scientifique

Question de recherche proposée :

> Comment les méthodes d'analyse de données et de Machine Learning peuvent-elles être utilisées pour extraire des connaissances pertinentes à partir de données criminelles agrégées malgré leurs limitations ?

La plateforme est considérée comme un moyen de mise en œuvre et de démonstration, non comme la problématique scientifique elle-même.

## 2. Démarche méthodologique

Le projet est maintenant documenté selon une logique proche de CRISP-DM :

1. compréhension du problème ;
2. compréhension et audit des données ;
3. préparation des données ;
4. analyse exploratoire ;
5. modélisation ;
6. validation ;
7. déploiement ;
8. discussion critique.

Le notebook `notebooks/Analyse_scientifique_criminalite_Jupyter.ipynb` développe ces étapes avec les graphiques et analyses nécessaires au mémoire.

## 3. Qualité et réconciliation des données

Le pipeline produit :

- `data/processed/data_quality_report.json` ;
- `data/processed/reconciliation_totaux.csv`.

Les écarts entre la somme des lignes détaillées et les totaux officiels sont explicitement comptabilisés. Ces écarts ne sont pas corrigés artificiellement : ils doivent être documentés et, idéalement, validés avec la source métier.

## 4. Analyse exploratoire

Le notebook ajoute :

- statistiques descriptives ;
- moyenne, médiane, écart-type et asymétrie ;
- proportion de valeurs nulles ;
- histogrammes bruts et logarithmiques ;
- corrélations de Spearman ;
- analyse IQR des observations atypiques ;
- comparaison des périodes ;
- avertissement spécifique sur l'annualisation exploratoire de 2026-S1.

## 5. Modèles supervisés

Les modèles comparés sont :

- référence médiane (`DummyRegressor`) ;
- Ridge ;
- Random Forest ;
- Gradient Boosting.

Deux validations sont maintenant enregistrées dans `artifacts/regression_metrics.json` :

- **KFold 5 plis** pour la performance interne ;
- **GroupKFold par période** pour tester la robustesse entre périodes.

Les métriques utilisées sont MAE, RMSE et R². Leur interprétation est intégrée à l'artefact de résultats.

## 6. Clustering

Les variables de comptage sont très asymétriques. Le clustering applique donc maintenant :

`log1p → StandardScaler → K-Means → PCA`.

Les diagnostics comparent également les scores obtenus sur les données brutes et après `log1p`. Le choix de `k` évite, lorsque possible, les solutions où le plus petit cluster représente moins de 5 % de l'échantillon.

Cette correction évite qu'un score silhouette artificiellement élevé soit interprété comme une segmentation robuste lorsqu'il ne fait qu'isoler quelques valeurs extrêmes.

## 7. Détection d'anomalies

Isolation Forest conserve une contamination de référence de 8 %, mais l'artefact `anomaly_metrics.json` contient maintenant une analyse de sensibilité pour 3 %, 5 %, 8 %, 10 % et 15 %.

Une anomalie est explicitement présentée comme un cas statistiquement inhabituel à vérifier, et non comme une erreur certaine.

## 8. Limites scientifiques à présenter

- faible nombre d'observations ;
- données agrégées ;
- absence de géolocalisation fine ;
- absence de série temporelle mensuelle ou journalière ;
- 2026-S1 incomplet par rapport à une année entière ;
- écarts entre détail et totaux officiels ;
- forte asymétrie et nombreux zéros ;
- dépendance des clusters aux transformations et à `k` ;
- dépendance des anomalies au paramètre de contamination ;
- absence de validation métier approfondie.

## 9. Positionnement final

Le projet doit être défendu comme une **plateforme exploratoire de Data Science** capable de structurer, contrôler, analyser et modéliser les données disponibles. Il ne constitue pas une prédiction spatio-temporelle opérationnelle de la criminalité.
