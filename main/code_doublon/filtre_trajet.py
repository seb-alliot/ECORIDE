from django.db.models import Q, Avg
from django.contrib import messages
from ..models import TrajetProposer, User
from ..forms import FiltreTrajetForm

def Filtre_trajet(request):
    resultat1 = None
    resultat2 = None

    filtre_form = FiltreTrajetForm(request.GET or None)

    # Récupère les IDs de la recherche stockée dans la session
    resultat_ids_first = request.session.get("first_resultat", [])
    resultat_ids_second = request.session.get("second_resultat", [])

    resultat_ids = list(set(resultat_ids_first) | set(resultat_ids_second))
    trajet4 = TrajetProposer.objects.filter(id__in=resultat_ids)

    if request.method == "GET" and request.GET.get("form_trajet") == "filtre_form" and filtre_form.is_valid():
        trajet4 = TrajetProposer.objects.filter(id__in=resultat_ids)

        if filtre_form.cleaned_data["note"]:
            note_minimum = filtre_form.cleaned_data["note"]
            chauffeurs = User.objects.annotate(
                note_moyenne=Avg("accusé__note")
            ).filter(note_moyenne__gte=note_minimum)

            for chauffeur in chauffeurs:
                trajet4 = trajet4.filter(chauffeur__in=chauffeurs)

        if filtre_form.cleaned_data["temps_trajet"]:
            trajet4 = trajet4.filter(
                temps_trajet__lte=filtre_form.cleaned_data["temps_trajet"]
            )

        if filtre_form.cleaned_data["prix"]:
            trajet4 = trajet4.filter(prix__lte=filtre_form.cleaned_data["prix"])

        resultat1 = trajet4.exclude(
            Q(voiture__type_moteur="Electrique") | Q(voiture__type_moteur="Hybride")
        ).filter()
        resultat2 = trajet4.exclude(
            Q(voiture__type_moteur="essence") | Q(voiture__type_moteur="diesel")
        )

        if resultat1.exists() or resultat2.exists():
            messages.success(request, "Hey voici juste pour vous !!")
        else:
            messages.error(
                request,
                "La déception ... Une autre date peut-être ?",
            )
    return filtre_form, resultat1, resultat2
