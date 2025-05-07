from django.contrib import admin
from django.urls import path
from main import views as main_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import logout
from django.urls import re_path
from django.views.static import serve
from .code import UserCreateView , activation, CustomPasswordResetView , CustomResetPasswordConfirmView


urlpatterns = [

    path("admin/", admin.site.urls),
    path("moderation/", main_views.Fait_Ton_Taff_De_Modo, name="moderation_email"),

    path("", main_views.accueil, name="index"),

    path("contact/", main_views.Contact, name="_contact"),
    path("faq/", main_views.mentions_legales, name="_faq"),

    path("inscription/", UserCreateView.as_view(), name="inscription"),
    path("activation/<token>/<uidb64>/", activation, name="activation"),

    path("connection1/", main_views.connection1, name="connection1"),
    path("connection2/", main_views.connection2, name="connection2"),
    path("logout/", main_views.logout_view, name="logout"),

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

    path("monprofile/", main_views.MonCompte, name="MonCompte"),
    path("reservation/", main_views.SelectionTrajet, name="reservation"),
    path(
        "Confirmation/<int:trajet_id>/<str:token>/",
        main_views.AvisSatisfaction,
        name="AvisSatisfaction",
    ),
]
urlpatterns += [
    re_path(r'^google59ae742b6eee40ef\.html$', serve, {'document_root': settings.STATIC_ROOT, 'path': 'google59ae742b6eee40ef.html'}),
    re_path(r'^sitemap\.xml$', serve, {'document_root': settings.STATIC_ROOT, 'path': 'sitemap.xml'}),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
