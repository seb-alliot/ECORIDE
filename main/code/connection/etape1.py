from django.contrib.auth import get_user_model
from django.contrib import messages
from ...forms import IdentifiantForm
from ...models import TokenValidation , User
from django.shortcuts import redirect
from django.utils.crypto import get_random_string

def PremierEtape(request):
    user = request.user
    if user.is_authenticated:
        return redirect("index")
    else:
        form = IdentifiantForm(request.POST or None)

        if request.method == "POST":
            if form.is_valid():
                username = form.cleaned_data.get("username")
                try:
                    user = get_user_model().objects.get(username=username)
                    if user.is_active:
                        request.session["user_id"] = user.id
                        # gestion du token de session
                        # On le recupere ou renevouvel
                        token, created = TokenValidation.objects.update_or_create(
                            user=user, defaults={"token": get_random_string(32)}
                        )
                        request.session["token"] = token.token

                        email = User.objects.get(username=username).email
                        from ..envoi_email import Deux_F_A
                        Deux_F_A(request, email, username)
                        return redirect("connection2")
                    else:
                        messages.error(request, "Votre compte n'est pas actif ou inexistant.")
                        return redirect("connection1")
                except get_user_model().DoesNotExist:
                    messages.error(request, "Utilisateur introuvable.")
                    return redirect("connection1")
        return form
