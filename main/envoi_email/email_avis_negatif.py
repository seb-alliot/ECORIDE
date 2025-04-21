from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from ..models import ReservationTrajet, AdresseUser, TrajetProposer
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse

def Envoi_Email_Avis_Trajet_Negatif(
    request, passager, trajet_id, reservations, commentaire, token, passagers
):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id, token])}"
        )
        reservation = ReservationTrajet.objects.filter(
            trajet_reserver=trajet_id
        ).first()
        trajet = TrajetProposer.objects.get(id=trajet_id)
        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
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

        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver

        subject = f"Avis negatif {trajet_id} de la part de {passagers}"

        context = {
            "prix_total": prix_total,
            "telephone": telephone,
            "trajet": trajet,
            "reservations": reservations,
            "site_url": site_url,
            "avis_satisfaction_url": avis_satisfaction_url,
            "passager": passager,
            "chauffeur": chauffeur,
            "date": date,
            "trajet_id": trajet_id,
            "commentaire": commentaire,
            "passagers": passagers,
        }

        message = render_to_string("style_email/_avis_negatif.html", context)

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=["staff.modo.ecoride@gmail.com"],
        )
        email.content_subtype = "html"
        email.send()

    except Exception as e:
        messages.error(
            request,
            f"Erreur lors de l'envoi de l'e-mail de votre retour negatif: {str(e)}",
        )
