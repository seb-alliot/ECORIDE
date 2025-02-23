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
ITSUKI, _ = User.objects.get_or_create(username="ITSUKI")

# Récupérer ou créer le crédit
credit, created = CreditUser.objects.get_or_create(user=ITSUKI)

# Ajouter du crédit
credit.add_credit(0)

print(f"Le nouveau solde de ITSUKI est de : {credit.credit} €, ils dois bosser se fainéant")
