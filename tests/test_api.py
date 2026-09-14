"""
Tests de base de l'API. Necessitent qu'un modele ait ete entraine au
prealable (python -m src.collecte --demo && python -m src.train).
"""
import os
import sys

from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.api.main import app

client = TestClient(app)
client.__enter__()  # declenche les evenements de demarrage (chargement du modele)


def test_sante():
    r = client.get("/sante")
    assert r.status_code == 200
    assert r.json()["statut"] == "ok"


def test_predict_date_valide():
    r = client.get("/predict", params={"date": "2026-11-15"})
    assert r.status_code == 200
    corps = r.json()
    assert 0.0 <= corps["probabilite_pluie"] <= 1.0
    assert corps["niveau_risque"] in ("faible", "modere", "eleve")


def test_predict_date_invalide():
    r = client.get("/predict", params={"date": "15-11-2026"})
    assert r.status_code == 422
