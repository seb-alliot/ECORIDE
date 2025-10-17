from django.test import TestCase
from django.contrib.auth.models import User
from ...models import TrajetProposer , CreditUser, Voiture
from datetime import datetime , timedelta
import uuid


class TrajetProposerTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Crée un utilisateur unique pour le chauffeur
        username = f"chauffeur_test_{uuid.uuid4().hex[:6]}"
        cls.chauffeur = User.objects.create_user(username=username, password="1234")

        credits, created = CreditUser.objects.get_or_create(user=cls.chauffeur, defaults={"credit": 100.00})
        voiture = Voiture.objects.create(
            user=cls.chauffeur,
            marque="Toyota",
            modele="Corolla",
            annee=2020,
            type_moteur="essence",
            couleur="Bleu",
            immatriculation="AB-123-CD"
        )
        # Crée un trajet proposé pour ce chauffeur
        cls.trajet = TrajetProposer.objects.create(
            chauffeur=cls.chauffeur,
            date=datetime.now(),
            prix=20.00,
            temps_trajet=timedelta(minutes=30),
            places=3,
            voiture=voiture
        )

    def test_relation_chauffeur(self):
        self.assertEqual(self.trajet.chauffeur.username, self.chauffeur.username)

    def test_update_prix(self):
        self.trajet.prix = 25.00
        self.trajet.save()
        self.assertEqual(TrajetProposer.objects.get(id=self.trajet.id).prix, 25.00)