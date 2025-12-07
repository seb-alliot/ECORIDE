"""
Tests unitaires pour les modèles ECORIDE
ADAPTÉ AUX VRAIS MODÈLES
Couvre : TrajetProposer, ReservationTrajet, CreditUser, NoteUser, Voiture
"""
from django.test import TestCase
from django.contrib.auth.models import User
from ...models import TrajetProposer, ReservationTrajet, CreditUser, Voiture, NoteUser
from datetime import datetime, timedelta, date, time
from decimal import Decimal
import uuid
import random


class TrajetProposerModelTest(TestCase):
    """Tests pour le modèle TrajetProposer"""

    @classmethod
    def setUpTestData(cls):
        username = f"chauffeur_{uuid.uuid4().hex[:6]}"
        cls.chauffeur = User.objects.create_user(username=username, password="testpass123")
        cls.credit, _ = CreditUser.objects.get_or_create(user=cls.chauffeur, defaults={"credit": Decimal("100.00")})
        int_immat = random.randint(0, 999)
        cls.voiture = Voiture.objects.create(
            user=cls.chauffeur,
            marque="toyota",
            modele="corolla",
            annee=2020,
            type_moteur="essence",
            couleur="bleu",
            immatriculation=f"AB-{str(int_immat).zfill(3)}-CD",
            places="4"  # CharField avec choices
        )

        cls.trajet = TrajetProposer.objects.create(
            chauffeur=cls.chauffeur,
            ville_depart="Paris",
            ville_arrivee="Lyon",
            date=date.today() + timedelta(days=7),
            heure=time(14, 0),  # TimeField
            prix=Decimal("25.00"),
            temps_trajet=timedelta(hours=2, minutes=30),
            places=3,  # IntegerField avec choices
            voiture=cls.voiture,
            etat="Disponible"
        )

    def test_trajet_creation(self):
        """Test de création basique d'un trajet"""
        self.assertEqual(self.trajet.chauffeur, self.chauffeur)
        self.assertEqual(self.trajet.ville_depart, "Paris")
        self.assertEqual(self.trajet.ville_arrivee, "Lyon")
        self.assertEqual(self.trajet.places, 3)
        self.assertEqual(self.trajet.etat, "Disponible")

    def test_trajet_str_method(self):
        """Test de la méthode __str__ du trajet"""
        expected = f"{self.trajet.ville_depart} -> {self.trajet.ville_arrivee} {self.trajet.date} {self.trajet.heure}"
        self.assertEqual(str(self.trajet), expected)

    def test_trajet_prix_positif(self):
        """Test que le prix est positif"""
        self.assertGreater(self.trajet.prix, 0)

    def test_trajet_places_positives(self):
        """Test que le nombre de places est positif"""
        self.assertGreater(self.trajet.places, 0)
        # Ne peut pas comparer avec voiture.places car c'est un CharField
        self.assertLessEqual(self.trajet.places, 6)

    def test_trajet_date_future(self):
        """Test que la date du trajet est dans le futur ou aujourd'hui"""
        self.assertGreaterEqual(self.trajet.date, date.today())

    def test_trajet_update_etat(self):
        """Test de modification de l'état d'un trajet"""
        self.trajet.etat = "Terminé"
        self.trajet.save()
        trajet_updated = TrajetProposer.objects.get(id=self.trajet.id)
        self.assertEqual(trajet_updated.etat, "Terminé")

    def test_trajet_total_payer_initial(self):
        """Test que total_payer est initialisé à 0"""
        self.assertEqual(self.trajet.total_payer, Decimal("0.00"))


