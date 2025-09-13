from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from ...models import TrajetProposer, CreditUser
from ..utils import get_mongo_db
from django.db import transaction
from dotenv import load_dotenv
import os
load_dotenv()
from datetime import datetime
from ..utils.recup_commission import get_commission


@receiver(pre_save, sender=TrajetProposer)
def crediter_annulation(sender, instance, **kwargs):
    commission = get_commission()

    if not instance.pk:
        return
    maintenant = datetime.now()
    ancien_trajet = TrajetProposer.objects.get(pk=instance.pk)

    if ancien_trajet.etat != "Annulé" and instance.etat == "Annulé":
        chauffeur = instance.chauffeur
        passagers = instance.passager.all() if hasattr(instance, 'passager') else []
        prix_unitaire = instance.prix
        places_reservees = instance.places

        try:
            with transaction.atomic():
                if ancien_trajet.date >= maintenant.date() and ancien_trajet.trajet_rembourser == True:
                    return
                credit_chauffeur = CreditUser.objects.select_for_update().get(user=chauffeur)
                credit_chauffeur.credit += commission
                credit_chauffeur.save()

                db = get_mongo_db()
                db["vue"].delete_one({"_id": str(instance.id)})

                superuser = User.objects.get(username='ECORIDE')
                credit_plateforme = CreditUser.objects.select_for_update().get(user=superuser)
                credit_plateforme.credit -= commission
                credit_plateforme.save()
                ancien_trajet.etat = "Annulé"
                ancien_trajet.trajet_rembourser = True

                # Créditer les passagers
                for participant in passagers:
                    credit_passager = CreditUser.objects.select_for_update().get(user=participant)
                    prix_total = prix_unitaire * places_reservees
                    credit_passager.credit += prix_total
                    credit_passager.save()

        except CreditUser.DoesNotExist as e:
            pass # la logique d'un utilisateur manquant est déjà gérée dans un autre signal
