from django.shortcuts import render, redirect
from django.contrib import messages
from ..forms import ContactForm


def  PriseDeContact(request, email_id_selected, mail, telephone, sujet, email_user, pseudo, commentaire):

    contact_form = ContactForm(request.POST or None, initial={"email": email_user,"pseudo":pseudo,"telephone":telephone, "sujet":sujet, "message": commentaire})

    if request.method == "POST":
        if contact_form.is_valid():
            reponse_modo = contact_form.cleaned_data["reponse"]
            
            from ..envoi_email import Envoi_Reponse_Modo
            Envoi_Reponse_Modo(request, email_user, commentaire, pseudo, reponse_modo)
            if request.POST.get("repondre") == "oui":
                mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                mail.expunge()
                messages.success(request, "Email supprimé.")
            return redirect("moderation_email")
        else:
            messages.error(request, "Erreur dans le formulaire.")
    return contact_form
