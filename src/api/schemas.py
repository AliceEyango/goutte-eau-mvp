from pydantic import BaseModel, Field


class PredictionReponse(BaseModel):
    date: str = Field(..., description="Date interrogee, format AAAA-MM-JJ")
    region: str
    station_id: str
    probabilite_pluie: float = Field(..., ge=0, le=1, description="Probabilite estimee de pluie (0 a 1)")
    niveau_risque: str = Field(..., description="faible, modere ou eleve")


class SanteReponse(BaseModel):
    statut: str
    modele_charge: bool
    nb_observations_entrainement: int | None = None
