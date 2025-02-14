#coding:utf-8

from django.contrib.auth import get_user_model, authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required

from .forms import (
    Inscription,
    IdentifiantForm,
    MotDePasseForm,
    AdresseForm,
    PreferenceForm,
    ChoixRoleForm,
    VoitureForm,
    TrajetForm,
    RechercheTrajetForm,
    FiltreTrajetForm,
    StatutTrajetForm,
    CustomSetPasswordForm,
    ConfirmEmailForm,
    ReservationTrajetForm,
    StatutReservationForm,
    AvisForm,
    AvisPassagerForm,
)
from .models import (
    CreditUser,
    ChoixRole,
    Preference,
    AdresseUser,
    Voiture,
    TrajetProposer,
    ReservationTrajet,
    ChangerStatutTrajet,
    ActivationToken,
    TokenValidation,
    NoteUser,
)
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetView

from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.core.mail import EmailMessage
from django.utils import timezone
from django.conf import settings
from django.views.generic import CreateView
from django.contrib.auth.models import User, AnonymousUser
from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP
import sys
from django.db.models import Avg, Value, Q
from django.db.models.functions import Coalesce

# ------------------------------------------------------------------------------------------
# ---------------------------------DEBUT CLASS DJANGO---------------------------------------
# ------------------------------------------------------------------------------------------

# Accueil en definition car fonction simple
def initialisation_template(request):
    photo_default_url = settings.MEDIA_URL + "photo_default/photo_default.jpg"
    user = request.user

    if request.user.is_authenticated:
        try:
            credit = CreditUser.objects.get(user=user)
        except CreditUser.DoesNotExist:
            credit = None
        trajets = TrajetProposer.objects.filter(chauffeur=user)
        adresse_user = AdresseUser.objects.filter(user=user).first()
    if user.is_anonymous:
        credit = None
        adresse_user = None
        trajets = None

    context = {
        "credit": credit,
        "adresse_user": adresse_user,
        "trajets": trajets,
        "photo_default_url": photo_default_url,
    }
    return context


def accueil(request):
    # Initialisation des formulaires
    adresse_form = TrajetForm()
    recherche_form = RechercheTrajetForm(request.GET)
    filtre_form = FiltreTrajetForm(request.GET)
    resultat = None
    resultat_filtrer = None

    form_trajet = request.GET.get("form_trajet")

    if request.method == "GET":
        # Formulaire de recherche de trajet
        if form_trajet == "recherche_form" and recherche_form.is_valid():
            ville_depart = recherche_form.cleaned_data["ville_depart"]
            ville_arrivee = recherche_form.cleaned_data["ville_arrivee"]
            date = recherche_form.cleaned_data["date"]
            resultat = TrajetProposer.objects.filter(
                ville_depart__icontains=ville_depart,
                ville_arrivee__icontains=ville_arrivee,
                date=date,
            )
            messages.success(request, "Recherche effectuée avec succès.")

        # Formulaire de filtrage de trajet
        if form_trajet == "filtre_form" and filtre_form.is_valid():
            type_moteur = filtre_form.cleaned_data["type_moteur"]
            places = filtre_form.cleaned_data["places"]
            prix = filtre_form.cleaned_data["prix"]

            resultat = TrajetProposer.objects.filter(
                type_moteur__icontains=type_moteur,
                places__icontains=places,
                prix=prix,
            )

            resultat_filtrer = TrajetProposer.objects.filter(
                type_moteur__icontains=type_moteur,
                places__icontains=places,
                prix__icontains=prix,
            )
            messages.success(request, "Filtrage effectué avec succès.")

    context = {
        "adresse_form": adresse_form,
        "recherche_form": recherche_form,
        "filtre_form": filtre_form,
        "resultat": resultat,
        "form_trajet": form_trajet,
        "resultat_filtrer": resultat_filtrer,
        "messages": messages.get_messages(request),
    }
    context.update(initialisation_template(request))
    return render(request, "index.html", context)


# --------------------------------------Vue generic django modifier----------------------------------------------------


# --------------------------ajout des crédit à la confirmation du compte------------------------------------------------


