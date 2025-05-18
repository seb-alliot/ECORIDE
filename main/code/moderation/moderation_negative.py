from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from ...models import TrajetProposer, ReservationTrajet, NoteUser, CreditUser
from ...forms import ModerationTrajetForm


def GereLesAvisNegatif(request, chauffeur_id, passager_id, trajet_id, commentaire):
    trajet = TrajetProposer.objects.filter(id=trajet_id).first()
    note_chauffeur = NoteUser.objects.filter(
        chauffeur=chauffeur_id,
        trajet=trajet_id,
        passager=passager_id,
    ).first()

    if not note_chauffeur:
        messages.error(request, "Note du chauffeur introuvable.")
        return redirect("moderation_email")

    try:
        reservation = ReservationTrajet.objects.get(
            trajet_reserver=trajet_id,
            passager=passager_id,
        )
    except ReservationTrajet.DoesNotExist:
        messages.error(request, "Réservation introuvable.")
        return redirect("moderation_email")

    moderation_form = ModerationTrajetForm(request.POST or None, initial={"commentaire": commentaire})

    if request.method == "POST":
        if moderation_form.is_valid():
            etat_paiement = moderation_form.cleaned_data["etat_paiement"]
            avis = moderation_form.cleaned_data["avis"]
            commentaire_saisi = moderation_form.cleaned_data["commentaire"]

            choix_modo = []
            info_commentaire = []

            try:
                # Gestion du commentaire
                if avis == "oui":
                    if note_chauffeur.commentaire_moderer:
                        info_commentaire.append("Commentaire déjà traité.")
                    else:
                        note_chauffeur.commentaire = commentaire_saisi
                        note_chauffeur.commentaire_moderer = True
                        note_chauffeur.etat_paiement = etat_paiement
                        note_chauffeur.decision_prise = True
                        note_chauffeur.save()
                        info_commentaire.append("Commentaire ajouté.")
                elif avis == "non":
                    if note_chauffeur.commentaire_moderer:
                        info_commentaire.append("Commentaire déjà traité.")
                    else:
                        note_chauffeur.commentaire_moderer = True
                        note_chauffeur.save()
                        info_commentaire.append("Commentaire refusé.")
                        choix_modo.append("Décision validée.")

                # Paiement
                if etat_paiement == "Payer":
                    if note_chauffeur.decision_prise:
                        choix_modo.append("Paiement déjà traité.")
                    else:
                        if request.POST.get("Valider") == "oui":
                            credit_chauffeur = CreditUser.objects.get(user=trajet.chauffeur)
                            credit_chauffeur.credit += reservation.prix_par_passager
                            credit_chauffeur.save()
                            reservation.etat_paiement = "Payer"
                            reservation.trajet_payer = True
                            reservation.save()
                            note_chauffeur.decision_prise = True
                            note_chauffeur.save()
                            choix_modo.append("Paiement accordé.")
                        else:
                            messages.error(request, "Validation manquante pour paiement.")
                            return redirect(f"{reverse('moderation_email')}?email_type=Avis+negatif")

                elif etat_paiement == "Refuser":
                    if request.POST.get("Valider") == "oui":
                        reservation.etat_paiement = "Refuser"
                        reservation.save()
                        note_chauffeur.decision_prise = True
                        reservation.trajet_payer = True

                        note_chauffeur.save()
                        choix_modo.append("Paiement refusé.")
                    else:
                        messages.error(request, "Validation manquante pour refus de paiement.")
                        return redirect(f"{reverse('moderation_email')}?email_type=Avis+negatif")


                # Messages rendus
                decision = ", ".join(choix_modo) if choix_modo else "aucune"
                commentaire_info = ", ".join(info_commentaire) if info_commentaire else "aucun"
                messages.info(request, f"Votre décision : {decision}. Commentaire : {commentaire_info}")
                return redirect(f"{reverse('moderation_email')}?email_type={f"Avis+negatif"}")

            except TrajetProposer.DoesNotExist:
                messages.error(request, "Trajet introuvable.")
            except CreditUser.DoesNotExist:
                messages.error(request, "Ce chauffeur n'existe plus.")
    return moderation_form
