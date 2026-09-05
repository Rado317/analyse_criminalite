from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold, cross_val_predict, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import (
    ANOMALIES_DATA_PATH,
    ARTIFACTS_DIR,
    ENRICHED_DATA_PATH,
    REGRESSION_METRICS_PATH,
    REGRESSION_MODEL_PATH,
    REGRESSION_PREDICTIONS_PATH,
)

TARGET = "Resultats_DEF"
CATEGORICAL_FEATURES = ["Annee", "Categorie"]
NUMERIC_FEATURES = [
    "Saisine_Plaintes_directes",
    "Saisine_FD",
    "Saisine_ST",
    "Saisine_Autres",
    "Victimes_H",
    "Victimes_F",
    "Victimes_G",
    "Victimes_F_fille",
    "MiseEnCause_Neutralises",
    "MiseEnCause_Interpelles",
]
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES


def _one_hot_encoder() -> OneHotEncoder:
    # Compatibilité avec plusieurs versions de scikit-learn.
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    except TypeError:  # pragma: no cover - anciennes versions
        return OneHotEncoder(handle_unknown="ignore", sparse=False)


def make_preprocessor() -> ColumnTransformer:
    numeric_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", _one_hot_encoder()),
        ]
    )
    return ColumnTransformer(
        [
            ("num", numeric_pipe, NUMERIC_FEATURES),
            ("cat", categorical_pipe, CATEGORICAL_FEATURES),
        ]
    )


def candidate_models() -> dict[str, object]:
    return {
        "Référence médiane": DummyRegressor(strategy="median"),
        "Ridge": Ridge(alpha=10.0),
        "Random Forest": RandomForestRegressor(
            n_estimators=350,
            max_depth=8,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        ),
        "Gradient Boosting": GradientBoostingRegressor(
            n_estimators=220,
            learning_rate=0.035,
            max_depth=3,
            loss="huber",
            random_state=42,
        ),
    }


def _cv_summary(pipe: Pipeline, X: pd.DataFrame, y: pd.Series, cv, groups=None) -> dict:
    scores = cross_validate(
        pipe,
        X,
        y,
        cv=cv,
        groups=groups,
        scoring={
            "mae": "neg_mean_absolute_error",
            "mse": "neg_mean_squared_error",
            "r2": "r2",
        },
        n_jobs=-1,
    )
    return {
        "mae": round(float(-scores["test_mae"].mean()), 4),
        "rmse": round(float(np.sqrt(-scores["test_mse"].mean())), 4),
        "r2": round(float(scores["test_r2"].mean()), 4),
        "r2_ecart_type": round(float(scores["test_r2"].std()), 4),
    }


def evaluate_models(df: pd.DataFrame) -> tuple[list[dict], str, Pipeline, pd.DataFrame, list[dict]]:
    X = df[FEATURES].copy()
    y = df[TARGET].astype(float)

    random_cv = KFold(n_splits=5, shuffle=True, random_state=42)
    period_cv = GroupKFold(n_splits=df["Annee"].nunique())
    groups = df["Annee"]

    results: list[dict] = []
    fitted: dict[str, Pipeline] = {}

    for name, estimator in candidate_models().items():
        pipe = Pipeline([("preprocess", make_preprocessor()), ("model", estimator)])
        random_scores = _cv_summary(pipe, X, y, random_cv)
        period_scores = _cv_summary(pipe, X, y, period_cv, groups=groups)
        pipe.fit(X, y)
        fitted[name] = pipe

        # Diagnostics d'entraînement calculés pour CHAQUE modèle (pas seulement
        # le meilleur), afin de pouvoir repérer un éventuel surapprentissage en
        # comparant ces valeurs aux scores de validation croisée.
        train_pred = np.maximum(pipe.predict(X), 0)
        training_diagnostics = {
            "mae_entrainement": round(float(mean_absolute_error(y, train_pred)), 4),
            "rmse_entrainement": round(float(mean_squared_error(y, train_pred) ** 0.5), 4),
            "r2_entrainement": round(float(r2_score(y, train_pred)), 4),
        }

        results.append(
            {
                "modele": name,
                "validation_kfold": random_scores,
                "validation_par_periode": period_scores,
                # Champs conservés pour compatibilité avec l'interface / artefacts existants.
                "mae_cv": random_scores["mae"],
                "rmse_cv": random_scores["rmse"],
                "r2_cv": random_scores["r2"],
                "r2_cv_ecart_type": random_scores["r2_ecart_type"],
                **training_diagnostics,
            }
        )

    # Le modèle sérialisé est sélectionné sur la RMSE KFold ; la validation par
    # période est reportée séparément pour mesurer la robustesse temporelle.
    best_name = min(results, key=lambda item: item["validation_kfold"]["rmse"])["modele"]
    best_pipe = fitted[best_name]

    cv_predictions = cross_val_predict(best_pipe, X, y, cv=random_cv, n_jobs=-1)
    prediction_table = df[["Record_ID", "Annee", "Categorie", "Infraction_Affaire_traitee"]].copy()
    prediction_table["Valeur_reelle"] = y.to_numpy()
    prediction_table["Prediction_CV"] = np.maximum(cv_predictions, 0).round(2)
    prediction_table["Erreur_absolue"] = (
        prediction_table["Valeur_reelle"] - prediction_table["Prediction_CV"]
    ).abs().round(2)
    prediction_table["Residu"] = (
        prediction_table["Valeur_reelle"] - prediction_table["Prediction_CV"]
    ).round(2)

    importance = permutation_importance(
        best_pipe,
        X,
        y,
        n_repeats=20,
        random_state=42,
        scoring="neg_mean_absolute_error",
        n_jobs=-1,
    )
    importances = sorted(
        [
            {"variable": feature, "importance": round(float(score), 4)}
            for feature, score in zip(FEATURES, importance.importances_mean)
        ],
        key=lambda item: item["importance"],
        reverse=True,
    )
    return results, best_name, best_pipe, prediction_table, importances


