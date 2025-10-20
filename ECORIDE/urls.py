from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import include

urlpatterns = [
    path("", include("..main.backend.urls")),
]
