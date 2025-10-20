from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from ....models import Voiture

@staff_member_required
def get_modeles_voiture(request):
    marque = request.GET.get("marque")
    if not marque:
        return JsonResponse({"modeles": []})

    marques_valides = [m[0] for m in Voiture.MARQUE]
    if marque not in marques_valides:
        return JsonResponse({"modeles": []})

    modeles = Voiture.MODELE.get(marque, [])
    return JsonResponse({"modeles": modeles})
