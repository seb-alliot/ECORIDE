from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from ...models import TrajetProposer, ReservationTrajet, CreditUser
from django.db import transaction
from ..envoi_email import Information_suppression_user

# On assure que la logique de suppression des trajets et réservations est bien gérée via transactions atomiques
# pour éviter les incohérences en cas d'erreur durant la suppression.

@receiver(pre_delete, sender=User)
def user_deleted(sender, instance, **kwargs):
    # Récupérer les trajets proposés par ce chauffeur
    trajets = TrajetProposer.objects.filter(chauffeur=instance)

    # Récupérer les réservations faites par ce passager
    reservations_en_tant_que_passager = ReservationTrajet.objects.filter(passager=instance)

    # Si c'est un chauffeur avec des trajets proposés
    if trajets.exists():
        with transaction.atomic():
            # Récupérer toutes les réservations qui concernent ses trajets
            reservations_des_trajets = ReservationTrajet.objects.filter(trajet_reserver__in=trajets)

            for res in reservations_des_trajets:
                if res.etat_reservation != "Annulé":
                    trajet = res.trajet_reserver
                    res.etat_reservation = "Annulé"
                    res.save()

                    # Remboursement
                    prix_rembourse = res.prix_par_passager
                    passager = res.passager
                    credit_passager = CreditUser.objects.get(user=passager)
                    credit_passager.credit += prix_rembourse
                    credit_passager.save()

                    # Email d'information envoyé au passager
                    Information_suppression_user(
                        passager=passager,
                        trajet=trajet,
                        reservation=res,
                        chauffeur=instance
                    )


    # Si l'utilisateur est aussi un passager qui a réservé des trajets
    if reservations_en_tant_que_passager.exists():
        with transaction.atomic():
            for res in reservations_en_tant_que_passager:
                if res.etat_reservation != "Annulé":
                    trajet = res.trajet_reserver
                    # Libérer les places
                    trajet.places += res.places
                    trajet.save()

                    # Annuler la réservation
                    res.etat_reservation = "Annulé"
                    res.reservation_rembourser = True
                    res.save()


                    # Suppression de la réservation (optionnel, à toi de voir si tu veux garder trace)
                    res.delete()

    # Enfin, supprimer les trajets du chauffeur
    if trajets.exists():
        trajets.delete()