class UserCreateView(CreateView):

    model = User
    form_class = Inscription
    template_name = "inscription/inscription.html"
    success_url = reverse_lazy("index")

    # Faire apparaitre l'image par default dans le template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo_default_url = settings.MEDIA_URL + "photo_default/photo_default.jpg"
        context["photo_default_url"] = photo_default_url
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()

        role = ChoixRole.objects.create(role="passager", user=user)
        credit_user = CreditUser.objects.create(user=user)
        note = NoteUser.objects.create(chauffeur=user)

        uidb64 = urlsafe_base64_encode(str(user.pk).encode("utf-8"))
        token = default_token_generator.make_token(user)
        activation_token = ActivationToken.objects.create(user=user, token=token)
        activation_url = self.request.build_absolute_uri(
            reverse(
                "activation", kwargs={"token": activation_token.token, "uidb64": uidb64}
            )
        )
        self.ActivationCompte(user, uidb64, activation_url)
        return redirect(self.success_url)

    def ActivationCompte(self, user, uidb64, activation_url):

        subject = "Activation de votre compte EcoRide"
        context = {"user": user, "activation_url": activation_url, "uidb64": uidb64}
        message = render_to_string("inscription/activation_email.html", context)
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="alliotsebastien04@gmail.com",
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send()


def activation(request, uidb64, token):
    try:
        user = urlsafe_base64_decode(uidb64).decode("utf-8")
        activation_token = ActivationToken.objects.get(token=token)
        user = activation_token.user

        if activation_token.is_expired():
            activation_token.delete()
            messages.error(request, "Le lien a expiré.")
            return redirect("inscription")
        user.is_active = True
        credit_user = CreditUser.objects.get(user=user)
        credit_user.credit += 20
        user.save()
        credit_user.save()
        activation_token.delete()
        messages.success(request, "Votre compte a été activé.")
        return redirect("connection1")
    except ActivationToken.DoesNotExist:
        messages.error(request, "Une erreur est survenue.")
        return redirect("inscription")


# ----------------------------reset passaword----------------------------------------------


class CustomPasswordResetView(PasswordResetView):
    form_class = ConfirmEmailForm
    template_name = "réinitialisation/password_reset_form.html"
    success_url = reverse_lazy("index")

    # Faire apparaitre l'image par default mais ne fonctionne pas ici, pourquoi?
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo_default_url = settings.MEDIA_URL + "photo_default/photo_default.jpg"
        context["photo_default_url"] = photo_default_url
        return context

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        user = User.objects.get(email=email)
        self.user = user
        messages.success(self.request, "Un e-mail de réinitialisation a été envoyé.")
        return super().form_valid(form)


class CustomResetPasswordConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "réinitialisation/password_reset_confirm.html"
    success_url = reverse_lazy("index")

    # ici non plus, les seul vue on je renvois un template dans les url path
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        photo_default_url = settings.MEDIA_URL + "photo_default/photo_default.jpg"
        context["photo_default_url"] = photo_default_url
        return context

    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été changé.")
        return super().form_valid(form)


# ------------------------------Connection en 2 étapes------------------------------------------------


# operation 1 : demande d'identifiant
def connection1(request):
    username = request.POST.get("username")
    username = None
    form = IdentifiantForm()

    if request.method == "POST":
        form = IdentifiantForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            try:
                user = get_user_model().objects.get(username=username)
                request.session["user_id"] = user.id
                # gestio du token de session
                token, created = TokenValidation.objects.get_or_create(
                    user=user, defaults={"token": get_random_string(32)}
                )
                request.session["token"] = token.token
                request.session["token"] = token.token
                return redirect("connection2")
            except get_user_model().DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
                return redirect("connection1")
    context = {
        "form": form,
    }
    context.update(initialisation_template(request))
    return render(request, "login/connection1.html", context)


# operation 2 : demande de mot de passe


