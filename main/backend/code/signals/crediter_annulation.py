from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver
from ...models import ReservationTrajet, CreditUser, TrajetProposer
from django.db import transaction



@receiver(pre_delete, sender=ReservationTrajet)
def remboursement_reservation_passager(sender, instance, **kwargs):
    passager = instance.passager
    print(passager)
    trajet = instance.trajet_reserver
    print(trajet)
    places_reservees = instance.places

    try:
        # Ne rien faire si déjà remboursé
        if instance.reservation_rembourser:
            return

        # On exclut les trajets déjà annulés/terminés par le chauffeur
        if trajet.etat not in ["Annulé", "Terminé"]:
            with transaction.atomic():
                credit_passager = CreditUser.objects.select_for_update().get(user=passager)
                trajet = TrajetProposer.objects.select_for_update().get(id=trajet.id)

                prix_total = trajet.prix * places_reservees

                # Rembourser le passager
                credit_passager.credit += prix_total
                credit_passager.save()

                # Remettre les places disponibles
                trajet.places += places_reservees

                trajet.save()

                # Marquer la réservation comme remboursée
                instance.reservation_rembourser = True

    except CreditUser.DoesNotExist:
        pass
