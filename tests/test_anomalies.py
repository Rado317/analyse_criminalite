import pandas as pd

from src.anomaly_detection import ANOMALY_FEATURES, detect_anomalies


def test_detect_anomalies_adds_expected_columns():
    rows = []
    for index in range(30):
        row = {feature: 1 + (index % 3) for feature in ANOMALY_FEATURES}
        row.update(
            {
                "Record_ID": f"INF-{index}",
                "Infraction_non_renseignee": index == 0,
                "Volume_activite": 10,
            }
        )
        rows.append(row)
    rows[-1]["Saisine_Plaintes_directes"] = 10000
    out, metrics, _ = detect_anomalies(pd.DataFrame(rows), contamination=0.1)
    assert "Est_anomalie" in out.columns
    assert "Niveau_anomalie" in out.columns
    assert metrics["nombre_observations"] == 30
    assert out["Est_anomalie"].any()
