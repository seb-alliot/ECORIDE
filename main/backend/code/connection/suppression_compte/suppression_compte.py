from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout



def SuppressionCompte(request):
    # 1. Vérification de l'authentification
    if not request.user.is_authenticated:
        messages.error(request, "Veuillez vous connecter pour effectuer cette action.")
        return redirect('login')

    user_delete = request.user
    suppression_compte_form = request.POST.get("choix_suppression")

    if request.method == "POST" and suppression_compte_form:
        choix = suppression_compte_form
        if choix == "oui":
            #le signal s'occupera de l'email de confirmation
            # Fermeture de la session avant de supprimer le compte, vide la mémoire de la session
            logout(request)
            # Suppression du compte utilisateur
            user_delete.delete()

            messages.success(request, f"Le compte de {user_delete.username} a été supprimé avec succès.")
            return redirect('index')
        else:
            messages.info(request, "La suppression du compte a été annulée.")
            return redirect('profile')

    return redirect('index')