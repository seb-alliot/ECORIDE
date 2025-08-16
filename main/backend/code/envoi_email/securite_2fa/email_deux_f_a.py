from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
import secrets
from django.shortcuts import redirect

def Deux_F_A(request, email, username):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        connection2_url = f"{site_url}{reverse('connection2')}"

        token_connection = str(secrets.randbelow(1000000)).zfill(6)
        request.session["token_connection"] = token_connection

        subject = "Code de connection"
        context = {
            "username": username,
            "email": email,
            "token_connection": token_connection,
            "site_url": site_url,
            "connection2": connection2_url,
        }

        message = render_to_string(
            "style_email/_2fa.html", context
            )

        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=[email],
        )
        email.content_subtype = "html"
        email.send()

        messages.success(request, "Votre code de connection vous a été envoyer par email.")
        return redirect("connection2")

    except Exception as e:
        messages.error(request, f"Erreur lors de l'envoi du code connection: {str(e)}")
        return redirect("connection1")
