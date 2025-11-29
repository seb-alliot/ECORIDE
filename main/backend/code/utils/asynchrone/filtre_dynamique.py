from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, Avg, FloatField
from django.db.models.functions import Round
from ....models import TrajetProposer, User, AdresseUser
from datetime import datetime
from django.conf import settings

from django.utils import timezone

def filtre_dynamique(request):
    maintenant = timezone.now()
    lien_photo_default = settings.MEDIA_URL + "photo_default/photo_default.jpg"

    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({"error": "Cette URL n'accepte que les requêtes AJAX."}, status=400)

    # ← NOUVEAU : Récupère les critères de recherche
    ville_depart = request.GET.get("ville_depart", "")
    ville_arrivee = request.GET.get("ville_arrivee", "")
    date = request.GET.get("date", "")
    pseudo = request.GET.get("pseudo", "")

    # Commence avec les mêmes filtres que la recherche initiale
    trajet4 = TrajetProposer.objects.filter(
        etat="Disponible",
        places__gt=0
    ).exclude(date__lt=maintenant.date())

    # Applique les critères de recherche si présents
    if ville_depart:
        trajet4 = trajet4.filter(ville_depart__icontains=ville_depart)
    if ville_arrivee:
        trajet4 = trajet4.filter(ville_arrivee__icontains=ville_arrivee)
    if date:
        trajet4 = trajet4.filter(date=date)
    if pseudo:
        trajet4 = trajet4.filter(chauffeur__username__icontains=pseudo)

    trajet4 = trajet4.annotate(note_chauffeur=Avg("chauffeur__accusé__note"))

    # Récupération des FILTRES depuis JS
    note = request.GET.get("note")
    temps_trajet = request.GET.get("temps_trajet")
    prix = request.GET.get("prix")


    # Applique les filtres
    if note:
        chauffeurs = User.objects.annotate(note_moyenne=Avg("accusé__note")).filter(note_moyenne__gte=note)
        trajet4 = trajet4.filter(chauffeur__in=chauffeurs)

    if temps_trajet:
        trajet4 = trajet4.filter(temps_trajet__lte=temps_trajet)

    if prix:
        trajet4 = trajet4.filter(prix__lte=prix)

    # Sépare écolo / non-écolo
    resultat1 = trajet4.exclude(Q(voiture__type_moteur="Electrique") | Q(voiture__type_moteur="Hybride"))
    resultat2 = trajet4.exclude(Q(voiture__type_moteur="essence") | Q(voiture__type_moteur="diesel"))

    resultat1 = resultat1.annotate(note_chauffeur=Round(Avg("chauffeur__accusé__note"), 2, output_field=FloatField()))
    resultat2 = resultat2.annotate(note_chauffeur=Round(Avg("chauffeur__accusé__note"), 2, output_field=FloatField()))

    html = render_to_string(
        "interface_utilisateur/utilisateur/onglet_1_trajet/passager/_resultat_filtre_recherche.html",
        {"resultat1": resultat1, "resultat2": resultat2, "photo_default_url": lien_photo_default},
        request=request
    )

    return JsonResponse({"html": html})