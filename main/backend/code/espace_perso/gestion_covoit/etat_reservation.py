from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from ....models import ReservationTrajet, CreditUser
from ....forms import StatutReservationForm
from django.db import transaction
from django.urls import reverse

def GereTaReservationPassager(request):
    user = request.user

    if request.method == "POST" and request.POST.get("form_soumis") == "reservation_form":
        reservation_id = request.POST.get("reservation_id")

        if not reservation_id:
            messages.error(request, "Aucune réservation spécifiée.")
            return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

        try:
            with transaction.atomic():
                reservation_form = StatutReservationForm(request.POST)

                reservation = get_object_or_404(ReservationTrajet, id=reservation_id, passager=user)

                if reservation.reservation_rembourser:
                    messages.error(request, "La réservation a déjà été remboursée.")
                    return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

                if reservation_form.is_valid():
                    etat_reservation = reservation_form.cleaned_data["etat_reservation"]

                    if etat_reservation == "Annulé":
                        # Remboursement
                        trajet = reservation.trajet_reserver
                        trajet.places += reservation.places

                        prix_payer = reservation.places * trajet.prix

                        credit_user = CreditUser.objects.get(user=request.user)
                        credit_user.credit += prix_payer
                        credit_user.save()

                        trajet.total_payer -= prix_payer
                        trajet.save()

                        reservation.etat_reservation = "Annulé"
                        reservation.reservation_rembourser = True
                        reservation.save()

                        messages.success(request, "Votre réservation a bien été annulée.")
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
                    else:
                        messages.error(request, "Action non reconnue.")
                        return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
                else:
                    messages.error(request, "Une erreur est survenue lors de la validation.")
                    return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

        except Exception as e:
            messages.error(request, f"Une erreur est survenue : {str(e)}")
            return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")

    return StatutReservationForm()