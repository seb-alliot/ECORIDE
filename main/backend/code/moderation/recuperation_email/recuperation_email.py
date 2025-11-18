import asyncio
from aioimaplib import aioimaplib
from email.header import decode_header
import chardet
import email
import os
import dotenv

dotenv.load_dotenv()

password = os.getenv("MAIL_IMAP_PASSWORD")
user = os.getenv("MAIL_IMAP_USER")
host = os.getenv("MAIL_IMAP_SERVER")


async def RecuperationEmail(request, mail_ids=None, emails=None):
    if emails is None:
        emails = []  # Initialisation une seule fois, avant la boucle

    get_email_type = request.GET.get("email_type", "").strip()
    selected_email = None
    email_id_selected = request.GET.get("email_id")

    mail = aioimaplib.IMAP4_SSL(host)
    await mail.wait_hello_from_server()
    await mail.login(user, password)
    await mail.select("INBOX")

    typ, data = await mail.search("ALL")
    mail_ids = data[0].split()

    for email_id in mail_ids:
        email_id_str = email_id.decode() if isinstance(email_id, bytes) else str(email_id)
        typ, data = await mail.fetch(email_id_str, "(RFC822)")
        if typ != "OK" or not data:
            continue

        raw_email = None
        for part in data:
            if isinstance(part, (bytes, bytearray)) and len(part) > 100:
                raw_email = bytes(part)
                break

        if raw_email is None:
            continue

        message = email.message_from_bytes(raw_email)

        subject, encoding = decode_header(message["Subject"])[0]
        if isinstance(subject, bytes) and encoding:
            subject = subject.decode(encoding if encoding else "utf-8")

        # Ignorer les réponses automatiques ou les sujets commençant par "Re:" chiant a gerer
        if subject.lower().startswith("re:"):
            continue

        message_id = message.get("Message-ID")
        sender = message.get("From")
        # Filtrage des emails selon le type demandé
        if get_email_type in ["Avis negatif", "Avis positif"]:
            # je filtre les avis positifs et négatifs en fonction du sujet
            if get_email_type and get_email_type.lower() not in subject.lower():
                continue
            if not (
                (
                    "Avis negatif" in subject
                    or "Avis positif" in subject
                    or "Prise de contact" in subject
                )
                and ("staff.modo.ecoride@gmail.com" in sender)
            ):
                continue
        # sinon je me permet d'afficher le sujet des la prise de contact
        # et comme j'envois des email a part de la meme adresse je filtre ici directement pour la sécurité
        if get_email_type == "Prise de contact":
            if not "staff.modo.ecoride@gmail.com" in sender or "Avis" in subject:
                continue


        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/html":
                    encodage_detecte = chardet.detect(part.get_payload(decode=True))
                    if encodage_detecte["encoding"]:
                        body = part.get_payload(decode=True).decode(encodage_detecte["encoding"])
                    else:
                        body = part.get_payload(decode=True).decode()
                    break
        else:
            body = message.get_payload(decode=True).decode()

        email_data = {
            "id": email_id_str,
            "subject": subject,
            "sender": sender,
            "body": body,
            "message_id": message_id,
        }
        emails.append(email_data)

        if email_id_selected and email_id_selected == email_data["id"]:
            selected_email = email_data

    await mail.logout()
    return get_email_type, email_id_selected, mail_ids, emails, selected_email
