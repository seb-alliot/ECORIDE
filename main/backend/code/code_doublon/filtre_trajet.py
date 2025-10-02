from django.db.models import Q, Avg
from django.contrib import messages
from ...models import TrajetProposer, User
from ...forms import FiltreTrajetForm
from datetime import datetime

# filtre initial synchrone avant d'etre remplacer par asynchrone_filtre_trajet.py
def Filtre_trajet(request):
    resultat1 = None
    resultat2 = None

    filtre_form = FiltreTrajetForm(request.GET or None)


    maintenant = datetime.now()
    trajet4 = TrajetProposer.objects.filter().annotate(note_chauffeur=Avg("chauffeur__accusé__note")).exclude(date__lte=maintenant)

    if request.method == "GET" and request.GET.get("form_trajet") == "filtre_form" and filtre_form.is_valid():
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
        ).filter().annotate(note_chauffeur=Avg("chauffeur__accusé__note"))
        resultat2 = trajet4.exclude(
            Q(voiture__type_moteur="essence") | Q(voiture__type_moteur="diesel")
        ).annotate(note_chauffeur=Avg("chauffeur__accusé__note"))

        if resultat1.exists() or resultat2.exists():
            messages.success(request, "Hey voici juste pour vous !!")

        else:
            messages.error(
                request,
                "La déception ... Une autre date peut-être ?",
            )
    return filtre_form, resultat1, resultat2