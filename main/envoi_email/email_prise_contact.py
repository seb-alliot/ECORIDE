from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib import messages

def envoi_email_prise_contact(request, telephone, pseudo, email_user, sujet,message ):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        contact_url = f"{site_url}{reverse('_contact')}"
        subject = "Prise de contact"
        context = {
            "telephone": telephone,
            "contact_url": contact_url,
            "sujet": sujet,
            "pseudo": pseudo,
            "email_user": email_user,
            "message": message,
            "site_url": site_url,
        }
        message = render_to_string("style_email/contact.html", context)
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=["staff.modo.ecoride@gmail.com"],
        )
        email.content_subtype = "html"
        email.send()
        message=request.POST.get("message")
        messages.success(request, "Votre message a bien été envoyé.")
    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi de l'e-mail de votre retour positif: {str(e)}")
