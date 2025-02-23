import os
import django

# Définir le module de paramètres Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ECORIDE.settings")

# Initialiser Django
django.setup()

# Importer les modèles après l'initialisation
from main.models import CreditUser, User
from decimal import Decimal

# Récupérer ou créer l'utilisateur
setsuna, _ = User.objects.get_or_create(username="setsuna")

# Récupérer ou créer le crédit
credit, created = CreditUser.objects.get_or_create(user=setsuna)

# Ajouter du crédit
credit.add_credit(1000000)

print(f"Le nouveau solde de Setsuna est de : {credit.credit} €")
