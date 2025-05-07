from ...models import TrajetProposer, ReservationTrajet
from collections import defaultdict


def Info_Reservation(request):
    user = request.user

    passager = ReservationTrajet.objects.filter(passager=user).first()
    trajet = TrajetProposer.objects.filter(chauffeur=user).first()
    reservation_chercher = ReservationTrajet.objects.filter(passager=user, etat_reservation__in=["Terminé", "Annulé", "Reserver"])
    reservation = defaultdict(list)
    for res in reservation_chercher:
        reservation[res.etat_reservation].append(res)
    reservation1 = reservation["Terminé"]
    reservation2 = reservation["Annulé"]
    reservation3 = reservation["Reserver"]
    prix_total_paye = ReservationTrajet.paiement_total_passager(request.user, trajet)

    return {
        'passager': passager,
        'reservation': reservation,
        'reservation1': reservation1,
        'reservation2': reservation2,
        'reservation3': reservation3,
        'prix_total_paye': prix_total_paye,
    }
