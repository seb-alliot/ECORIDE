import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def Graphique(jours, resa, gains):
    fig, ax1 = plt.subplots(figsize=(10, 4))

    bar_width = 0.35
    x = range(len(jours))

    ax1.bar(x, resa, bar_width, label='Réservations', color='skyblue')
    ax1.bar([i + bar_width for i in x], gains, bar_width, label='Gains (€)', color='salmon')

    ax1.set_xlabel('Jour')
    ax1.set_ylabel('Valeurs')
    ax1.set_title('Graphique des réservations et gains par jour')
    ax1.set_xticks([i + bar_width / 2 for i in x])
    ax1.set_xticklabels(jours)
    ax1.legend()

    buffer = BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)

    # Encodage base64 pour affichage dans template
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    return image_base64
