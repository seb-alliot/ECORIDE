import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64


# Fonction pour créer un graphique des réservations et des gains par jour
# Entierement commenté pour m'en souvenir plus tard
def Graphique(jours, resa, gains):
    # Crée une figure et un axe de graphique avec une taille de 10x4 pouces
    fig, ax1 = plt.subplots(figsize=(10, 4))

    # Définit la largeur des barres du graphique
    bar_width = 0.35
    # Crée une liste de positions [0, 1, 2, 3...] pour placer les barres sur l'axe X
    x = range(len(jours))

    # Dessine les barres pour les réservations (première série)
    # x = positions, resa = hauteurs, bar_width = largeur, color = couleur des barres
    ax1.bar(x, resa, bar_width, label='Réservations', color='skyblue')

    # Dessine les barres pour les gains (deuxième série), décalées à droite de bar_width
    # [i + bar_width for i in x] décale chaque barre pour qu'elles soient côte à côte
    ax1.bar([i + bar_width for i in x], gains, bar_width, label='Gains (€)', color='salmon')

    # label optionnels pour les axes et le titre
    # Définit le label de l'axe X (horizontal)
    ax1.set_xlabel('Jour')
    # Définit le label de l'axe Y (vertical)
    ax1.set_ylabel('Valeurs')
    # Définit le titre du graphique
    ax1.set_title('Graphique des réservations et gains par jour')

    # Positionne les graduations (ticks) de l'axe X au centre entre les deux barres
    # [i + bar_width / 2 for i in x] centre le label entre réservations et gains
    ax1.set_xticks([i + bar_width / 2 for i in x])
    # Remplace les numéros par les noms des jours (Lundi, Mardi, etc.)
    ax1.set_xticklabels(jours)
    # Affiche la légende (Réservations, Gains) en haut du graphique
    ax1.legend()

    # Crée un buffer mémoire (fichier virtuel) pour stocker l'image sans l'écrire sur disque
    buffer = BytesIO()
    # Ajuste automatiquement les marges pour éviter que le texte soit coupé
    plt.tight_layout()
    # Sauvegarde le graphique dans le buffer en format PNG
    plt.savefig(buffer, format='png')
    # Remet le curseur de lecture au début du buffer
    buffer.seek(0)
    # Ferme la figure pour libérer la mémoire
    plt.close(fig)

    # Encode l'image PNG en base64 (convertit les bytes en texte)
    # base64.b64encode() → encode les bytes
    # buffer.read() → lit tout le contenu du buffer
    # .decode('utf-8') → convertit les bytes en string
    # Résultat : une longue chaîne de caractères représentant l'image
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

    # Retourne l'image encodée en base64 pour l'utiliser dans le template HTML
    # Dans le template : <img src="data:image/png;base64,{{ image_base64 }}">
    return image_base64