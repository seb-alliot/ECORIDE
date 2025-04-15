from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from ..models import TrajetProposer, ReservationTrajet
from ..forms import TerminerTrajetForm
import uuid


def FiniTonCovoiturage(request):
    user = request.user
    trajet_terminer_form = TerminerTrajetForm(request.POST)
    trajet = TrajetProposer.objects.filter(chauffeur=user).first()

    if request.method == "POST" and request.POST.get("form_soumis") == "trajet_terminer_form":

        trajet_terminer_form = TerminerTrajetForm(request.POST)
        trajet_id = request.POST.get("trajet_id")
        if trajet_terminer_form.is_valid():
            token = None
            if token is None:
                token = uuid.uuid4()

            if request.user == trajet.chauffeur:
                trajet = get_object_or_404(TrajetProposer, id=trajet_id)
                # bien mettre trajet.chauffeur et non pas role.chauffeur  ou display comme en html sa ne fonctionne pas, erreur muette
                statut_trajet = trajet_terminer_form.cleaned_data["etat"]
                if statut_trajet == "Terminé":
                    reservations = ReservationTrajet.objects.filter(
                        trajet_reserver=trajet
                    )
                    reservations.update(etat_reservation="Terminé")
                    trajet.etat = statut_trajet
                    trajet.save()
                    messages.success(request, "Vous êtes arrivé à bon port !")
                    from ..envoi_email import Envoi_Email_Terminer
                    Envoi_Email_Terminer(request, trajet_id, reservations, token)
                    return redirect("MonCompte")
                else:
                    messages.error(request, "Aucun trajet trouvé.")
                    return redirect("MonCompte")
            else:
                messages.error(request, "Vous n'êtes pas le conducteur de ce trajet.")
                return redirect("MonCompte")
        else:
            trajet_terminer_form = TerminerTrajetForm()
            messages.error(request, "Une erreur est survenue lors de la validation du trajet.")
    else:
        trajet_terminer_form = TerminerTrajetForm()
    return trajet_terminer_form
