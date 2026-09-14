"""
API du MVP Goutte d'eau.

Expose une estimation du risque de pluie pour une date donnee, sur la
station de reference du pilote (Paris-Montsouris, region Ile-de-France).

Lancement local :
    uvicorn src.api.main:app --reload
"""
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import joblib

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import config
from src import features
from src.api.schemas import PredictionReponse, SanteReponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("api")

_modele = None
_metriques = {}


def _charger_modele():
    global _modele, _metriques
    if os.path.exists(config.MODEL_PATH):
        _modele = joblib.load(config.MODEL_PATH)
    if os.path.exists(config.METRICS_PATH):
        with open(config.METRICS_PATH, encoding="utf-8") as f:
            _metriques = json.load(f)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _charger_modele()
    if _modele is None:
        logger.warning(
            "Aucun modele trouve (%s). Lancez d'abord src/train.py.",
            config.MODEL_PATH,
        )
    yield


app = FastAPI(
    title="API Projet Goutte d'eau - MVP",
    description=(
        "Estimation du risque de pluie a partir d'une date, sur la station "
        "de reference du pilote (Paris-Montsouris, Ile-de-France)."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

# CORS ouvert en local pour permettre a l'interface Streamlit de consommer l'API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

def _niveau_risque(proba):
    if proba < 0.30:
        return "faible"
    if proba < 0.55:
        return "modere"
    return "eleve"


@app.get("/sante", response_model=SanteReponse, tags=["technique"])
def sante():
    return SanteReponse(
        statut="ok",
        modele_charge=_modele is not None,
        nb_observations_entrainement=_metriques.get("nb_observations_total"),
    )


@app.get("/predict", response_model=PredictionReponse, tags=["prevision"])
def predict(
    date_cible: str = Query(
        ..., alias="date", description="Date cible au format AAAA-MM-JJ", examples=["2026-10-12"]
    )
):
    if _modele is None:
        raise HTTPException(status_code=503, detail="Modele non disponible. Lancez src/train.py.")
    try:
        date.fromisoformat(date_cible)
    except ValueError:
        raise HTTPException(status_code=422, detail="Format de date invalide. Utilisez AAAA-MM-JJ.")

    X = [features.encoder_date(date_cible)]
    proba = float(_modele.predict_proba(X)[0][1])

    return PredictionReponse(
        date=date_cible,
        region=config.REGION,
        station_id=config.STATION_SYNOP_ID,
        probabilite_pluie=round(proba, 3),
        niveau_risque=_niveau_risque(proba),
    )
