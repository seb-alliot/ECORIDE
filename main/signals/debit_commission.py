from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from ..models import TrajetProposer, CreditUser
from django.db import transaction


@receiver(post_save, sender=TrajetProposer)
def debit_commission(sender, instance, created, **kwargs):
    if not created:
        return  # Si c'est pas une création, on ne fait rien

    commission = 2
    chauffeur = instance.chauffeur

    try:
        with transaction.atomic():
            # Débiter le chauffeur
            credit_user = CreditUser.objects.get(user=chauffeur)

            if credit_user.credit < commission:
                print(f"Le compte de {chauffeur.username} n'a pas assez de crédits pour le trajet proposé.")
                return

            credit_user.credit -= commission
            credit_user.save()

            # Créditer la plateforme (par username explicite ici : ITSUKI)
            superuser = User.objects.filter(username='ECORIDE').first()
            if superuser:
                credit_plateforme, _ = CreditUser.objects.get_or_create(user=superuser)
                credit_plateforme.credit += commission
                credit_plateforme.save()

                print(f"Le compte de {chauffeur.username} a été débité de {commission} €.")
                print(f"Le compte de la plateforme ({superuser.username}) a été crédité de {commission} €.")
            else:
                print("Aucun superuser nommé 'ITSUKI' trouvé pour créditer la plateforme.")

    except CreditUser.DoesNotExist:
        print(f"Le compte crédit de {chauffeur.username} est introuvable.")
