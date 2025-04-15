# coding:utf-8

from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test
from email.header import decode_header

from .forms import (
    ContactForm,
    ModerationTrajetForm,
    ModerationAvisPositifForm,
    AfficherTrajetForm,
)
from .models import (
    CreditUser,
    TrajetProposer,
    ReservationTrajet,
    NoteUser,
)

from .donnee_template import (
    InfoTrajet,
    Info_Reservation,
    initialisation_template,
)
from .code_doublon import (
    RechercheTrajet,
    Filtre_trajet
)
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
from .utils import ChoisisTonCovoite, DonneTonAvis, UserCreateView , PriseContact
from .connection import PremierEtape, DeuxiemeEtape
from .moderation import (
    ConnectionImaplib,
    RecuperationEmail,
)
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.conf import settings
from django.views.generic import CreateView
from django.contrib.auth.models import User
import chardet, email
from bs4 import BeautifulSoup


# Accueil en definition car fonction simple

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
        #envoie des message au template, inutile si balise message dans le template
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

# ----------------------Espace Personnel initialisation de données---------------------

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
    demarrer_ou_annuler_form= GereTonCovoiteChauffeur(request)

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

    context.update({

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
    })

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
        request, "interface_utilisateur/utilisateur/reservation/reservation.html", context
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


