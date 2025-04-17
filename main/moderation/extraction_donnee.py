from bs4 import BeautifulSoup
from ..models import TrajetProposer, ReservationTrajet, User
from ..forms import  AfficherTrajetForm
from django.contrib import messages
from django.shortcuts import redirect

def ExtractionDonnee(request, email_type, selected_email):
    body = selected_email["body"]
    trajet_id = None
    trajet = None
    chauffeur_id = None
    passager_id = None
    date_resa = None
    email_user = None
    pseudo = None
    telephone = None
    sujet = None
    commentaire = None
    passager = None
    chauffeur = None

    extraire = BeautifulSoup(body, "html.parser")
    # On extrait le commentaire du passager
    div_commentaire = extraire.find("div", class_="commentaire")
    if div_commentaire and div_commentaire.p:
        commentaire = div_commentaire.p.get_text().replace("Commentaire: ", "").strip()
    # on fait sauter Commentaire : pour avoir juste le commentaire
    if commentaire.startswith("Commentaire :"):
        commentaire = commentaire.replace("Commentaire :", "").strip()

    title_id = extraire.find("title")
    if email_type in ["Avis positif", "Avis negatif"]:
        if title_id:
            title_id = title_id.get_text()
            trajet_id = title_id.split(" ")[-1]
            #vérification massive des id existants sinon next :)
            try:
                print(f"trajet_id: {trajet_id}, chauffeur_id: {chauffeur_id}")
                if not trajet_id or trajet_id in [None, "", "auth.User.None", "None"]:
                    messages.info(request, "Le trajet n'existe plus.")
                    return redirect("moderation_email")
                trajet = TrajetProposer.objects.filter(id=trajet_id).first()
                if not trajet:
                    messages.info(request, "Le trajet n'existe plus.")
                    return redirect("moderation_email")
                chauffeur = trajet.chauffeur
                chauffeur_id = chauffeur.id if chauffeur else None
                print(f"Chauffeur: {chauffeur}", f"Chauffeur ID: {chauffeur_id}")
                if not chauffeur:
                    messages.info(request, "Le chauffeur n'existe plus.")
                    return redirect("moderation_email")
                reservation = ReservationTrajet.objects.filter(trajet_reserver=trajet).first()
                if reservation:
                    passager = reservation.passager
                    passager_id = passager.id if passager else None
                    print(f"Passager: {passager}")
                    if not passager:
                        messages.info(request, "Le passager n'existe plus.")
                        return redirect("moderation_email")
                else:
                    messages.info(request, "La réservation n'existe plus.")
                    return redirect("moderation_email")
                if not reservation:
                    messages.info(request, "La réservation n'existe plus.")
                    return redirect("moderation_email")
                if not passager:
                    messages.info(request, "Le passager n'existe plus.")
                    return redirect("moderation_email")
                print(f"Trajet: {trajet}, Chauffeur: {chauffeur}, Passager: {passager}")
                print(f"Réservation: {reservation}")
                print(f"Passager (réservation): {reservation.passager}")
            except (ValueError, TypeError):
                messages.info(request, "Erreur de traitement de la réservation.")
                return redirect("moderation_email")

            date_resa = trajet.date
            print(f"la date de reservation concerne ", date_resa)
            trajet = (
                (trajet.ville_depart) + " - " + (trajet.ville_arrivee)
                if trajet
                else None
            )

    elif email_type == "Prise de contact":
        div_email = extraire.find("div", class_="email_user")

        # On extrait l'email de l'utilisateur
        if div_email and div_email.p:
            email_user = div_email.p.get_text().replace("Email: ", "").strip()

        # on fait sauter Commentaire : pour avoir juste le commentaire
        if email_user.startswith("Email :"):
            email_user = email_user.replace("Email :", "").strip()
        else:
            email_user = "non renseigné"

        # On extrait le pseudo
        div_pseudo = extraire.find("div", class_="pseudo")
        if div_pseudo and div_pseudo.p:
            pseudo = div_pseudo.p.get_text().replace("Nom : ", "").strip()
        # on fait sauter Pseudo : pour avoir juste le pseudo
        if pseudo.startswith("Nom :"):
            pseudo = pseudo.replace("Nom :", "").strip()
        else:
            pseudo = "non renseigné"

        # On extrait le telephone
        div_telephone = extraire.find("div", class_="telephone")
        if div_telephone and div_telephone.p:
            telephone = div_telephone.p.get_text().replace("telephone :", "").strip()
        # on fait sauter telephone : pour avoir juste le telephone
        if telephone.startswith("telephone :"):
            telephone = telephone.replace("telephone :", "").strip()
        else:
            telephone = "non renseigné"

        # On extrait le sujet
        div_sujet = extraire.find("div", class_="sujet")
        if div_sujet and div_sujet.p:
            sujet = div_sujet.p.get_text().replace("sujet : ", "").strip()
        # on fait sauter sujet : pour avoir juste le sujet
        if sujet.startswith("sujet:"):
            sujet = sujet.replace("sujet :", "").strip()
        else:
            sujet = "non renseigné"

    affichage_trajet_form = AfficherTrajetForm(request.POST or None, initial={"chauffeur": chauffeur,"trajet": trajet, "date_reservation": date_resa,"passager":passager})

    return affichage_trajet_form , telephone, sujet, email_user, pseudo, commentaire, trajet_id, email_type, selected_email, passager_id, chauffeur_id
