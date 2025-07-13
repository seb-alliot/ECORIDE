from django.db.models.signals import pre_delete
from django.dispatch import receiver
from ...models import ReservationTrajet, CreditUser, TrajetProposer
from django.db import transaction

@receiver(pre_delete, sender=ReservationTrajet)
def remboursement_reservation_passager(sender, instance, **kwargs):
    passager = instance.passager
    trajet = instance.trajet_reserver
    places_reservees = instance.places

    try:
        # On exclut les trajets déjà annulés ou terminés
        if trajet.etat_reservation not in ["Annulé", "Terminé"]:
            # Vérifier si le trajet est annulé
            with transaction.atomic():
                credit_passager = CreditUser.objects.select_for_update().get(user=passager)
                trajet = TrajetProposer.objects.select_for_update().get(id=trajet.id)

                prix_unitaire = trajet.prix
                prix_total = prix_unitaire * places_reservees

                # Rembourser le passager
                credit_passager.credit += prix_total
                credit_passager.save()

                # Remettre les places disponibles
                trajet.places += places_reservees
                trajet.etat_reservation = "Annulé"
                trajet.etat_trajet = "Annulé"
                trajet.save()


    except CreditUser.DoesNotExist:
        pass  # Le passager a forcement un compte de crédit ou est supprimé
