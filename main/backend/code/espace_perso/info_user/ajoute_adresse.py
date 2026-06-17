from django.contrib import messages
from django.shortcuts import redirect
from ....models import AdresseUser
from ....forms import AdresseForm
from django.urls import reverse


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
                return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
            else:
                for erreur in adresse_form.non_field_errors():
                    messages.error(request, erreur)
                for champ, erreurs in adresse_form.errors.items():
                    if champ == "__all__":
                        continue
                    libelle = adresse_form.fields[champ].label or champ
                    for erreur in erreurs:
                        messages.error(request, f"{libelle} : {erreur}")
                if not adresse_form.errors:
                    messages.error(request, "Tous les champs sont obligatoires.")
                return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
        else:
            adresse_form = AdresseForm(instance=adresse_user, user=user)

        return adresse_form

    except Exception as e:
        messages.error(request, f"Une erreur est survenue lors de la mise à jour de vos informations. {e}")
        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
