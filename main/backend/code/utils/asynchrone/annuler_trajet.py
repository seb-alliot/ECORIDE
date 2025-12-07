import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from ....models import TrajetProposer
import datetime

@login_required
@require_POST
def annuler_trajet(request):

    user = request.user
    try:
        data = json.loads(request.body)
        print(data)
        trajets_ids = data.get('trajet', [])
    except (json.JSONDecodeError, KeyError, TypeError):
        trajets_ids = []

    aujourdhui = datetime.date.today()

    trajets5 = TrajetProposer.objects.filter(
        id__in=trajets_ids,
        chauffeur=user,
        date__lt=aujourdhui,
        etat='Disponible'
    )

    nb_annules = 0
    for trajet in trajets5:
        trajet.etat = 'Annulé'
        trajet.save()
        nb_annules += 1

    return JsonResponse({
        'success': True,
        'nb_annules': nb_annules,
        'message': f'{nb_annules} trajet{"s" if nb_annules > 1 else ""} automatiquement nettoyé{"s" if nb_annules > 1 else ""}.'
    })
