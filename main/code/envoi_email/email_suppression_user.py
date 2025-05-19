from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings

def Information_suppression_user(
    passager, trajet, reservation, chauffeur):
    site_url = settings.SITE_URL
    monprofile_url = f"{site_url}{reverse('MonCompte')}"

    email = passager.email
    prix_total = reservation.prix_par_passager

    subject = f"Bonjour {passager.username}, votre réservation a été annulée"

    context = {
        "prix_total": prix_total,
        "reservation": reservation,
        "passager": passager,
        "chauffeur": chauffeur,
        "trajet": trajet,
        "monprofile_url": monprofile_url,
        }

    message = render_to_string("style_email/_reservation_annulé.html", context)

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email="staff.modo.ecoride@gmail.com",
        to=[email],
    )
    email.content_subtype = "html"
    email.send()