def connection2(request):
    connected_users = request.session.get("connected_users", [])
    user_id = request.session.get("user_id")
    token = request.session.get("token")

    if request.method == "POST":
        form = MotDePasseForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]
            if user_id is None:
                messages.error(request, "L'identifiant n'a pas étè trouvé.")
                return redirect("connection1")
        try:
            user = get_user_model().objects.get(id=user_id)
            authenticated_user = authenticate(username=user.username, password=password)
            if authenticated_user:

                if user_id not in connected_users:
                    connected_users.append(user_id)
                    request.session["connected_users"] = connected_users
                TokenValidation.objects.filter(user=user).delete()
                login(request, authenticated_user)
                request.session.pop("user_id", None)
                request.session.pop("token", None)

                messages.success(request, "Vous êtes connecté.")
                return redirect("index")
            else:
                messages.error(request, "Votre mot de passe incorrect.")
                return redirect("connection2")
        except get_user_model().DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
            return redirect("connection1")
    else:
        form = MotDePasseForm()
    context = {
        "form": form,
    }
    context.update(initialisation_template(request))
    return render(request, "login/connection2.html", context)


# --------------------------Deconnection-----------------------------------------------


def logout_view(request):
    logout(request)
    return redirect("/")


# --------------------------Espace Personnel-------------------------------------------
@login_required
def MonCompte(request):
    # Récupération des données utilisateur
    user = request.user

    adresse_user = get_object_or_404(AdresseUser, user=request.user)\
        or None if AdresseUser.objects.filter(user=request.user).exists() else None
    role = ChoixRole.objects.filter(user=user).first()
    preference = Preference.objects.filter(user_preference=user).first()
    trajet = TrajetProposer.objects.filter(chauffeur=user).first()
    voiture = Voiture.objects.filter(user=user)
    reservation = ReservationTrajet.objects.filter(passager=user)
    prix_total_paye = ReservationTrajet.paiement_total_passager(request.user, trajet)
    chauffeur = TrajetProposer.objects.filter(chauffeur=user).first()

    # Initialisation des formulaires
    adresse_form = AdresseForm(instance=adresse_user)
    preference_form = PreferenceForm(instance=preference)
    role_form = ChoixRoleForm(instance=role)
    voiture_form = VoitureForm(request.POST)
    trajet_form = TrajetForm(user=user)
    etat_form = StatutTrajetForm(request.POST)
    reservation_form = StatutReservationForm(request.POST)

    filtre_form = FiltreTrajetForm(request.GET)
    recherche_form = RechercheTrajetForm(request.GET)

    resultat = None
    resultat_filtrer = None

    form_trajet = request.GET.get("form_trajet")
    form_soumis = request.POST.get("form_soumis")

    if request.method == "POST":

        # __________ Formulaire d'ajout d'adresse___________
        if form_soumis == "adresse_form":
            adresse_form = AdresseForm(
                request.POST, request.FILES, instance=adresse_user
            )
            if adresse_form.is_valid():
                adresse = adresse_form.save(commit=False)
                adresse.user = user
                adresse.save()
                messages.success(request, "Vos informations  été mis à jour.")
                return redirect("MonCompte")
            else:
                messages.error(request, "Tous les champs sont obligatoires.")

        # _________Formulaire de choix de rôle___________________
        elif form_soumis == "role_form":
            role_form = ChoixRoleForm(request.POST, instance=role)
            if role_form.is_valid():
                role = role_form.save(commit=False)
                role.user = user
                role.save()
                messages.success(request, "Votre rôle a été modifié")

                return redirect("MonCompte")
            else:
                messages.error(request, "Un soucis est arrivé quand a comment vous définir.")

        # _________Formulaire des preferences chauffeur___________________
        elif form_soumis == "preference_form":
            preference_form = PreferenceForm(request.POST, instance=preference)
            if preference_form.is_valid():
                preference = preference_form.save(commit=False)
                preference.user_preference = user
                preference.save()
                messages.success(request, "Vos préférences ont été enregistrées.")
                return redirect("MonCompte")
            else:
                messages.error(request, "Vos préférences pourris ont été rejeter.")


        # __________Formulaire d'ajout de voiture___________
        elif form_soumis == "voiture_form":
            voiture_form = VoitureForm(request.POST)
            if voiture_form.is_valid():
                voiture = voiture_form.save(commit=False)
                voiture.user = user
                voiture.save()
                messages.success(request, "Votre véhicule a bien été ajouté.")
                return redirect("MonCompte")
            else:
                messages.error(
                    request,
                    "Votre est bon pour la casse et refusé par la même occasion, désolé :'( ",
                )

        # __________Formulaire de proposition de trajet___
        elif form_soumis == "trajet_form":
            trajet_form = TrajetForm(request.POST)
            if trajet_form.is_valid():
                trajet = trajet_form.save(commit=False)
                commission = 2
                try:
                    # __on retire la commission au credit utilisateur__
                    credit_user = CreditUser.objects.get(user=user)
                    if credit_user.credit < 2:
                        messages.error(
                            request, "Crédit insuffisant pour proposer un covoiturage."
                        )
                        return redirect("MonCompte")
                    else:
                        credit_user.credit -= commission
                        credit_user.save()

                    # __on recupere l'admin__
                    superuser = User.objects.filter(is_superuser=True).first()
                    # __on recupere ses credit__
                    credit_admin = CreditUser.objects.get(user=superuser)

                    # __on ajoute la commission au credit admin__
                    credit_admin.credit += commission
                    credit_admin.save()

                    trajet.chauffeur = user
                    trajet.save()
                    messages.success(
                        request, "Votre covoiturage a été ajouté avec succé"
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
                messages.error(
                    request, "Une erreur lors de la proposition de covoiturage."
                )
                return redirect("MonCompte")

        # Formulaire de changement de statut de trajet
        elif form_soumis == "etat_form":
            etat_form = StatutTrajetForm(request.POST)
            trajet_id = request.POST.get("trajet_id")
            if etat_form.is_valid():

                # ______PARTIE CHAUFFEUR______

                if request.user == trajet.chauffeur:
                    trajet = get_object_or_404(TrajetProposer, id=trajet_id)
                    # bien mettre trajet.chauffeur et non pas role.chauffeur  ou display comme en html sa ne fonctionne pas, erreur muette
                    statut_trajet = etat_form.cleaned_data["statut"]
                    Changer_statut = ChangerStatutTrajet.objects.create(
                        trajet=trajet,
                        statut=statut_trajet,
                    )
                    if statut_trajet == "Terminé":
                        reservations = ReservationTrajet.objects.filter(
                            trajet_reserver=trajet
                        )
                        trajet.etat = statut_trajet
                        trajet.save()
                        messages.success(request, "Trajet terminé avec succès.")
                        Envoi_Email_Terminer(request, trajet_id, reservations)

                    elif statut_trajet == "En cours":
                        trajet.etat = statut_trajet
                        trajet.save()
                        messages.success(request, "Trajet demarrer, bon voyage")

                    # ______________ANNULATION TRAJET PAR LE CHAUFFEUR_____________

                    elif statut_trajet == "Annulé":
                        try:
                            # Récupérer le trajet concerné
                            trajet_reserver = get_object_or_404(TrajetProposer, id=trajet_id)

                            # Vérifier si le trajet a déjà été remboursé
                            if trajet_reserver.trajet_rembourser:
                                messages.error(request, "Le trajet a déjà été remboursé.")
                                return redirect("MonCompte")

                            reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_reserver)
                            total_place_reserver = sum(reservation.places for reservation in reservations)

                            # Rendre les places disponibles à nouveau
                            trajet_reserver.places += total_place_reserver
                            trajet_reserver.etat = "Annulé"
                            trajet_reserver.trajet_rembourser = True
                            reservation.etat_reservation = "Annulé"
                            reservation.save()
                            trajet_reserver.save()

                            # Remboursement des passagers
                            for reservation in reservations:
                                try:
                                    prix_payer = reservation.places * trajet_reserver.prix
                                    credit_passager = get_object_or_404(CreditUser, user=reservation.passager)
                                    credit_passager.credit += prix_payer
                                    credit_passager.save()

                                    reservation.etat_reservation = "Annulé"
                                    reservation.reservation_rembourser = True
                                    reservation.save()
                                except Exception as e:
                                    messages.error(
                                        request, f"Erreur lors du remboursement du passager : {str(e)}"
                                    )
                                    continue

                            # Redonne la comme au chauffeur
                            try:
                                credit_chauffeur = get_object_or_404(CreditUser, user=trajet_reserver.chauffeur)
                                comission = 2
                                credit_chauffeur.credit += comission
                                credit_chauffeur.save()
                            except Exception as e:
                                messages.error(
                                    request, f"Erreur lors du retrait des gains du chauffeur : {str(e)}"
                                )

                            # Retirer la commission de l'admin
                            try:
                                superuser = User.objects.filter(is_superuser=True).first()
                                if superuser:
                                    credit_admin = get_object_or_404(CreditUser, user=superuser)
                                    comission_admin = 2
                                    credit_admin.credit -= comission_admin
                                    credit_admin.save()
                                else:
                                    messages.error(request, "L'administrateur n'a pas été trouvé.")
                            except Exception as e:
                                messages.error(
                                    request, f"Erreur lors du débit de la commission pour la plateforme : {str(e)}"
                                )

                            # Envoyer l'email d'annulation
                            Envoi_Email_Annulation(request, trajet_id, reservations)
                            messages.success(request, "Trajet annulé et remboursements effectués avec succès.")
                            return redirect("MonCompte")

                        except Exception as e:
                            messages.error(request, f"Erreur lors de l'annulation du trajet : {str(e)}")


        # ______________ANNULATION TRAJET PAR LE PASSAGER____
        elif form_soumis == "reservation_form":
            reservation_form = StatutReservationForm(request.POST)
            reservation_id = request.POST.get("reservation_id")
            reservation = get_object_or_404(ReservationTrajet, id=reservation_id)

            if reservation.reservation_rembourser:
                messages.error(request, "La réservation a déjà été remboursée.")
                return redirect("MonCompte")

            if reservation_form.is_valid():
                if request.user == reservation.passager:
                    etat_reservation = reservation_form.cleaned_data["etat_reservation"]

                    if etat_reservation == "Annulé":
                        trajet = reservation.trajet_reserver
                        trajet.places += reservation.places
                        trajet.save()

                        prix_payer = reservation.places * trajet.prix
                        credit_user = CreditUser.objects.get(user=request.user)
                        credit_user.credit += prix_payer
                        credit_user.save()

                        trajet.total_payer -= prix_payer
                        trajet.save()

                        reservation.etat_reservation = "Annulé"
                        reservation.reservation_rembourser = True
                        reservation.save()
                        messages.success(request, "Réservation annulée avec succès.")
                        return redirect("MonCompte")
                    else:
                        messages.error(request, "Réservation introuvable.")
                        return redirect("MonCompte")

    # ______________Recherche de trajet____________________

    # on ne peut pas reserver son propre trajet en tant que passager a retirer une fois le back en place
    if request.method == "GET":
        resultat = None

        # Formulaire de recherche de trajet
        if form_trajet == "recherche_form" and recherche_form.is_valid():
            ville_depart = recherche_form.cleaned_data["ville_depart"]
            ville_arrivee = recherche_form.cleaned_data["ville_arrivee"]
            date = recherche_form.cleaned_data["date"]

            resultat = TrajetProposer.objects.filter(
                # icontains pour la recherche insensible a la casse
                ville_depart__icontains=ville_depart,
                ville_arrivee__icontains=ville_arrivee,
                date=date,
                etat = "Disponible",
                places__gt=0,
            )
            resultat = resultat.exclude(chauffeur=user.id, etat="Terminé")

            request.session["resultat_recherche"] = list(
                resultat.values_list("id", flat=True)
            )
            messages.success(request, "Recherche effectuée avec succès.")

        # ______________FILTRE DE TRAJET____________________

        # Formulaire de filtrage de trajet
        elif form_trajet == "filtre_form" and filtre_form.is_valid():
            request.session.get("resultat_recherche") == resultat
            resultat = TrajetProposer.objects.filter(
                id__in=request.session.get("resultat_recherche")
            )

            if filtre_form.cleaned_data["note"]:
                note_minimum = filtre_form.cleaned_data["note"]
                chauffeurs = User.objects.annotate(
                    note_moyenne=Avg("accusé__note")
                ).filter(note_moyenne__gte=note_minimum)

                for chauffeur in chauffeurs:
                    print(f"Chauffeur: {chauffeur.username}, Note Moyenne: {chauffeur.note_moyenne}")
                resultat = resultat.filter(chauffeur__in=chauffeurs)

            if filtre_form.cleaned_data["temps_trajet"]:
                resultat = resultat.filter(temps_trajet__lte=filtre_form.cleaned_data["temps_trajet"])

            if filtre_form.cleaned_data["prix"]:
                resultat = resultat.filter(prix__lte=filtre_form.cleaned_data["prix"])

            messages.success(request, "Filtrage effectué avec succès dans  la depression")

    context = {
        # utilisateur
        "role": role,
        "preference": preference,
        "adresse_user": adresse_user,
        "voiture": voiture,
        "chauffeur": chauffeur,

        #trajet
        "prix_total_paye": prix_total_paye,
        "trajet": trajet,
        "reservation": reservation,
        "reservations": "reservations",

        # recherche et filtre
        "resultat": resultat,
        "resultat_filtrer": resultat_filtrer,

        #formulaire:

        # __utilisateur__
        "preference_form": preference_form,
        "adresse_form": adresse_form,
        "role_form": role_form,
        "voiture_form": voiture_form,

        #__trajet__
        "trajet_form": trajet_form,
        "filtre_form": filtre_form,
        "recherche_form": recherche_form,

        #__reservation__
        "reservation_form": reservation_form,
        "etat_form": etat_form,

        "messages": messages.get_messages(request),
    }
    context.update(initialisation_template(request))
    return render(request, "interface_utilisateur/utilisateur/MonCompte.html", context)


