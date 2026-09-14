import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path

NAVY = "#1F3864"
BLUE = "#2E5C8A"
LIGHTBLUE = "#DCE6F1"
GREY = "#F2F2F2"
WHITE = "#FFFFFF"
DARKGREY = "#595959"


def box(ax, x, y, w, h, text, fc=LIGHTBLUE, ec=NAVY, fontsize=10.5, textcolor=NAVY, bold=True):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        linewidth=1.4, edgecolor=ec, facecolor=fc, mutation_aspect=1,
    )
    ax.add_patch(p)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
             fontsize=fontsize, color=textcolor, fontweight="bold" if bold else "normal",
             wrap=True)


def arrow(ax, xy1, xy2, color=DARKGREY, style="-|>", lw=1.6, connectionstyle="arc3,rad=0.0"):
    a = FancyArrowPatch(xy1, xy2, arrowstyle=style, mutation_scale=14,
                         color=color, linewidth=lw, connectionstyle=connectionstyle)
    ax.add_patch(a)


def label(ax, x, y, text, fontsize=8.5, color=DARKGREY, style="italic"):
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color=color, style=style)


# ---------------------------------------------------------------
# Diagramme 1 : architecture generale
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6.2))
ax.set_xlim(0, 11)
ax.set_ylim(0, 6.2)
ax.axis("off")

# Sources externes
box(ax, 0.3, 4.7, 2.4, 1.0, "data.gouv.fr\nAPI tabulaire\n(Infoclimat / SYNOP)", fc=WHITE, ec=DARKGREY, textcolor=DARKGREY, fontsize=9.5)

# Collecte
box(ax, 3.3, 4.7, 2.2, 1.0, "Collecte\n(src/collecte.py)", fc=LIGHTBLUE)
arrow(ax, (2.7, 5.2), (3.3, 5.2))

# Base de donnees
box(ax, 6.1, 4.7, 2.2, 1.0, "Base SQLite\n(mesures journalieres)", fc=LIGHTBLUE)
arrow(ax, (5.5, 5.2), (6.1, 5.2))

# Entrainement
box(ax, 6.1, 3.0, 2.2, 1.0, "Entrainement\n(src/train.py)", fc=LIGHTBLUE)
arrow(ax, (7.2, 4.7), (7.2, 4.0))

# Modele
box(ax, 3.3, 3.0, 2.2, 1.0, "Modele entraine\n(models/*.joblib)", fc="#FDE9D9", ec="#C55A11", textcolor="#C55A11")
arrow(ax, (6.1, 3.5), (5.5, 3.5))

# API
box(ax, 3.3, 1.3, 2.2, 1.0, "API FastAPI\nGET /predict", fc=LIGHTBLUE)
arrow(ax, (4.4, 3.0), (4.4, 2.3))

# UI
box(ax, 6.1, 1.3, 2.2, 1.0, "Interface\nStreamlit", fc=LIGHTBLUE)
arrow(ax, (5.5, 1.8), (6.1, 1.8))

# Utilisateurs
box(ax, 8.9, 1.3, 1.9, 1.0, "Utilisateur\n(demonstration)", fc=WHITE, ec=DARKGREY, textcolor=DARKGREY, fontsize=9.5)
arrow(ax, (8.3, 1.8), (8.9, 1.8))

label(ax, 4.4, 0.9, "date -> probabilite de pluie", fontsize=8.5)
label(ax, 1.5, 4.3, "collecte periodique (batch)", fontsize=8.5)

ax.set_title("Diagramme d'architecture - MVP Projet Goutte d'eau", fontsize=13, color=NAVY, fontweight="bold", pad=14)
plt.tight_layout()
plt.savefig("diagramme_architecture.png", dpi=200, facecolor="white")
plt.close()

# ---------------------------------------------------------------
# Diagramme 2 : diagramme de composants
# ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 7.2))
ax.set_xlim(0, 11)
ax.set_ylim(0, 7.2)
ax.axis("off")

