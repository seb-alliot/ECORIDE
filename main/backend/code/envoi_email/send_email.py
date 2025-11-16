import os
import logging
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

def envoi_email(request, *, to, subject, template, context=None, from_email="staff.modo.ecoride@gmail.com"):
    try:
        if request is None:
            domain = f"{os.getenv('DOMAINE')}"
        else:
            domain = get_current_site(request).domain

        if context is None:
            context = {}
        context.setdefault("site_url", f"http://{domain}")

        message_html = render_to_string(template, context)
        email = EmailMessage(
            subject=subject,
            body=message_html,
            from_email=from_email,
            to=[to],
        )
        email.content_subtype = "html"
        email.send()

    except Exception as e:
        if request:
            from django.contrib import messages
            messages.error(request, f"Une erreur est survenue : {str(e)}")
        else:
            # Pas de request => juste logger
            logger.error(f"Erreur lors de l'envoi de l'email à {to} : {str(e)}")
