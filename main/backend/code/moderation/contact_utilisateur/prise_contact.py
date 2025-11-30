from django.shortcuts import redirect
from django.contrib import messages
from ....forms import ContactForm
from ...utils import supprimer_mail
from django.urls import reverse
import asyncio



def PrisedeContact(request, email_id_selected, telephone, sujet, email_user, pseudo, commentaire):
    user= request.user

    contact_form = ContactForm(request.POST or None, initial={"email": email_user,"pseudo":pseudo,"telephone":telephone, "sujet":sujet, "message": commentaire})
    if user.is_superuser:
        for name, field in contact_form.fields.items():
            #name permet de cibler le nom du champ
            #field permet de cibler le champ en lui même
            if name != "reponse":
                field.widget.attrs["readonly"] = True

    if request.method == "POST":
        if contact_form.is_valid():
            reponse_modo = contact_form.cleaned_data["reponse"]
            subject = "Prise de contact"
            contact_url = request.build_absolute_uri(reverse("_contact"))
            context = {
                "pseudo": pseudo,
                "telephone": telephone,
                "email_user": email_user,
                "sujet": sujet,
                "reponse_modo": reponse_modo,
                "contact_url": contact_url,
            }

            from ...envoi_email.send_email import envoi_email
            envoi_email(request, to=email_user, subject=subject, template="style_email/_reponse_modo.html", context=context)
            if request.POST.get("repondre") == "oui":
                asyncio.run(supprimer_mail(email_id_selected))
                messages.success(request, "Email traité.")
            return redirect(f"{reverse('moderation_email')}?email_type=Prise+de+contact")

        else:
            messages.error(request, "Erreur dans le formulaire.")
    return contact_form