class ReservationTrajetModelTest(TestCase):
    """Tests pour le modèle ReservationTrajet"""

    @classmethod
    def setUpTestData(cls):
        # Chauffeur
        chauffeur_username = f"chauffeur_{uuid.uuid4().hex[:6]}"
        cls.chauffeur = User.objects.create_user(username=chauffeur_username, password="testpass123")
        cls.credit_chauffeur, _ = CreditUser.objects.get_or_create(
            user=cls.chauffeur,
            defaults={"credit": Decimal("100.00")}
        )

        # Passager
        passager_username = f"passager_{uuid.uuid4().hex[:6]}"
        cls.passager = User.objects.create_user(username=passager_username, password="testpass123")
        cls.credit_passager, _ = CreditUser.objects.get_or_create(
            user=cls.passager,
            defaults={"credit": Decimal("200.00")}
        )
        int_immat = random.randint(0, 999)
        # Voiture
        cls.voiture = Voiture.objects.create(
            user=cls.chauffeur,
            marque="renault",
            modele="clio",
            annee=2019,
            type_moteur="diesel",
            couleur="rouge",
            immatriculation=f"CD-{str(int_immat).zfill(3)}-EF",
            places="4"
        )

        # Trajet
        cls.trajet = TrajetProposer.objects.create(
            chauffeur=cls.chauffeur,
            ville_depart="Marseille",
            ville_arrivee="Nice",
            date=date.today() + timedelta(days=5),
            heure=time(10, 0),
            prix=Decimal("30.00"),
            temps_trajet=timedelta(hours=1, minutes=30),
            places=3,
            voiture=cls.voiture,
            etat="Disponible"
        )

        # Réservation
        cls.reservation = ReservationTrajet.objects.create(
            trajet_reserver=cls.trajet,
            passager=cls.passager,
            places=2,
            prix_par_passager=Decimal("30.00"),
            etat_reservation="Reserver"  # Valeur correcte selon ton modèle
        )

    def test_reservation_creation(self):
        """Test de création d'une réservation"""
        self.assertEqual(self.reservation.trajet_reserver, self.trajet)
        self.assertEqual(self.reservation.passager, self.passager)
        self.assertEqual(self.reservation.places, 2)
        self.assertEqual(self.reservation.etat_reservation, "Reserver")

    def test_reservation_prix_calcul(self):
        """Test du calcul du prix total de la réservation"""
        prix_total = self.reservation.places * self.trajet.prix
        self.assertEqual(prix_total, Decimal("60.00"))

    def test_reservation_str_method(self):
        """Test de la méthode __str__ de la réservation"""
        expected = f"{self.reservation.passager} a réservé {self.reservation.places} places pour le trajet {self.reservation.trajet_reserver}d'un montant de {self.reservation.prix_par_passager} €"
        self.assertEqual(str(self.reservation), expected)

    def test_reservation_places_disponibles(self):
        """Test que les places réservées ne dépassent pas les places disponibles"""
        self.assertLessEqual(self.reservation.places, self.trajet.places)

    def test_reservation_update_etat(self):
        """Test de modification de l'état d'une réservation"""
        self.reservation.etat_reservation = "Annulé"
        self.reservation.save()
        reservation_updated = ReservationTrajet.objects.get(id=self.reservation.id)
        self.assertEqual(reservation_updated.etat_reservation, "Annulé")

    def test_reservation_etat_paiement_default(self):
        """Test que l'état de paiement par défaut est 'Payer'"""
        self.assertEqual(self.reservation.etat_paiement, "Payer")


class CreditUserModelTest(TestCase):
    """Tests pour le modèle CreditUser"""

    @classmethod
    def setUpTestData(cls):
        username = f"user_{uuid.uuid4().hex[:6]}"
        cls.user = User.objects.create_user(username=username, password="testpass123")
        cls.credit_user = CreditUser.objects.get(user=cls.user)

    def test_credit_creation(self):
        """Test de création d'un crédit utilisateur"""
        self.assertEqual(self.credit_user.user, self.user)
        # 20 crédit ajouté via le signals de création de l'utilisateur
        self.assertEqual(self.credit_user.credit, Decimal("20.00"))

    def test_credit_positif(self):
        """Test que le crédit est positif"""
        self.assertGreaterEqual(self.credit_user.credit, 0)

    def test_credit_update(self):
        """Test de mise à jour du crédit"""
        self.credit_user.credit = Decimal("100.00")
        self.credit_user.save()
        credit_updated = CreditUser.objects.get(user=self.user)
        self.assertEqual(credit_updated.credit, Decimal("100.00"))

    def test_credit_debit(self):
        """Test de débit du crédit"""
        montant_initial = self.credit_user.credit
        self.credit_user.credit -= Decimal("20.00")
        self.credit_user.save()
        self.assertEqual(self.credit_user.credit, montant_initial - Decimal("20.00"))

    def test_credit_str_method(self):
        """Test de la méthode __str__ du crédit"""
        expected = f"Solde de {self.user.username}: {self.credit_user.credit} €"
        self.assertEqual(str(self.credit_user), expected)

    def test_credit_add_credit_method(self):
        """Test de la méthode add_credit"""
        credit_avant = self.credit_user.credit
        result = self.credit_user.add_credit(Decimal("25.00"))
        self.assertEqual(self.credit_user.credit, credit_avant + Decimal("25.00"))
        self.assertIn("Crédit ajouté", result)


