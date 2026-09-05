import pandas as pd

from src.train import CATEGORICAL_FEATURES, NUMERIC_FEATURES, TARGET, evaluate_models


def test_training_reports_two_validation_strategies():
    rows = []
    periods = ["2024", "2025", "2026-S1"]
    for index in range(45):
        row = {
            "Record_ID": f"R-{index}",
            "Annee": periods[index % 3],
            "Categorie": f"C{index % 4}",
            "Infraction_Affaire_traitee": f"I{index}",
        }
        for position, feature in enumerate(NUMERIC_FEATURES):
            row[feature] = (index + position) % 12
        row[TARGET] = max(0, int(0.8 * row["MiseEnCause_Interpelles"] + (index % 3)))
        rows.append(row)

    results, best_name, _, predictions, importances = evaluate_models(pd.DataFrame(rows))
    assert best_name
    assert len(results) == 4
    assert "validation_kfold" in results[0]
    assert "validation_par_periode" in results[0]
    assert "Residu" in predictions.columns
    assert len(importances) == len(CATEGORICAL_FEATURES + NUMERIC_FEATURES)
