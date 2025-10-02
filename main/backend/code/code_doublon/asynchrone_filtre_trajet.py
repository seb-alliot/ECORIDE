from django.http import JsonResponse
from django.template.loader import render_to_string
from django.db.models import Q, Avg, FloatField
from django.db.models.functions import Round
from ...models import TrajetProposer, User, AdresseUser
from datetime import datetime
from django.conf import settings

def async_function(request):
    maintenant = datetime.now()
    lien_photo_default = settings.MEDIA_URL + "photo_default/photo_default.jpg"
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({"error": "Cette URL n'accepte que les requêtes AJAX."}, status=400)

    trajet4 = TrajetProposer.objects.annotate(
        note_chauffeur=Avg("chauffeur__accusé__note")
    ).exclude(date__lte=maintenant)
    chauffeurs = trajet4.values("chauffeur").distinct()

    # Récupération des photos des chauffeurs
    for conducteur in chauffeurs:
        # Correction: Accéder à l'ID du chauffeur via la clé 'chauffeur' du dictionnaire
        user_id = conducteur['chauffeur']
        photo_adresse_user = AdresseUser.objects.filter(user_id=user_id).first()

        # S'assurer que l'objet AdresseUser existe avant d'accéder à la photo
        if photo_adresse_user and photo_adresse_user.photo:
            photo_url = photo_adresse_user.photo.url
        else:
            photo_url = lien_photo_default

        conducteur["photo"] = photo_url
    # Récupération des filtres depuis JS
    note = request.GET.get("note")
    temps_trajet = request.GET.get("temps_trajet")
    prix = request.GET.get("prix")

    if note:
        chauffeurs = User.objects.annotate(note_moyenne=Avg("accusé__note")).filter(note_moyenne__gte=note)
        trajet4 = trajet4.filter(chauffeur__in=chauffeurs)

    if temps_trajet:
        trajet4 = trajet4.filter(temps_trajet__lte=temps_trajet)

    if prix:
        trajet4 = trajet4.filter(prix__lte=prix)

    resultat1 = trajet4.exclude(Q(voiture__type_moteur="Electrique") | Q(voiture__type_moteur="Hybride"))
    resultat2 = trajet4.exclude(Q(voiture__type_moteur="essence") | Q(voiture__type_moteur="diesel"))

    resultat1 = resultat1.annotate(note_chauffeur=Round(Avg("chauffeur__accusé__note"), 2, output_field=FloatField()))
    resultat2 = resultat2.annotate(note_chauffeur=Round(Avg("chauffeur__accusé__note"), 2, output_field=FloatField()))

    html = render_to_string(
        "interface_utilisateur/utilisateur/onglet_1_trajet/passager/_resultat_filtre_recherche.html",
        {"resultat1": resultat1, "resultat2": resultat2},
        request=request
    )
    return JsonResponse({"html": html})
