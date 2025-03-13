from django.contrib import admin
from django.urls import include, path
from main import views as main_views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import logout


urlpatterns = [
    # main
    # moderation
    path("admin/", admin.site.urls),
    path("moderation/", main_views.Fait_Ton_Taff_De_Modo, name="moderation_email"),
    # UTILISATEURS
    # Création de compte
    path("", main_views.accueil, name="index"),
    path("contact/", main_views.Contact, name="_contact"),
    path("faq/", main_views.mentions_legales, name="_faq"),
    path("inscription/", main_views.UserCreateView.as_view(), name="inscription"),
    path("activation/<token>/<uidb64>/", main_views.activation, name="activation"),
    # connexion en 2 étapes
    path("connection1/", main_views.connection1, name="connection1"),
    path("connection2/", main_views.connection2, name="connection2"),
    path("logout/", main_views.logout_view, name="logout"),
    # 1ère étape: envoi d'un email en validant l'email
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy("index"),
            form_class=main_views.ConfirmEmailForm,
            template_name="réinitialisation/password_reset_form.html",
        ),
        name="password_reset",
    ),
    # 2ème étape: Changement du mot de passe via le lien de l'étape 1
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy("index"),
            form_class=main_views.CustomSetPasswordForm,
            template_name="réinitialisation/password_reset_confirm.html",
        ),
        name="password_reset_confirm",
    ),
    path(
        "password_reset_done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset_done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Mon compte
    path("monprofile/", main_views.MonCompte, name="MonCompte"),
    # réservation de trajet
    path("reservation/", main_views.SelectionTrajet, name="reservation"),
    path(
        "Confirmation/<int:trajet_id>/<str:token>/",
        main_views.AvisSatisfaction,
        name="AvisSatisfaction",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
