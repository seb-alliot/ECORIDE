from django.db.models import Q
from django.contrib import messages
from .models import TrajetProposer, User
from django.db.models import Avg, Value, Q



def RechercheTrajet(request, recherche_form, user, trajet4):
    if request.method == "GET" and recherche_form.is_valid():
        ville_depart = recherche_form.cleaned_data["ville_depart"]
        ville_arrivee = recherche_form.cleaned_data["ville_arrivee"]
        date = recherche_form.cleaned_data["date"]

        resultat = TrajetProposer.objects.filter(
            ville_depart__icontains=ville_depart,
            ville_arrivee__icontains=ville_arrivee,
            date=date,
            etat="Disponible",
        )

        if user.is_authenticated:
            trajet4 = resultat.exclude(chauffeur=user)

        request.session["resultat_recherche"] = list(
            resultat.values_list("id", flat=True)
        )

        first_resultat = trajet4.exclude(
            Q(voiture__type_moteur="Electrique") | Q(voiture__type_moteur="Hybride")
        )
        second_resultat = trajet4.exclude(
            Q(voiture__type_moteur="essence") | Q(voiture__type_moteur="diesel")
        )

        if first_resultat.exists() or second_resultat.exists():
            messages.success(request, "Hey voici juste pour vous !!")
        else:
            messages.error(
                request,
                "La déception ... Une autre date peut-être ?",
            )
        return first_resultat, second_resultat


def Filtre_trajet(request, filtre_form):
    if request.method == "GET" and filtre_form.is_valid():
        resultat = TrajetProposer.objects.filter(
            id__in=request.session.get("resultat_recherche")
        )

        if filtre_form.cleaned_data["note"]:
            note_minimum = filtre_form.cleaned_data["note"]
            chauffeurs = User.objects.annotate(
                note_moyenne=Avg("accusé__note")
            ).filter(note_moyenne__gte=note_minimum)

            for chauffeur in chauffeurs:
                resultat = resultat.filter(chauffeur__in=chauffeurs)

        if filtre_form.cleaned_data["temps_trajet"]:
            resultat = resultat.filter(
                temps_trajet__lte=filtre_form.cleaned_data["temps_trajet"]
            )

        if filtre_form.cleaned_data["prix"]:
            resultat = resultat.filter(prix__lte=filtre_form.cleaned_data["prix"])

        first_resultat = resultat.exclude(
            Q(voiture__type_moteur="Electrique") | Q(voiture__type_moteur="Hybride")
        )
        second_resultat = resultat.exclude(
            Q(voiture__type_moteur="essence") | Q(voiture__type_moteur="diesel")
        )

        if first_resultat.exists() or second_resultat.exists():
            messages.success(request, "Vos exigences ont trouvé satisfaction.")
        elif not resultat.exists():
            messages.error(request, "Oups !! La recherche n'a rien donné.")

        return first_resultat, second_resultat
