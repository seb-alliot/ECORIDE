from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import admin

from .code import (
    UserCreateView,
    activation,
    CustomPasswordResetView,
    CustomResetPasswordConfirmView,
    annuler_trajet,
    filtre_dynamique,
    get_modeles_voiture,
    voiture_chauffeur,
)
from . import views



urlpatterns = [
    path("admin/",admin.site.urls),
    path("moderation/", views.Fait_Ton_Taff_De_Modo, name="moderation_email"),
    path("", views.accueil, name="index"),

    path("contact/", views.Contact, name="_contact"),
    path("faq/", views.Faq, name="_faq"),
    path("rgpd/", views.rgpd, name="_rgpd"),
    path("mentions_legales/", views.mentions_legales, name="_mentions_legales"),

    path("inscription/", UserCreateView.as_view(), name="inscription"),
    path("activation/<token>/<uidb64>/", activation, name="activation"),

    path("connection1/", views.connection1, name="connection1"),
    path("connection2/", views.connection2, name="connection2"),
    path("logout/", views.logout_view, name="logout"),

    path("password_reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "reset/<uidb64>/<token>/",
        CustomResetPasswordConfirmView.as_view(),
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
    path(
        "Confirmation/<int:trajet_id>/<str:token>/",
        views.AvisSatisfaction,
        name="AvisSatisfaction",
    ),
    path("monprofile/", views.MonCompte, name="MonCompte"),
    path("reservation/", views.SelectionTrajet, name="reservation"),

    # vue ajax
    path("annuler_trajet5", annuler_trajet, name="annuler_trajet5"),
    path("filtre_dynamique", filtre_dynamique, name="filtre_dynamique"),
    path("model-voiture/", get_modeles_voiture, name="model_voiture"),
    path("voiture-chauffeur/", voiture_chauffeur, name="voiture_chauffeur"),
]
