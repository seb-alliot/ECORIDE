from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from ...models import TrajetProposer, CreditUser
from django.db import transaction


@receiver(post_save, sender=TrajetProposer)
def debit_commission(sender, instance, created, **kwargs):
    if not created:
        return

    commission = 2
    chauffeur = instance.chauffeur

    try:
        with transaction.atomic():
            # Débiter le chauffeur
            credit_user = CreditUser.objects.get(user=chauffeur)

            if credit_user.credit < commission:
                return

            credit_user.credit -= commission
            credit_user.save()

            # Créditer la plateforme (par username explicite ici : ECORIDE)
            superuser = User.objects.filter(username='ECORIDE').first()
            if superuser:
                credit_plateforme, _ = CreditUser.objects.get_or_create(user=superuser)
                credit_plateforme.credit += commission
                credit_plateforme.save()
            else:
                pass # le super user existe forcement donc l'erreur n'est pas possible

    except CreditUser.DoesNotExist:
        pass # Le chauffeur a forcement un compte de crédit ou est supprimé
