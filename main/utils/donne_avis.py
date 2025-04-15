from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
import uuid
from django.contrib import messages
from django.http import HttpResponseRedirect
from ..models import TrajetProposer, NoteUser, ReservationTrajet, CreditUser
from ..forms import AvisForm



def DonneTonAvis(request, trajet_id, token):

    trajet = get_object_or_404(TrajetProposer, id=trajet_id)
    reservation = ReservationTrajet.objects.filter(trajet_reserver=trajet).first()
    chauffeur = trajet.chauffeur
    passager = reservation.passager
    # Vérifie si le passager a déjà donné une note ou un commentaire pour ce trajet
    note_existe = NoteUser.objects.filter(
        chauffeur=chauffeur, passager=passager, trajet=trajet
    ).first()

    if request.user != passager:
        messages.error(request, "Vous n'êtes pas sur le bon compte pour répondre à cet email.")
        return redirect("index")

    avis_soumis = None
    avis_form = AvisForm(request.POST)

    if request.method == "POST" and avis_form.is_valid():
        avis_soumis = avis_form.cleaned_data["avis"]
        nouvelle_note = avis_form.cleaned_data["note"]
        nouveau_commentaire = avis_form.cleaned_data["commentaire"]

        if note_existe:
            # Cas où l'utilisateur a déjà donné une note et/ou un commentaire

            if note_existe.avis_donne and avis_soumis != note_existe.avis:
                # Si un avis a déjà été donné, on empêche l'utilisateur de changer son avis
                messages.error(request, "Vous ne pouvez pas modifier votre avis une fois qu'il a été soumis.")
                return HttpResponseRedirect(reverse('AvisSatisfaction', kwargs={'trajet_id': trajet.id, 'token': token}))
            if note_existe.note_attribuee and nouvelle_note:
                # Si une note existe déjà, on empêche l'ajout d'une nouvelle
                messages.error(request, "Vous avez déjà donné une note pour ce trajet.")
                return HttpResponseRedirect(reverse('AvisSatisfaction', kwargs={'trajet_id': trajet.id, 'token': token}))

            if note_existe.commentaire_attribuee and nouveau_commentaire:
                # Si un commentaire existe déjà, on empêche l'ajout d'un nouveau
                messages.error(request, "Vous avez déjà donné un commentaire pour ce trajet.")
                return HttpResponseRedirect(reverse('AvisSatisfaction', kwargs={'trajet_id': trajet.id, 'token': token}))

            # Mise à jour de la note ou du commentaire si possible
            if not note_existe.note_attribuee and nouvelle_note:
                note_existe.note = nouvelle_note
                note_existe.note_attribuee = True
                messages.success(request, "Votre note a bien été prise en compte.")

            if not note_existe.commentaire_attribuee and nouveau_commentaire:
                note_existe.commentaire = nouveau_commentaire
                note_existe.commentaire_attribuee = True
                messages.success(request, "Votre commentaire a bien été pris en compte.")

            note_existe.save()

        else:
            # Création d'une nouvelle note si aucune note existante
            note_existe = NoteUser.objects.create(
                passager=request.user,
                chauffeur=chauffeur,
                trajet=trajet,
                note=nouvelle_note if nouvelle_note else None,
                commentaire=nouveau_commentaire if nouveau_commentaire else None,
                avis_donne=True if avis_soumis else False,
            )
            if nouvelle_note:
                note_existe.note_attribuee = True
            if nouveau_commentaire:
                note_existe.commentaire_attribuee = True
            if avis_soumis:
                note_existe.avis_donne = True
            note_existe.save()

        # Logique pour l'avis "oui" ou "non"
        if avis_soumis:
            commentaire = note_existe.commentaire
            token = None
            if token is None:
                token = uuid.uuid4()

            if avis_soumis == "oui":
                # Crédits au chauffeur
                chauffeur = trajet.chauffeur
                credit_chauffeur = CreditUser.objects.get(user=chauffeur)
                facture_passager = reservation.prix_par_passager
                credit_chauffeur.credit += facture_passager
                credit_chauffeur.save()

                # Envoi email positif
                from ..envoi_email import Envoi_Email_Avis_Trajet_Positif
                Envoi_Email_Avis_Trajet_Positif(
                    request, chauffeur, trajet_id, reservation, commentaire, token
                )

            elif avis_soumis == "non":
                # Envoi email négatif
                from ..envoi_email import Envoi_Email_Avis_Trajet_Negatif
                Envoi_Email_Avis_Trajet_Negatif(
                    request, request.user, trajet_id, reservation, commentaire, token
                )
            return redirect("AvisSatisfaction", trajet_id=trajet_id, token=token)
    return avis_form