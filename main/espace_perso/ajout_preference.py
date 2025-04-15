from django.shortcuts import redirect
from django.contrib import messages
from ..models import Preference
from ..forms import PreferenceForm

def DonneTesPreferences(request):
    user = request.user
    preference = Preference.objects.filter(user_preference_id=user).first()
    preference_form = PreferenceForm(request.POST, instance=preference)

    if request.method == "POST" and request.POST.get("form_soumis") == "preference_form":
        preference_form = PreferenceForm(request.POST, instance=preference)
        if preference_form.is_valid():
            preference = preference_form.save(commit=False)
            preference.user_preference = user
            preference.save()
            messages.success(
                request, "Vos préférences ont été enregistrées, vous avez bon goût."
            )
            return redirect("MonCompte")
        else:
            preference_form = PreferenceForm(request.POST, instance=preference)
            messages.error(request, "Vos préférences pourries ont été rejetées.")
    return preference_form
