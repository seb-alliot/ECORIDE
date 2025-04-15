from django.http import HttpResponseRedirect
from email.header import decode_header
import chardet
import email

def RecuperationEmail(request, mail_ids, mail, emails):
    if not mail_ids:
        return HttpResponseRedirect("/admin/moderateur/moderation_email/",
            {"error": "Aucun email à modérer."}
        )

    email_id_selected = request.GET.get("email_id")
    email_type = request.GET.get("email_type", "").strip()
    filtered_emails = []

    for current_email_id in mail_ids:
        result, data = mail.fetch(current_email_id, "(RFC822)")
        if result != "OK" or not data or not data[0]:
            continue

        raw_email = data[0][1]
        if raw_email is None:
            continue

        message = email.message_from_bytes(raw_email)
        subject, encoding = decode_header(message["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")

        if subject.lower().startswith("re:"):
            continue

        sender = message.get("From")
        if not (
            ("Avis negatif" in subject or "Avis positif" in subject or "Prise de contact" in subject)
            and ("staff.modo.ecoride@gmail.com" in sender)
        ):
            continue

        if email_type and email_type not in subject:
            continue

        body = ""
        if message.is_multipart():
            for part in message.walk():
                if part.get_content_type() == "body/html":
                    charset = chardet.detect(part.get_payload())["encoding"]
                    if charset:
                        body = part.get_payload(decode=True).decode(charset)
                    else:
                        body = part.get_payload(decode=True).decode()
                    break
        else:
            body = message.get_payload(decode=True).decode()

        email_data = {
            "subject": subject,
            "sender": sender,
            "body": body,
        }

        filtered_emails.append({
            "id": current_email_id.decode(),
            "subject": subject,
            "sender": sender,
            "email_id": current_email_id,
        })

        emails.append(email_data)

    return email_id_selected, email_type, current_email_id, body, email_data, subject, emails
