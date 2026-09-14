# Projet Goutte d'eau — MVP (bloc 2)

MVP de l'architecture fonctionnelle du Projet Goutte d'eau : collecte de
données météorologiques, entraînement d'un modèle de risque de pluie,
restitution via une API, démonstration via une interface graphique.

Ce document complète le cahier des charges (partie 1) livré à l'issue du
bloc 1. Il couvre le périmètre du bloc 2 : planification, architecture,
développement du MVP, éco-responsabilité et accessibilité.

## 1. Périmètre

Conformément à l'énoncé, le MVP est limité à une seule région : l'Île-de-
France, via la station SYNOP de référence **Paris-Montsouris (07156)**,
cohérente avec le département pilote (75) retenu dans le cahier des charges.

L'entrée de l'API est une simple date. Le modèle ne reçoit donc pas de
mesure en temps réel : il apprend la climatologie du risque de pluie à
cette période de l'année, sur la base de l'historique collecté. Cette
estimation est un indicateur de tendance saisonnière, pas une prévision
météorologique court terme au sens du modèle final visé par le projet.

## 2. Architecture

Voir `diagrams/diagramme_architecture.png` et `diagrams/diagramme_composants.png`.

Le pipeline se déroule en quatre étapes découplées :

1. **Collecte** (`src/collecte.py`) : interroge l'API tabulaire de
   data.gouv.fr sur la réutilisation *« API de récupération de données
   météorologiques du réseau Infoclimat (StatIC) et de Météo-France
   (SYNOP) »*, filtrée sur la station Paris-Montsouris, et enregistre les
   mesures nettoyées en base.
2. **Base de données** (`src/db.py`) : SQLite, table unique
   `mesures_journalieres`, limitée aux champs utiles à l'entraînement
   (date, précipitations, indicateur binaire de pluie, température de
   contexte, source).
3. **Entraînement** (`src/train.py`, `src/features.py`,
   `src/evaluate.py`) : régression logistique sur un encodage cyclique de
   la date, choisie pour rester légère (pas de deep learning) et cohérente
   avec la nature de l'entrée disponible.
4. **Restitution** : API FastAPI (`src/api/main.py`, endpoint
   `GET /predict?date=AAAA-MM-JJ`) et interface Streamlit
   (`ui/streamlit_app.py`) consommant cette API.

## 3. Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4. Collecte des données

Deux modes sont disponibles.

### Mode réel

```bash
python -m src.collecte
```

Ce mode interroge l'API tabulaire de data.gouv.fr. Il nécessite de
renseigner au préalable, dans `config.py`, l'identifiant de la ressource
SYNOP correspondant à la reprise citée dans l'énoncé (visible sur la page
du jeu de données, rubrique « ressources »). L'API impose un découpage par
page ou par période (limite de volume par requête) : la collecte gère la
pagination et applique une politique de nouvelle tentative en cas d'échec
réseau ponctuel.

### Mode démonstration (hors ligne)

```bash
python -m src.collecte --demo
```

Ce mode génère un historique synthétique reproduisant, de façon
simplifiée, la climatologie connue de Paris-Montsouris (fréquence de jours
de pluie par mois, température moyenne). Il a été utilisé pour valider
l'ensemble du pipeline dans l'environnement de développement de ce
livrable, qui n'a pas d'accès sortant vers data.gouv.fr. **Ces données
sont clairement marquées `source = "synthetique_demo"` en base et ne
doivent jamais être utilisées pour une mise en production.**

## 5. Entraînement et évaluation

```bash
python -m src.train
```

Le modèle et ses métriques sont sauvegardés dans `models/`. Quatre
indicateurs qualité sont calculés (voir `src/evaluate.py`) :

| Indicateur | Rôle |
|---|---|
| Exactitude | Proportion de jours correctement classés |
| F1-score | Compromis précision / rappel sur la classe « pluie » |
| AUC-ROC | Capacité à ordonner les jours par risque croissant |
| Brier score | Qualité de calibration de la probabilité restituée |

