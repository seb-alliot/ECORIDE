from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from ...models import TrajetProposer, ReservationTrajet, CreditUser
from django.db import transaction



from dotenv import load_dotenv
load_dotenv()
from ..utils import get_mongo_db

@receiver(pre_delete, sender=User)
def user_deleted(sender, instance, **kwargs):

    user_email = instance.email
    from ..envoi_email.send_email import envoi_email
    subject = "Suppression de votre compte - Ecoride"
    template = "style_email/_confirmation_suppression_compte.html"

    context = {"username": instance.username}
    envoi_email(
        request=None,
        to=user_email,
        subject=subject,
        template=template,
        context=context
    )
    # Récupérer les trajets proposés par ce chauffeur
    trajets = TrajetProposer.objects.filter(chauffeur=instance)

    # Récupérer les réservations faites par ce passager
    reservations_en_tant_que_passager = ReservationTrajet.objects.filter(passager=instance)

    # Si c'est un chauffeur avec des trajets proposés
    if trajets.exists():
        with transaction.atomic():
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
                    from ..envoi_email.send_email import envoi_email
                    subject = "Annulation de votre réservation - Ecoride"
                    to = passager.email
                    template = "style_email/_reservation_annule.html"
                    context = {
                        "passager": passager,
                        "trajet": trajet,
                        "reservation": res,
                        "chauffeur": instance,
                    }
                    envoi_email(
                        request=None,
                        to=to,
                        subject=subject,
                        template=template,
                        context=context
                    )



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

    if trajets.exists():
        for trajet in trajets:
            db = get_mongo_db()
            db["vue"].delete_one({"_id": str(trajet.id)})
        trajets.delete()