@user_passes_test(lambda u: isinstance(u, User) and u.is_superuser)
def Fait_Ton_Taff_De_Modo(request):

            # Connexion au serveur IMAP
            # Même principe que email dans settings
            emails, mail_ids, mail = ConnectionImaplib(request)

            selected_email = "qu'est ce qui est none?"

            chauffeur = "Chauffeur"
            trajet = "Trajet"
            date_resa = "Date de réservation"
            passager = "Passager"
            email_user = "Email"
            pseudo = "Pseudo"
            telephone = "Téléphone"
            sujet = "Sujet"
            commentaire = "Commentaire"

            email_type = request.GET.get("email_type", "").strip()

            # Récupération de l'email sélectionné (si existant)
            email_id_selected = request.GET.get("email_id")
            # Si pas d'email on fait en sorte de ne pas générer d'erreur
            for email_id in mail_ids:
                result, data = mail.fetch(email_id, "(RFC822)")
                if result != "OK" or not data or not data[0]:
                    continue

                raw_email = data[0][1]
                if raw_email is None:
                    continue

                message = email.message_from_bytes(raw_email)
                subject, encoding = decode_header(message["Subject"])[0]

                if isinstance(subject, bytes) and encoding:
                    subject = subject.decode(encoding if encoding else "utf-8")
                if subject.lower().startswith("re:"):
                    continue

                # on applique un filtre sur ce que l'on veux sur le template
                sender = message.get("From")
                if not (
                    ("Avis negatif" in subject
                    or "Avis positif" in subject
                    or "Prise de contact" in subject
                    )
                    and ("staff.modo.ecoride@gmail.com" in sender)
                ):
                    continue
                if email_type and email_type not in subject:
                    continue

                body = ""
                # on autopsie l'email recu
                if message.is_multipart():
                    for part in message.walk():
                        if part.get_content_type() == "body/html":
                            gerer_caractere_speciaux = chardet.detect(part.get_payload())
                            if gerer_caractere_speciaux["encoding"]:
                                body = part.get_payload(decode=True).decode(
                                    gerer_caractere_speciaux["encoding"]
                                )
                            else:
                                body = part.get_payload(decode=True).decode()

                            break
                else:
                    body = message.get_payload(decode=True).decode()

                # On extrait le commentaire du passager

                email_data = {
                    "id": email_id.decode(),
                    "subject": subject,
                    "sender": sender,
                    "body": body,
                }
                emails.append(email_data)

                # Si l'email sélectionné correspond à celui-ci, on l'affiche
                if email_id_selected and email_id_selected == email_data["id"]:
                    selected_email = email_data

                    extraire = BeautifulSoup(body, "html.parser")
                    # On extrait le commentaire du passager
                    # On extrait le commentaire du passager
                    div_commentaire = extraire.find("div", class_="commentaire")
                    if div_commentaire and div_commentaire.p:
                        commentaire = (
                            div_commentaire.p.get_text().replace("Commentaire: ", "").strip()
                        )
                    # on fait sauter Commentaire : pour avoir juste le commentaire
                    if commentaire.startswith("Commentaire :"):
                        commentaire = commentaire.replace("Commentaire :", "").strip()



                    title_id = extraire.find("title")
                    if email_type == "Avis positif" or email_type == "Avis negatif":
                        if title_id:
                            title_id = title_id.get_text("pour le Trajet")
                            trajet_id = title_id.split(" ")[-1]
                            print(f"le trajet_id est ", trajet_id)
                            trajet = TrajetProposer.objects.filter(id=trajet_id).first()
                            print(f"le trajet est ", trajet)
                            chauffeur = trajet.chauffeur
                            chauffeur_id = chauffeur.id
                            print(f"le chauffeur id est ", chauffeur_id)
                            print(f"le chauffeur concerne ", chauffeur)
                            reservation = ReservationTrajet.objects.filter(trajet_reserver=trajet).first()
                            print(f"la reservation concerne ", reservation)
                            if reservation:
                                passager = reservation.passager
                                passager_id = passager.id
                            print(f"le passager concerne ", passager)
                            date_resa = trajet.date
                            print(f"la date de reservation concerne ", date_resa)
                            trajet = (trajet.ville_depart) + " - " + (trajet.ville_arrivee) if trajet else None
                    elif email_type == "Prise de contact":
                        div_email = extraire.find("div", class_="email_user")
                        if div_email and div_email.p:
                            email_user = (
                                div_email.p.get_text().replace("Email: ", "").strip()
                            )
                        # on fait sauter Commentaire : pour avoir juste le commentaire
                        if email_user.startswith("Email :"):
                            email_user = email_user.replace("Email :", "").strip()
                        # On extrait le pseudo
                        div_pseudo = extraire.find("div", class_="pseudo")
                        if div_pseudo and div_pseudo.p:
                            pseudo = (
                                div_pseudo.p.get_text().replace("Nom : ", "").strip()
                            )
                        # on fait sauter Pseudo : pour avoir juste le pseudo
                        if pseudo.startswith("Nom :"):
                            pseudo = pseudo.replace("Nom :", "").strip()
                        # On extrait le telephone
                        div_telephone = extraire.find("div", class_="telephone")
                        if div_telephone and div_telephone.p:
                            telephone = (
                                div_telephone.p.get_text().replace("telephone :", "").strip()
                            )
                        # on fait sauter telephone : pour avoir juste le telephone
                        if telephone.startswith("telephone :"):
                            telephone = telephone.replace("telephone :", "").strip()

                        # On extrait le sujet
                        div_sujet = extraire.find("div", class_="sujet")
                        if div_sujet and div_sujet.p:
                            sujet = (
                                div_sujet.p.get_text().replace("sujet : ", "").strip()
                            )
                        # on fait sauter sujet : pour avoir juste le sujet
                        if sujet.startswith("sujet:"):
                            sujet = sujet.replace("sujet :", "").strip()

            contact_form = ContactForm(request.POST or None, initial={"email": email_user,"pseudo":pseudo,"telephone":telephone,"sujet":sujet, "message": commentaire})
            moderation_positive_form = ModerationAvisPositifForm(request.POST or None, initial={"commentaire": commentaire})
            moderation_form = ModerationTrajetForm(request.POST or None, initial={"commentaire": commentaire})
            affichage_trajet_form = AfficherTrajetForm(request.POST or None, initial={"chauffeur": chauffeur,"trajet": trajet, "date_reservation": date_resa,"passager":passager})

            if email_type == "Avis negatif":
                if moderation_form.is_valid():
                    choix_moderateur = moderation_form.cleaned_data["etat_paiement"]
                    choix_commentaire = moderation_form.cleaned_data["avis"]
                    note_chauffeur, created = NoteUser.objects.get_or_create(
                        chauffeur=chauffeur_id,
                        passager=passager_id,
                        )
                    try:
                        if note_chauffeur.commentaire_moderer == True:
                            messages.info(request, "Le commentaire a déjà été modéré.")
                            pass
                        else:
                            # Récupérer ou créer la note

                            note_chauffeur.commentaire = moderation_form.cleaned_data["commentaire"]
                        if choix_commentaire == "oui":
                            note_chauffeur.commentaire_moderer = True
                            note_chauffeur.etat_paiement = choix_moderateur
                            note_chauffeur.decision_prise = True
                            note_chauffeur.save()
                            note_chauffeur.commentaire_moderer = True
                            messages.info(request, "Le commentaire a bien été enregistré.")
                        elif choix_commentaire == "non":
                            note_chauffeur.commentaire_moderer = True

                        if choix_moderateur == "Payer":
                            if note_chauffeur.decision_prise == True:
                                messages.info(request, "Le paiement a déjà été traiter.")
                                return redirect("moderation_email")
                            else:
                                reservation.etat_paiement = "Payer"
                                credit_chauffeur = CreditUser.objects.get(user=trajet.chauffeur)
                                facture_passager = reservation.prix_par_passager
                                if request.POST.get("Valider") == "oui":
                                    credit_chauffeur.credit += facture_passager
                                    credit_chauffeur.save()
                                    reservation.trajet_payer = True
                                    note_chauffeur.decision_prise = True
                                    reservation.save()

                                    mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                                    mail.expunge()
                                    messages.success(request, "Le paiement a été accordé.")

                        elif choix_moderateur == "Refuser":
                            if request.POST.get("Valider") == "oui":
                                reservation.etat_paiement = "Refuser"
                                reservation.trajet_payer = True
                                note_chauffeur.decision_prise = True
                                reservation.save()
                                messages.success(
                                    request, "Vous avez bien refusé le paiement au chauffeur."
                                )
                                mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                                mail.expunge()
                    except TrajetProposer.DoesNotExist:
                        messages.error(request, "Trajet introuvable.")
                    except ReservationTrajet.DoesNotExist:
                        messages.error(request, "Réservation introuvable.")
                    except CreditUser.DoesNotExist:
                        messages.error(request, "Ce chauffeur n'existe plus.")

            elif email_type == "Avis positif":
                if moderation_positive_form.is_valid():
                    try:
                        trajet = trajet_id
                        reservation = reservation
                        # Récupérer ou créer l'instance pour appliqué la note
                        if request.POST.get("action") == "Ajouter":
                            note_chauffeur, created = NoteUser.objects.get_or_create(
                                chauffeur=chauffeur_id,
                                passager=passager_id,
                                trajet=trajet,
                            )
                            note_chauffeur.commentaire = moderation_positive_form.cleaned_data["commentaire"]
                            note_chauffeur.commentaire_moderer = True
                            note_chauffeur.decision_prise = True
                            note_chauffeur.save()

                            mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                            mail.expunge()
                            messages.success(request, "Le commentaire a bien été enregistré.")
                        elif request.POST.get("action") == "Refuser":
                            note_chauffeur.commentaire_moderer = True
                            note_chauffeur.decision_prise = True
                            mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                            mail.expunge()
                            messages.success(request, "Votre décision est valider.")

                    except TrajetProposer.DoesNotExist:
                        messages.error(request, "Trajet introuvable.")
                    except CreditUser.DoesNotExist:
                        messages.error(request, "Ce chauffeur n'existe plus.")
                elif request.POST.get("supprimer_email") == "oui":
                    mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                    mail.expunge()
                    messages.success(request, "Email supprimé.")
                else:
                    print(moderation_positive_form.errors)

            elif email_type == "Prise de contact":
                if contact_form.is_valid():

                    reponse_modo = contact_form.cleaned_data["reponse"]
                    from .envoi_email import Envoi_Reponse_Modo
                    Envoi_Reponse_Modo(request, email_user, commentaire , pseudo, reponse_modo)
                    if request.POST.get("repondre") == "oui":
                        mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                        mail.expunge()
                        messages.success(request, "Email supprimé.")

            context = {
                "emails": emails,
                "selected_email": selected_email,
                "messages": messages.get_messages(request),
                "mail_ids": mail_ids,
                "commentaire": commentaire,
                # Formulaire
                "affichage_trajet_form": affichage_trajet_form,
                "moderation_positive_form": moderation_positive_form,
                "contact_form": contact_form,
                "moderation_form": moderation_form,
            }
            context.update(initialisation_template(request))
            return render(
                request, "admin/moderateur/moderation_email/moderation_email.html", context
            )



# _________________En cour_________________

#Factorisation

# _________________A FAIRE_________________


# ------------------------------------A faire avec javascript------------------------------------------------------


# --------retour sur onglet actif dynamique-------
# --------ajout de voiture dynamique , faire un choix de marque avec model dynamique-------
#Nombre de place selectionnable dynamique sur reservation et proposition de trajet
#factorisation du code quand j'aurai tout fini , dynamisme fonctionnalité op

# _________________A FINIR_________________

# responsive sur les deux derniere fonctions pour l'admin