# -----------------------------------------------------------------------------------------


def SelectionTrajet(request):
    user = request.user

    if not user.is_authenticated:
        messages.info(
            request,
            "Vous pouvez consulter les trajets, mais vous devez vous inscrire pour réserver.",
        )

    # Initialisation des données utilisateur
    photo_default_url = settings.MEDIA_URL + "photo_default/photo_default.jpg"
    adresse_user = AdresseUser.objects.filter(user=user).first() if user.is_authenticated else None

    try:
        credit_user = CreditUser.objects.get(user=user) if user.is_authenticated else None
        credits = credit_user.credit if credit_user else 0
    except CreditUser.DoesNotExist:
        credits = 0

    # Récupération du trajet
    trajet_id = request.GET.get("trajet_id")
    trajet = get_object_or_404(TrajetProposer, id=trajet_id)
    chauffeur = trajet.chauffeur

    # Récupération des notes du chauffeur
    note_chauffeur = NoteUser.objects.filter(chauffeur=chauffeur).first()

    # Vérification d'une réservation existante pour l'utilisateur
    reservation = ReservationTrajet.objects.filter(passager=user, trajet_reserver=trajet).first()

    # Initialisation du formulaire
    reservation_form = ReservationTrajetForm(request.POST or None, instance=reservation)

    # Logique de réservation uniquement pour les utilisateurs authentifiés
    if request.method == "POST" and user.is_authenticated:
        if reservation_form.is_valid():
            places_reservees = reservation_form.cleaned_data["places"]

            # Vérification du crédit suffisant
            prix_total = trajet.prix * places_reservees
            if credits < prix_total:
                messages.error(request, "Crédit insuffisant pour réserver ce trajet.")
                return redirect("interface_utilisateur/utilisateur/reservation.html")

            # Vérification du nombre de places disponibles
            if places_reservees > trajet.places:
                messages.error(request, "Nombre de places insuffisant pour ce trajet.")
                return redirect("interface_utilisateur/utilisateur/reservation.html")

            # Vérification et mise à jour de la réservation
            if reservation:
                if reservation.etat_reservation == "Annulé":
                    reservation = ReservationTrajet.objects.create(
                        trajet_reserver=trajet,
                        passager=user,
                        prix_par_passager=prix_total,
                        places=places_reservees,
                    )
                else:
                    reservation.places += places_reservees
                    reservation.paiement_passager(places_reservees)
            else:
                reservation = ReservationTrajet.objects.create(
                    trajet_reserver=trajet,
                    passager=user,
                    prix_par_passager=prix_total,
                    places=places_reservees,
                )
                credit_user.credit -= prix_total
                credit_user.save()

            # Mise à jour des places restantes
            trajet.places -= places_reservees
            trajet.save()

            messages.success(request, "Réservation effectuée avec succès.")
            return redirect("MonCompte")
        else:
            messages.error(request, "Erreur lors de la réservation.")

    # Contexte pour le template
    context = {
        "note_chauffeur": note_chauffeur,
        "chauffeur": chauffeur,
        "reservation_trajet": reservation,
        "reservation_form": reservation_form,
        "photo_default_url": photo_default_url,
        "adresse_user": adresse_user,
        "credits": credits,
        "trajet": trajet,
        "messages": messages.get_messages(request),
    }
    context.update(initialisation_template(request))

    return render(request, "interface_utilisateur/utilisateur/reservation.html", context)


