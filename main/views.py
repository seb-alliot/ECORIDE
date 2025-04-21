# coding:utf-8

from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from email.header import decode_header

from .forms import (
    AfficherTrajetForm,
)

from .donnee_template import (
    InfoTrajet,
    Info_Reservation,
    initialisation_template,
)
from .code_doublon import RechercheTrajet, Filtre_trajet
from .espace_perso import (
    AjoutTonAdresse,
    AjouteTaCaisse,
    DonneTesPreferences,
    ChangeTonRole,
    FiniTonCovoiturage,
    GereTonCovoiteChauffeur,
    ProposeTonCovoiturage,
    GereTaReservationPassager,
)
from .utils import ChoisisTonCovoite, DonneTonAvis, UserCreateView, PriseContact
from .connection import PremierEtape, DeuxiemeEtape, is_superuser_or_moderateur
from .moderation import (
    ConnectionImaplib,
    RecuperationEmail,
    ExtractionDonnee,
    GereLesAvisNegatif,
    GereLesAvisPositif,
    PriseDeContact,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
from django.views.generic import CreateView
from django.contrib.auth.models import User


def Contact(request):
    context = {}

    contact_demander = PriseContact(request)
    if isinstance(contact_demander, HttpResponseRedirect):
        return contact_demander
    contact_form, adresse_user = contact_demander
    context["contact_form"] = contact_form
    context["adresse_user"] = adresse_user

    context.update(initialisation_template(request))
    return render(
        request,
        "interface_utilisateur/utilisateur/footer/_contact.html",
        context,
    )

def mentions_legales(request):

    context = {}
    context.update(initialisation_template(request))
    return render(
        request,
        "interface_utilisateur/utilisateur/footer/_faq.html",
        context,
    )

def accueil(request):
    context = {}

    recherche_form, first_resultat, second_resultat = RechercheTrajet(request)
    filtre_form, resultat1, resultat2 = Filtre_trajet(request)

    if request.method == "GET":

        # Formulaire de recherche de trajet
        if recherche_form:
            context["recherche_form"] = recherche_form

        elif filtre_form:
            context["filtre_form"] = filtre_form

    context = {
        # recherche
        "first_resultat": first_resultat,
        "second_resultat": second_resultat,
        # filtre
        "resultat1": resultat1,
        "resultat2": resultat2,
        # formulaire de la page
        "filtre_form": filtre_form,
        "recherche_form": recherche_form,
        # envoie des message au template, inutile si balise message dans le template
        "messages": messages.get_messages(request),
    }
    context.update(initialisation_template(request))
    return render(request, "index.html", context)

# ------------------------------Connection en 2 étapes------------------------------------------------

# operation 1 : demande d'identifiant
def connection1(request):
    context = {}

    form = PremierEtape(request)
    if isinstance(form, HttpResponseRedirect):
        return form
    context["form"] = form

    context.update(initialisation_template(request))
    return render(request, "login/connection1.html", context)


# operation 2 : demande de mot de passe et code connection 2fa
def connection2(request):
    context = {}

    form = DeuxiemeEtape(request)
    if isinstance(form, HttpResponseRedirect):
        return form
    context["form"] = form

    context.update(initialisation_template(request))
    return render(request, "login/connection2.html", context)


# --------------------------Deconnection-----------------------------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect("/")


# --------------------------Espace Personnel-------------------------------------------
@login_required(login_url="connection1")
def MonCompte(request):
    context = {}

    # Appel des fontions pour les formulaire
    preference_form = DonneTesPreferences(request)
    role_form = ChangeTonRole(request)
    adresse_form = AjoutTonAdresse(request)
    voiture_form = AjouteTaCaisse(request)
    trajet_form = ProposeTonCovoiturage(request)
    reservation_form = GereTaReservationPassager(request)
    trajet_terminer_form = FiniTonCovoiturage(request)
    demarrer_ou_annuler_form = GereTonCovoiteChauffeur(request)

    recherche_form, first_resultat, second_resultat = RechercheTrajet(request)
    filtre_form, resultat1, resultat2 = Filtre_trajet(request)

    if request.method == "POST":
        forms_post = {
            "adresse_form": adresse_form,
            "role_form": role_form,
            "preference_form": preference_form,
            "voiture_form": voiture_form,
            "trajet_form": trajet_form,
            "trajet_terminer_form": trajet_terminer_form,
            "demarrer_ou_annuler_form": demarrer_ou_annuler_form,
            "reservation_form": reservation_form,
        }

        for form_name, form_instance in forms_post.items():
            if form_instance:
                context[form_name] = form_instance
                return redirect("MonCompte")

    if request.method == "GET":
        form_get = {
            recherche_form: recherche_form,
            filtre_form: filtre_form,
        }
        for form_name, form_instance in form_get.items():
            if form_instance:
                context[form_name] = form_instance

    context.update(
        {
            # recherche
            "first_resultat": first_resultat,
            "second_resultat": second_resultat,
            # filtre
            "resultat1": resultat1,
            "resultat2": resultat2,
            # formulaire
            # __utilisateur__
            "adresse_form": adresse_form,
            "preference_form": preference_form,
            "role_form": role_form,
            "voiture_form": voiture_form,
            # __trajet__
            "demarrer_ou_annuler_form": demarrer_ou_annuler_form,
            "trajet_terminer_form": trajet_terminer_form,
            "trajet_form": trajet_form,
            "filtre_form": filtre_form,
            "recherche_form": recherche_form,
            # __reservation__
            "reservation_form": reservation_form,
            "messages": messages.get_messages(request),
        }
    )

    context.update(InfoTrajet(request))
    context.update(Info_Reservation(request))
    context.update(initialisation_template(request))
    return render(request, "interface_utilisateur/utilisateur/MonCompte.html", context)

# -----------------------------------------------------------------------------------------

def SelectionTrajet(request):
    context = {}

    result = ChoisisTonCovoite(request)
    if isinstance(result, HttpResponseRedirect):
        return result

    # Sinon, on peut unpack normalement
    reservation_form, trajet, commentaire = result

    context = {
        "reservation_form": reservation_form,
        "trajet": trajet,
        "commentaire": commentaire,
    }

    context.update(initialisation_template(request))
    return render(
        request,
        "interface_utilisateur/utilisateur/reservation/reservation.html",
        context,
    )

@login_required
def AvisSatisfaction(request, trajet_id, token):
    context = {}

    avis_form = DonneTonAvis(request, trajet_id, token)
    if isinstance(avis_form, HttpResponseRedirect):
        return avis_form
    context["avis_form"] = avis_form
    context.update(initialisation_template(request))
    return render(
        request, "interface_utilisateur/utilisateur/avis_satisfaction.html", context
    )

def Fait_Ton_Taff_De_Modo(request):
    # on gere l'acces au page admin/moderateur
    if not is_superuser_or_moderateur(request.user):
        return HttpResponseRedirect("index")
    #else:
        #messages.info(request,"Bienvenue dans votre espace moderateur")
    context = {}
    moderation_positive_form = None
    moderation_form = None
    contact_form = None
    selected_email = None
    # Connexion au serveur IMAP
    # Même principe que email dans settings
    mail, data, result, mail_ids, emails = ConnectionImaplib(request)
    affichage_trajet_form = AfficherTrajetForm(request.POST or None)
    email_recuperer = RecuperationEmail(request, mail, data, result, mail_ids, emails)
    if isinstance(email_recuperer, HttpResponseRedirect):
        return email_recuperer
    email_type, email_id_selected, mail_ids, emails, selected_email = email_recuperer


    #___________________Extraction des données du mail____________________
    if selected_email:
        donnee_extrait = ExtractionDonnee(request, email_type, selected_email)

        if isinstance(donnee_extrait, HttpResponseRedirect):
            return donnee_extrait
        affichage_trajet_form , telephone, sujet, email_user, pseudo, commentaire, trajet_id, email_type, selected_email, passager_id, chauffeur_id = donnee_extrait

        #_______gestion avis negatif avec choix paiment et ajout commentaire____
        if email_type == "Avis negatif":

            moderation_form = GereLesAvisNegatif(request, chauffeur_id, passager_id, trajet_id, commentaire)
            if isinstance(moderation_form, HttpResponseRedirect):
                return moderation_form
            context["moderation_form"] = moderation_form

        #_______gestion avis positif et ajout commentaire____
        elif email_type == "Avis positif":

            moderation_positive_form = GereLesAvisPositif(request, email_id_selected, mail, trajet_id, commentaire, chauffeur_id, passager_id)
            if isinstance(moderation_positive_form, HttpResponseRedirect):
                return moderation_positive_form
            context["moderation_positive_form"] = moderation_positive_form

        #_____repondre au mail de contact____
        elif email_type == "Prise de contact":

            contact_form = PriseDeContact(request, email_id_selected, mail, telephone, sujet, email_user, pseudo, commentaire)
            if isinstance(affichage_trajet_form, HttpResponseRedirect):
                return affichage_trajet_form
            context["contact_form"] = contact_form

    context = {
        "emails": emails,
        "selected_email": selected_email,
        "messages": messages.get_messages(request),
        "mail_ids": mail_ids,
        "affichage_trajet_form": affichage_trajet_form,
        "moderation_positive_form": moderation_positive_form,
        "moderation_form": moderation_form,
        "contact_form": contact_form,
    }
    context.update(initialisation_template(request))
    return render(
        request, "admin/moderateur/moderation_email/moderation_email.html", context
    )

# _________________En cour_________________

# Factorisation

# _________________A FAIRE_________________


# ------------------------------------A faire avec javascript------------------------------------------------------


# --------retour sur onglet actif dynamique-------
# --------ajout de voiture dynamique , faire un choix de marque avec model dynamique-------
# Nombre de place selectionnable dynamique sur reservation et proposition de trajet
# factorisation du code quand j'aurai tout fini , dynamisme fonctionnalité op

# _________________A FINIR_________________

# responsive sur les deux derniere fonctions pour l'admin