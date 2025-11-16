from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from ....models import TrajetProposer, NoteUser, ReservationTrajet, CreditUser
from ....forms import AvisForm
from ...securite import confirm_token
from ...envoi_email.send_email import envoi_email
from django.db import transaction

def DonneTonAvis(request, trajet_id, token):
    username_token = confirm_token(token)
    if username_token != request.user.username:
        messages.error(request, "Vous n'êtes pas le destinataire pour ce lien.")
        return redirect("index")

    # Récupère le trajet et la réservation
    trajet = get_object_or_404(TrajetProposer, id=trajet_id)
    reservation = get_object_or_404(ReservationTrajet, trajet_reserver=trajet, passager__username=username_token)
    chauffeur = trajet.chauffeur
    passagers = request.user
    if not trajet or not reservation:
        messages.info(request, "Le trajet ou la réservation n'existe plus.")
        return redirect("index")
    # Vérifie si une note existe déjà pour ce passager pour le chauffeur sur ce trajet
    note_existante = NoteUser.objects.filter(
        passager=reservation.passager,
        chauffeur=chauffeur,
        trajet=trajet,
    ).first()

    avis_form = AvisForm(request.POST or None)

    if request.method == "POST" and avis_form.is_valid():
        avis_soumis = avis_form.cleaned_data["avis"]
        nouvelle_note = avis_form.cleaned_data["note"]
        nouveau_commentaire = avis_form.cleaned_data["commentaire"]

        if note_existante:
            info_liste_fourni = []
            info_liste_succe = []
            # Blocage modification avis
            if note_existante.avis_donne and avis_soumis != note_existante.avis:
                info_liste_fourni.append("avis")
            if note_existante.avis_donne:
                info_liste_fourni.append("avis")
            # blocage modification note
            if note_existante.note_attribuee and nouvelle_note:
                info_liste_fourni.append("note")
            elif not note_existante.note_attribuee and nouvelle_note:
                note_existante.note = nouvelle_note
                note_existante.note_attribuee = True
                info_liste_succe.append("note")
            # blocage modification commentaire
            if note_existante.commentaire_attribuee and nouveau_commentaire:
                info_liste_fourni.append("commentaire")
            elif not note_existante.commentaire_attribuee:
                if not nouveau_commentaire or nouveau_commentaire.strip() == "":
                    note_existante.commentaire = None
                    note_existante.commentaire_attribuee = False
                else:
                    note_existante.commentaire = nouveau_commentaire
                    note_existante.commentaire_attribuee = True
                info_liste_succe.append("commentaire")

            # On centralise les messages pour éviter de spammer la modération
            if info_liste_fourni:
                messages.info(request, f"Vous avez déja renseigné : {', '.join(info_liste_fourni)}.")
            if info_liste_succe:
                messages.success(request, f"Merci de votre retour pour : {', '.join(info_liste_succe)}.")
            note_existante.avis = avis_soumis
            note_existante.avis_donne = True
            note_existante.save()

            # Si tout est déjà attribué, on bloque l'envoi de l'email pour libérer des ressources en email
            if (
                note_existante.avis_donne
                and note_existante.note_attribuee
                and note_existante.commentaire_attribuee
            ):
                return redirect("index")
        else:
            # Création de la note
            note_existante = NoteUser.objects.create(
                passager=reservation.passager,
                chauffeur=chauffeur,
                trajet=trajet,
                avis=avis_soumis,
                commentaire_attribuee=True,
                # boleen obligatoire a la soumission
                avis_donne=True,
                #gestion boleen pour le commentaire et note si fournis
                note=nouvelle_note if nouvelle_note else None,
                note_attribuee=True if nouvelle_note else False,
            )

        commentaire = note_existante.commentaire
        info_liste_mail = []
        if avis_soumis == "oui":
            with transaction.atomic():
                commentaire = nouveau_commentaire if nouveau_commentaire else None
                # Ajout de crédit au chauffeur
                credit_chauffeur = CreditUser.objects.get(user=chauffeur)
                credit_chauffeur.credit += reservation.prix_par_passager
                credit_chauffeur.save()
                # Vérifier si le commentaire est déjà attribué avant d'envoyer l'email
                # Si le commentaire existe on n'envoie pas l'email, eviter de spam
                if note_existante.commentaire_attribuee and not note_existante.note_attribuee:
                    messages.info(request, "Vous avez déja renseigné un commentaire.")
                else:
                    commentaire = nouveau_commentaire if nouveau_commentaire else None
                    subject = "Avis positif"
                    template = "style_email/_avis_positif.html"
                    envoi_email(
                        request=request,
                        to="staff.modo.ecoride@gmail.com",
                        subject=subject,
                        template="style_email/_avis_positif.html",
                        context={
                            "chauffeur": chauffeur,
                            "trajet": trajet,
                            "reservation": reservation,
                            "commentaire": commentaire,
                            "token": token,
                            "passagers": passagers,
                        }
                    )
                    info_liste_mail.append("avis positif")

        elif avis_soumis == "non":
            # Si le commentaire est déjà attribué, on n'envoie pas l'email
            # Eviter de spam
            if  note_existante.commentaire_attribuee and not note_existante.note_attribuee:
                messages.info(request, "Vous avez déja renseigné un commentaire.")
            else:
                commentaire = nouveau_commentaire if nouveau_commentaire else None
                subject = "Avis negatif"
                template = "style_email/_avis_negatif.html"
                envoi_email(
                    request=request,
                    to="staff.modo.ecoride@gmail.com",
                    subject=subject,
                    template=template,
                    context={
                        "chauffeur": chauffeur,
                        "trajet": trajet,
                        "reservation": reservation,
                        "commentaire": commentaire,
                        "token": token,
                        "passagers": passagers,
                    }
                )
                info_liste_mail.append("avis négatif")
        if info_liste_mail:
            messages.success(
                request, f"Votre {', '.join(info_liste_mail)} a été envoyer, nous vous remercions pour votre retour."
            )

    return avis_form , trajet , reservation
