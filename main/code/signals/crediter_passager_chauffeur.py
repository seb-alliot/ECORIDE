from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from ...models import TrajetProposer, CreditUser
from ..utils import get_mongo_db
from django.db import transaction
from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()


@receiver(pre_delete, sender=TrajetProposer)
def crediter_user(sender, instance, **kwargs):
    commission = 2
    chauffeur = instance.chauffeur
    passagers = instance.passager.all() if hasattr(instance, 'passager') else []

    prix_unitaire = instance.prix
    places_reservees = instance.places

    try:
        with transaction.atomic():
            credit_chauffeur = CreditUser.objects.select_for_update().get(user=chauffeur)
            credit_chauffeur.credit += commission
            credit_chauffeur.save()

            db = get_mongo_db()
            db["vue"].delete_one({"_id": str(instance.id)})

            superuser = User.objects.get(username='ECORIDE')
            credit_plateforme = CreditUser.objects.select_for_update().get(user=superuser)
            credit_plateforme.credit -= commission
            credit_plateforme.save()

            for participant in passagers:
                credit_passager = CreditUser.objects.select_for_update().get(user=participant)
                prix_total = prix_unitaire * places_reservees
                credit_passager.credit += prix_total
                credit_passager.save()

    except CreditUser.DoesNotExist as e:
        print(f"[Erreur Crédit] : {e}")
