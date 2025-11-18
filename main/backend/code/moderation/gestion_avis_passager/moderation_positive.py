from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from ....models import NoteUser, TrajetProposer, User
from ....forms import ModerationAvisPositifForm
from ...utils import supprimer_mail
import asyncio

def GereLesAvisPositif(request,email_type, email_id_selected, mail, trajet_id, commentaire, chauffeur_id, passager_id):

    trajet = TrajetProposer.objects.filter(id=trajet_id).first()
    passager = User.objects.filter(id=passager_id).first()
    chauffeur = User.objects.filter(id=chauffeur_id).first()
    note_chauffeur = NoteUser.objects.filter(
        chauffeur=chauffeur,
        trajet=trajet,
        passager=passager
    ).first()

    if not trajet or not passager or not chauffeur or not note_chauffeur:
        messages.error(request, "Données introuvables pour ce commentaire.")
        return redirect("moderation_email")

    moderation_form = ModerationAvisPositifForm(request.POST or None, initial={"commentaire": commentaire})

    if request.method == "POST":
        if moderation_form.is_valid():
            action = request.POST.get("action")
            supprimer_email = request.POST.get("supprimer_email") == "oui"
            infos = []
            deletions = []

            try:
                if action == "Ajouter":
                    if note_chauffeur.commentaire:
                        infos.append("Commentaire déjà existant")
                    else:
                        note_chauffeur.commentaire = moderation_form.cleaned_data["commentaire"]
                        note_chauffeur.commentaire_moderer = True
                        note_chauffeur.decision_prise = True
                        note_chauffeur.save()
                        infos.append("Commentaire ajouté")
                        asyncio.run(supprimer_mail(email_id_selected))
                        messages.success(request, "Email traité.")

                elif action == "Refuser":
                    if note_chauffeur.commentaire:
                        infos.append("Commentaire déjà existant")
                    else:
                        note_chauffeur.commentaire_moderer = True
                        note_chauffeur.decision_prise = True
                        note_chauffeur.save()
                        infos.append("Décision validée")
                        asyncio.run(supprimer_mail(email_id_selected))
                        messages.success(request, "Email traité.")

                else:
                    messages.error(request, "Action inconnue.")
                    return redirect(f"{reverse('moderation_email')}?email_type=Avis+positif")

                if supprimer_email:
                    mail.store(email_id_selected, "+FLAGS", "\\Deleted")
                    mail.expunge()
                    deletions.append("Email supprimé")

                # Messages d'infos
                if deletions or infos:
                    for msg in deletions + infos:
                        messages.info(request, msg)
                return redirect(f"{reverse('moderation_email')}?email_type={email_type}")

            except Exception as e:
                return
        else:
            messages.error(request, "Formulaire invalide.")

    return moderation_form
