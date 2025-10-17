from django.test import TestCase
from django.contrib.auth.models import User
from main.backend.models import CreditUser
import uuid

class CreditUserTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Crée un utilisateur unique
        username = f"user_test_{uuid.uuid4().hex[:6]}"
        cls.user = User.objects.create_user(username=username, password="1234")

        # Crée CreditUser uniquement si il n'existe pas encore pour cet utilisateur
        cls.credit_user, created = CreditUser.objects.get_or_create(user=cls.user, defaults={"credit": 50.00})

    def test_relation_user(self):
        self.assertEqual(self.credit_user.user.username, self.user.username)

    def test_update_credit(self):
        self.credit_user.credit = 100.00
        self.credit_user.save()
        self.assertEqual(CreditUser.objects.get(user=self.user).credit, 100.00)
