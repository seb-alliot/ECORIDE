from django.shortcuts import redirect
from django.contrib import messages
from ...models import Voiture
from ...forms import VoitureForm
from django.urls import reverse

def AjouteTaCaisse(request):
    user = request.user
    try:
        voiture = Voiture.objects.get(user=user)
    except Voiture.DoesNotExist:
        voiture = None
    voiture_form = VoitureForm(request.POST)

    if request.method == "POST" and request.POST.get("form_soumis") == "voiture_form":
        voiture_form = VoitureForm(request.POST)
        if voiture_form.is_valid():
            voiture = voiture_form.save(commit=False)
            voiture.user = user
            voiture.save()
            messages.success(request, "Votre véhicule a bien été ajouté.")
            return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
        else:
            immatriculation = request.POST.get("immatriculation")
            if Voiture.objects.filter(immatriculation=immatriculation).exists():
                messages.error(request, "Cette immatriculation est déjà prise.")
            else:
                if immatriculation:
                    messages.error(request, "L'immatriculation n'a pas le bon format.")
    return voiture_form