def main() -> None:
    if not ANOMALIES_DATA_PATH.exists():
        raise FileNotFoundError("Exécutez d'abord : python -m src.anomaly_detection")
    df = pd.read_csv(ANOMALIES_DATA_PATH)
    results, best_name, best_pipe, predictions, importances = evaluate_models(df)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": best_pipe,
            "features": FEATURES,
            "model_name": best_name,
            "target": TARGET,
        },
        REGRESSION_MODEL_PATH,
    )
    predictions.to_csv(REGRESSION_PREDICTIONS_PATH, index=False, encoding="utf-8-sig")
    df.to_csv(ENRICHED_DATA_PATH, index=False, encoding="utf-8-sig")

    payload = {
        "cible": TARGET,
        "question_modelisation": (
            "Dans quelle mesure les variables agrégées disponibles permettent-elles d'estimer "
            "Resultats_DEF dans cet échantillon ?"
        ),
        "objectif": (
            "Comparer expérimentalement plusieurs modèles pour estimer le nombre de résultats DEF "
            "à partir des saisines, victimes, personnes mises en cause, catégorie et période."
        ),
        "meilleur_modele": best_name,
        "critere_selection": "RMSE moyenne en validation croisée KFold à 5 plis",
        "nombre_observations": int(len(df)),
        "validations": {
            "kfold": (
                "KFold 5 plis, mélange déterministe : performance interne sur des observations "
                "de structure similaire."
            ),
            "par_periode": (
                "GroupKFold par période : une période complète est laissée de côté à chaque pli "
                "pour tester la robustesse entre périodes."
            ),
        },
        "interpretation_metriques": {
            "MAE": "Erreur absolue moyenne, dans l'unité de Resultats_DEF.",
            "RMSE": "Erreur quadratique moyenne ; pénalise davantage les grosses erreurs.",
            "R2": (
                "Part de variabilité expliquée ; un R² négatif signifie que le modèle peut être "
                "moins performant qu'une prédiction constante sur le pli évalué."
            ),
        },
        "resultats": sorted(results, key=lambda row: row["validation_kfold"]["rmse"]),
        "importance_variables_exploratoire": importances,
        "avertissement_importance": (
            "L'importance par permutation mesure une contribution prédictive dans cet échantillon ; "
            "elle ne démontre pas une relation causale."
        ),
        "limites": [
            "Seulement 152 observations agrégées.",
            "Deux années complètes et un premier semestre seulement.",
            "Absence de granularité mensuelle ou journalière.",
            "Absence de géolocalisation fine.",
            "La validation par période peut révéler une performance inférieure à la validation KFold.",
            "Le modèle est une preuve de concept et non un système de prédiction criminelle opérationnel.",
        ],
        "avertissement": (
            "Prototype académique sur trois périodes agrégées. Le modèle ne prédit ni une personne, "
            "ni un quartier, ni un événement futur précis."
        ),
    }
    REGRESSION_METRICS_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
