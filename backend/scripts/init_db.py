from __future__ import annotations

import argparse

import pandas as pd
from sqlalchemy import delete, func, select

from src.config import ENRICHED_DATA_PATH
from src.database import Base, SessionLocal, engine
from src.models import Infraction


def to_bool(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def row_to_model(row: pd.Series) -> Infraction:
    return Infraction(
        record_id=str(row["Record_ID"]),
        annee=str(row["Annee"]),
        categorie=str(row["Categorie"]),
        infraction=str(row["Infraction_Affaire_traitee"]),
        infraction_normalisee=str(row["Infraction_normalisee"]),
        saisine_plaintes_directes=int(row["Saisine_Plaintes_directes"]),
        saisine_fd=int(row["Saisine_FD"]),
        saisine_st=int(row["Saisine_ST"]),
        saisine_autres=int(row["Saisine_Autres"]),
        victimes_h=int(row["Victimes_H"]),
        victimes_f=int(row["Victimes_F"]),
        victimes_g=int(row["Victimes_G"]),
        victimes_f_fille=int(row["Victimes_F_fille"]),
        neutralises=int(row["MiseEnCause_Neutralises"]),
        interpelles=int(row["MiseEnCause_Interpelles"]),
        resultats_en_cours=int(row["Resultats_En_cours"]),
        resultats_retraits=int(row["Resultats_Retraits"]),
        resultats_dat=int(row["Resultats_DAT"]),
        resultats_def=int(row["Resultats_DEF"]),
        total_saisines=int(row["Total_saisines"]),
        total_victimes=int(row["Total_victimes"]),
        total_resultats=int(row["Total_resultats"]),
        volume_activite=int(row["Volume_activite"]),
        taux_def_sur_saisines=float(row["Taux_DEF_sur_saisines"]),
        cluster=int(row["Cluster"]) if pd.notna(row.get("Cluster")) else None,
        pca_1=float(row["PCA_1"]) if pd.notna(row.get("PCA_1")) else None,
        pca_2=float(row["PCA_2"]) if pd.notna(row.get("PCA_2")) else None,
        score_anomalie=float(row["Score_anomalie"]) if pd.notna(row.get("Score_anomalie")) else None,
        est_anomalie=to_bool(row.get("Est_anomalie", False)),
        niveau_anomalie=str(row.get("Niveau_anomalie", "Normale")),
        raisons_anomalie=str(row.get("Raisons_anomalie", "")) if pd.notna(row.get("Raisons_anomalie")) else "",
        observations=str(row.get("Observations_Objets_saisis", "")) if pd.notna(row.get("Observations_Objets_saisis")) else "",
    )


def init_database(force: bool = False) -> int:
    if not ENRICHED_DATA_PATH.exists():
        raise FileNotFoundError("Données enrichies absentes. Lancez : python -m scripts.prepare_artifacts")

    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        current_count = db.scalar(select(func.count(Infraction.id))) or 0
        if current_count and not force:
            return int(current_count)
        if force:
            db.execute(delete(Infraction))
            db.commit()

        df = pd.read_csv(ENRICHED_DATA_PATH)
        db.add_all([row_to_model(row) for _, row in df.iterrows()])
        db.commit()
        return len(df)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Remplace les données existantes")
    args = parser.parse_args()
    count = init_database(force=args.force)
    print(f"Base initialisée : {count} lignes")


if __name__ == "__main__":
    main()