Sur le jeu de démonstration (5 ans, 1 827 jours), les valeurs obtenues sont
consultables dans `models/metrics.json` après exécution. Elles serviront
de référence de comparaison une fois le modèle réentraîné sur des données
réelles.

## 6. Lancement de l'API et de l'interface

```bash
uvicorn src.api.main:app --reload
# dans un second terminal
streamlit run ui/streamlit_app.py
```

Endpoints exposés :

- `GET /predict?date=AAAA-MM-JJ` : probabilité de pluie et niveau de risque
  (faible, modéré, élevé).
- `GET /sante` : état du service et du modèle chargé.
- `GET /docs` : documentation interactive générée par FastAPI (OpenAPI).

## 7. Tests

```bash
pytest tests/
```

## 8. Éco-responsabilité

Le MVP applique plusieurs bonnes pratiques dès cette phase, en cohérence
avec l'exigence C12 du bloc de compétences.

- **Sobriété du modèle** : régression logistique à deux variables plutôt
  qu'un réseau de neurones. L'entraînement complet s'exécute en quelques
  secondes sur un poste standard, sans ressource GPU, pour un usage à
  faible impact évalué autour de quelques wattheures.
- **Sobriété des données** : seuls les champs nécessaires à l'entraînement
  sont conservés en base (pas de champ brut inutile). La collecte cible
  une seule station, conformément au périmètre du pilote, plutôt que
  l'ensemble du réseau national.
- **Fréquence de réentraînement raisonnée** : un modèle climatologique
  évolue lentement. Un réentraînement mensuel, voire saisonnier, suffit et
  évite des cycles de calcul inutiles.
- **Choix d'hébergement** : pour la suite du projet, un hébergement chez
  un fournisseur ayant publié une trajectoire de décarbonation vérifiable
  (objectifs PUE et part d'énergie renouvelable communiqués) sera
  privilégié. Les offres à considérer pour la mise en production incluent
  les fournisseurs disposant de certifications environnementales
  reconnues (ISO 14001, label du Green Web Foundation ou équivalent) et
  d'un centre de données situé en France ou dans l'Union européenne, ce
  qui limite également la latence et facilite la conformité RGPD abordée
  dans le cahier des charges.
- **Dimensionnement à la demande** : l'API et l'entraînement étant peu
  gourmands, un hébergement mutualisé ou une instance de petite taille
  suffisent pour ce pilote, évitant un surdimensionnement de
  l'infrastructure.

## 9. Accessibilité

L'interface Streamlit livrée est une démonstration fonctionnelle, pas
l'interface finale. Les règles suivantes sont documentées ici pour guider
la phase ultérieure de conception d'une interface complète, conformément
au référentiel général d'amélioration de l'accessibilité (RGAA), déclinaison
française des normes WCAG :

- contraste suffisant entre texte et fond (ratio minimal de 4,5:1 pour le
  texte courant) ;
- navigation complète au clavier, sans dépendance à la souris ;
- libellés explicites pour chaque champ de saisie (le sélecteur de date
  doit être annoncé correctement par les lecteurs d'écran) ;
- indication du niveau de risque non fondée uniquement sur la couleur : un
  libellé textuel (« risque faible / modéré / élevé ») accompagne toujours
  le code couleur, déjà appliqué dans la version actuelle de l'interface ;
- structure de page hiérarchisée (titres, sous-titres) pour faciliter la
  navigation par les technologies d'assistance ;
- textes alternatifs pour tout élément visuel porteur d'information dans
  les versions futures (graphiques, cartes).

## 10. Limites connues et prochaines étapes

- Le modèle actuel est purement climatologique (fonction de la date
  seule). L'intégration des flux de capteurs IoT en temps réel, prévue au
  cahier des charges, permettra de passer d'une estimation saisonnière à
  une prévision court terme, conformément à l'ambition du projet.
- La collecte réelle nécessite de finaliser l'identifiant de ressource
  data.gouv.fr dans `config.py` et un accès réseau sortant vers ce
  domaine, non disponible dans l'environnement où ce livrable a été
  développé et testé.
- L'interface graphique sera reprise dans une phase ultérieure pour
  répondre pleinement aux règles d'accessibilité listées en section 9.
