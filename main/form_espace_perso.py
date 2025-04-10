from django.contrib import messages
from django.contrib.auth.models import User
from django.shortcuts import redirect , get_object_or_404

from .forms import AdresseForm , ChoixRoleForm , PreferenceForm , VoitureForm , TrajetForm , TerminerTrajetForm
from .models import AdresseUser , ChoixRole , Preference , Voiture , CreditUser , TrajetProposer , ReservationTrajet

import uuid

def AjoutAdresse(request, adresse_user=None, user=None):
    user = request.user

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
            return None, redirect("MonCompte")
        else:
            if "email" in adresse_form.errors:
                messages.error(request, "Cette adresse email est déjà prise.")
            else:
                messages.error(request, "Tous les champs sont obligatoires.")
    else:
        adresse_form = AdresseForm(instance=adresse_user, user=user)

    return adresse_form

def ChangeTonRole(request):
    user = request.user
    role = ChoixRole.objects.filter(user=user).first()

    role_form = ChoixRoleForm(instance=role)
    if request.method == "POST" and request.POST.get("form_soumis") == "role_form":
        role_form = ChoixRoleForm(request.POST, instance=role)
        if role_form.is_valid():
            role = role_form.save(commit=False)
            role.user = user
            role.save()
            messages.success(request, "Votre rôle a été mis à jour.")
            return redirect("MonCompte")
        else:
            role_form = ChoixRoleForm(request.POST, instance=role)
            messages.error(request, "Veuillez sélectionner un rôle valide.")
    context = {
        "role_form": role_form,
        "role": role,
    }
    return role_form

def DonneTesPreferences(request):
    user = request.user
    preference = Preference.objects.filter(user_preference_id=user).first()
    preference_form = PreferenceForm(request.POST, instance=preference)

    if request.method == "POST" and request.POST.get("form_soumis") == "preference_form":
        preference_form = PreferenceForm(request.POST, instance=preference)
        if preference_form.is_valid():
            preference = preference_form.save(commit=False)
            preference.user_preference = user
            preference.save()
            messages.success(
                request, "Vos préférences ont été enregistrées, vous avez bon goût."
            )
            return redirect("MonCompte")
        else:
            preference_form = PreferenceForm(request.POST, instance=preference)
            messages.error(request, "Vos préférences pourries ont été rejetées.")
    return preference_form

def AjouteTaCaisse(request):
    user = request.user
    voiture = Voiture.objects.filter(user=user).first()
    voiture_form = VoitureForm(request.POST)

    if request.method == "POST" and request.POST.get("form_soumis") == "voiture_form":
        voiture_form = VoitureForm(request.POST)
        if voiture_form.is_valid():
            voiture = voiture_form.save(commit=False)
            voiture.user = user
            voiture.save()
            messages.success(request, "Votre véhicule a bien été ajouté.")
            return redirect("MonCompte")
        else:
            immatriculation = request.POST.get("immatriculation")
            if Voiture.objects.filter(immatriculation=immatriculation).exists():
                messages.error(request, "Cette immatriculation est déjà prise.")
            else:
                if immatriculation:
                    messages.error(request, "L'immatriculation n'a pas le bon format.")
    return voiture_form

def ProposeTonCovoiturage(request):
    user = request.user
    trajet_form = TrajetForm(request.POST)

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

def FiniTonCovoiturage(request):
    user = request.user
    trajet_terminer_form = TerminerTrajetForm(request.POST)
    trajet = TrajetProposer.objects.filter(chauffeur=user).first()

    if request.method == "POST" and request.POST.get("form_soumis") == "trajet_terminer_form":

        trajet_terminer_form = TerminerTrajetForm(request.POST)
        trajet_id = request.POST.get("trajet_id")
        if trajet_terminer_form.is_valid():
            token = None
            if token is None:
                token = uuid.uuid4()

            if request.user == trajet.chauffeur:
                trajet = get_object_or_404(TrajetProposer, id=trajet_id)
                # bien mettre trajet.chauffeur et non pas role.chauffeur  ou display comme en html sa ne fonctionne pas, erreur muette
                statut_trajet = trajet_terminer_form.cleaned_data["etat"]
                if statut_trajet == "Terminé":
                    reservations = ReservationTrajet.objects.filter(
                        trajet_reserver=trajet
                    )
                    reservations.update(etat_reservation="Terminé")
                    trajet.etat = statut_trajet
                    trajet.save()
                    messages.success(request, "Vous êtes arrivé à bon port !")
                    from main.views import Envoi_Email_Terminer
                    Envoi_Email_Terminer(request, trajet_id, reservations, token)
    return trajet_terminer_form
