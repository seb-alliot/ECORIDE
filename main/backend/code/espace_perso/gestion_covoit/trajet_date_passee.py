import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from ....models import TrajetProposer

@login_required
@require_POST
def annuler_trajet(request):
    """
    Annule les trajets 'Disponible' envoyés depuis le front via requete asynchrone.
    Retourne un JsonResponse avec le nombre de trajets annulés.
    """
    user = request.user
    try:
        data = json.loads(request.body)
        print("Data received for trajet annulation:", data)
        trajets_ids = data.get('trajet', [])
        print("Trajets IDs to cancel:", trajets_ids)
    except (json.JSONDecodeError, KeyError, TypeError):
        trajets_ids = []

    trajets5 = TrajetProposer.objects.filter(
        id__in=trajets_ids,
        chauffeur=user,
        etat='Disponible',
    )
    print("Trajets trouvé pour annulation:", trajets5)

    nb_annules = 0
    for trajet in trajets5:
        trajet.etat = 'Annulé'
        trajet.save()  # sauvegarde pour les signaux
        nb_annules += 1

    return JsonResponse({
        'success': True,
        'nb_annules': nb_annules
    })
