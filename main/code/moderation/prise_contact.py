from django.shortcuts import redirect
from django.contrib import messages
from ...forms import ContactForm
from django.http import HttpResponseRedirect
from django.urls import reverse



def PriseDeContact(request, email_id_selected, mail, telephone, sujet, email_user, pseudo, commentaire):
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

            from ..envoi_email import Envoi_Reponse_Modo
            Envoi_Reponse_Modo(request, email_user, commentaire, pseudo, reponse_modo)
            if request.POST.get("repondre") == "oui":
                mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                mail.expunge()
                messages.success(request, "Email supprimé.")
            return redirect(f"{reverse('moderation_email')}?email_type=Prise+de+contact")

        else:
            messages.error(request, "Erreur dans le formulaire.")
    return contact_form
