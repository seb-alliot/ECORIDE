from ....models import TrajetProposer
from django.utils import timezone
from collections import defaultdict
from datetime import timedelta
from ....forms import AfficherReservationForm


def Affiche_gain_jour(request):
    jour_semaine_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]

    commission = 2.0

    gain_afficher = defaultdict(list)
    compteur_gain = defaultdict(float)
    formulaire_pres_remplis_gain = []

    aujourd_hui = timezone.localtime(timezone.now()).date()
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())

    # On filtres tous les trajets de la semaine en cours en excluant ceux annulés --> commmission remboursée
    tout_trajet = TrajetProposer.objects.filter(created_at__date__gte=debut_semaine).exclude(etat="Annulé").order_by('created_at')

    for trajet in tout_trajet:
        local_created_at = timezone.localtime(trajet.created_at)
        jour = jour_semaine_fr[local_created_at.weekday()]

        gain_afficher[jour].append(commission)
        compteur_gain[jour] += commission

    for jour in jour_semaine_fr:
        total_gain = compteur_gain.get(jour, 0.0)  # Si pas de trajet, le gain est 0.0
        formulaire_pres_remplis_gain.append(AfficherReservationForm(initial={'total_gain': total_gain}))

    return formulaire_pres_remplis_gain
