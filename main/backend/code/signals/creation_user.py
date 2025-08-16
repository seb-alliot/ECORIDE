from ...models import User, CreditUser, ChoixRole
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        user = instance
        # Créer un rôle par défaut
        ChoixRole.objects.create(user=user, role="passager")
        if getattr(user, "username", None) == "ECORIDE":
            credit_user = CreditUser.objects.create(user=user, credit=0)
        else:
            credit_user = CreditUser.objects.create(user=user, credit=20)
