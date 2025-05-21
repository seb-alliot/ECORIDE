from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"


    def ready(self):
        import main.signals.suppression_user
        import main.signals.debit_commission
        import main.signals.creation_user
        import main.signals.debit_reservation
        import main.signals.crediter_annulation
        import main.signals.crediter_passager_chauffeur
