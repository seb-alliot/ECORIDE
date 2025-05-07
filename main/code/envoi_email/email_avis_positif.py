from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from ...models import ReservationTrajet, AdresseUser, TrajetProposer
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
import uuid

def Envoi_Email_Avis_Trajet_Positif(
    request, chauffeur, trajet_id, reservation, commentaire, token, passagers
):

    try:
        message_id = f"<avis-{trajet_id}-{uuid.uuid4()}@ecoride.com>"

        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id, token])}"
        )
        reservation = ReservationTrajet.objects.filter(
            trajet_reserver=trajet_id
        ).first()
        trajet = TrajetProposer.objects.get(id=trajet_id)
        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        date = reservation.trajet_reserver.date
        chauffeur = trajet.chauffeur
        try:
            telephone = (
                AdresseUser.objects.get(user=chauffeur).telephone
                if AdresseUser.objects.filter(user=chauffeur).exists()
                else None
            )
        except AdresseUser.DoesNotExist:
            telephone = None
        prix_total = reservation.prix_par_passager

        subject = f"Avis positif {trajet_id} de la part de {passagers}"

        context = {
            "prix_total": prix_total,
            "telephone": telephone,
            "trajet": trajet,
            "reservations": reservations,
            "site_url": site_url,
            "avis_satisfaction_url": avis_satisfaction_url,
            "passagers": passagers,
            "chauffeur": chauffeur,
            "date": date,
            "trajet_id": trajet_id,
            "commentaire": commentaire,
        }

        message = render_to_string("style_email/_avis_positif.html", context)

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=["staff.modo.ecoride@gmail.com"],
            headers={"Message-ID": message_id},
        )
        email.content_subtype = "html"
        email.send()

    except Exception as e:
        messages.error(
            request,
            f"Erreur lors de l'envoi de l'e-mail d'avis positif: {str(e)}",
        )
