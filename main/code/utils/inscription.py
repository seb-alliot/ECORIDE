import re
from django.contrib.auth.tokens import default_token_generator
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.utils.http import urlsafe_base64_encode
from django.views.generic.edit import CreateView
from django.template.loader import render_to_string
from ...models import ChoixRole, CreditUser, ActivationToken, User
from ...forms import Inscription

class UserCreateView(CreateView):
    model = User
    form_class = Inscription
    template_name = "inscription/inscription.html"
    success_url = reverse_lazy("index")

    # utilisation de dispatch car vue generique
    # opere avant le traitement de la requete get ou post
    # permet de rediriger l'utilisateur vers la page d'accueil s'il est déjà connecté
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("index")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            ChoixRole.objects.create(role="passager", user=user)
            CreditUser.objects.create(user=user)

            uidb64 = urlsafe_base64_encode(str(user.pk).encode("utf-8"))
            token = default_token_generator.make_token(user)
            ActivationToken.objects.create(user=user, token=token)

            activation_url = self.request.build_absolute_uri(
                reverse("activation", kwargs={"token": token, "uidb64": uidb64})
            )
            self.send_activation_email(user, uidb64, activation_url)

            messages.success(self.request, "Votre compte a été créé avec succès.")
            return redirect(self.success_url)
        except Exception as e:
            messages.error(self.request, f"Une erreur est survenue : {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        username = self.request.POST.get("username")
        email = self.request.POST.get("email")
        password1 = self.request.POST.get("password1")
        password2 = self.request.POST.get("password2")

        if username and User.objects.filter(username=username).exists():
            messages.error(self.request, "Ce nom d'utilisateur est déjà pris.")

        if email and User.objects.filter(email=email).exists():
            messages.error(self.request, "Cette adresse e-mail est déjà utilisée.")

        if password1 and password2:
            if password1 != password2:
                messages.error(self.request, "Les mots de passe ne correspondent pas.")
            elif not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$", password1):
                messages.error(
                    self.request,
                    "Le mot de passe doit comporter au moins 8 caractères, avec une majuscule, une minuscule, un chiffre et un caractère spécial."
                )

        return super().form_invalid(form)

    def send_activation_email(self, user, uidb64, activation_url):
        subject = "Activation de votre compte EcoRide"
        context = {"user": user, "activation_url": activation_url, "uidb64": uidb64}
        message = render_to_string("style_email/activation_email.html", context)
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email="staff.modo.ecoride@gmail.com",
            to=[user.email],
        )
        email.content_subtype = "html"
        email.send()