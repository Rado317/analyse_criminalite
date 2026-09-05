from __future__ import annotations

from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Infraction(Base):
    __tablename__ = "infractions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    record_id: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    annee: Mapped[str] = mapped_column(String(20), index=True)
    categorie: Mapped[str] = mapped_column(String(255), index=True)
    infraction: Mapped[str] = mapped_column(String(255), index=True)
    infraction_normalisee: Mapped[str] = mapped_column(String(255), index=True)

    saisine_plaintes_directes: Mapped[int] = mapped_column(Integer, default=0)
    saisine_fd: Mapped[int] = mapped_column(Integer, default=0)
    saisine_st: Mapped[int] = mapped_column(Integer, default=0)
    saisine_autres: Mapped[int] = mapped_column(Integer, default=0)
    victimes_h: Mapped[int] = mapped_column(Integer, default=0)
    victimes_f: Mapped[int] = mapped_column(Integer, default=0)
    victimes_g: Mapped[int] = mapped_column(Integer, default=0)
    victimes_f_fille: Mapped[int] = mapped_column(Integer, default=0)
    neutralises: Mapped[int] = mapped_column(Integer, default=0)
    interpelles: Mapped[int] = mapped_column(Integer, default=0)
    resultats_en_cours: Mapped[int] = mapped_column(Integer, default=0)
    resultats_retraits: Mapped[int] = mapped_column(Integer, default=0)
    resultats_dat: Mapped[int] = mapped_column(Integer, default=0)
    resultats_def: Mapped[int] = mapped_column(Integer, default=0)

    total_saisines: Mapped[int] = mapped_column(Integer, default=0)
    total_victimes: Mapped[int] = mapped_column(Integer, default=0)
    total_resultats: Mapped[int] = mapped_column(Integer, default=0)
    volume_activite: Mapped[int] = mapped_column(Integer, default=0)
    taux_def_sur_saisines: Mapped[float] = mapped_column(Float, default=0.0)

    cluster: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    pca_1: Mapped[float | None] = mapped_column(Float, nullable=True)
    pca_2: Mapped[float | None] = mapped_column(Float, nullable=True)
    score_anomalie: Mapped[float | None] = mapped_column(Float, nullable=True)
    est_anomalie: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    niveau_anomalie: Mapped[str] = mapped_column(String(30), default="Normale", index=True)
    raisons_anomalie: Mapped[str] = mapped_column(Text, default="")
    observations: Mapped[str] = mapped_column(Text, default="")
