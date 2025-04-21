from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from ..models import ReservationTrajet
from django.core.mail import EmailMessage


def Envoi_Email_Annulation(request, trajet_id, reservations):

    try:
        site_url = f"http://{get_current_site(request).domain}"
        monprofile_url = f"{site_url}{reverse('MonCompte')}"

        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver
            subject = "Annulation de votre trajet"

            context = {
                "reservations": reservations,
                "site_url": site_url,
                "monprofile_url": monprofile_url,
                "passager": passager,
                "chauffeur": chauffeur,
                "date": date,
                "trajet": trajet,
            }

            message = render_to_string(
                "style_email/annulation_confirmation.html", context
            )

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email="staff.modo.ecoride@gmail.com",
                to=[passager.email],
            )
            email.content_subtype = "html"
            email.send()

    except Exception as e:
        messages.error(
            request, f"Erreur lors de l'envoi de l'e-mail d'annulation : {str(e)}"
        )
