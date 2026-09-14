"""
Entrainement du modele d'estimation du risque de pluie.

Choix technique (cf. exigence C12 : pas d'entrainement lourd ou
inapproprie) : une regression logistique sur un encodage cyclique de la
date. Ce modele est volontairement simple :
  - il correspond a la nature de l'entree disponible (une seule date, sans
    mesure en temps reel) ;
  - il s'entraine en quelques secondes sur un poste standard, sans GPU ;
  - il reste interpretable : le risque estime est une probabilite
    climatologique lissee sur l'annee, et non une prevision court terme.
"""
import json
import logging
import os
import sys

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src import db, features
from src.evaluate import evaluer_modele

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("train")


def entrainer():
    mesures = db.fetch_all_mesures()
    if len(mesures) < 100:
        raise RuntimeError(
            "Pas assez de donnees en base pour entrainer un modele "
            f"({len(mesures)} lignes). Lancez d'abord la collecte "
            "(src/collecte.py)."
        )

    X, y = features.construire_matrice(mesures)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    modele = LogisticRegression(max_iter=1000, class_weight="balanced")
    modele.fit(X_train, y_train)

    metriques = evaluer_modele(modele, X_test, y_test)
    metriques["nb_observations_total"] = len(mesures)
    metriques["nb_observations_test"] = len(y_test)
    metriques["variables"] = features.NOMS_VARIABLES
    metriques["station_id"] = config.STATION_SYNOP_ID
    metriques["region"] = config.REGION

    os.makedirs(config.MODELS_DIR, exist_ok=True)
    joblib.dump(modele, config.MODEL_PATH)
    with open(config.METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metriques, f, ensure_ascii=False, indent=2)

    logger.info("Modele entraine et sauvegarde : %s", config.MODEL_PATH)
    logger.info("Metriques : %s", json.dumps(metriques, ensure_ascii=False))
    return metriques


if __name__ == "__main__":
    entrainer()
