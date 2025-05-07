import os
import imaplib
from django.shortcuts import render


def ConnectionImaplib(request):

    mail = imaplib.IMAP4_SSL(
    os.getenv("MAIL_IMAP_SERVER"), int(os.getenv("MAIL_IMAP_PORT"))
    )
    mail.login(os.getenv("MAIL_IMAP_USER"), os.getenv("MAIL_IMAP_PASSWORD"))
    # selectionne la boite de recception cibler a charger
    mail.select("inbox")

    result, data = mail.search(None, "ALL")

    if result != "OK":
        return render(
        request,
            "admin/moderateur/moderation_email/moderation_email.html",
            {"error": "Il n'y a pas d'emails a modérer."},
        )
    mail_ids = data[0].split()
    emails = []
    return mail, data, result ,mail_ids, emails
