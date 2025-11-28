
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from ....models import Voiture

@staff_member_required
def voiture_chauffeur(request):
    chauffeur = request.GET.get("id_chauffeur")
    if not chauffeur:
        return JsonResponse({"id_voiture": []})

    voitures = Voiture.objects.filter(user__id=chauffeur)
    model_voiture = [voiture.modele for voiture in voitures]
    places_voiture = [voiture.places for voiture in voitures]
    return JsonResponse({"id_voiture": model_voiture, "id_places": places_voiture})