from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage

def Envoi_Reponse_Modo(request, email_user , message , pseudo, reponse_modo):
    try:
        site_url = f"http://{get_current_site(request).domain}"

        subject = "Réponse à votre demande"
        context = {
            "pseudo": pseudo,
            "message": message,
            "reponse_modo": reponse_modo,
            "site_url": site_url,
        }

        message = render_to_string("style_email/_reponse_modo.html", context)

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=[email_user],
        )
        email.content_subtype = "html"
        email.send()
        messages.success(request, "Réponse envoyé.")
    except Exception as e:
        messages.error(request, f"Erreur est survenu : {str(e)}")
