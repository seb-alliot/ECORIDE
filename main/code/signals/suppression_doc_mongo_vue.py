from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from ...models import TrajetProposer
from ..utils import get_mongo_db

@receiver(pre_save, sender=TrajetProposer)
def verif_etat(sender, instance, **kwargs):
    if instance.pk:
        try:
            ancien = sender.objects.get(pk=instance.pk)
            print(f"Ancien état du trajet {instance.id} : {ancien.etat}")
            if ancien.etat != instance.etat:
                print(f"Changement d'état du trajet {instance.id} de {ancien.etat} à {instance.etat}")
                instance.etat_actuel = ancien.etat
        except sender.DoesNotExist:
            instance.etat_actuel = None
    else:
        instance.etat_actuel = None

@receiver(post_save, sender=TrajetProposer)
def suppression_mongo_doc_vue(sender, instance, created, **kwargs):
    if created:
        return

    ancien_etat = getattr(instance, "etat_actuel", None)
    nouvel_etat = instance.etat

    if ancien_etat != nouvel_etat and nouvel_etat in ['Annulé', 'Terminé']:
        db = get_mongo_db()
        result = db["vue"].delete_one({"_id": str(instance.id)})
        if result.deleted_count > 0:
            print(f"[MongoDB] : Vue du trajet {instance.id} supprimée.")
        else:
            print(f"[MongoDB] : Aucune vue trouvée pour le trajet {instance.id}.")
