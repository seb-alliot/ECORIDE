from django.shortcuts import redirect
from django.contrib.auth.models import User
from ....models import AdresseUser
from ....forms import ContactForm
from ...envoi_email.send_email import envoi_email
from django.contrib import messages

def PriseContact(request, *, to, subject, template, context=None, from_email="staff.modo.ecoride@gmail.com"):

    user = request.user
    adresse_user = None
    if user.is_authenticated:
        try:
            adresse_user = AdresseUser.objects.get(user=user)
            contact_form = ContactForm(request.POST or None, user=user)
        except AdresseUser.DoesNotExist:
            email = User.objects.get(username=user).email
            contact_form = ContactForm(request.POST or None, initial={"email": email})
    elif user.is_anonymous:
        contact_form = ContactForm(request.POST or None)

    if request.method == "POST":
        if contact_form.is_valid():
            to = from_email
            subject = contact_form.cleaned_data["sujet"]
            template="style_email/contact.html"
            context = {
                "telephone": contact_form.cleaned_data["telephone"],
                "pseudo": contact_form.cleaned_data["pseudo"],
                "email_user": contact_form.cleaned_data["email"],
                "sujet": contact_form.cleaned_data["sujet"],
                "message": contact_form.cleaned_data["message"],
            }
            envoi_email(request, to=to, subject=subject, template=template, context=context)
            messages.success(request, "Votre message a bien été envoyé. Nous vous répondrons dans les plus brefs délais.")
            return redirect("index")
    return contact_form, adresse_user