def Envoi_Email_Annulation(request, trajet_id, reservations):

    try:
        site_url = f"http://{get_current_site(request).domain}"
        monprofile_url = f"{site_url}{reverse('MonCompte')}"

        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver
            subject = "Annulation de votre trajet"

            context = {
                "reservations": reservations,
                "site_url": site_url,
                "monprofile_url": monprofile_url,
                "passager": passager,
                "chauffeur": chauffeur,
                "date": date,
                "trajet": trajet,
            }

            message = render_to_string(
                "style_email/annulation_confirmation.html", context
            )

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email="alliotsebastien04@gmail.com",
                to=[passager.email],
            )
            email.content_subtype = "html"
            email.send()

        messages.success(request, "E-mail d'annulation envoyé avec succès.")

    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail d'annulation: {str(e)}")
        messages.error(
            request, f"Erreur lors de l'envoi de l'e-mail d'annulation : {str(e)}"
        )


def Envoi_Email_Terminer(request, trajet_id, reservations):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id])}"
        )

        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver
            subject = "Confirmation de fin de covoiturage"

            context = {
                "reservations": reservations,
                "site_url": site_url,
                "avis_satisfaction_url": avis_satisfaction_url,
                "passager": passager,
                "chauffeur": chauffeur,
                "date": date,
                "trajet": trajet,
            }

            message = render_to_string(
                "style_email/covoit_termine.html", context
            )

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email="alliotsebastien04@gmail.com",
                to=[passager.email],
            )
            email.content_subtype = "html"
            email.send()

        messages.success(request, "E-mail de confirmation de fin de covoiturage.")

    except Exception as e:
        print(
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturage: {str(e)}"
        )
        messages.error(
            request,
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturag : {str(e)}",
        )

