from aioimaplib import aioimaplib
from dotenv import load_dotenv
import os

load_dotenv()

async def supprimer_mail(email_id):
    mail = aioimaplib.IMAP4_SSL(os.getenv("MAIL_IMAP_SERVER"))
    await mail.wait_hello_from_server()
    await mail.login(os.getenv("MAIL_IMAP_USER"), os.getenv("MAIL_IMAP_PASSWORD"))
    await mail.select("INBOX")
    await mail.store(email_id, "+FLAGS", "\\Deleted")
    await mail.expunge()
    await mail.logout()