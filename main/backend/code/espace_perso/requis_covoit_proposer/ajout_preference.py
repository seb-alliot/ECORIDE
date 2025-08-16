from django.shortcuts import redirect
from django.contrib import messages
from ....models import Preference
from ....forms import PreferenceForm
from django.urls import reverse

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
            return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
        else:
            preference_form = PreferenceForm(request.POST, instance=preference)
            messages.error(request, "Vos préférences pourries ont été rejetées.")
            return redirect(f"{reverse('MonCompte')}?{request.META['QUERY_STRING']}")
    return preference_form
