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
sebastien, _ = User.objects.get_or_create(username="sebastien")

# Récupérer ou créer le crédit
credit, created = CreditUser.objects.get_or_create(user=sebastien)

# Ajouter du crédit
credit.add_credit(1000000)

print(f"Le nouveau solde de Sebastien est de : {credit.credit} €")
