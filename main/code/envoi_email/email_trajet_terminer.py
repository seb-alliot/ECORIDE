from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from ...models import ReservationTrajet
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from ..securite import reservation_token

def Envoi_Email_Terminer(request, trajet_id):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)

        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver

            # Génère un token unique par passager
            token = reservation_token(passager.username)
            lien_verification = f"{site_url}{reverse('AvisSatisfaction', kwargs={'trajet_id': trajet.id, 'token': token})}"

            subject = "Confirmation de fin de covoiturage"
            context = {
                "reservations": reservations,
                "site_url": site_url,
                "avis_satisfaction_url": lien_verification,
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
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturage : {str(e)}",
        )
