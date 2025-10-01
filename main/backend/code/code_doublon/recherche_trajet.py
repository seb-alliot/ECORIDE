from django.contrib import messages
from django.db.models import Q, Avg
from ...models import TrajetProposer
from ...forms import RechercheTrajetForm
from django.utils import timezone

def RechercheTrajet(request):
    user = request.user
    maintenant = timezone.localtime()
    first_resultat = None
    second_resultat = None
    recherche_form = RechercheTrajetForm(request.GET or None)
    trajet4 = TrajetProposer.objects.filter(etat__in="Disponible").exclude(date__lte=maintenant).annotate(note_chauffeur=Avg("chauffeur__accusé__note"))
    if request.method == "GET" and request.GET.get("form_trajet") == "recherche_form" and recherche_form.is_valid():

        ville_depart = recherche_form.cleaned_data["ville_depart"]
        ville_arrivee = recherche_form.cleaned_data["ville_arrivee"]
        date = recherche_form.cleaned_data["date"]
        pseudo = recherche_form.cleaned_data["pseudo"]
        if pseudo:
            trajet4 = trajet4.filter(chauffeur__username__icontains=pseudo)

        trajet4 = TrajetProposer.objects.filter(
        ville_depart__icontains=ville_depart,
        ville_arrivee__icontains=ville_arrivee,
        date=maintenant.date(),
        etat__in=["Disponible"],
        places__gt=0,
    ).annotate(note_chauffeur=Avg("chauffeur__accusé__note"))

        if user.is_authenticated:
            trajet4 = trajet4.exclude(chauffeur=user)

        first_resultat = trajet4.exclude(
            Q(voiture__type_moteur="Electrique") | Q(voiture__type_moteur="Hybride")
        )
        second_resultat = trajet4.exclude(
            Q(voiture__type_moteur="essence") | Q(voiture__type_moteur="diesel")
        )

        if first_resultat.exists() or second_resultat.exists():
            messages.success(request, "Hey voici juste pour vous !!")
        elif not first_resultat.exists() and not second_resultat.exists():
            messages.error(request, "La déception ... Une autre date peut-être ?")

    return recherche_form, first_resultat, second_resultat
