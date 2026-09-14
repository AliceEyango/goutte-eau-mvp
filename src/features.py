"""
Preparation des variables explicatives.

Le perimetre du MVP est volontairement restreint : l'API ne recoit qu'une
date en entree (cf. enonce). Le modele apprend donc la climatologie du
risque de pluie a partir de la position de la date dans l'annee, station par
station. Cet encodage cyclique (sinus / cosinus du jour de l'annee) evite
la discontinuite artificielle entre le 31 decembre et le 1er janvier.
"""
import math
from datetime import date


def jour_de_l_annee(date_str):
    d = date.fromisoformat(date_str)
    return d.timetuple().tm_yday


def encoder_date(date_str):
    """Retourne les variables explicatives associees a une date (liste)."""
    jda = jour_de_l_annee(date_str)
    angle = 2 * math.pi * jda / 365.25
    return [math.sin(angle), math.cos(angle)]


NOMS_VARIABLES = ["jour_annee_sin", "jour_annee_cos"]


def construire_matrice(mesures):
    """
    Construit (X, y) a partir des mesures issues de la base.
    X : variables explicatives (encodage cyclique de la date)
    y : 1 si pluie observee, 0 sinon
    """
    X, y = [], []
    for m in mesures:
        X.append(encoder_date(m["date"]))
        y.append(int(m["pluie_observee"]))
    return X, y
