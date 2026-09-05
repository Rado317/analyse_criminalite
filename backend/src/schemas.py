from pydantic import BaseModel, Field


class PredictionInput(BaseModel):
    annee: str = Field(default="2026-S1")
    categorie: str
    saisine_plaintes_directes: int = Field(default=0, ge=0)
    saisine_fd: int = Field(default=0, ge=0)
    saisine_st: int = Field(default=0, ge=0)
    saisine_autres: int = Field(default=0, ge=0)
    victimes_h: int = Field(default=0, ge=0)
    victimes_f: int = Field(default=0, ge=0)
    victimes_g: int = Field(default=0, ge=0)
    victimes_f_fille: int = Field(default=0, ge=0)
    neutralises: int = Field(default=0, ge=0)
    interpelles: int = Field(default=0, ge=0)


class PredictionOutput(BaseModel):
    resultats_def_estimes: float
    modele: str
    avertissement: str
