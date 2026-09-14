"""
Configuration du MVP - Projet Goutte d'eau.

Le pilote (cf. cahier des charges, partie 1) porte sur le departement de
Paris (75). Le MVP est volontairement limite a une seule region : l'Ile-de-
France, via la station SYNOP de reference Paris-Montsouris.
"""
import os

# Station SYNOP Meteo-France utilisee comme source de reference pour le MVP.
# Paris-Montsouris est la station SYNOP officielle de Paris (reseau RESO40 / OMM).
STATION_SYNOP_ID = "07156"
STATION_NOM = "Paris-Montsouris"
REGION = "Ile-de-France"
DEPARTEMENT = "75"

# Jeu de donnees data.gouv.fr (reutilisation citee dans l'enonce) :
# "API de recuperation de donnees meteorologiques du reseau Infoclimat (StatIC)
#  et de Meteo-France (SYNOP)", exposee via l'API tabulaire de data.gouv.fr.
# L'identifiant de ressource ci-dessous doit etre verifie / mis a jour depuis
# la page du jeu de donnees au moment de la mise en production (voir README,
# section "Collecte des donnees").
DATA_GOUV_TABULAR_API_BASE = "https://tabular-api.data.gouv.fr/api/resources"
DATA_GOUV_RESOURCE_ID = "A_COMPLETER_DEPUIS_DATA_GOUV_FR"

# Chemins locaux
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "goutte_eau.db")
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "modele_risque_pluie.joblib")
METRICS_PATH = os.path.join(MODELS_DIR, "metrics.json")

# Fenetre d'historique utilisee pour l'entrainement (annees)
HISTORIQUE_ANNEES = 5

API_HOST = os.environ.get("GOUTTE_EAU_API_HOST", "127.0.0.1")
API_PORT = int(os.environ.get("GOUTTE_EAU_API_PORT", "8000"))
