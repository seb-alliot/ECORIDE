from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from ..models import ReservationTrajet, CreditUser
from ..forms import StatutReservationForm

def GereTaReservationPassager(request):
    user = request.user
    reservation_form = StatutReservationForm(request.POST)
    reservation = ReservationTrajet.objects.filter(passager=user).first()
    reservation_id = request.POST.get("reservation_id")

    if request.method == "POST" and request.POST.get("form_soumis") == "reservation_form":

        reservation_form = StatutReservationForm(request.POST)
        reservation_id = request.POST.get("reservation_id")
        reservation = get_object_or_404(ReservationTrajet, id=reservation_id)

        if reservation.reservation_rembourser:
            messages.error(request, "La réservation a déjà été remboursée.")
            return redirect("MonCompte")
        else:
            if reservation_form.is_valid():
                if request.user == reservation.passager:
                    etat_reservation = reservation_form.cleaned_data[
                    "etat_reservation"
                    ]

                    if etat_reservation == "Annulé":
                        trajet = reservation.trajet_reserver
                        trajet.places += reservation.places
                        trajet.save()

                        prix_payer = reservation.places * trajet.prix
                        credit_user = CreditUser.objects.get(user=request.user)
                        credit_user.credit += prix_payer
                        credit_user.save()
                        trajet.total_payer -= prix_payer
                        trajet.save()

                        reservation.etat_reservation = "Annulé"
                        reservation.reservation_rembourser = True
                        reservation.save()
                        messages.success(
                        request, "Votre réservation a bien été annulée."
                        )
                        return redirect("MonCompte")
                    else:
                        messages.error(request, "Aucune réservation trouvée.")
                        return redirect("MonCompte")
    return reservation_form