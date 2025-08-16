from django.http import JsonResponse
from ...models import Voiture

def recupere_places_voiture(request):
    voiture_id = request.GET.get('voiture_id')  # Récupérer l'ID de la voiture de la requête AJAX
    try:
        voiture = Voiture.objects.get(id=voiture_id)  # Récupérer la voiture via son ID
        # Retourner la valeur de places dans une réponse JSON
        return JsonResponse({'places': voiture.places})
    except Voiture.DoesNotExist:
        # Si la voiture n'existe pas, retourner une erreur
        return JsonResponse({'error': 'Voiture non trouvée'}, status=404)