# ------------------------------------En cour-----------------------------------------------------

def Envoi_Email_Avis_Trajet_Nagatif(request,passager, trajet_id, reservations):
    try:
        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id])}"
        )

        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver
            subject = "Confirmation de fin de covoiturage"

            context = {
                "reservations": reservations,
                "site_url": site_url,
                "avis_satisfaction_url": avis_satisfaction_url,
                "passager": passager,
                "chauffeur": chauffeur,
                "date": date,
                "trajet": trajet,
            }

            message = render_to_string(
                "style_email/covoit_termine.html", context
            )

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email="alliotsebastien04@gmail.com",
                to=["staff.modo.ecoride@gmail.com"],
            )
            email.content_subtype = "html"
            email.send()

        messages.success(request, "E-mail de confirmation de fin de covoiturage.")

    except Exception as e:
        print(
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturage: {str(e)}"
        )
        messages.error(
            request,
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturag : {str(e)}",
        )

def Envoi_Email_Avis_Trajet_Positif(request, chauffeur, trajet_id, reservations):

    try:
        site_url = f"http://{get_current_site(request).domain}"
        avis_satisfaction_url = (
            f"{site_url}{reverse('AvisSatisfaction', args=[trajet_id])}"
        )

        reservations = ReservationTrajet.objects.filter(trajet_reserver=trajet_id)
        for res in reservations:
            passager = res.passager
            chauffeur = res.trajet_reserver.chauffeur
            date = res.trajet_reserver.date
            trajet = res.trajet_reserver
            subject = "Confirmation de fin de covoiturage"

            context = {
                "reservations": reservations,
                "site_url": site_url,
                "avis_satisfaction_url": avis_satisfaction_url,
                "passager": passager,
                "chauffeur": chauffeur,
                "date": date,
                "trajet": trajet,
            }

            message = render_to_string(
                "style_email/covoit_termine.html", context
            )

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email="alliotsebastien04@gmail.com",
                to=["staff.modo.ecoride@gmail.com"],
            )
            email.content_subtype = "html"
            email.send()

        messages.success(request, "E-mail de confirmation de fin de covoiturage.")

    except Exception as e:
        print(
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturage: {str(e)}"
        )
        messages.error(
            request,
            f"Erreur lors de l'envoi de l'e-mail de confirmation de fin de covoiturag : {str(e)}",
        )


