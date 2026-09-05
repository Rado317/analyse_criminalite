import pandas as pd

from src.clustering import CLUSTER_FEATURES, cluster_dataframe


def test_clustering_uses_log_transform_and_creates_clusters():
    rows = []
    for index in range(40):
        row = {feature: (index % 5) + 1 for feature in CLUSTER_FEATURES}
        if index >= 30:
            row = {feature: row[feature] * 8 for feature in CLUSTER_FEATURES}
        rows.append(row)

    out, metrics, bundle = cluster_dataframe(pd.DataFrame(rows))
    assert "Cluster" in out.columns
    assert "PCA_1" in out.columns
    assert metrics["transformation"] == "log1p + StandardScaler"
    assert bundle["transform"] == "log1p"
