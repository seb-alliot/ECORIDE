from django.contrib import messages
from ..models import NoteUser, TrajetProposer, CreditUser, ReservationTrajet, User
from ..forms import ModerationAvisPositifForm
from django.shortcuts import redirect


def GereLesAvisPositif(request, email_id_selected, mail, trajet_id, commentaire, chauffeur_id, passager_id):

    trajet = TrajetProposer.objects.filter(id=trajet_id).first()
    reservation = ReservationTrajet.objects.filter(
        trajet_reserver__chauffeur=request.POST.get("chauffeur_id"),).first()
    passager = User.objects.get(id=passager_id)
    moderation_positive_form = ModerationAvisPositifForm(request.POST or None, initial={"commentaire": commentaire})
    if request.method == "POST":
        if moderation_positive_form.is_valid():
            try:
                reservation = reservation
                # Récupérer ou créer l'instance pour appliqué la note
                if request.POST.get("action") == "Ajouter":
                    note_chauffeur, created = NoteUser.objects.get_or_create(
                        chauffeur=chauffeur_id,
                        passager=passager,
                        trajet=trajet,
                    )
                    note_chauffeur.commentaire = moderation_positive_form.cleaned_data[
                        "commentaire"
                    ]
                    note_chauffeur.commentaire_moderer = True
                    note_chauffeur.decision_prise = True
                    note_chauffeur.save()

                    mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                    mail.expunge()
                    messages.success(request, "Le commentaire a bien été enregistré.")
                    return redirect("moderation_email")
                elif request.POST.get("action") == "Refuser":
                    note_chauffeur, _ = NoteUser.objects.get_or_create(
                        chauffeur=chauffeur_id,
                        passager=passager,
                        trajet=trajet,
                    )
                    note_chauffeur.commentaire_moderer = True
                    note_chauffeur.decision_prise = True
                    note_chauffeur.save()
                    mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                    mail.expunge()
                    messages.success(request, "Votre décision est valider.")
                    return redirect("moderation_email")

            except TrajetProposer.DoesNotExist:
                messages.error(request, "Trajet introuvable.")
            except CreditUser.DoesNotExist:
                messages.error(request, "Ce chauffeur n'existe plus.")
        elif request.POST.get("supprimer_email") == "oui":
            mail.store(email_id_selected, "+FLAGS", "\\Deleted")
            mail.expunge()
            messages.success(request, "Email supprimé.")
            return redirect("moderation_email")
    return moderation_positive_form