def AvisSatisfaction(request, trajet_id):
    trajet = get_object_or_404(TrajetProposer, id=trajet_id)
    reservation = ReservationTrajet.objects.filter(trajet_reserver=trajet).first()
    chauffeur = trajet.chauffeur
    note_chauffeur = NoteUser.objects.filter(chauffeur=trajet.chauffeur).first()

    if not note_chauffeur:
        note_chauffeur = NoteUser(user=chauffeur)
    # surtout pas d'instance, sinon sa ecrase les données existante et donc les notes moyennes

    avis_soumis = None

    # oui ou non
    avis_form = AvisForm(request.POST)

    # suivant l'avis, mail different pour un moderateur, pres triage des avis
    Avis_Passager = AvisPassagerForm(request.POST)


    if request.method == "POST":
        if avis_form.is_valid():
            avis_soumis = avis_form.cleaned_data["avis"]

            if avis_soumis == "oui":
                avis_trajet = avis_form.save(commit=False)

                chauffeur = trajet.chauffeur
                credit_chauffeur = CreditUser.objects.get(user=chauffeur)
                facture_passager= reservation.prix_par_passager
                credit_chauffeur.credit += facture_passager
                credit_chauffeur.save()

                avis_trajet = avis_form.save(commit=False)
                avis_trajet.chauffeur = trajet.chauffeur
                avis_trajet.passager = request.user
                avis_trajet.trajet = trajet
                avis_trajet.save()
                Envoi_Email_Avis_Trajet_Positif(request, chauffeur, trajet_id, reservation)
                return redirect("AvisSatisfaction", trajet_id=trajet_id)


            elif avis_soumis == "non":
                passager = reservation.passager
                Envoi_Email_Avis_Trajet_Nagatif(request, passager,trajet_id, reservation)
                return redirect("AvisSatisfaction", trajet_id=trajet_id)




            messages.success(request, "Votre avis a été enregistré.")
            return redirect("MonCompte")
        else:
            messages.error(
                request, "Erreur lors de l'enregistrement de votre avis."
            )


    context = {

        "trajet": trajet,
        "chauffeur": chauffeur,
        "reservation": reservation,
        "avis_soumis": avis_soumis,

        "AvisPassagerForm": AvisPassagerForm,
        "avis_form": avis_form,
        "messages": messages.get_messages(request),
    }
    context.update(initialisation_template(request))
    return render(
        request, "interface_utilisateur/utilisateur/avis_satisfaction.html", context
    )


# ------------------------------------A FAIRE------------------------------------------------------


# --------Trouver comment ajouter la photo par default sur le reset mdp-----------------------------
# --------Trouver comment supprimé l'ancienne photo avant d'udpate la nouvelle----------------------

# ------------------------------------A Finir avec javascript------------------------------------------------------


# --------retour sur onglet actif dynamique-------
# --------rendre les fitres de trajet dynamique-------
# --------choix de role dynamique -------
# --------ajout de voiture dynamique-------
# --------confirmation de trajet dynamique-------


# Pour plutart quand je serais a l'optimisation du site par tranche de defenition de fonction
