from django.db.models.signals import post_save
from django.dispatch import receiver
from ...models import ReservationTrajet, CreditUser, TrajetProposer
from django.db import transaction

@receiver(post_save, sender=ReservationTrajet)
def debit_credit_reservation(sender, instance, created, **kwargs):
    if not created:
        return

    passager = instance.passager
    trajet = instance.trajet_reserver
    places_reservees = instance.places

    try:
        credit_passager = CreditUser.objects.select_for_update().get(user=passager)
        trajet = TrajetProposer.objects.select_for_update().get(id=trajet.id)

        prix_unitaire = trajet.prix
        prix_total = prix_unitaire * places_reservees

        with transaction.atomic():
            # Débiter le passager
            credit_passager.credit -= prix_total
            credit_passager.save()

            # Mise à jour des places disponibles
            trajet.places -= places_reservees
            trajet.save()

            # Mise à jour du prix unitaire dans la réservation
            instance.prix_par_passager = prix_total
            instance.save(update_fields=["prix_par_passager"])

    except CreditUser.DoesNotExist:
        pass  # Le passager a forcement un compte de crédit ou est supprimé, ou le trajet n'existe pas et dans se cas il est géré ailleurs