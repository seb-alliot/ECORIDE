from bs4 import BeautifulSoup
from ...models import TrajetProposer, ReservationTrajet, User
from ...forms import  AfficherTrajetForm
from django.contrib import messages
from django.shortcuts import redirect
import re


def ExtractionDonnee(request, email_type, selected_email):
    body = selected_email["body"]
    trajet_id = None
    trajet = None
    chauffeur_id = None
    passager_id = None
    date_resa = None
    commentaire = None
    passager = None
    chauffeur = None
    # Valeurs par défaut a extraire
    email_user = "Non renseigné"
    pseudo = "Non renseigné"
    telephone = "Non renseigné"
    sujet = "Non renseigné"
    commentaire = "Non renseigné"

    extraire = BeautifulSoup(body, "html.parser")
    div_commentaire = extraire.find("div", class_="commentaire")
    # On extrait le commentaire du passager
    try:
        if div_commentaire and div_commentaire.p:
                commentaire = div_commentaire.p.get_text().replace("Commentaire:", "").replace("Commentaire :", "").strip()
        else:
            commentaire = None
    except AttributeError:
        messages.info(request, "Aucun commentaire.")
    title_id = extraire.find("title")
    if email_type in ["Avis positif", "Avis negatif"]:
        if title_id:
            title_id = title_id.get_text()
            trajet_id = title_id.split(" ")[-1]
            try:
                if not trajet_id or trajet_id in [None, "", "auth.User.None", "None"]:
                    messages.info(request, "Le trajet n'existe plus.")
                trajet = TrajetProposer.objects.filter(id=trajet_id).first() if trajet_id else None
                if not trajet:
                    messages.info(request, "Le trajet n'existe plus")

                chauffeur = trajet.chauffeur
                if not chauffeur:
                    messages.info(request, "Le chauffeur n'existe plus.")
                chauffeur_id = chauffeur.id if chauffeur else None
                # On extrait le nom du passager
                trouve_le_nom = re.search(r"de la part de (\w+)", title_id)
                if trouve_le_nom:
                    passager = trouve_le_nom.group(1)
                    passager = User.objects.filter(username=passager).first()
                    passager_id = passager.id if passager else None
                reservation = ReservationTrajet.objects.filter(trajet_reserver=trajet, passager=passager, prix_par_passager__isnull=False).first()
                prix = reservation.prix_par_passager if reservation else None

            except (ValueError, TypeError):
                return redirect("moderation_email")

            date_resa = trajet.date.strftime("%d/%m/%Y")
            trajet = (
                (trajet.ville_depart) + " - " + (trajet.ville_arrivee)
                if trajet
                else None
            )

    elif email_type == "Prise de contact":
        try:
            # Email
            div_email = extraire.find("div", class_="email_user")
            if div_email and div_email.p:
                email_user = div_email.p.get_text().replace("Email:", "").replace("Email :", "").strip()

            # Pseudo
            div_pseudo = extraire.find("div", class_="pseudo")
            if div_pseudo and div_pseudo.p:
                pseudo = div_pseudo.p.get_text().replace("Nom:", "").replace("Nom :", "").strip()

            # Téléphone
            div_telephone = extraire.find("div", class_="telephone")
            if div_telephone and div_telephone.p:
                telephone = div_telephone.p.get_text().replace("telephone:", "").replace("telephone :", "").strip()

            # Sujet
            div_sujet = extraire.find("div", class_="sujet")
            if div_sujet and div_sujet.p:
                sujet = div_sujet.p.get_text().replace("sujet:", "").replace("sujet :", "").strip()

            # Commentaire
            div_commentaire = extraire.find("div", class_="commentaire")
            if div_commentaire and div_commentaire.p:
                commentaire = div_commentaire.p.get_text().replace("Commentaire:", "").replace("Commentaire :", "").strip()

        except AttributeError:
            messages.info(request, "Des données n'ont pas pu être récupérées.")
            return redirect("moderation_email")


    affichage_trajet_form = AfficherTrajetForm(request.POST or None, initial={"chauffeur": chauffeur,"trajet": trajet, "date_reservation": date_resa,"passager":passager, "prix": prix})

    return affichage_trajet_form , telephone, sujet, email_user, pseudo, commentaire, trajet_id, email_type, selected_email, passager_id, chauffeur_id
