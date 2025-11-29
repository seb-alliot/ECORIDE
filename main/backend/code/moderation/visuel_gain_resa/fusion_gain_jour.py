from ....forms import AfficherReservationForm


def Fusion_donnee(request):

    # On récupère les réservations et les gains
    from .. import Afficher_reservations
    reservations = Afficher_reservations(request)
    from .. import Affiche_gain_jour
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
    # On initialise des dictionnaires pour stocker les données
    dict_resa = {}
    dict_gain = {}

    # On extrait les données du formulaire fusionné
    for form in formulaire_pres_remplis_fusion:
        jour = form.initial.get('jour')
        resa = form.initial.get('total_resa', 0)
        gain = form.initial.get('total_gain', 0)
        dict_resa[jour] = resa
        dict_gain[jour] = gain

    # On aligne tous les jours, avec 0 par défaut si jour absent
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    resa = [dict_resa.get(j, 0) for j in jours]
    gains = [dict_gain.get(j, 0) for j in jours]
    total_reservations = sum(resa)
    total_gains = sum(gains)
    return formulaire_pres_remplis_fusion, jours, resa, gains, total_reservations, total_gains