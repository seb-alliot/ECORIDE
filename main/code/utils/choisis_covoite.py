from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Avg, Q
from ...models import TrajetProposer, NoteUser, ReservationTrajet, CreditUser, Preference
from ...forms import ReservationTrajetForm
from django.db import transaction


def ChoisisTonCovoite(request):
    user = request.user
    # Récupération du trajet
    trajet_id = request.GET.get("trajet_id")
    trajet = TrajetProposer.objects.filter(
        id=trajet_id
        ).annotate(note_chauffeur=Avg("chauffeur__accusé__note")).first()
    commentaire = NoteUser.objects.filter(
        chauffeur=trajet.chauffeur,
    ).exclude(
        Q(commentaire__exact="Aucun commentaire trouvé.") |
        Q(commentaire__isnull=True) |
        Q(commentaire__exact="")
    ).order_by("passager", "?").distinct("passager").values("commentaire")[:3] #utilisation de distinct pour ne pas avoir de doublon, possible que sur postgresql

    preference = Preference.objects.filter(user_preference=trajet.chauffeur).first()

    try:
        credit_user = (
            CreditUser.objects.get(user=user) if user.is_authenticated else None
        )
        credits = credit_user.credit if credit_user else 0
    except CreditUser.DoesNotExist:
        credits = 0

    # Vérification d'une réservation existante pour l'utilisateur
    if not user.is_authenticated:
        reservation = None
    else:
        reservation = ReservationTrajet.objects.filter(
            passager=user, trajet_reserver=trajet
        ).first()

        # Initialisation du formulaire
    reservation_form = ReservationTrajetForm(request.POST or None, instance=reservation)

    # Logique de réservation uniquement pour les utilisateurs authentifiés
    if request.method == "POST" and user.is_authenticated:
        if reservation_form.is_valid():
            places_reservees = reservation_form.cleaned_data["places"]
            if request.POST.get("Reserver") == "oui":
                with transaction.atomic():
                    trajet = TrajetProposer.objects.select_for_update().get(id=trajet.id)
                    # Vérification du crédit suffisant
                    prix_total = trajet.prix * places_reservees
                    if credits < prix_total:
                        messages.error(
                            request, "Vos crédits sont insuffisant pour réserver ce trajet."
                        )
                        return HttpResponseRedirect(f"{reverse('reservation')}?trajet_id={trajet.id}")

                    # Vérification du nombre de places disponibles
                    elif places_reservees > trajet.places:
                        messages.error(
                            request,
                            "Le nombre de places est insuffisant actuellement pour votre demande.",
                        )
                        return redirect(f"{reverse('reservation')}?trajet_id={trajet.id}")
                        #ou return HttpResponseRedirect(f"{reverse('reservation')}?trajet_id={trajet.id}") #

                    # Vérification et mise à jour de la réservation
                    if reservation:
                        if reservation.etat_reservation == "Annulé":
                            # On réactive la réservation sinon gros bug pas sympa et bien muet
                            reservation.etat_reservation = "Reserver"
                            reservation.places = 0
                            reservation.prix_par_passager = 0
                            reservation.save()
                            # Mise à jour des données
                            reservation.paiement_passager(places_reservees)

                        else:
                            reservation.places += places_reservees
                            reservation.paiement_passager(places_reservees)
                    else:
                        reservation = ReservationTrajet.objects.create(
                            trajet_reserver=trajet,
                            passager=user,
                            prix_par_passager=prix_total,
                            places=places_reservees,
                        )
                        credit_user.credit -= prix_total
                        credit_user.save()

                        # Mise à jour des places restantes
                    trajet.places -= places_reservees
                    trajet.save()

                    messages.success(request, "La réservation est validée, bonne route !")
                    return redirect(f"{reverse('reservation')}?trajet_id={trajet.id}")
            else:
                messages.error(request, "Vos creédits sont insuffisants pour réserver.")
    return reservation_form , trajet, commentaire, preference
