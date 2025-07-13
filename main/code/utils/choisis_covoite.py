from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.db.models import Avg, Q
from ...models import TrajetProposer, NoteUser, ReservationTrajet, CreditUser, Preference
from ...forms import ReservationTrajetForm
from django.db import transaction
from .compteur_vue_mongo import increment_vue
import os
from dotenv import load_dotenv
from pymongo import MongoClient


def ChoisisTonCovoite(request):
    user = request.user
    # Récupération du trajet
    load_dotenv()
    uri = os.getenv("uri")
    client = MongoClient(uri)
    db = client["ECORIDE"]

    trajet_id = request.GET.get("trajet_id")
    compteur = increment_vue(db, trajet_id)

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
                    prix_total = trajet.prix * places_reservees

                    if credits < prix_total:
                        messages.error(
                            request, "Vos crédits sont insuffisants pour réserver ce trajet."
                        )
                        return redirect(f"{reverse('reservation')}?trajet_id={trajet.id}")

                    if places_reservees > trajet.places:
                        messages.error(
                            request,
                            "Le nombre de places est insuffisant actuellement pour votre demande.",
                        )
                        return redirect(f"{reverse('reservation')}?trajet_id={trajet.id}")

                    # Si une réservation existe déjà
                    if reservation:
                        if reservation.etat_reservation == "Annulé":
                            reservation.etat_reservation = "Reserver"
                            reservation.places = 0
                            reservation.prix_par_passager = 0
                            reservation.save()
                        reservation.places += places_reservees
                        reservation.save()
                    else:
                        # La création déclenchera le signal qui gèrera le reste
                        ReservationTrajet.objects.create(
                            trajet_reserver=trajet,
                            passager=user,
                            places=places_reservees,
                            prix_par_passager=0  # Sera fixé par le signal
                        )

                    messages.success(request, "La réservation est validée, bonne route !")
                    return redirect(f"{reverse('reservation')}?trajet_id={trajet.id}")

    return reservation_form , trajet, commentaire, preference, compteur
