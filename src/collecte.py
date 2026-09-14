"""
Collecte des donnees meteorologiques et enregistrement en base.

Source de reference : API tabulaire de data.gouv.fr, sur la reutilisation
"API de recuperation de donnees meteorologiques du reseau Infoclimat (StatIC)
et de Meteo-France (SYNOP)". Seule la station Paris-Montsouris (07156) est
collectee, conformement au perimetre du MVP (une seule region).

Utilisation :
    python -m src.collecte --demo            # mode hors ligne / demonstration
    python -m src.collecte                    # collecte reelle via l'API

Le mode --demo genere un historique synthetique documente (src/synth_data.py)
et permet de valider l'ensemble du pipeline (base, entrainement, API,
interface) sans dependance reseau. Le mode reel interroge l'API tabulaire de
data.gouv.fr et necessite un acces internet sortant vers data.gouv.fr, ainsi
que l'identifiant de ressource a renseigner dans config.py.
"""
import argparse
import logging
import sys
import time
import os

import requests

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src import db, synth_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("collecte")

SEUIL_PLUIE_MM = 1.0
PAGE_SIZE = 1000
TIMEOUT_S = 30
MAX_RETRIES = 3


def _requete_page(session, page):
    """
    Interroge une page de l'API tabulaire de data.gouv.fr pour la ressource
    configuree, filtree sur la station SYNOP cible.

    L'API tabulaire pagine ses resultats et impose de decouper les requetes
    en periodes ou en pages successives (cf. description de la reutilisation
    sur data.gouv.fr : "il faut donc decouper en periodes temporelles").
    """
    url = f"{config.DATA_GOUV_TABULAR_API_BASE}/{config.DATA_GOUV_RESOURCE_ID}/data/"
    params = {"page": page, "page_size": PAGE_SIZE, "id_station": config.STATION_SYNOP_ID}
    for tentative in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, params=params, timeout=TIMEOUT_S)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            logger.warning("Tentative %s/%s echouee (%s)", tentative, MAX_RETRIES, exc)
            time.sleep(2 * tentative)
    raise RuntimeError(f"Echec de la collecte apres {MAX_RETRIES} tentatives (page {page})")


def _normaliser_ligne(ligne_brute):
    """
    Convertit une ligne brute de l'API SYNOP vers le schema minimal stocke
    en base (cf. exigence C12 : pas de champ inutile a l'entrainement).
    """
    cumul = ligne_brute.get("rr24") or ligne_brute.get("precipitations_mm") or 0.0
    try:
        cumul = float(cumul)
    except (TypeError, ValueError):
        cumul = 0.0
    date_mesure = (ligne_brute.get("date") or ligne_brute.get("validity_date") or "")[:10]
    temperature = ligne_brute.get("t") or ligne_brute.get("temperature_moy_c")
    return {
        "date": date_mesure,
        "station_id": config.STATION_SYNOP_ID,
        "precipitations_mm": cumul,
        "pluie_observee": 1 if cumul >= SEUIL_PLUIE_MM else 0,
        "temperature_moy_c": float(temperature) if temperature not in (None, "") else None,
        "source": "synop",
    }


def collecter_donnees_reelles():
    if config.DATA_GOUV_RESOURCE_ID.startswith("A_COMPLETER"):
        raise RuntimeError(
            "Identifiant de ressource data.gouv.fr non renseigne. "
            "Ouvrez la page du jeu de donnees sur data.gouv.fr, copiez "
            "l'identifiant de la ressource SYNOP et renseignez-le dans "
            "config.DATA_GOUV_RESOURCE_ID avant de lancer la collecte reelle."
        )
    session = requests.Session()
    page = 1
    total_lignes = 0
    while True:
        payload = _requete_page(session, page)
        lignes = payload.get("data", [])
        if not lignes:
            break
        lignes_normalisees = [_normaliser_ligne(l) for l in lignes if l.get("date") or l.get("validity_date")]
        db.upsert_mesures(lignes_normalisees)
        total_lignes += len(lignes_normalisees)
        logger.info("Page %s : %s lignes inserees (total %s)", page, len(lignes_normalisees), total_lignes)
        if not payload.get("next_page") and len(lignes) < PAGE_SIZE:
            break
        page += 1
    logger.info("Collecte reelle terminee : %s lignes en base.", total_lignes)


def collecter_donnees_demo():
    lignes = synth_data.generer_historique()
    db.upsert_mesures(lignes)
    logger.info("Mode demo : %s lignes synthetiques inserees en base.", len(lignes))
    logger.warning(
        "Ces donnees sont synthetiques (climatologie approximee de Paris-Montsouris) "
        "et servent uniquement a valider le pipeline hors ligne. "
        "Elles ne doivent pas etre utilisees comme donnees d'observation reelles."
    )


def main():
    parser = argparse.ArgumentParser(description="Collecte des mesures meteorologiques du MVP Goutte d'eau.")
    parser.add_argument("--demo", action="store_true", help="Utiliser le generateur de donnees hors ligne.")
    args = parser.parse_args()

    db.init_db()
    if args.demo:
        collecter_donnees_demo()
    else:
        collecter_donnees_reelles()
    logger.info("Total de mesures en base : %s", db.count_mesures())


if __name__ == "__main__":
    main()
