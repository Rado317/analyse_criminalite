from __future__ import annotations

import json
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Integer, cast, desc, func, select
from sqlalchemy.orm import Session

from scripts.init_db import init_database
from src.config import (
    ALLOWED_ORIGINS,
    ANOMALY_METRICS_PATH,
    CLUSTER_METRICS_PATH,
    QUALITY_REPORT_PATH,
    RECONCILIATION_PATH,
    REGRESSION_METRICS_PATH,
    REGRESSION_MODEL_PATH,
)
from src.database import get_db
from src.models import Infraction
from src.schemas import PredictionInput, PredictionOutput


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        init_database(force=False)
    except Exception as exc:
        print(f"Initialisation DB non bloquante : {exc}")
    yield


app = FastAPI(
    title="API — Analyse intelligente des infractions",
    version="2.0.0",
    description=(
        "API académique pour l'analyse statistique, le clustering, la détection "
        "d'anomalies et l'estimation expérimentale des infractions 2024-2026-S1."
    ),
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def apply_filters(query, annee: str | None, categorie: str | None):
    if annee:
        query = query.where(Infraction.annee == annee)
    if categorie:
        query = query.where(Infraction.categorie == categorie)
    return query


def read_json_file(path, missing_message: str) -> dict:
    if not path.exists():
        raise HTTPException(status_code=404, detail=missing_message)
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/")
def root() -> dict:
    return {
        "message": "API d'analyse intelligente des infractions",
        "documentation": "/docs",
        "version": "2.0.0",
    }


@app.get("/health")
def health(db: Session = Depends(get_db)) -> dict:
    count = db.scalar(select(func.count(Infraction.id))) or 0
    return {"status": "ok", "lignes_en_base": int(count)}


@app.get("/api/v1/years")
def years(db: Session = Depends(get_db)) -> list[str]:
    return list(db.scalars(select(Infraction.annee).distinct().order_by(Infraction.annee)).all())


@app.get("/api/v1/categories")
def categories(db: Session = Depends(get_db)) -> list[str]:
    return list(
        db.scalars(select(Infraction.categorie).distinct().order_by(Infraction.categorie)).all()
    )


@app.get("/api/v1/summary")
def summary(
    annee: str | None = None,
    categorie: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    query = select(
        func.count(Infraction.id),
        func.sum(Infraction.saisine_plaintes_directes),
        func.sum(Infraction.total_saisines),
        func.sum(Infraction.total_victimes),
        func.sum(Infraction.interpelles),
        func.sum(Infraction.resultats_def),
        func.sum(cast(Infraction.est_anomalie, Integer)),
    )
    query = apply_filters(query, annee, categorie)
    row = db.execute(query).one()
    return {
        "annee": annee or "Toutes",
        "categorie": categorie or "Toutes",
        "lignes": int(row[0] or 0),
        "plaintes_directes": int(row[1] or 0),
        "total_saisines": int(row[2] or 0),
        "victimes": int(row[3] or 0),
        "interpelles": int(row[4] or 0),
        "resultats_def": int(row[5] or 0),
        "anomalies": int(row[6] or 0),
    }


@app.get("/api/v1/infractions")
def list_infractions(
    annee: str | None = None,
    categorie: str | None = None,
    cluster: int | None = None,
    anomalie: bool | None = None,
    limit: int = Query(default=200, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = select(Infraction)
    query = apply_filters(query, annee, categorie)
    if cluster is not None:
        query = query.where(Infraction.cluster == cluster)
    if anomalie is not None:
        query = query.where(Infraction.est_anomalie == anomalie)
    rows = db.scalars(query.order_by(desc(Infraction.saisine_plaintes_directes)).limit(limit)).all()
    return [
        {
            "record_id": row.record_id,
            "annee": row.annee,
            "categorie": row.categorie,
            "infraction": row.infraction,
            "plaintes_directes": row.saisine_plaintes_directes,
            "total_saisines": row.total_saisines,
            "victimes": row.total_victimes,
            "interpelles": row.interpelles,
            "resultats_def": row.resultats_def,
            "cluster": row.cluster,
            "pca_1": row.pca_1,
            "pca_2": row.pca_2,
            "est_anomalie": row.est_anomalie,
            "niveau_anomalie": row.niveau_anomalie,
            "score_anomalie": row.score_anomalie,
            "raisons_anomalie": row.raisons_anomalie,
        }
        for row in rows
    ]


@app.get("/api/v1/statistics/by-year")
def statistics_by_year(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        select(
            Infraction.annee,
            func.sum(Infraction.saisine_plaintes_directes),
            func.sum(Infraction.total_victimes),
            func.sum(Infraction.interpelles),
            func.sum(Infraction.resultats_def),
        )
        .group_by(Infraction.annee)
        .order_by(Infraction.annee)
    ).all()
    return [
        {
            "annee": row[0],
            "plaintes_directes": int(row[1] or 0),
            "victimes": int(row[2] or 0),
            "interpelles": int(row[3] or 0),
            "resultats_def": int(row[4] or 0),
        }
        for row in rows
    ]


@app.get("/api/v1/statistics/top-infractions")
def top_infractions(
    metric: str = Query(default="plaintes_directes"),
    annee: str | None = None,
    limit: int = Query(default=15, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[dict]:
    allowed = {
        "plaintes_directes": Infraction.saisine_plaintes_directes,
        "victimes": Infraction.total_victimes,
        "interpelles": Infraction.interpelles,
        "resultats_def": Infraction.resultats_def,
    }
    if metric not in allowed:
        raise HTTPException(status_code=400, detail=f"Métrique invalide. Choix : {list(allowed)}")
    column = allowed[metric]
    query = select(Infraction.infraction, func.sum(column).label("valeur"))
    if annee:
        query = query.where(Infraction.annee == annee)
    rows = db.execute(
        query.group_by(Infraction.infraction).order_by(desc("valeur")).limit(limit)
    ).all()
    return [{"infraction": row[0], "valeur": int(row[1] or 0)} for row in rows]


@app.get("/api/v1/clusters")
def clusters(db: Session = Depends(get_db)) -> list[dict]:
    rows = db.execute(
        select(
            Infraction.cluster,
            func.count(Infraction.id),
            func.avg(Infraction.total_saisines),
            func.avg(Infraction.total_victimes),
            func.avg(Infraction.interpelles),
            func.avg(Infraction.resultats_def),
        )
        .where(Infraction.cluster.is_not(None))
        .group_by(Infraction.cluster)
        .order_by(Infraction.cluster)
    ).all()
    return [
        {
            "cluster": int(row[0]),
            "nombre_lignes": int(row[1]),
            "moyenne_saisines": round(float(row[2] or 0), 2),
            "moyenne_victimes": round(float(row[3] or 0), 2),
            "moyenne_interpelles": round(float(row[4] or 0), 2),
            "moyenne_resultats_def": round(float(row[5] or 0), 2),
        }
        for row in rows
    ]


@app.get("/api/v1/clustering-metrics")
def clustering_metrics() -> dict:
    return read_json_file(CLUSTER_METRICS_PATH, "Clustering non préparé.")


@app.get("/api/v1/anomalies")
def anomalies(
    niveau: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[dict]:
    query = select(Infraction).where(Infraction.est_anomalie.is_(True))
    if niveau:
        query = query.where(Infraction.niveau_anomalie == niveau)
    rows = db.scalars(query.order_by(desc(Infraction.score_anomalie)).limit(limit)).all()
    return [
        {
            "record_id": row.record_id,
            "annee": row.annee,
            "categorie": row.categorie,
            "infraction": row.infraction,
            "niveau": row.niveau_anomalie,
            "score": row.score_anomalie,
            "raisons": row.raisons_anomalie,
            "plaintes_directes": row.saisine_plaintes_directes,
            "victimes": row.total_victimes,
            "interpelles": row.interpelles,
        }
        for row in rows
    ]


@app.get("/api/v1/anomaly-metrics")
def anomaly_metrics() -> dict:
    return read_json_file(ANOMALY_METRICS_PATH, "Détection d'anomalies non préparée.")


@app.get("/api/v1/data-quality")
def data_quality() -> dict:
    return read_json_file(QUALITY_REPORT_PATH, "Rapport qualité absent.")


@app.get("/api/v1/reconciliation")
def reconciliation() -> list[dict]:
    if not RECONCILIATION_PATH.exists():
        raise HTTPException(status_code=404, detail="Réconciliation absente.")
    df = pd.read_csv(RECONCILIATION_PATH)
    return df.to_dict(orient="records")


@app.get("/api/v1/model-metrics")
def model_metrics() -> dict:
    return read_json_file(REGRESSION_METRICS_PATH, "Modèle de régression non préparé.")


@app.post("/api/v1/predict/results-def", response_model=PredictionOutput)
def predict_results_def(payload: PredictionInput) -> PredictionOutput:
    if not REGRESSION_MODEL_PATH.exists():
        raise HTTPException(status_code=503, detail="Modèle absent. Lancez python -m scripts.prepare_all")
    bundle = joblib.load(REGRESSION_MODEL_PATH)
    row = pd.DataFrame(
        [
            {
                "Annee": payload.annee,
                "Categorie": payload.categorie,
                "Saisine_Plaintes_directes": payload.saisine_plaintes_directes,
                "Saisine_FD": payload.saisine_fd,
                "Saisine_ST": payload.saisine_st,
                "Saisine_Autres": payload.saisine_autres,
                "Victimes_H": payload.victimes_h,
                "Victimes_F": payload.victimes_f,
                "Victimes_G": payload.victimes_g,
                "Victimes_F_fille": payload.victimes_f_fille,
                "MiseEnCause_Neutralises": payload.neutralises,
                "MiseEnCause_Interpelles": payload.interpelles,
            }
        ]
    )
    prediction = max(0.0, float(bundle["pipeline"].predict(row)[0]))
    return PredictionOutput(
        resultats_def_estimes=round(prediction, 2),
        modele=str(bundle["model_name"]),
        avertissement=(
            "Estimation académique sur données agrégées. "
            "Ne pas l'utiliser pour une décision individuelle ou opérationnelle."
        ),
    )
