from django.shortcuts import render
from ..models import TrajetProposer, Voiture
from collections import defaultdict

def InfoTrajet(request):
    user = request.user
    type_moteur = Voiture.objects.filter(type_moteur=user)

    chauffeur = TrajetProposer.objects.filter(chauffeur=user).first()
    trajets = TrajetProposer.objects.filter(chauffeur=user)
    trajet_chercher = TrajetProposer.objects.filter(chauffeur=user, etat__in=["Terminé", "Annulé", "En cours", "Disponible"])

    trajet_voulu = defaultdict(list)
    # Initialiser les listes vides dès le départ
    trajet1, trajet2, trajet3, trajet4 = [], [], [], []

    for trajet in trajet_chercher:
        trajet_voulu[trajet.etat].append(trajet)

    trajet1 = trajet_voulu["Terminé"]
    trajet2 = trajet_voulu["Annulé"]
    trajet3 = trajet_voulu["En cours"]
    trajet4 = trajet_voulu["Disponible"]

    return {
        'chauffeur': chauffeur,
        'type_moteur': type_moteur,
        'trajets': trajets,
        'trajet1': trajet1,
        'trajet2': trajet2,
        'trajet3': trajet3,
        'trajet4': trajet4
    }
