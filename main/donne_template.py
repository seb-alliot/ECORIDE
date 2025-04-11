from .models import TrajetProposer, ReservationTrajet, Voiture
from .models import CreditUser, AdresseUser
from django.conf import settings
from django.contrib.auth.models import User


def initialisation_template(request):
    photo_default_url = settings.MEDIA_URL + "photo_default/photo_default.jpg"
    user = request.user

    if request.user.is_authenticated:
        try:
            credit = CreditUser.objects.get(user=user)
        except CreditUser.DoesNotExist:
            credit = None
        trajets = TrajetProposer.objects.filter(chauffeur=user)
        adresse_user = AdresseUser.objects.filter(user=user).first()
    if user.is_anonymous:
        credit = None
        adresse_user = None
        trajets = None

    context = {
        "user": user,
        "credit": credit,
        "adresse_user": adresse_user,
        "photo_default_url": photo_default_url,
        "credit": credit,
        "adresse_user": adresse_user,
        "trajets": trajets,
        "photo_default_url": photo_default_url,
    }
    return context

def InfoTrajet(request):
    user = request.user
    type_moteur = Voiture.objects.filter(type_moteur=user)

    chauffeur = TrajetProposer.objects.filter(chauffeur=user).first()
    trajet = TrajetProposer.objects.filter(chauffeur=user).first()
    trajet1 = TrajetProposer.objects.filter(chauffeur=user ,etat="Terminé")
    trajet2 = TrajetProposer.objects.filter(chauffeur=user , etat="Annulé")
    trajet3 = TrajetProposer.objects.filter(chauffeur=user , etat="En cours")
    trajet4 = TrajetProposer.objects.filter(chauffeur=user , etat="Disponible")

    return {
        'chauffeur': chauffeur,
        'type_moteur': type_moteur,
        'trajet': trajet,
        'trajet1': trajet1,
        'trajet2': trajet2,
        'trajet3': trajet3,
        'trajet4': trajet4
    }

def Info_Reservation(request):
    user = request.user

    chauffeur = TrajetProposer.objects.filter(chauffeur=user).first()
    trajet = TrajetProposer.objects.filter(chauffeur=user).first()
    reservation = ReservationTrajet.objects.filter(passager=user)
    reservation1 = reservation.filter(etat_reservation="Terminé", passager=user)
    reservation2 = reservation.filter(etat_reservation="Annulé", passager=user)
    reservation3 = reservation.filter(etat_reservation="Reserver", passager=user)
    prix_total_paye = ReservationTrajet.paiement_total_passager(request.user, trajet)

    return {
        'chauffeur': chauffeur,
        'reservation': reservation,
        'reservation1': reservation1,
        'reservation2': reservation2,
        'reservation3': reservation3,
        'prix_total_paye': prix_total_paye,
    }