from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.contrib import messages
from ....forms import MotDePasseForm
from ....models import TokenValidation
from django.shortcuts import redirect

def DeuxiemeEtape(request):
    user = request.user
    if user.is_authenticated:
        return redirect("index")
    else:
        connected_users = request.session.get("connected_users", [])
        user_id = request.session.get("user_id")
        token = request.session.get("token")
        token_connection_session = request.session.get("token_connection")

        if not token:
            return redirect("connection1")

        if request.method == "POST":
            form = MotDePasseForm(request.POST)

            if form.is_valid():
                password = form.cleaned_data["password"]
                token_connection = form.cleaned_data["token_connection"]
                if user_id is None:
                    messages.error(request, "L'identifiant n'a pas étè trouvé.")
                    return redirect("connection1")
            try:
                user = get_user_model().objects.get(id=user_id)
                authenticated_user = authenticate(username=user.username, password=password)
                if authenticated_user:

                    if user_id not in connected_users:
                        connected_users.append(user_id)
                        request.session["connected_users"] = connected_users
                    if token_connection_session != token_connection:
                        messages.error(request, "Code de connexion incorrect.")
                        return redirect("connection2")

                    TokenValidation.objects.filter(user=user).delete()
                    login(request, authenticated_user)
                    request.session.pop("user_id", None)
                    request.session.pop("token", None)

                    messages.info(request, "Vous êtes connecté.")
                    return redirect("index")
                else:
                    messages.error(request, "Vos identifiants sont érronés.")
                    return redirect("connection2")
            except get_user_model().DoesNotExist:
                messages.error(request, "Vos identifiants sont érronés.")
                return redirect("connection1")
        else:
            form = MotDePasseForm()
        return form