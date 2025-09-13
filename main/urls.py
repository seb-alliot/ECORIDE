from django.urls import path, include
from main.backend import views as main_views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.static import serve

urlpatterns = [

    path("", main_views.accueil, name="index"),
    path("ECORIDE/", include("main.backend.urls")),
]
urlpatterns += [
    re_path(r'^google59ae742b6eee40ef\.html$', serve, {'document_root': settings.STATIC_ROOT, 'path': 'google59ae742b6eee40ef.html'}),
    re_path(r'^sitemap\.xml$', serve, {'document_root': settings.STATIC_ROOT, 'path': 'sitemap.xml'}),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
