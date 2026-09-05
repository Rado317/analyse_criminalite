from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

from src.config import (
    CLEAN_DATA_PATH,
    PROCESSED_DIR,
    QUALITY_REPORT_PATH,
    RAW_DETAIL_PATH,
    RAW_TOTALS_PATH,
    RECONCILIATION_PATH,
)

NUMERIC_COLUMNS = [
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
    "Resultats_En_cours",
    "Resultats_Retraits",
    "Resultats_DAT",
    "Resultats_DEF",
]

TOTAL_COMPARISON_COLUMNS = NUMERIC_COLUMNS.copy()


def read_semicolon_csv(path: Path) -> pd.DataFrame:
    """Lit les CSV fournis, y compris les lignes contenant des caractères spéciaux."""
    return pd.read_csv(
        path,
        sep=";",
        encoding="utf-8-sig",
        engine="python",
        dtype=object,
        on_bad_lines="warn",
    )


def normalize_text(value: object) -> str:
    if pd.isna(value):
        return "inconnu"
    text = str(value).strip().lower().replace("’", "'")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = re.sub(r"[^a-z0-9'\s/-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "inconnu"


def parse_non_negative_integer(value: object) -> int:
    """Convertit '-', vide, NaN et les nombres avec zéros initiaux en entiers."""
    if pd.isna(value):
        return 0
    text = str(value).strip().replace("\u00a0", "").replace(" ", "")
    if text in {"", "-", "--", "nan", "None"}:
        return 0
    text = text.replace(",", ".")
    try:
        number = float(text)
    except ValueError as exc:
        raise ValueError(f"Valeur numérique invalide: {value!r}") from exc
    if number < 0:
        raise ValueError(f"Valeur négative interdite: {value!r}")
    return int(round(number))


def stable_record_id(row: pd.Series) -> str:
    raw = "|".join(
        [
            str(row["Annee"]),
            str(row["Categorie"]),
            str(row["Infraction_normalisee"]),
            str(row.name),
        ]
    )
    return "INF-" + hashlib.sha1(raw.encode("utf-8")).hexdigest()[:12].upper()


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    required = {"Annee", "Categorie", "Infraction_Affaire_traitee"} | set(NUMERIC_COLUMNS)
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Colonnes manquantes: {missing}")

    out = df.copy()
    out["Annee"] = out["Annee"].fillna("Période inconnue").astype(str).str.strip()
    out["Categorie"] = (
        out["Categorie"].fillna("Catégorie inconnue").astype(str).str.strip()
    )

    original_missing_label = out["Infraction_Affaire_traitee"].isna() | (
        out["Infraction_Affaire_traitee"].astype(str).str.strip() == ""
    )
    out["Infraction_Affaire_traitee"] = (
        out["Infraction_Affaire_traitee"]
        .fillna("Infraction non renseignée")
        .astype(str)
        .str.strip()
    )

    # Le fichier détaillé ne devrait pas contenir de lignes de total.
    total_mask = out["Infraction_Affaire_traitee"].str.upper().str.contains(
        r"S/\s*TOTAL|TOTAL\s+GENERAL", regex=True, na=False
    )
    out = out.loc[~total_mask].copy()
    original_missing_label = original_missing_label.loc[out.index]

    if "Infraction_normalisee" not in out.columns:
        out["Infraction_normalisee"] = out["Infraction_Affaire_traitee"].map(normalize_text)
    else:
        provided = out["Infraction_normalisee"].fillna("").astype(str).str.strip()
        out["Infraction_normalisee"] = np.where(
            provided.eq(""),
            out["Infraction_Affaire_traitee"].map(normalize_text),
            provided.map(normalize_text),
        )

    for column in NUMERIC_COLUMNS:
        out[column] = out[column].map(parse_non_negative_integer).astype("int64")

    out["Total_saisines"] = out[
        ["Saisine_Plaintes_directes", "Saisine_FD", "Saisine_ST", "Saisine_Autres"]
    ].sum(axis=1)
    out["Total_victimes"] = out[
        ["Victimes_H", "Victimes_F", "Victimes_G", "Victimes_F_fille"]
    ].sum(axis=1)
    out["Total_resultats"] = out[
        ["Resultats_En_cours", "Resultats_Retraits", "Resultats_DAT", "Resultats_DEF"]
    ].sum(axis=1)
    out["Volume_activite"] = (
        out["Total_saisines"]
        + out["Total_victimes"]
        + out["MiseEnCause_Interpelles"]
        + out["MiseEnCause_Neutralises"]
    )
    out["Taux_DEF_sur_saisines"] = np.where(
        out["Total_saisines"] > 0,
        out["Resultats_DEF"] / out["Total_saisines"],
        0.0,
    ).round(4)
    out["Facteur_annualisation"] = np.where(out["Annee"].eq("2026-S1"), 2.0, 1.0)
    out["Plaintes_directes_annualisees"] = (
        out["Saisine_Plaintes_directes"] * out["Facteur_annualisation"]
    ).round().astype(int)
    out["Infraction_non_renseignee"] = original_missing_label.astype(bool).to_numpy()
    out["Record_ID"] = out.apply(stable_record_id, axis=1)

    if "Observations_Objets_saisis" not in out.columns:
        out["Observations_Objets_saisis"] = ""
    out["Observations_Objets_saisis"] = out["Observations_Objets_saisis"].fillna("").astype(str)

    preferred_order = [
        "Record_ID",
        "Annee",
        "Categorie",
        "Infraction_Affaire_traitee",
        "Infraction_normalisee",
        *NUMERIC_COLUMNS,
        "Total_saisines",
        "Total_victimes",
        "Total_resultats",
        "Volume_activite",
        "Taux_DEF_sur_saisines",
        "Facteur_annualisation",
        "Plaintes_directes_annualisees",
        "Infraction_non_renseignee",
        "Observations_Objets_saisis",
    ]
    out = out[preferred_order].reset_index(drop=True)
    return out


def reconcile_general_totals(clean: pd.DataFrame, totals_path: Path = RAW_TOTALS_PATH) -> pd.DataFrame:
    if not totals_path.exists():
        return pd.DataFrame()

    official = read_semicolon_csv(totals_path)
    for column in TOTAL_COMPARISON_COLUMNS:
        if column in official.columns:
            official[column] = official[column].map(parse_non_negative_integer)

    detail = clean.groupby("Annee", as_index=False)[TOTAL_COMPARISON_COLUMNS].sum()
    rows: list[dict] = []
    for _, official_row in official.iterrows():
        year = str(official_row["Annee"]).strip()
        detail_row = detail.loc[detail["Annee"] == year]
        if detail_row.empty:
            continue
        detail_values = detail_row.iloc[0]
        for column in TOTAL_COMPARISON_COLUMNS:
            official_value = int(official_row.get(column, 0) or 0)
            detail_value = int(detail_values[column])
            rows.append(
                {
                    "Annee": year,
                    "Indicateur": column,
                    "Total_detail": detail_value,
                    "Total_officiel": official_value,
                    "Ecart": detail_value - official_value,
                    "Concordance": detail_value == official_value,
                }
            )
    return pd.DataFrame(rows)


def data_quality_report(clean: pd.DataFrame, reconciliation: pd.DataFrame) -> dict:
    numeric = clean[NUMERIC_COLUMNS]
    year_counts = clean.groupby("Annee").size().astype(int).to_dict()
    category_counts = clean.groupby("Categorie").size().astype(int).to_dict()
    non_matching = 0 if reconciliation.empty else int((~reconciliation["Concordance"]).sum())

    return {
        "nombre_lignes": int(len(clean)),
        "nombre_colonnes": int(clean.shape[1]),
        "periodes": sorted(clean["Annee"].unique().tolist()),
        "nombre_categories": int(clean["Categorie"].nunique()),
        "nombre_infractions_normalisees": int(clean["Infraction_normalisee"].nunique()),
        "lignes_par_periode": year_counts,
        "lignes_par_categorie": category_counts,
        "labels_non_renseignes": int(clean["Infraction_non_renseignee"].sum()),
        "doublons_record_id": int(clean["Record_ID"].duplicated().sum()),
        "valeurs_negatives": int((numeric < 0).sum().sum()),
        "lignes_sans_activite": int((clean["Volume_activite"] == 0).sum()),
        "ecarts_avec_totaux_officiels": non_matching,
        "limites": [
            "Les données sont agrégées par infraction et par période.",
            "2026-S1 couvre seulement le premier semestre.",
            "Aucune date mensuelle, adresse ou coordonnée géographique n'est disponible.",
            "Les résultats ML sont exploratoires et ne servent pas à une décision individuelle.",
        ],
    }


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw = read_semicolon_csv(RAW_DETAIL_PATH)
    clean = clean_dataframe(raw)
    reconciliation = reconcile_general_totals(clean)
    report = data_quality_report(clean, reconciliation)

    clean.to_csv(CLEAN_DATA_PATH, index=False, encoding="utf-8-sig")
    reconciliation.to_csv(RECONCILIATION_PATH, index=False, encoding="utf-8-sig")
    QUALITY_REPORT_PATH.write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Données nettoyées : {CLEAN_DATA_PATH} ({len(clean)} lignes)")
    print(f"Rapport qualité : {QUALITY_REPORT_PATH}")
    print(f"Réconciliation : {RECONCILIATION_PATH}")


if __name__ == "__main__":
    main()
