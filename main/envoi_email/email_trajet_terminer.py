from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from ..models import ReservationTrajet
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse

def Envoi_Email_Terminer(request, trajet_id, reservations, token):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id,token])}"
        )

        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver
            subject = "Confirmation de fin de covoiturage"

            context = {
                "reservations": reservations,
                "site_url": site_url,
                "avis_satisfaction_url": avis_satisfaction_url,
                "passager": passager,
                "chauffeur": chauffeur,
                "date": date,
                "trajet": trajet,
            }

            message = render_to_string("style_email/covoit_termine.html", context)

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
            request,
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturag : {str(e)}",
        )
