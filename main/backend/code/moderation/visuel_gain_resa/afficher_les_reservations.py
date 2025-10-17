from django.utils import timezone
from collections import defaultdict
from datetime import timedelta
from ....models import ReservationTrajet
from ....forms import AfficherReservationForm

def Afficher_reservations(request):
    jour_semaine_fr = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    # jour_semaine_fr[0] correspond à lundi car weekday() renvoie 0 pour lundi, jusqu'à 6 pour dimanche

    reservations_afficher = defaultdict(list)
    compteur_resa = defaultdict(int)
    formulaire_pres_remplis_resa = []
    # On récupère la date du jour, en tenant compte du fuseau horaire local
    aujourd_hui = timezone.localtime(timezone.now()).date()

    # On calcule la date du lundi de la semaine en cours
    debut_semaine = aujourd_hui - timedelta(days=aujourd_hui.weekday())

    # On récupère toutes les réservations créées depuis ce lundi, triées par date de création
    reservations = ReservationTrajet.objects.filter(created_at__date__gte=debut_semaine).order_by('created_at')

    for res in reservations:
        local_created_at = timezone.localtime(res.created_at)

        res.jour_semaine = jour_semaine_fr[local_created_at.weekday()]

        reservations_afficher[res.jour_semaine].append(res)

        compteur_resa[res.jour_semaine] += 1

    for jour in jour_semaine_fr:
        total_resa = compteur_resa.get(jour, 0) # apres une virgule on passe à une valeur par default

        # On pres remplis un formulaire pour facilité la mise en page
        formulaire_pres_remplis_resa.append(AfficherReservationForm(initial={'jour': jour,'total_resa': total_resa}))

    return formulaire_pres_remplis_resa
