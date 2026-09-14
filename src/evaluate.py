"""
Evaluation du modele - indicateurs qualite du MVP.

Quatre indicateurs sont retenus, cohabitant bien avec un probleme de
classification binaire desequilibre (les jours sans pluie restent
majoritaires sur l'annee) :
  - exactitude (accuracy) : proportion de jours correctement classes ;
  - F1-score : compromis precision / rappel sur la classe "pluie" ;
  - AUC-ROC : capacite du modele a ordonner les jours par risque croissant ;
  - Brier score : qualite de calibration de la probabilite renvoyee par
    l'API (plus la valeur est basse, mieux la probabilite reflete la
    frequence reelle de pluie).
"""
from sklearn.metrics import (
    accuracy_score, f1_score, roc_auc_score, brier_score_loss,
    precision_score, recall_score,
)


def evaluer_modele(modele, X_test, y_test):
    y_pred = modele.predict(X_test)
    y_proba = modele.predict_proba(X_test)[:, 1]

    return {
        "exactitude": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "rappel": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "auc_roc": round(roc_auc_score(y_test, y_proba), 4),
        "brier_score": round(brier_score_loss(y_test, y_proba), 4),
    }
