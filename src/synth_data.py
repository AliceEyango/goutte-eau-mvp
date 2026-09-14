"""
Generateur de donnees synthetiques - MODE DEMO / HORS LIGNE UNIQUEMENT.

Ce module ne remplace pas la collecte reelle (voir collecte.py). Il sert a
deux choses :
  1. permettre de faire tourner l'ensemble du pipeline (base, entrainement,
     API, interface) sans dependre d'un acces reseau a data.gouv.fr, par
     exemple dans un environnement de developpement isole ou en sandbox ;
  2. fournir un jeu de donnees de demonstration reproductible pour les tests.

Le generateur reproduit, de facon simplifiee, la climatologie connue de
Paris-Montsouris : frequence de jours de pluie plus elevee en automne et en
hiver, plus faible en ete, avec un cumul moyen coherent avec les normales
saisonnieres publiees par Meteo-France. Les valeurs ne doivent pas etre
utilisees comme donnees d'observation reelles.
"""
import random
from datetime import date, timedelta

import config

# Probabilite de jour pluvieux par mois, approximee a partir des normales
# 1991-2020 de Paris-Montsouris (nombre moyen de jours de pluie par mois).
PROBA_PLUIE_PAR_MOIS = {
    1: 0.36, 2: 0.33, 3: 0.34, 4: 0.33, 5: 0.35, 6: 0.31,
    7: 0.29, 8: 0.28, 9: 0.30, 10: 0.36, 11: 0.38, 12: 0.38,
}
TEMPERATURE_MOY_PAR_MOIS = {
    1: 5.5, 2: 6.2, 3: 9.3, 4: 12.0, 5: 15.5, 6: 18.7,
    7: 21.0, 8: 20.8, 9: 17.3, 10: 13.2, 11: 8.8, 12: 5.9,
}
SEUIL_PLUIE_MM = 1.0  # seuil retenu pour considerer un jour comme "jour de pluie"


def generer_historique(annees=config.HISTORIQUE_ANNEES, graine=42):
    """
    Genere un historique journalier synthetique sur `annees` annees pleines,
    se terminant a la veille d'aujourd'hui.
    """
    rng = random.Random(graine)
    fin = date.today() - timedelta(days=1)
    debut = fin.replace(year=fin.year - annees)

    lignes = []
    jour = debut
    while jour <= fin:
        proba = PROBA_PLUIE_PAR_MOIS[jour.month]
        pluie = 1 if rng.random() < proba else 0
        cumul = round(max(0.0, rng.gammavariate(1.6, 4.0)), 1) if pluie else 0.0
        # un cumul peut rester sous le seuil malgre un tirage "pluie"
        pluie_observee = 1 if cumul >= SEUIL_PLUIE_MM else 0
        temp_base = TEMPERATURE_MOY_PAR_MOIS[jour.month]
        temperature = round(rng.gauss(temp_base, 2.2), 1)

        lignes.append({
            "date": jour.isoformat(),
            "station_id": config.STATION_SYNOP_ID,
            "precipitations_mm": cumul,
            "pluie_observee": pluie_observee,
            "temperature_moy_c": temperature,
            "source": "synthetique_demo",
        })
        jour += timedelta(days=1)
    return lignes
