from __future__ import annotations

import json
from collections import Counter

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import RobustScaler

from src.config import (
    ANOMALIES_DATA_PATH,
    ANOMALY_METRICS_PATH,
    ANOMALY_MODEL_PATH,
    ARTIFACTS_DIR,
    CLUSTERED_DATA_PATH,
)

ANOMALY_FEATURES = [
    "Saisine_Plaintes_directes",
    "Saisine_FD",
    "Saisine_ST",
    "Saisine_Autres",
    "Total_victimes",
    "MiseEnCause_Neutralises",
    "MiseEnCause_Interpelles",
    "Resultats_En_cours",
    "Resultats_Retraits",
    "Resultats_DAT",
    "Resultats_DEF",
]


def robust_z_scores(series: pd.Series) -> pd.Series:
    values = series.astype(float)
    median = values.median()
    mad = np.median(np.abs(values - median))
    if mad == 0:
        std = values.std(ddof=0)
        if std == 0:
            return pd.Series(np.zeros(len(values)), index=series.index)
        return (values - values.mean()) / std
    return 0.6745 * (values - median) / mad


def detect_anomalies(df: pd.DataFrame, contamination: float = 0.08) -> tuple[pd.DataFrame, dict, Pipeline]:
    out = df.copy()
    X = out[ANOMALY_FEATURES].astype(float)
    pipeline = Pipeline(
        [
            ("scaler", RobustScaler()),
            (
                "model",
                IsolationForest(
                    n_estimators=400,
                    contamination=contamination,
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )
    predictions = pipeline.fit_predict(X)
    raw_scores = pipeline.decision_function(X)

    reasons: list[list[str]] = [[] for _ in range(len(out))]
    # Règle volontairement stricte : seules les valeurs au-delà du 99e percentile
    # ET d'une borne IQR renforcée sont signalées. Cela évite de classer comme
    # anomalies toutes les infractions simplement fréquentes dans une distribution
    # très asymétrique et riche en zéros.
    thresholds: dict[str, float] = {}
    for feature in ANOMALY_FEATURES:
        values = out[feature].astype(float)
        q1 = float(values.quantile(0.25))
        q3 = float(values.quantile(0.75))
        iqr = q3 - q1
        threshold = max(float(values.quantile(0.99)), q3 + 3.0 * iqr)
        thresholds[feature] = threshold
        for position, value in enumerate(values.to_numpy()):
            if value > threshold:
                reasons[position].append(f"{feature}: valeur extrêmement élevée")

    for position, (_, row) in enumerate(out.iterrows()):
        if bool(row.get("Infraction_non_renseignee", False)):
            reasons[position].append("Libellé d'infraction non renseigné")
        if int(row.get("Volume_activite", 0)) == 0:
            reasons[position].append("Ligne sans activité numérique")

    out["Score_anomalie"] = (-raw_scores).round(6)
    out["Anomalie_ML"] = predictions == -1
    out["Raisons_anomalie"] = ["; ".join(items) for items in reasons]
    out["Anomalie_regle"] = out["Raisons_anomalie"].str.len() > 0
    out["Est_anomalie"] = out["Anomalie_ML"] | out["Anomalie_regle"]

    flagged_scores = out.loc[out["Est_anomalie"], "Score_anomalie"]
    q50 = float(flagged_scores.quantile(0.50)) if not flagged_scores.empty else 0.0
    q80 = float(flagged_scores.quantile(0.80)) if not flagged_scores.empty else 0.0

    def severity(row: pd.Series) -> str:
        if not row["Est_anomalie"]:
            return "Normale"
        if row["Infraction_non_renseignee"] or row["Score_anomalie"] >= q80:
            return "Élevée"
        if row["Score_anomalie"] >= q50:
            return "Moyenne"
        return "Faible"

    out["Niveau_anomalie"] = out.apply(severity, axis=1)
    counts = Counter(out.loc[out["Est_anomalie"], "Niveau_anomalie"].tolist())
    # Analyse de sensibilité : le nombre d'anomalies dépend du paramètre
    # contamination. On le documente au lieu de présenter 8 % comme une vérité.
    sensitivity = []
    for value in [0.03, 0.05, 0.08, 0.10, 0.15]:
        test_pipeline = Pipeline(
            [
                ("scaler", RobustScaler()),
                (
                    "model",
                    IsolationForest(
                        n_estimators=300,
                        contamination=value,
                        random_state=42,
                        n_jobs=-1,
                    ),
                ),
            ]
        )
        test_pred = test_pipeline.fit_predict(X)
        sensitivity.append(
            {
                "contamination": value,
                "nombre_anomalies_ml": int((test_pred == -1).sum()),
                "pourcentage": round(float((test_pred == -1).mean() * 100), 2),
            }
        )

    metrics = {
        "algorithme": "Isolation Forest + règles robustes",
        "contamination": contamination,
        "nombre_observations": int(len(out)),
        "nombre_anomalies_ml": int(out["Anomalie_ML"].sum()),
        "nombre_anomalies_regles": int(out["Anomalie_regle"].sum()),
        "nombre_anomalies_finales": int(out["Est_anomalie"].sum()),
        "repartition_severite": dict(counts),
        "variables": ANOMALY_FEATURES,
        "sensibilite_contamination": sensitivity,
        "justification_contamination": (
            "La valeur 0,08 est un réglage exploratoire. Le tableau de sensibilité montre "
            "comment le nombre de cas signalés varie lorsque ce paramètre change."
        ),
        "seuils_regles": {key: round(value, 3) for key, value in thresholds.items()},
        "avertissement": (
            "Une anomalie statistique n'est pas automatiquement une erreur. "
            "Elle doit être vérifiée dans les documents sources."
        ),
    }
    return out, metrics, pipeline


def main() -> None:
    if not CLUSTERED_DATA_PATH.exists():
        raise FileNotFoundError("Exécutez d'abord : python -m src.clustering")
    df = pd.read_csv(CLUSTERED_DATA_PATH)
    anomalies, metrics, pipeline = detect_anomalies(df)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    anomalies.to_csv(ANOMALIES_DATA_PATH, index=False, encoding="utf-8-sig")
    joblib.dump({"pipeline": pipeline, "features": ANOMALY_FEATURES}, ANOMALY_MODEL_PATH)
    ANOMALY_METRICS_PATH.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Détection terminée : {metrics['nombre_anomalies_finales']} anomalies potentielles")


if __name__ == "__main__":
    main()
