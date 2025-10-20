from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib import messages
from ....models import User
from ....forms import ConfirmEmailForm

class CustomPasswordResetView(PasswordResetView):
    form_class = ConfirmEmailForm
    template_name = "réinitialisation/password_reset_form.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        try:
            user = User.objects.get(email=email)
            self.user = user
            messages.success(self.request, "Un email de réinitialisation a été envoyé.")
        except User.DoesNotExist:
            messages.error(self.request, "Aucun utilisateur trouvé avec cet email.")

        return super().form_valid(form)