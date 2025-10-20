from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetConfirmView
from ....forms import CustomSetPasswordForm


class CustomResetPasswordConfirmView(PasswordResetConfirmView):
    form_class = CustomSetPasswordForm
    template_name = "réinitialisation/password_reset_confirm.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        messages.success(self.request, "Votre mot de passe a été changé.")
        return super().form_valid(form)