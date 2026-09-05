from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from src.config import (
    ARTIFACTS_DIR,
    CLEAN_DATA_PATH,
    CLUSTERED_DATA_PATH,
    CLUSTER_METRICS_PATH,
    CLUSTER_MODEL_PATH,
)

CLUSTER_FEATURES = [
    "Total_saisines",
    "Total_victimes",
    "MiseEnCause_Interpelles",
    "MiseEnCause_Neutralises",
    "Resultats_DEF",
    "Resultats_En_cours",
]


def _transform_counts(X: pd.DataFrame, use_log1p: bool) -> tuple[np.ndarray, StandardScaler]:
    """Prépare les variables de comptage avant K-Means.

    log1p réduit l'influence des valeurs extrêmes tout en conservant les zéros.
    Cette transformation est adaptée ici car les variables sont des comptages
    très asymétriques.
    """
    values = X.astype(float).to_numpy()
    if use_log1p:
        values = np.log1p(values)
    scaler = StandardScaler()
    return scaler.fit_transform(values), scaler


def evaluate_k_values(X_scaled: np.ndarray) -> list[dict]:
    rows: list[dict] = []
    max_k = min(6, len(X_scaled) - 1)
    for k in range(2, max_k + 1):
        labels = KMeans(n_clusters=k, n_init=30, random_state=42).fit_predict(X_scaled)
        if len(set(labels)) < 2:
            continue
        counts = pd.Series(labels).value_counts().sort_index()
        rows.append(
            {
                "k": int(k),
                "silhouette": float(silhouette_score(X_scaled, labels)),
                "taille_min_cluster": int(counts.min()),
                "taille_max_cluster": int(counts.max()),
                "ratio_cluster_min": float(counts.min() / len(labels)),
                "tailles_clusters": {str(int(i)): int(v) for i, v in counts.items()},
            }
        )
    return rows


def choose_k(rows: list[dict]) -> int:
    if not rows:
        raise ValueError("Pas assez de diversité pour calculer le clustering.")

    # On évite qu'un score silhouette très élevé soit retenu uniquement parce
    # qu'il isole quelques valeurs extrêmes dans un micro-cluster.
    eligible = [row for row in rows if row["ratio_cluster_min"] >= 0.05]
    candidates = eligible or rows
    return int(max(candidates, key=lambda row: row["silhouette"])["k"])


def cluster_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, dict, dict]:
    X = df[CLUSTER_FEATURES].astype(float)

    # Diagnostic scientifique : comparer valeurs brutes et transformation log1p.
    X_raw_scaled, _ = _transform_counts(X, use_log1p=False)
    raw_diagnostics = evaluate_k_values(X_raw_scaled)

    X_scaled, scaler = _transform_counts(X, use_log1p=True)
    log_diagnostics = evaluate_k_values(X_scaled)
    best_k = choose_k(log_diagnostics)

    kmeans = KMeans(n_clusters=best_k, n_init=40, random_state=42)
    labels = kmeans.fit_predict(X_scaled)
    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X_scaled)

    out = df.copy()
    out["Cluster"] = labels.astype(int)
    out["PCA_1"] = coords[:, 0]
    out["PCA_2"] = coords[:, 1]

    profile = (
        out.groupby("Cluster")[CLUSTER_FEATURES]
        .mean()
        .round(2)
        .reset_index()
        .to_dict(orient="records")
    )
    sizes = out["Cluster"].value_counts().sort_index().astype(int).to_dict()
    selected = next(row for row in log_diagnostics if row["k"] == best_k)

    metrics = {
        "algorithme": "K-Means sur log1p(comptages) puis StandardScaler",
        "transformation": "log1p + StandardScaler",
        "justification_transformation": (
            "Les variables de comptage sont fortement asymétriques et riches en zéros. "
            "log1p réduit l'influence des valeurs extrêmes sans supprimer les observations."
        ),
        "meilleur_k": best_k,
        "score_silhouette": float(selected["silhouette"]),
        "diagnostic_brut": raw_diagnostics,
        "diagnostic_log1p": log_diagnostics,
        "regle_selection_k": (
            "Maximisation du score silhouette parmi les solutions dont le plus petit cluster "
            "représente au moins 5 % des observations, si une telle solution existe."
        ),
        "variance_pca_expliquee": [float(x) for x in pca.explained_variance_ratio_],
        "taille_clusters": {str(k): int(v) for k, v in sizes.items()},
        "profils": profile,
        "interpretation": (
            "Les clusters représentent des profils statistiques exploratoires. "
            "Ils ne mesurent ni la dangerosité ni un risque individuel."
        ),
        "limite": (
            "Le résultat dépend du choix des variables, de la transformation et de k. "
            "Une validation métier est nécessaire avant toute interprétation opérationnelle."
        ),
    }
    bundle = {
        "scaler": scaler,
        "kmeans": kmeans,
        "pca": pca,
        "features": CLUSTER_FEATURES,
        "best_k": best_k,
        "transform": "log1p",
    }
    return out, metrics, bundle


def main() -> None:
    if not CLEAN_DATA_PATH.exists():
        raise FileNotFoundError("Exécutez d'abord : python -m src.data_cleaning")
    df = pd.read_csv(CLEAN_DATA_PATH)
    clustered, metrics, bundle = cluster_dataframe(df)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    clustered.to_csv(CLUSTERED_DATA_PATH, index=False, encoding="utf-8-sig")
    joblib.dump(bundle, CLUSTER_MODEL_PATH)
    CLUSTER_METRICS_PATH.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        f"Clustering terminé : k={metrics['meilleur_k']}, "
        f"silhouette={metrics['score_silhouette']:.3f} (log1p + standardisation)"
    )


if __name__ == "__main__":
    main()