class VoitureModelTest(TestCase):
    """Tests pour le modèle Voiture"""

    @classmethod
    def setUpTestData(cls):
        username = f"proprietaire_{uuid.uuid4().hex[:6]}"
        cls.proprietaire = User.objects.create_user(username=username, password="testpass123")
        int_immat = random.randint(0, 999)
        cls.voiture = Voiture.objects.create(
            user=cls.proprietaire,
            marque="peugeot",
            modele="308",
            annee=2021,
            type_moteur="Hybride",
            couleur="gris_clair",
            immatriculation=f"EF-{str(int_immat).zfill(3)}-GH",
            places="5"  #
        )

    def test_voiture_creation(self):
        """Test de création d'une voiture"""
        self.assertEqual(self.voiture.user, self.proprietaire)
        self.assertEqual(self.voiture.marque, "peugeot")
        self.assertEqual(self.voiture.modele, "308")
        self.assertEqual(self.voiture.places, "5")

    def test_voiture_annee_valide(self):
        """Test que l'année est valide"""
        self.assertGreaterEqual(self.voiture.annee, 1950)
        self.assertLessEqual(self.voiture.annee, datetime.now().year)

    def test_voiture_str_method(self):
        """Test de la méthode __str__ de la voiture"""
        expected = f"{self.voiture.marque} {self.voiture.modele}"
        self.assertEqual(str(self.voiture), expected)

    def test_voiture_type_moteur_valide(self):
        """Test que le type de moteur est dans les choix valides"""
        types_valides = ["Electrique", "Hybride", "essence", "diesel"]
        self.assertIn(self.voiture.type_moteur, types_valides)

    def test_voiture_places_valide(self):
        """Test que le nombre de places est dans les choix valides"""
        places_valides = ["1", "2", "3", "4", "5", "6"]
        self.assertIn(self.voiture.places, places_valides)


class NoteUserModelTest(TestCase):
    """Tests pour le modèle NoteUser"""

    @classmethod
    def setUpTestData(cls):
        # Chauffeur
        chauffeur_username = f"chauffeur_{uuid.uuid4().hex[:6]}"
        cls.chauffeur = User.objects.create_user(username=chauffeur_username, password="testpass123")

        # Passager
        passager_username = f"passager_{uuid.uuid4().hex[:6]}"
        cls.passager = User.objects.create_user(username=passager_username, password="testpass123")
        int_immat = random.randint(0, 999)
        # Voiture et trajet
        cls.voiture = Voiture.objects.create(
            user=cls.chauffeur,
            marque="citroen",
            modele="c3",
            annee=2020,
            type_moteur="essence",
            couleur="blanc",
            immatriculation=f"GH-{str(int_immat).zfill(3)}-IJ",
            places="4"
        )

        cls.trajet = TrajetProposer.objects.create(
            chauffeur=cls.chauffeur,
            ville_depart="Toulouse",
            ville_arrivee="Bordeaux",
            date=date.today() + timedelta(days=3),
            heure=time(9, 0),
            prix=Decimal("20.00"),
            temps_trajet=timedelta(hours=1),
            places=3,
            voiture=cls.voiture,
            etat="Terminé"
        )

        # Note
        cls.note = NoteUser.objects.create(
            passager=cls.passager,
            chauffeur=cls.chauffeur,
            trajet=cls.trajet,
            avis="oui",
            note=Decimal("5.0"),
            commentaire="Excellent trajet !",
            avis_donne=True,
            note_attribuee=True,
            commentaire_attribuee=True
        )

    def test_note_creation(self):
        """Test de création d'une note"""
        self.assertEqual(self.note.passager, self.passager)
        self.assertEqual(self.note.chauffeur, self.chauffeur)
        self.assertEqual(self.note.trajet, self.trajet)
        self.assertEqual(self.note.avis, "oui")
        self.assertEqual(self.note.note, Decimal("5.0"))

    def test_note_valeur_valide(self):
        """Test que la note est entre 1 et 5"""
        self.assertGreaterEqual(self.note.note, Decimal("1.0"))
        self.assertLessEqual(self.note.note, Decimal("5.0"))

    def test_note_avis_valide(self):
        """Test que l'avis est 'oui' ou 'non' ou ''"""
        self.assertIn(self.note.avis, ["oui", "non", ""])

    def test_note_str_method(self):
        """Test de la méthode __str__ de la note"""
        expected = f"Note de {self.note.chauffeur}: {self.note.note} {self.note.commentaire} {self.note.avis} "
        self.assertEqual(str(self.note), expected)

    def test_note_booleens_default(self):
        """Test des valeurs booléennes par défaut"""
        # Créer un nouveau trajet pour éviter la contrainte unique
        nouveau_trajet = TrajetProposer.objects.create(
            chauffeur=self.chauffeur,
            ville_depart="Bordeaux",
            ville_arrivee="Toulouse",
            date=date.today() + timedelta(days=5),
            heure=time(10, 0),
            prix=Decimal("25.00"),
            temps_trajet=timedelta(hours=1, minutes=30),
            places=3,
            voiture=self.voiture,
            etat="Terminé"
        )

        nouvelle_note = NoteUser.objects.create(
            passager=self.passager,
            chauffeur=self.chauffeur,
            trajet=nouveau_trajet,  # Utiliser le nouveau trajet
            avis="non"
        )
        self.assertFalse(nouvelle_note.note_attribuee)
        self.assertFalse(nouvelle_note.avis_donne)
        self.assertFalse(nouvelle_note.commentaire_attribuee)

    def test_note_unique_together(self):
        """Test que la contrainte unique_together fonctionne"""
        with self.assertRaises(Exception):
            NoteUser.objects.create(
                passager=self.passager,
                chauffeur=self.chauffeur,
                trajet=self.trajet,  # Même combinaison
                avis="oui",
                note=Decimal("4.0")
            )