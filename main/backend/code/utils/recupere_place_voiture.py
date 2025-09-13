from django.http import JsonResponse
from ...models import Voiture

def recupere_places_voiture(request):
    voiture_id = request.GET.get('voiture_id')
    try:
        voiture = Voiture.objects.get(id=voiture_id)
        return JsonResponse({'places': voiture.places})
    except Voiture.DoesNotExist:
        return JsonResponse({'error': 'Voiture non trouvée'}, status=404)
