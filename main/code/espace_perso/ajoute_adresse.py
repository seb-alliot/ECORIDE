from django.contrib import messages
from django.shortcuts import redirect
from ...models import AdresseUser
from ...forms import AdresseForm
import logging

# Création du logger
logger = logging.getLogger(__name__)

def AjoutTonAdresse(request, adresse_user=None, user=None):
    user = request.user
    try:
        if adresse_user is None:
            adresse_user = AdresseUser.objects.filter(user=user).first()
            if adresse_user is None:
                adresse_user = AdresseUser(user=user, email=user.email)

        if request.method == "POST" and request.POST.get("form_soumis") == "adresse_form":
            adresse_form = AdresseForm(request.POST, request.FILES, instance=adresse_user, user=user)

            if adresse_form.is_valid():
                adresse = adresse_form.save(commit=False)
                adresse.user = user
                adresse.save()
                messages.success(request, "Vos informations ont été mises à jour.")
                return redirect("MonCompte")
            else:
                if "email" in adresse_form.errors:
                    messages.error(request, "Cette adresse email est déjà prise.")
                else:
                    messages.error(request, "Tous les champs sont obligatoires.")
        else:
            adresse_form = AdresseForm(instance=adresse_user, user=user)

        return adresse_form

    except Exception as e:
        logger.error(f"Erreur lors de l'ajout de l'adresse pour l'utilisateur {user.id}: {str(e)}")
        messages.error(request, "Une erreur est survenue lors de la mise à jour de vos informations.")
        return redirect("MonCompte")
