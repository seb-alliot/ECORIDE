from email.header import decode_header
import chardet
import email

def RecuperationEmail(request, mail, data, result, mail_ids, emails):

    email_type = request.GET.get("email_type", "").strip()
    selected_email = None

    #confort ux uniquement
    # Récupération de l'email sélectionné (si existant)
    email_id_selected = request.GET.get("email_id")
    # Si pas d'email on fait en sorte de ne pas générer d'erreur
    for email_id in mail_ids:
        result, data = mail.fetch(email_id, "(RFC822)")
        if result != "OK" or not data or not data[0]:
            continue

        raw_email = data[0][1]
        if raw_email is None:
            continue

        message = email.message_from_bytes(raw_email)
        subject, encoding = decode_header(message["Subject"])[0]
        if isinstance(subject, bytes) and encoding:
            subject = subject.decode(encoding if encoding else "utf-8")
        if subject.lower().startswith("re:"):
            continue
        if email_type and email_type.lower() not in subject.lower():
            continue
        # on applique un filtre sur ce que l'on veux recuperer comme email
        message_id = message.get("Message-ID")

        sender = message.get("From")
        if not (
            (
                "Avis negatif" in subject
                or "Avis positif" in subject
                or "Prise de contact" in subject
            )
            and ("staff.modo.ecoride@gmail.com" in sender)
        ):
            continue

        body = ""
        # on autopsie l'email recu
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "text/html":
                    gerer_caractere_speciaux = chardet.detect(part.get_payload())
                    if gerer_caractere_speciaux["encoding"]:
                        body = part.get_payload(decode=True).decode(
                            gerer_caractere_speciaux["encoding"]
                        )
                    else:
                        body = part.get_payload(decode=True).decode()
                    break
        else:
            body = message.get_payload(decode=True).decode()
        email_data = {
            "id": email_id.decode(),
            "subject": subject,
            "sender": sender,
            "body": body,
            "message_id": message_id,
        }
        emails.append(email_data)
        if email_id_selected and email_id_selected == email_data["id"]:
            selected_email = email_data


    return email_type, email_id_selected, mail_ids, emails, selected_email
