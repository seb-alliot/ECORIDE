from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password

import secrets

from ....forms import IdentifiantForm
from ....models import TokenValidation
from ...envoi_email.send_email import envoi_email

def PremierEtape(request):
    user_request = request.user
    if user_request.is_authenticated:
        return redirect("index")
    else:
        form = IdentifiantForm(request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                username = form.cleaned_data.get("username")
                try:
                    user_to_connect = get_user_model().objects.get(username=username)

                    if user_to_connect.is_active:

                        request.session["user_id"] = user_to_connect.id

                        # --- Génération des tokens sécurisés ---
                        token_session_check = get_random_string(32)
                        two_fa = str(secrets.randbelow(100000000)).zfill(8)
                        two_fa_hashed = make_password(two_fa)

                        # 1. Mise à jour de la DB : Stockage sécurisé du CODE 2FA
                        TokenValidation.objects.update_or_create(
                            user=user_to_connect,
                            defaults={
                                "code_2fa": two_fa_hashed,
                                "session_token": token_session_check,
                                "action": "2FA_login"
                            }
                        )

                        # 2. Session : Stockage uniquement du jeton anti-saut d'étape
                        request.session["token"] = token_session_check

                        email = user_to_connect.email

                        subject = "Votre code de connexion"
                        context = {
                            "username": username,
                            "email": email,
                            "token_connection": two_fa
                        }

                        envoi_email(request, to=email, subject=subject, template="style_email/_2fa.html", context=context)
                        return redirect("connection2")
                    else:
                        messages.error(request, "Votre compte n'est pas actif.")
                        return redirect("connection1")
                except get_user_model().DoesNotExist:
                    messages.error(request, "Utilisateur introuvable.")
                    return redirect("connection1")
            else:
                messages.error(request, "Votre compte est inexistant.")

        return form