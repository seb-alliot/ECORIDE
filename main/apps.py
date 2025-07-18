from django.apps import AppConfig

class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"

    def ready(self):
        import main.code.signals.suppression_user
        import main.code.signals.debit_commission
        import main.code.signals.creation_user
        import main.code.signals.debit_reservation
        import main.code.signals.crediter_annulation
        import main.code.signals.crediter_passager_chauffeur
        import main.code.signals.suppression_doc_mongo_vue
