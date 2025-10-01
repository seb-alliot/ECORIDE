from django.contrib import messages
from django.shortcuts import redirect
from django.db import transaction
from ....models import  CreditUser
from ....forms import TrajetForm
from django.urls import reverse
from django.utils import timezone


def ProposeTonCovoiturage(request):
    user = request.user
    trajet_form = TrajetForm(request.POST, user=user)
    maintenant = timezone.localtime()

    if request.method == "POST" and request.POST.get("form_soumis") == "trajet_form":

        if trajet_form.is_valid():
            trajet = trajet_form.save(commit=False)
            try:
                with transaction.atomic():
                    if trajet_form.cleaned_data["date"] < maintenant.date():
                        messages.error(
                            request,
                            "La date de départ ne peux être inférieur à la date actuelle.",
                        )
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
                    #credit_user = CreditUser.objects.get(user=user) code de base
                    # on verrouille les credits de l'utilisateur pour éviter les problèmes avec select_for_update
                    credit_user = CreditUser.objects.select_for_update().get(user=user)
                    # __(on retire la commission au credit utilisateur) ==> transformer via le signal, une verif reste ici pour le request message
                    if credit_user.credit < 2:
                        messages.error(
                            request,
                            "Vos crédits sont insuffisants pour proposer un covoiturage.",
                        )
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
                    else:
                        trajet.chauffeur = user
                        trajet.save()
                        # on reinitialise le formulaire pour éviter de garder les données et eviter les erreurs
                        # sur les page actualisées
                        trajet_form = TrajetForm()

                        messages.success(
                            request,
                            "Votre covoiturage a bien été ajouté. Merci pour votre contribution !",
                        )
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
            except CreditUser.DoesNotExist:
                messages.error(
                    request,
                    "Erreur lors de la mise à jour du crédit administrateur.",
                )
                return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
        else:
            trajet_form = TrajetForm()
            messages.error(
                request,
                "Une erreur est apparue lors de la proposition de covoiturage.",
            )
    return trajet_form