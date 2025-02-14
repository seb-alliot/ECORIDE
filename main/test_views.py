from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages import get_messages

from main.models import (
    AdresseUser,
    ChoixRole,
    Preference,
    TrajetProposer,
    Voiture,
    ReservationTrajet,
    CreditUser,
)
from main.forms import (
    AdresseForm,
    PreferenceForm,
    ChoixRoleForm,
    VoitureForm,
    TrajetForm,
    StatutTrajetForm,
    FiltreTrajetForm,
    RechercheTrajetForm,
)


class MonCompteViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")
        self.url = reverse("MonCompte")

    def test_mon_compte_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "interface_utilisateur/utilisateur/MonCompte.html"
        )

    def test_mon_compte_post_adresse_form(self):
        adresse_user = AdresseUser.objects.create(user=self.user, adresse="123 Street")
        data = {"form_soumis": "adresse_form", "adresse": "456 Avenue"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Vos informations  été mis à jour.")

    def test_mon_compte_post_role_form(self):
        data = {"form_soumis": "role_form", "role": "chauffeur"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Votre rôle a été enregistré.")

    def test_mon_compte_post_preference_form(self):
        data = {"form_soumis": "preference_form", "preference": "non-fumeur"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Vos préférences ont été enregistrées.")

    def test_mon_compte_post_voiture_form(self):
        data = {"form_soumis": "voiture_form", "marque": "Toyota", "modele": "Corolla"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Votre véhicule a bien été ajouté.")

    def test_mon_compte_post_trajet_form(self):
        CreditUser.objects.create(user=self.user, credit=10)
        data = {
            "form_soumis": "trajet_form",
            "ville_depart": "Paris",
            "ville_arrivee": "Lyon",
            "date": "2023-12-31",
            "prix": 20,
            "places": 3,
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Votre covoiturage a été ajouté avec succé")

    def test_mon_compte_post_etat_form(self):
        trajet = TrajetProposer.objects.create(
            chauffeur=self.user,
            ville_depart="Paris",
            ville_arrivee="Lyon",
            date="2023-12-31",
            prix=20,
            places=3,
        )
        data = {"form_soumis": "etat_form", "trajet_id": trajet.id, "statut": "Terminé"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Trajet terminé avec succès.")
        from main.models import (
            AdresseUser,
            ChoixRole,
            Preference,
            TrajetProposer,
            Voiture,
            ReservationTrajet,
            CreditUser,
        )
        from main.forms import (
            AdresseForm,
            PreferenceForm,
            ChoixRoleForm,
            VoitureForm,
            TrajetForm,
            StatutTrajetForm,
            FiltreTrajetForm,
            RechercheTrajetForm,
        )

        class MonCompteViewTests(TestCase):
            def setUp(self):
                self.client = Client()
                self.user = User.objects.create_user(
                    username="testuser", password="12345"
                )
                self.client.login(username="testuser", password="12345")
                self.url = reverse("MonCompte")

            def test_mon_compte_get(self):
                response = self.client.get(self.url)
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(
                    response, "interface_utilisateur/utilisateur/MonCompte.html"
                )

            def test_mon_compte_post_adresse_form(self):
                adresse_user = AdresseUser.objects.create(
                    user=self.user, adresse="123 Street"
                )
                data = {"form_soumis": "adresse_form", "adresse": "456 Avenue"}
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, self.url)
                messages = list(get_messages(response.wsgi_request))
                self.assertEqual(str(messages[0]), "Vos informations  été mis à jour.")

            def test_mon_compte_post_role_form(self):
                data = {"form_soumis": "role_form", "role": "chauffeur"}
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, self.url)
                messages = list(get_messages(response.wsgi_request))
                self.assertEqual(str(messages[0]), "Votre rôle a été enregistré.")

            def test_mon_compte_post_preference_form(self):
                data = {"form_soumis": "preference_form", "preference": "non-fumeur"}
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, self.url)
                messages = list(get_messages(response.wsgi_request))
                self.assertEqual(
                    str(messages[0]), "Vos préférences ont été enregistrées."
                )

            def test_mon_compte_post_voiture_form(self):
                data = {
                    "form_soumis": "voiture_form",
                    "marque": "Toyota",
                    "modele": "Corolla",
                }
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, self.url)
                messages = list(get_messages(response.wsgi_request))
                self.assertEqual(str(messages[0]), "Votre véhicule a bien été ajouté.")

            def test_mon_compte_post_trajet_form(self):
                CreditUser.objects.create(user=self.user, credit=10)
                data = {
                    "form_soumis": "trajet_form",
                    "ville_depart": "Paris",
                    "ville_arrivee": "Lyon",
                    "date": "2023-12-31",
                    "prix": 20,
                    "places": 3,
                }
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, self.url)
                messages = list(get_messages(response.wsgi_request))
                self.assertEqual(
                    str(messages[0]), "Votre covoiturage a été ajouté avec succé"
                )

            def test_mon_compte_post_etat_form(self):
                trajet = TrajetProposer.objects.create(
                    chauffeur=self.user,
                    ville_depart="Paris",
                    ville_arrivee="Lyon",
                    date="2023-12-31",
                    prix=20,
                    places=3,
                )
                data = {
                    "form_soumis": "etat_form",
                    "trajet_id": trajet.id,
                    "statut": "Terminé",
                }
                response = self.client.post(self.url, data)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, self.url)
                messages = list(get_messages(response.wsgi_request))
                self.assertEqual(str(messages[0]), "Trajet terminé avec succès.")
                from main.models import (
                    AdresseUser,
                    ChoixRole,
                    Preference,
                    TrajetProposer,
                    Voiture,
                    ReservationTrajet,
                    CreditUser,
                    ChangerStatutTrajet,
                )
                from main.forms import (
                    AdresseForm,
                    PreferenceForm,
                    ChoixRoleForm,
                    VoitureForm,
                    TrajetForm,
                    StatutTrajetForm,
                    FiltreTrajetForm,
                    RechercheTrajetForm,
                )

                class MonCompteViewTests(TestCase):
                    def setUp(self):
                        self.client = Client()
                        self.user = User.objects.create_user(
                            username="testuser", password="12345"
                        )
                        self.client.login(username="testuser", password="12345")
                        self.url = reverse("MonCompte")

                    def test_mon_compte_get(self):
                        response = self.client.get(self.url)
                        self.assertEqual(response.status_code, 200)
                        self.assertTemplateUsed(
                            response, "interface_utilisateur/utilisateur/MonCompte.html"
                        )

                    def test_mon_compte_post_adresse_form(self):
                        adresse_user = AdresseUser.objects.create(
                            user=self.user, adresse="123 Street"
                        )
                        data = {"form_soumis": "adresse_form", "adresse": "456 Avenue"}
                        response = self.client.post(self.url, data)
                        self.assertEqual(response.status_code, 302)
                        self.assertRedirects(response, self.url)
                        messages = list(get_messages(response.wsgi_request))
                        self.assertEqual(
                            str(messages[0]), "Vos informations  été mis à jour."
                        )

                    def test_mon_compte_post_role_form(self):
                        data = {"form_soumis": "role_form", "role": "chauffeur"}
                        response = self.client.post(self.url, data)
                        self.assertEqual(response.status_code, 302)
                        self.assertRedirects(response, self.url)
                        messages = list(get_messages(response.wsgi_request))
                        self.assertEqual(
                            str(messages[0]), "Votre rôle a été enregistré."
                        )

                    def test_mon_compte_post_preference_form(self):
                        data = {
                            "form_soumis": "preference_form",
                            "preference": "non-fumeur",
                        }
                        response = self.client.post(self.url, data)
                        self.assertEqual(response.status_code, 302)
                        self.assertRedirects(response, self.url)
                        messages = list(get_messages(response.wsgi_request))
                        self.assertEqual(
                            str(messages[0]), "Vos préférences ont été enregistrées."
                        )

                    def test_mon_compte_post_voiture_form(self):
                        data = {
                            "form_soumis": "voiture_form",
                            "marque": "Toyota",
                            "modele": "Corolla",
                        }
                        response = self.client.post(self.url, data)
                        self.assertEqual(response.status_code, 302)
                        self.assertRedirects(response, self.url)
                        messages = list(get_messages(response.wsgi_request))
                        self.assertEqual(
                            str(messages[0]), "Votre véhicule a bien été ajouté."
                        )

                    def test_mon_compte_post_trajet_form(self):
                        CreditUser.objects.create(user=self.user, credit=10)
                        data = {
                            "form_soumis": "trajet_form",
                            "ville_depart": "Paris",
                            "ville_arrivee": "Lyon",
                            "date": "2023-12-31",
                            "prix": 20,
                            "places": 3,
                        }
                        response = self.client.post(self.url, data)
                        self.assertEqual(response.status_code, 302)
                        self.assertRedirects(response, self.url)
                        messages = list(get_messages(response.wsgi_request))
                        self.assertEqual(
                            str(messages[0]),
                            "Votre covoiturage a été ajouté avec succé",
                        )

                    def test_mon_compte_post_etat_form(self):
                        trajet = TrajetProposer.objects.create(
                            chauffeur=self.user,
                            ville_depart="Paris",
                            ville_arrivee="Lyon",
                            date="2023-12-31",
                            prix=20,
                            places=3,
                        )
                        data = {
                            "form_soumis": "etat_form",
                            "trajet_id": trajet.id,
                            "statut": "Terminé",
                        }
                        response = self.client.post(self.url, data)
                        self.assertEqual(response.status_code, 302)
                        self.assertRedirects(response, self.url)
                        messages = list(get_messages(response.wsgi_request))
                        self.assertEqual(
                            str(messages[0]), "Trajet terminé avec succès."
                        )
                        from main.models import (
                            AdresseUser,
                            ChoixRole,
                            Preference,
                            TrajetProposer,
                            Voiture,
                            ReservationTrajet,
                            CreditUser,
                            ChangerStatutTrajet,
                        )
                        from main.forms import (
                            AdresseForm,
                            PreferenceForm,
                            ChoixRoleForm,
                            VoitureForm,
                            TrajetForm,
                            StatutTrajetForm,
                            FiltreTrajetForm,
                            RechercheTrajetForm,
                        )

                        class MonCompteViewTests(TestCase):
                            def setUp(self):
                                self.client = Client()
                                self.user = User.objects.create_user(
                                    username="testuser", password="12345"
                                )
                                self.client.login(username="testuser", password="12345")
                                self.url = reverse("MonCompte")

                            def test_mon_compte_get(self):
                                response = self.client.get(self.url)
                                self.assertEqual(response.status_code, 200)
                                self.assertTemplateUsed(
                                    response,
                                    "interface_utilisateur/utilisateur/MonCompte.html",
                                )

                            def test_mon_compte_post_adresse_form(self):
                                adresse_user = AdresseUser.objects.create(
                                    user=self.user, adresse="123 Street"
                                )
                                data = {
                                    "form_soumis": "adresse_form",
                                    "adresse": "456 Avenue",
                                }
                                response = self.client.post(self.url, data)
                                self.assertEqual(response.status_code, 302)
                                self.assertRedirects(response, self.url)
                                messages = list(get_messages(response.wsgi_request))
                                self.assertEqual(
                                    str(messages[0]),
                                    "Vos informations  été mis à jour.",
                                )

                            def test_mon_compte_post_role_form(self):
                                data = {"form_soumis": "role_form", "role": "chauffeur"}
                                response = self.client.post(self.url, data)
                                self.assertEqual(response.status_code, 302)
                                self.assertRedirects(response, self.url)
                                messages = list(get_messages(response.wsgi_request))
                                self.assertEqual(
                                    str(messages[0]), "Votre rôle a été enregistré."
                                )

                            def test_mon_compte_post_preference_form(self):
                                data = {
                                    "form_soumis": "preference_form",
                                    "preference": "non-fumeur",
                                }
                                response = self.client.post(self.url, data)
                                self.assertEqual(response.status_code, 302)
                                self.assertRedirects(response, self.url)
                                messages = list(get_messages(response.wsgi_request))
                                self.assertEqual(
                                    str(messages[0]),
                                    "Vos préférences ont été enregistrées.",
                                )

                            def test_mon_compte_post_voiture_form(self):
                                data = {
                                    "form_soumis": "voiture_form",
                                    "marque": "Toyota",
                                    "modele": "Corolla",
                                }
                                response = self.client.post(self.url, data)
                                self.assertEqual(response.status_code, 302)
                                self.assertRedirects(response, self.url)
                                messages = list(get_messages(response.wsgi_request))
                                self.assertEqual(
                                    str(messages[0]),
                                    "Votre véhicule a bien été ajouté.",
                                )

                            def test_mon_compte_post_trajet_form(self):
                                CreditUser.objects.create(user=self.user, credit=10)
                                data = {
                                    "form_soumis": "trajet_form",
                                    "ville_depart": "Paris",
                                    "ville_arrivee": "Lyon",
                                    "date": "2023-12-31",
                                    "prix": 20,
                                    "places": 3,
                                }
                                response = self.client.post(self.url, data)
                                self.assertEqual(response.status_code, 302)
                                self.assertRedirects(response, self.url)
                                messages = list(get_messages(response.wsgi_request))
                                self.assertEqual(
                                    str(messages[0]),
                                    "Votre covoiturage a été ajouté avec succé",
                                )

                            def test_mon_compte_post_etat_form(self):
                                trajet = TrajetProposer.objects.create(
                                    chauffeur=self.user,
                                    ville_depart="Paris",
                                    ville_arrivee="Lyon",
                                    date="2023-12-31",
                                    prix=20,
                                    places=3,
                                )
                                data = {
                                    "form_soumis": "etat_form",
                                    "trajet_id": trajet.id,
                                    "statut": "Terminé",
                                }
                                response = self.client.post(self.url, data)
                                self.assertEqual(response.status_code, 302)
                                self.assertRedirects(response, self.url)
                                messages = list(get_messages(response.wsgi_request))
                                self.assertEqual(
                                    str(messages[0]), "Trajet terminé avec succès."
                                )
                                from main.models import (
                                    AdresseUser,
                                    ChoixRole,
                                    Preference,
                                    TrajetProposer,
                                    Voiture,
                                    ReservationTrajet,
                                    CreditUser,
                                    ChangerStatutTrajet,
                                )
                                from main.forms import (
                                    AdresseForm,
                                    PreferenceForm,
                                    ChoixRoleForm,
                                    VoitureForm,
                                    TrajetForm,
                                    StatutTrajetForm,
                                    FiltreTrajetForm,
                                    RechercheTrajetForm,
                                )

                                class MonCompteViewTests(TestCase):
                                    def setUp(self):
                                        self.client = Client()
                                        self.user = User.objects.create_user(
                                            username="testuser", password="12345"
                                        )
                                        self.client.login(
                                            username="testuser", password="12345"
                                        )
                                        self.url = reverse("MonCompte")

                                    def test_mon_compte_get(self):
                                        response = self.client.get(self.url)
                                        self.assertEqual(response.status_code, 200)
                                        self.assertTemplateUsed(
                                            response,
                                            "interface_utilisateur/utilisateur/MonCompte.html",
                                        )

                                    def test_mon_compte_post_adresse_form(self):
                                        adresse_user = AdresseUser.objects.create(
                                            user=self.user, adresse="123 Street"
                                        )
                                        data = {
                                            "form_soumis": "adresse_form",
                                            "adresse": "456 Avenue",
                                        }
                                        response = self.client.post(self.url, data)
                                        self.assertEqual(response.status_code, 302)
                                        self.assertRedirects(response, self.url)
                                        messages = list(
                                            get_messages(response.wsgi_request)
                                        )
                                        self.assertEqual(
                                            str(messages[0]),
                                            "Vos informations  été mis à jour.",
                                        )

                                    def test_mon_compte_post_trajet_form(self):
                                        CreditUser.objects.create(
                                            user=self.user, credit=10
                                        )
                                        data = {
                                            "form_soumis": "trajet_form",
                                            "ville_depart": "Paris",
                                            "ville_arrivee": "Lyon",
                                            "date": "2023-12-31",
                                            "prix": 20,
                                            "places": 3,
                                        }
                                        response = self.client.post(self.url, data)
                                        self.assertEqual(response.status_code, 302)
                                        self.assertRedirects(response, self.url)
                                        messages = list(
                                            get_messages(response.wsgi_request)
                                        )
                                        self.assertEqual(
                                            str(messages[0]),
                                            "Votre covoiturage a été ajouté avec succé",
                                        )

                                    def test_mon_compte_post_etat_form(self):
                                        trajet = TrajetProposer.objects.create(
                                            chauffeur=self.user,
                                            ville_depart="Paris",
                                            ville_arrivee="Lyon",
                                            date="2023-12-31",
                                            prix=20,
                                            places=3,
                                        )
                                        data = {
                                            "form_soumis": "etat_form",
                                            "trajet_id": trajet.id,
                                            "statut": "Terminé",
                                        }
                                        response = self.client.post(self.url, data)
                                        self.assertEqual(response.status_code, 302)
                                        self.assertRedirects(response, self.url)
                                        messages = list(
                                            get_messages(response.wsgi_request)
                                        )
                                        self.assertEqual(
                                            str(messages[0]),
                                            "Trajet terminé avec succès.",
                                        )

                                    def test_mon_compte_post_invalid_adresse_form(self):
                                        data = {
                                            "form_soumis": "adresse_form",
                                            "adresse": "",  # Invalid data
                                        }
                                        response = self.client.post(self.url, data)
                                        self.assertEqual(response.status_code, 200)
                                        messages = list(
                                            get_messages(response.wsgi_request)
                                        )
                                        self.assertEqual(str(messages[0]), "a.")

                                    def test_mon_compte_post_invalid_trajet_form(self):
                                        data = {
                                            "form_soumis": "trajet_form",
                                            "ville_depart": "",
                                            "ville_arrivee": "",
                                            "date": "",
                                            "prix": "",
                                            "places": "",
                                        }
                                        response = self.client.post(self.url, data)
                                        self.assertEqual(response.status_code, 302)
                                        self.assertRedirects(response, self.url)
                                        messages = list(
                                            get_messages(response.wsgi_request)
                                        )
                                        self.assertEqual(
                                            str(messages[0]),
                                            "Une erreur lors de la proposition de covoiturage.",
                                        )

                                    def test_mon_compte_post_invalid_etat_form(self):
                                        trajet = TrajetProposer.objects.create(
                                            chauffeur=self.user,
                                            ville_depart="Paris",
                                            ville_arrivee="Lyon",
                                            date="2023-12-31",
                                            prix=20,
                                            places=3,
                                        )
                                        data = {
                                            "form_soumis": "etat_form",
                                            "trajet_id": trajet.id,
                                            "statut": "",  # Invalid data
                                        }
                                        response = self.client.post(self.url, data)
                                        self.assertEqual(response.status_code, 200)
                                        messages = list(
                                            get_messages(response.wsgi_request)
                                        )
                                        self.assertEqual(
                                            len(messages), 0
                                        )  # No success message should be present

                                    def test_mon_compte_get_recherche_form(self):
                                        data = {
                                            "form_trajet": "recherche_form",
                                            "ville_depart": "Paris",
                                            "ville_arrivee": "Lyon",
                                            "date": "2023-12-31",
                                        }
                                        response = self.client.get(self.url, data)
                                        self.assertEqual(response.status_code, 200)
                                        messages = list(
                                            get_messages(response.wsgi_request)
                                        )
                                        self.assertEqual(
                                            str(messages[0]),
                                            "Recherche effectuée avec succès.",
                                        )

                                    def test_mon_compte_get_filtre_form(self):
                                        trajet = TrajetProposer.objects.create(
                                            chauffeur=self.user,
                                            ville_depart="Paris",
                                            ville_arrivee="Lyon",
                                            date="2023-12-31",
                                            prix=20,
                                            places=3,
                                        )
                                        session = self.client.session
                                        session["resultat_recherche"] = [trajet.id]
                                        session.save()
                                        data = {
                                            "form_trajet": "filtre_form",
                                            "type_moteur": "Essence",
                                            "temps_trajet": "2:00",
                                            "prix": 25,
                                        }
                                        response = self.client.get(self.url, data)
                                        self.assertEqual(response.status_code, 200)
                                        messages = list(
                                            get_messages(response.wsgi_request)
                                        )
                                        self.assertEqual(
                                            str(messages[0]),
                                            "Filtrage effectué avec succès.",
                                        )
