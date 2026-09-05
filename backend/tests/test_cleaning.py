import pandas as pd

from src.data_cleaning import clean_dataframe


def test_clean_dataframe_creates_features():
    df = pd.DataFrame(
        [
            {
                "Annee": "2026-S1",
                "Categorie": "Test",
                "Infraction_Affaire_traitee": "Vol à main armée",
                "Saisine_Plaintes_directes": "02",
                "Saisine_FD": "-",
                "Saisine_ST": None,
                "Saisine_Autres": 1,
                "Victimes_H": 1,
                "Victimes_F": 2,
                "Victimes_G": 0,
                "Victimes_F_fille": 0,
                "MiseEnCause_Neutralises": 0,
                "MiseEnCause_Interpelles": 1,
                "Resultats_En_cours": 0,
                "Resultats_Retraits": 0,
                "Resultats_DAT": 0,
                "Resultats_DEF": 1,
            }
        ]
    )
    out = clean_dataframe(df)
    assert out.loc[0, "Saisine_Plaintes_directes"] == 2
    assert out.loc[0, "Saisine_FD"] == 0
    assert out.loc[0, "Total_victimes"] == 3
    assert out.loc[0, "Plaintes_directes_annualisees"] == 4
    assert out.loc[0, "Record_ID"].startswith("INF-")
