from ..forms import AfficherReservationForm
from ..moderation import Afficher_reservations, Affiche_gain_jour

def Fusion_donnee(request):

    # On récupère les réservations et les gains
    reservations = Afficher_reservations(request)
    gains = Affiche_gain_jour(request)

    # On fusionne les données dans un seul formulaire
    formulaire_pres_remplis_fusion = []
    # zip permet de regrouper les réservations et les gains par jour
    # car les deux listes sont ordonnées de la meme maniere et meme longueur
    for reservation, gain in zip(reservations, gains):
        # On crée un nouveau formulaire avec les données fusionnées
        fusion_form = AfficherReservationForm(initial={
            'jour': reservation.initial['jour'],
            'total_resa': reservation.initial['total_resa'],
            'total_gain': gain.initial['total_gain']
        })
        formulaire_pres_remplis_fusion.append(fusion_form)

    return formulaire_pres_remplis_fusion
