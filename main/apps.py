from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"


class utilisateurConfig(AppConfig):
    name = "utilisateur"

    def ready(self):
        import signals
