from django.db.models.signals import pre_delete, post_save

from django.dispatch import receiver
from django.contrib.auth.models import User
from ...models import TrajetProposer, CreditUser, ReservationTrajet
from ..utils import get_mongo_db
from django.db import transaction
from dotenv import load_dotenv
import os
from decimal import Decimal

load_dotenv()
commission = Decimal(os.getenv("COMMISSION", "0"))


def process_annulation_trajet(instance: TrajetProposer):
    chauffeur = instance.chauffeur

    with transaction.atomic():
        # Créditer le chauffeur (commission)
        credit_chauffeur = CreditUser.objects.select_for_update().get(user=chauffeur)
        credit_chauffeur.credit += commission
        credit_chauffeur.save()

        # Supprimer la vue Mongo liée au trajet
        db = get_mongo_db()
        db["vue"].delete_one({"_id": str(instance.id)})

        # Débiter la plateforme
        superuser = User.objects.get(username="ECORIDE")
        credit_plateforme = CreditUser.objects.select_for_update().get(user=superuser)
        credit_plateforme.credit -= commission
        credit_plateforme.save()

        # Rembourser les passagers
        reservations = ReservationTrajet.objects.filter(trajet_reserver=instance)
        for participant in reservations:
            credit_passager = CreditUser.objects.select_for_update().get(user=participant.passager)
            prix_total = participant.prix_par_passager * participant.places
            credit_passager.credit += prix_total
            credit_passager.save()

@receiver(pre_delete, sender=TrajetProposer)
# le pre delete pour la vue admin, comme sa la logique de remboursement est appliquée automatiquement
def crediter_user(sender, instance, **kwargs):
    non_remboursable = ["Terminé", "En cours", "Annulé"]
    if instance.etat not in non_remboursable:
        try:
            process_annulation_trajet(instance)
        except CreditUser.DoesNotExist as e:
            raise ValueError(f"Erreur lors de la mise à jour des crédits pour le trajet {instance.id}: {e}")


@receiver(post_save, sender=TrajetProposer)
def crediter_passager_chauffeur(sender, instance, created, **kwargs):
    if instance.etat == "Annulé":
        try:
            process_annulation_trajet(instance)
        except CreditUser.DoesNotExist as e:
            raise ValueError(f"Erreur lors de la mise à jour des crédits pour le trajet {instance.id}: {e}")
