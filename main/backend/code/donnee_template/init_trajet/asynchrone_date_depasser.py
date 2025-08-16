from django.shortcuts import render
from ....models import TrajetProposer, Voiture
from collections import defaultdict
from django.utils import timezone


def TrajetDateDepasser(request):
    user=request.user
    aujourd_hui = timezone.localdate()
    trajet_depasser = TrajetProposer.objects.filter(chauffeur=user, date__lte=aujourd_hui)

    trajet5 = list(
        trajet_depasser.values(
            "id", "etat",
        )
    )

    return {
        "trajet5": trajet5
    }