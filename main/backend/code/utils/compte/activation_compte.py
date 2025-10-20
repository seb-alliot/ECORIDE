from django.contrib import messages
from django.shortcuts import redirect
from django.utils.http import urlsafe_base64_decode
from ....models import ActivationToken

def activation(request, uidb64, token):
    try:
        user = urlsafe_base64_decode(uidb64).decode("utf-8")
        activation_token = ActivationToken.objects.get(token=token)
        user = activation_token.user

        if activation_token.is_expired():
            activation_token.delete()
            messages.error(request, "Le lien a expiré.")
            return redirect("inscription")
        user.is_active = True
        user.save()
        activation_token.delete()
        messages.success(request, "Votre compte a été activé.")
        return redirect("connection1")
    except ActivationToken.DoesNotExist:
        messages.error(request, "Une erreur est survenue.")
        return redirect("inscription")