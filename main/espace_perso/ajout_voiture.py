from django.shortcuts import redirect
from django.contrib import messages
from ..models import Voiture
from ..forms import VoitureForm

def AjouteTaCaisse(request):
    user = request.user
    voiture = Voiture.objects.filter(user=user).first()
    voiture_form = VoitureForm(request.POST)

    if request.method == "POST" and request.POST.get("form_soumis") == "voiture_form":
        voiture_form = VoitureForm(request.POST)
        if voiture_form.is_valid():
            voiture = voiture_form.save(commit=False)
            voiture.user = user
            voiture.save()
            messages.success(request, "Votre véhicule a bien été ajouté.")
            return redirect("MonCompte")
        else:
            immatriculation = request.POST.get("immatriculation")
            if Voiture.objects.filter(immatriculation=immatriculation).exists():
                messages.error(request, "Cette immatriculation est déjà prise.")
            else:
                if immatriculation:
                    messages.error(request, "L'immatriculation n'a pas le bon format.")
    return voiture_form
