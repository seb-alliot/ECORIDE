from django.shortcuts import render, redirect
from django.contrib import messages
from ..models import TrajetProposer, ReservationTrajet, NoteUser, CreditUser, User
from ..forms import ModerationTrajetForm


def GereLesAvisNegatif(request,mail,email_id_selected,commentaire, chauffeur_id, passager_id, trajet_id):

    trajet = TrajetProposer.objects.filter(id=trajet_id).first()
    print(f"le trajet est  ", trajet)
    id_trajet = trajet.id
    print(f"le trajet id a pour numéro de bdd :", id_trajet)
    try:
        chauffeur = User.objects.get(pk=chauffeur_id)
        passager = User.objects.get(pk=passager_id)
    except User.DoesNotExist:
        messages.error(request, "Utilisateur introuvable.")
        return redirect("moderation_email")

    moderation_form = ModerationTrajetForm(request.POST or None, initial={"commentaire": commentaire})
    if request.method == "POST":
        if moderation_form.is_valid():
            choix_moderateur = moderation_form.cleaned_data["etat_paiement"]
            choix_commentaire = moderation_form.cleaned_data["avis"]
            note_chauffeur = NoteUser.objects.create(
                chauffeur=chauffeur,
                passager=passager,
            )
            reservation = ReservationTrajet.objects.filter(
                passager=passager_id,
            ).first()
            try:
                if choix_commentaire == "oui":
                    if note_chauffeur.commentaire_moderer:
                        messages.error(request, "Le commentaire a déjà été modéré.")
                    else:
                        note_chauffeur.commentaire_moderer = True
                        note_chauffeur.etat_paiement = choix_moderateur
                        note_chauffeur.decision_prise = True
                        note_chauffeur.save()
                        note_chauffeur.commentaire_moderer = True
                        messages.info(request, "Le commentaire a bien été enregistré.")
                elif choix_commentaire == "non":
                    if note_chauffeur.commentaire_moderer:
                        messages.error(request, "Le commentaire a déjà été modéré.")
                    else:
                        note_chauffeur.commentaire_moderer = True
                        messages.info(request, "Votre choix pour le commentaire a été enregistré.")

                if choix_moderateur == "Payer":
                    if note_chauffeur.decision_prise:
                        messages.info(request, "Le paiement a déjà été traiter.")
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
                            return redirect("moderation_email")
                        else:
                            messages.error(request, "Erreur dans le traitement du paiement.")
                            return redirect("moderation_email")

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
                        return redirect("moderation_email")
                    else:
                        messages.error(request, "Erreur dans le traitement du paiement.")
                        return redirect("moderation_email")
            except TrajetProposer.DoesNotExist:
                messages.error(request, "Trajet introuvable.")
            except ReservationTrajet.DoesNotExist:
                messages.error(request, "Réservation introuvable.")
            except CreditUser.DoesNotExist:
                messages.error(request, "Ce chauffeur n'existe plus.")
    return moderation_form
