from django.contrib.auth import authenticate, login, get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.hashers import check_password # ✅ Correction : Importation de check_password
from ....forms import MotDePasseForm
from ....models import TokenValidation


MAX_TENTATIVE = 3

def DeuxiemeEtape(request):
    if request.user.is_authenticated:
        return redirect("index")

    # Récupération session
    user_id = request.session.get("user_id")
    token_etape1 = request.session.get("token")
    tentative = request.session.get("tentative_connection", 0)
    connected_users = request.session.get("connected_users", [])

    # Vérification du passage de l'etape 1 sinon redirection
    if not user_id or not token_etape1 or tentative >= MAX_TENTATIVE:
        if tentative >= MAX_TENTATIVE:
            messages.error(request, "Trop de tentatives. Veuillez recommencer l'étape 1.")
            return redirect("connection1")

    if request.method == "POST":
        form = MotDePasseForm(request.POST)

        if form.is_valid():
            password = form.cleaned_data["password"]
            two_fa = form.cleaned_data["token_connection"]

            try:
                # 1. Récupération de l'utilisateur
                User = get_user_model()
                user = User.objects.get(id=user_id)

                token_two_fa = TokenValidation.objects.get(user=user)

                # 2. Vérification du token 2FA ==> check_password est natif de django
                if not check_password(two_fa, token_two_fa.code_2fa):
                    tentative += 1
                    request.session["tentative_connection"] = tentative
                    messages.error(request, f"Code incorrect. Il vous reste {MAX_TENTATIVE - tentative} tentatives.")
                    return redirect("connection2")

                authenticated_user = authenticate(username=user.username, password=password)

                if not authenticated_user:
                    tentative += 1
                    request.session["tentative_connection"] = tentative
                    messages.error(request, f"Mot de passe incorrect. Il vous reste {MAX_TENTATIVE - tentative} tentatives.")
                    return redirect("connection2")

                if user_id not in connected_users:
                    connected_users.append(user_id)
                    request.session["connected_users"] = connected_users

                token_two_fa.delete()
                login(request, authenticated_user)

                # On nettoie la session de login
                for key in ["user_id", "token", "token_connection", "tentative_connection"]:
                    request.session.pop(key, None)

                messages.success(request, "Vous êtes connecté.")
                return redirect("index")

            except TokenValidation.DoesNotExist:
                messages.error(request, "Code de connexion invalide ou expiré. Veuillez recommencer l'étape 1.")
                # Nettoyage complet de la session de connexion
                for key in ["user_id", "token", "token_connection", "tentative_connection"]:
                    request.session.pop(key, None)
                return redirect("connection1")

            except User.DoesNotExist:
                messages.error(request, "Utilisateur introuvable. Veuillez recommencer l'étape 1.")
                # Comme au dessus
                for key in ["user_id", "token", "token_connection", "tentative_connection"]:
                    request.session.pop(key, None)
                return redirect("connection1")

    else:
        form = MotDePasseForm()


    return form