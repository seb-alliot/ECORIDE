from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User


def SuppressionCompte(request):
    user = request.user
    choix = request.POST.get("choix")
    # Suppression de l'utilisateur
    try:
        if request.method == "POST":
            if choix == "oui":
                # Suppression de l'utilisateur
                user = User.objects.get(id=user.id)
                user.delete()
                messages.success(request, "Le compte a été supprimé avec succès.")
            else:
                pass
    except User.DoesNotExist:
        messages.error(request, "L'utilisateur n'existe pas.")

    return redirect('index')