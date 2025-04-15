from django.contrib import messages
from django.shortcuts import redirect
from ..models import  CreditUser, User
from ..forms import TrajetForm


def ProposeTonCovoiturage(request):
    user = request.user
    trajet_form = TrajetForm(request.POST, user=user)

    if request.method == "POST" and request.POST.get("form_soumis") == "trajet_form":

        trajet_form = TrajetForm(request.POST)
        if trajet_form.is_valid():
            trajet = trajet_form.save(commit=False)
            commission = 2
            try:
                # __on retire la commission au credit utilisateur__
                credit_user = CreditUser.objects.get(user=user)
                if credit_user.credit < 2:
                    messages.error(
                        request,
                        "Vos crédits sont insuffisants pour proposer un covoiturage.",
                    )
                    return redirect("MonCompte")
                else:
                    credit_user.credit -= commission
                    credit_user.save()
                    # __on recupere l'admin__
                    superuser = User.objects.filter(is_superuser=True).first()
                    # __on recupere ses credit__
                    credit_admin, created = CreditUser.objects.get_or_create(user=superuser)

                    # __on ajoute la commission au credit admin__
                    credit_admin.credit += commission
                    credit_admin.save()

                    trajet.chauffeur = user
                    trajet.save()
                    trajet_form = TrajetForm()

                    messages.success(
                        request,
                        "Votre covoiturage a bien été ajouté. Merci pour votre contribution !",
                    )
            except CreditUser.DoesNotExist:
                messages.error(
                    request,
                    "Erreur lors de la mise à jour du crédit administrateur.",
                )
                return redirect("MonCompte")
            except Exception as e:
                messages.error(
                    request,
                    f"Erreur lors de la proposition de covoiturage : {str(e)}",
                )
                return redirect("MonCompte")
        else:
            trajet_form = TrajetForm()
            messages.error(
                request,
                "Une erreur est apparue lors de la proposition de covoiturage.",
            )
    return trajet_form