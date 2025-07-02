# coding:utf-8

from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
import json
from .forms import (
    AfficherTrajetForm,
)

from .models import (
    Voiture
)

from .code import (
    InfoTrajet,
    Info_Reservation,
    initialisation_template,
    RechercheTrajet,
    Filtre_trajet,
    AjoutTonAdresse,
    AjouteTaCaisse,
    DonneTesPreferences,
    ChangeTonRole,
    FiniTonCovoiturage,
    GereTonCovoiteChauffeur,
    ProposeTonCovoiturage,
    GereTaReservationPassager,
    ChoisisTonCovoite,
    DonneTonAvis,
    PriseContact,
    PremierEtape,
    DeuxiemeEtape,
    is_superuser_or_moderateur,
    Admin_access,
    ConnectionImaplib,
    RecuperationEmail,
    ExtractionDonnee,
    GereLesAvisNegatif,
    GereLesAvisPositif,
    PriseDeContact,
    Fusion_donnee,
    SuppressionCompte,
)



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
    # Onglet de la page factorisé
    tabs = ["_tab1.html", "_tab2.html", "_tab3.html", "_tab4.html", "_tab5.html"]
    context["tabs"] = tabs
    context["models_data"] = json.dumps(Voiture.MODELE, cls=DjangoJSONEncoder)


    # Appel des fontions pour les formulaires
    preference_form = DonneTesPreferences(request)
    role_form = ChangeTonRole(request)
    adresse_form = AjoutTonAdresse(request)
    voiture_form = AjouteTaCaisse(request)
    trajet_form = ProposeTonCovoiturage(request)
    reservation_form = GereTaReservationPassager(request)
    trajet_terminer_form = FiniTonCovoiturage(request)
    demarrer_ou_annuler_form = GereTonCovoiteChauffeur(request)
    suppression_compte_form = SuppressionCompte(request)

    try:
        voitures_user = request.user.voiture.all()  # grâce à related_name="voitures"
        voitures_data = {
            str(voiture.id): voiture.places for voiture in voitures_user
        }
        context["voitures_data_json"] = json.dumps(voitures_data, cls=DjangoJSONEncoder)
    except AttributeError:
        # Si l'utilisateur n'a pas de voiture associée, on initialise un dictionnaire vide
        context["voitures_data_json"] = json.dumps({})

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
            "suppression_compte_form": suppression_compte_form,
        }

        for form_name, form_instance in forms_post.items():
            if form_instance:
                if isinstance(form_instance, HttpResponseRedirect):
                    return form_instance
                context[form_name] = form_instance

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
    reservation_form, trajet, commentaire, preference, compteur = result

    context = {
        "compteur": compteur,
        "preference": preference,
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

    # 1er onglet, moderation des mails
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
            if isinstance(contact_form, HttpResponseRedirect):
                return contact_form

    # 2ème onglet admin
    # Pas besoin de isinstance car on ne fait pas de redirection, et une seul données renvoyée
    user = request.user
    admin = Admin_access(request,user)
    formulaire_pres_remplis_fusion = Fusion_donnee(request)

    context = {
        "admin": admin,
        "formulaire_pres_remplis_fusion": formulaire_pres_remplis_fusion,
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
