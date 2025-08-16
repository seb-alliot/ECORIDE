from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main.backend"

    def ready(self):
        import main.backend.code.signals.suppression_user
        import main.backend.code.signals.debit_commission
        import main.backend.code.signals.creation_user
        import main.backend.code.signals.debit_reservation
        import main.backend.code.signals.crediter_annulation
        import main.backend.code.signals.crediter_passager_chauffeur
        import main.backend.code.signals.suppression_doc_mongo_vue
