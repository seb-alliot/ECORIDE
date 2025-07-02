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

        if credit_passager.credit < prix_total:
            print(f"{passager.username} n'a pas assez de crédits.")
            return

        if places_reservees > trajet.places:
            print("Pas assez de places disponibles.")
            return

        with transaction.atomic():
            # Débiter le passager
            credit_passager.credit -= prix_total
            credit_passager.save()

            # Crédite temporairement la plateforme ou une file d'attente, à ajuster si besoin
            # Mise à jour des places disponibles
            trajet.places -= places_reservees
            trajet.save()

            # Mise à jour du prix unitaire dans la réservation
            instance.prix_par_passager = prix_unitaire
            instance.save(update_fields=["prix_par_passager"])

            print(f"Le compte de {passager.username} a été débité de {prix_total} €.")
            print(f"{places_reservees} place(s) réservée(s) sur le trajet {trajet.id}.")

    except CreditUser.DoesNotExist:
        print(f"Crédit inexistant pour {passager.username}.")
    except TrajetProposer.DoesNotExist:
        print(f"Trajet {trajet.id} inexistant.")
