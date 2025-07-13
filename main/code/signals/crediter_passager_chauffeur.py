from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from ...models import TrajetProposer, CreditUser
from django.db import transaction

@receiver(pre_delete, sender=TrajetProposer)
def crediter_user(sender, instance,  **kwargs):


    commission = 2
    chauffeur = instance.chauffeur
    passagers = instance.passager.all() if hasattr(instance, 'passager') else []

    prix_unitaire = instance.prix
    places_reservees = instance.places

    try:
        with transaction.atomic():
            # Créditer le chauffeur
            credit_chauffeur = CreditUser.objects.select_for_update().get(user=chauffeur)
            credit_chauffeur.credit += commission
            credit_chauffeur.save()

            # Débiter la plateforme
            superuser = User.objects.filter(username='ECORIDE').first()
            if superuser:
                credit_plateforme, _ = CreditUser.objects.select_for_update().get_or_create(user=superuser)
                credit_plateforme.credit -= commission
                credit_plateforme.save()
            else:
                pass # le super user existe forcement donc l'erreur n'est pas possible

            # Créditer passager
            for participant in passagers:
                credit_passager = CreditUser.objects.select_for_update().get(user=participant)
                prix_total = prix_unitaire * places_reservees
                credit_passager.credit += prix_total
                credit_passager.save()
                print(f"Le compte de {participant.username} a été crédité de {prix_total} €.")

    except CreditUser.DoesNotExist as e:
        pass # Le passager a forcement un compte de crédit ou est supprimé
