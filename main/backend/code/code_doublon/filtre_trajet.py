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

    # Une seule annotation initiale
    trajet4 = (TrajetProposer.objects
                .exclude(date__lte=maintenant)
                .annotate(note_chauffeur=Avg("chauffeur__accusé__note")))

    if request.method == "GET" and request.GET.get("form_trajet") == "filtre_form" and filtre_form.is_valid():

        # Filtre par note (sans boucle)
        if filtre_form.cleaned_data["note"]:
            note_minimum = filtre_form.cleaned_data["note"]
            chauffeurs = User.objects.annotate(
                note_moyenne=Avg("accusé__note")
            ).filter(note_moyenne__gte=note_minimum)
            trajet4 = trajet4.filter(chauffeur__in=chauffeurs)

        # Filtre par temps
        if filtre_form.cleaned_data["temps_trajet"]:
            trajet4 = trajet4.filter(temps_trajet__lte=filtre_form.cleaned_data["temps_trajet"])

        # Filtre par prix
        if filtre_form.cleaned_data["prix"]:
            trajet4 = trajet4.filter(prix__lte=filtre_form.cleaned_data["prix"])

        # Séparation écolo/classique (sans re-annoter)
        resultat1 = trajet4.exclude(
            Q(voiture__type_moteur="Electrique") | Q(voiture__type_moteur="Hybride")
        )
        resultat2 = trajet4.exclude(
            Q(voiture__type_moteur="essence") | Q(voiture__type_moteur="diesel")
        )

        if resultat1.exists() or resultat2.exists():
            messages.success(request, "Hey voici juste pour vous !!")
        else:
            messages.error(request, "La déception ... Une autre date peut-être ?")

    return filtre_form, resultat1, resultat2