# Conteneur "Collecte et donnees"
box(ax, 0.3, 4.6, 4.6, 2.3, "", fc="#F7F9FC", ec="#B5C7E0", bold=False)
label(ax, 2.6, 6.65, "Collecte et donnees", fontsize=10.5, color=NAVY, style="normal")
box(ax, 0.6, 5.6, 1.9, 0.9, "collecte.py", fc=LIGHTBLUE, fontsize=9)
box(ax, 2.7, 5.6, 1.9, 0.9, "synth_data.py\n(mode demo)", fc=LIGHTBLUE, fontsize=8.5)
box(ax, 1.6, 4.75, 1.9, 0.75, "db.py (SQLite)", fc=LIGHTBLUE, fontsize=9)
arrow(ax, (1.55, 5.6), (2.2, 5.5))
arrow(ax, (3.65, 5.6), (2.9, 5.5))

# Conteneur "Modele"
box(ax, 5.2, 4.6, 3.1, 2.3, "", fc="#F7F9FC", ec="#B5C7E0", bold=False)
label(ax, 6.75, 6.65, "Modelisation", fontsize=10.5, color=NAVY, style="normal")
box(ax, 5.5, 5.6, 1.2, 0.9, "features.py", fc=LIGHTBLUE, fontsize=8.5)
box(ax, 6.9, 5.6, 1.2, 0.9, "train.py", fc=LIGHTBLUE, fontsize=8.5)
box(ax, 6.2, 4.75, 1.3, 0.75, "evaluate.py", fc=LIGHTBLUE, fontsize=8.5)
arrow(ax, (6.7, 6.05), (6.9, 6.05))
arrow(ax, (7.4, 5.6), (6.9, 5.5))

# Conteneur "Service"
box(ax, 0.3, 1.9, 8.0, 2.3, "", fc="#F7F9FC", ec="#B5C7E0", bold=False)
label(ax, 4.3, 3.95, "Service et restitution", fontsize=10.5, color=NAVY, style="normal")
box(ax, 0.6, 2.9, 2.0, 0.9, "api/main.py\n(FastAPI)", fc=LIGHTBLUE, fontsize=8.5)
box(ax, 2.9, 2.9, 2.0, 0.9, "api/schemas.py", fc=LIGHTBLUE, fontsize=8.5)
box(ax, 5.5, 2.9, 2.3, 0.9, "ui/streamlit_app.py", fc=LIGHTBLUE, fontsize=8.5)
box(ax, 3.2, 2.0, 1.9, 0.75, "config.py", fc="#EDEDED", ec=DARKGREY, textcolor=DARKGREY, fontsize=8.5)
arrow(ax, (2.6, 3.35), (2.9, 3.35))
arrow(ax, (4.9, 3.35), (5.5, 3.35))
arrow(ax, (4.15, 2.75), (4.15, 2.9), connectionstyle="arc3,rad=0.0")

# Conteneur "Qualite"
box(ax, 8.7, 1.9, 2.1, 2.3, "", fc="#F7F9FC", ec="#B5C7E0", bold=False)
label(ax, 9.75, 3.95, "Qualite", fontsize=10.5, color=NAVY, style="normal")
box(ax, 8.9, 2.9, 1.7, 0.9, "tests/\ntest_api.py", fc=LIGHTBLUE, fontsize=8.5)

arrow(ax, (2.6, 4.75), (2.6, 4.6))       # db -> modelisation (via train qui lit la db)
arrow(ax, (2.6, 4.75), (1.6, 3.8), connectionstyle="arc3,rad=-0.25")
arrow(ax, (6.75, 4.6), (1.6, 3.8), connectionstyle="arc3,rad=0.25")
arrow(ax, (8.6, 3.35), (8.9, 3.35))

ax.set_title("Diagramme de composants - MVP Projet Goutte d'eau", fontsize=13, color=NAVY, fontweight="bold", pad=14)
plt.tight_layout()
plt.savefig("diagramme_composants.png", dpi=200, facecolor="white")
plt.close()

print("Diagrammes generes.")
