"""
Interface graphique minimale du MVP - Projet Goutte d'eau.

Objectif : prouver le fonctionnement du modele (cf. instructions du bloc 2),
pas de couvrir l'ensemble des usages agricoles (traite dans une phase
ulterieure du cahier des charges).

Lancement local (l'API doit deja tourner sur le port configure) :
    streamlit run ui/streamlit_app.py
"""
import os
import sys
from datetime import date, timedelta

import requests
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

API_URL = f"http://{config.API_HOST}:{config.API_PORT}"

st.set_page_config(page_title="Goutte d'eau - Risque de pluie", page_icon="🌧️", layout="centered")

st.title("Projet Goutte d'eau")
st.subheader("Estimation du risque de pluie - MVP")
st.caption(
    f"Station de reference : {config.STATION_NOM} ({config.STATION_SYNOP_ID}) "
    f"- Region {config.REGION}"
)

with st.form("formulaire_date"):
    date_choisie = st.date_input(
        "Choisissez une date",
        value=date.today() + timedelta(days=1),
        min_value=date(2000, 1, 1),
        max_value=date(2100, 12, 31),
        help="Date pour laquelle estimer le risque de pluie.",
    )
    valider = st.form_submit_button("Estimer le risque")

if valider:
    try:
        reponse = requests.get(
            f"{API_URL}/predict", params={"date": date_choisie.isoformat()}, timeout=10
        )
        reponse.raise_for_status()
        resultat = reponse.json()
    except requests.RequestException as exc:
        st.error(
            "Impossible de contacter l'API. Verifiez qu'elle est demarree "
            f"({API_URL}). Detail technique : {exc}"
        )
    else:
        proba = resultat["probabilite_pluie"]
        niveau = resultat["niveau_risque"]

        couleur = {"faible": "green", "modere": "orange", "eleve": "red"}[niveau]
        libelle = {"faible": "Risque faible", "modere": "Risque modere", "eleve": "Risque eleve"}[niveau]

        st.markdown(f"### Resultat pour le {date_choisie.strftime('%d/%m/%Y')}")
        st.markdown(
            f"<span style='color:{couleur}; font-size:1.3em; font-weight:bold;'>{libelle}</span>",
            unsafe_allow_html=True,
        )
        st.progress(min(max(proba, 0.0), 1.0))
        st.write(f"Probabilite estimee de pluie : **{proba * 100:.1f} %**")
        st.caption(
            "Estimation fondee sur la climatologie historique de la station. "
            "Elle ne remplace pas une prevision meteorologique court terme."
        )

st.divider()
st.caption(
    "Interface de demonstration. Une version accessible et complete sera "
    "realisee dans une phase ulterieure du projet (voir document explicatif, "
    "section accessibilite)."
)
