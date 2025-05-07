from django.shortcuts import redirect
from django.contrib import messages
from ...models import ChoixRole
from ...forms import ChoixRoleForm

def ChangeTonRole(request):
    user = request.user
    role = ChoixRole.objects.filter(user=user).first()

    role_form = ChoixRoleForm(instance=role)
    if request.method == "POST" and request.POST.get("form_soumis") == "role_form":
        role_form = ChoixRoleForm(request.POST, instance=role)
        if role_form.is_valid():
            role = role_form.save(commit=False)
            role.user = user
            role.save()
            messages.success(request, "Votre rôle a été mis à jour.")
            return redirect("MonCompte")
        else:
            role_form = ChoixRoleForm(request.POST, instance=role)
            messages.error(request, "Veuillez sélectionner un rôle valide.")
    context = {
        "role_form": role_form,
        "role": role,
    }
    return role_form
