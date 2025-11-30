from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from ....models import Voiture

@staff_member_required
def voiture_chauffeur(request):
    chauffeur = request.GET.get("id_chauffeur")
    if not chauffeur:
        return JsonResponse({"voitures": [], "places": []})

    voitures = Voiture.objects.filter(user__id=chauffeur)

    voitures_list = [
        {
            "id": voiture.id,
            "marque": voiture.marque,
            "modele": voiture.modele,
            "places": voiture.places
        }
        for voiture in voitures
    ]

    # Récupérer le nombre max de places
    max_places = max([voiture.places for voiture in voitures]) if voitures else 0

    return JsonResponse({
        "voitures": voitures_list,
        "max_places": max_places
    })