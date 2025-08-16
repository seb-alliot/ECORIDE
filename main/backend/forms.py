from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth.models import User
from datetime import datetime
import re
from django.core.exceptions import ValidationError
from main.backend.models import (
    TrajetProposer,
    Voiture,
    ChoixRole,
    Preference,
    AdresseUser,
    ReservationTrajet,
    NoteUser,
)
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import timedelta
from django.forms import widgets

# --------------------- Gestion des utilisateurs -------------------->


class Inscription(UserCreationForm):
    username = forms.CharField(
        max_length=20,
        label="Identifiant",
        widget=forms.TextInput(attrs={"placeholder": "Identifiant"}),
        required=True,
    )
    email = forms.EmailField(
        max_length=100,
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
        required=True,
    )
    password1 = forms.CharField(
        max_length=20,
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"placeholder": "Mot de passe"}),
        required=True,
    )
    password2 = forms.CharField(
        max_length=20,
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={"placeholder": "Mot de passe"}),
        required=True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Cet identifiant est déjà utilisé.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")

        return cleaned_data


class IdentifiantForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        label="Identifiant",
        widget=forms.TextInput(attrs={"placeholder": "Identifiant"}),
        required=True,
    )

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("Cet identifiant n'existe pas.")
        return username


class MotDePasseForm(forms.Form):
    password = forms.CharField(
        max_length=128,
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={"placeholder": "Mot de passe"}),
        required=True,
    )
    token_connection = forms.CharField(
        max_length=128,
        label="Token de connexion",
        widget=forms.TextInput(attrs={"placeholder": "Code de connexion"}),
        required=True,
    )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$", password):
            raise forms.ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères, une lettre majuscule, une lettre minuscule et un chiffre."
            )
        return password


class ConfirmEmailForm(PasswordResetForm):
    email = forms.EmailField(
        max_length=100,
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
        required=True,
    )

    def clean_email(self):
        email = self.cleaned_data.get("email").strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email n'existe pas.")
        return email


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update(
            {"placeholder": "New password"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"placeholder": "New password"}
        )


# ---------------------------- Gestion des trajets ---------------------------->


class TrajetForm(forms.ModelForm):
    class Meta:
        model = TrajetProposer
        fields = [
            "ville_depart",
            "ville_arrivee",
            "date",
            "heure",
            "places",
            "prix",
            "voiture",
            "temps_trajet",
        ]
        widgets = {
            "ville_depart": forms.TextInput(attrs={"placeholder": "Départ de"}),
            "ville_arrivee": forms.TextInput(attrs={"placeholder": "Arrivée à"}),
            "date": forms.DateInput(attrs={"type": "date"}),
            "heure": forms.TimeInput(format="%H:%M", attrs={"type": "time"}),
            "places": forms.Select(choices=TrajetProposer.PLACES),
            "prix": forms.NumberInput(attrs={"placeholder": "Prix"}),
            "temps_trajet": forms.TextInput(attrs={"placeholder": "Durée: 1h30m"}),
        }

    temps_trajet = forms.CharField(
        label="Durée du trajet",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Durée: 1h30m"}),
    )

    def clean_temps_trajet(self):
        durée = self.cleaned_data.get("temps_trajet")
        if durée:
            # Conversion des heures et minutes
            heure_minute = re.findall(r"(\d+)(h|m)", durée)
            total_minutes = 0
            for val, unit in heure_minute:
                if unit == "h":
                    # Conversion des heures en minutes
                    total_minutes += int(val) * 60
                elif unit == "m":
                    # Ajout des minutes
                    total_minutes += int(val)

            # Conversion en timedelta (en minutes) obligatoire
            return timedelta(minutes=total_minutes)

        return None
    def clean_ville_depart(self):
        ville_depart = self.cleaned_data.get("ville_depart")
        if ville_depart:
            return ville_depart.lower().strip()
        return None

    def clean_ville_arrivee(self):
        ville_arrivee = self.cleaned_data.get("ville_arrivee")
        if ville_arrivee:
            return ville_arrivee.lower().strip()
        return None
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        champs_obligatoires = [
            "ville_depart",
            "ville_arrivee",
            "date",
            "heure",
            "places",
            "prix",
            "temps_trajet",
            "voiture",
        ]
        for champ in champs_obligatoires:
            self.fields[champ].required = True
        if user:
            self.fields["voiture"].queryset = Voiture.objects.filter(user=user)




class RechercheTrajetForm(forms.Form):
    ville_depart = forms.CharField(
        max_length=100,
        label="Ville de départ",
        widget=forms.TextInput(attrs={"placeholder": "Départ de..."}),
        required=False,
    )
    ville_arrivee = forms.CharField(
        max_length=100,
        label="Ville d'arrivée",
        widget=forms.TextInput(attrs={"placeholder": "Arrivée à..."}),
        required=False,
    )
    date = forms.DateField(
        label="Date",
        widget=forms.DateInput(attrs={"type": "date"}),
        required=True
    )
    pseudo = forms.CharField(
        max_length=100,
        label="Chauffeur",
        widget=forms.TextInput(attrs={"placeholder": "Chauffeur"}),
        required=False,
    )

    def clean_pseudo(self):
        pseudo = self.cleaned_data.get("pseudo")
        if pseudo and not User.objects.filter(username=pseudo).exists():
            raise forms.ValidationError("Ce chauffeur n'existe pas.")
        return pseudo

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date < datetime.now().date():
            raise forms.ValidationError("La date ne peut pas être dans le passé.")
        return date

    def clean_ville_depart(self):
        ville_depart = self.cleaned_data.get("ville_depart")
        if ville_depart:
            return ville_depart.lower().strip()
        return None

    def clean_ville_arrivee(self):
        ville_arrivee = self.cleaned_data.get("ville_arrivee")
        if ville_arrivee:
            return ville_arrivee.lower().strip()
        return None

class FiltreTrajetForm(forms.Form):

    temps_trajet = forms.CharField(
        label="Durée du trajet",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Durée: 00h00m"}),
    )

    prix = forms.FloatField(
        label="Prix",
        widget=forms.NumberInput(attrs={"placeholder": "Prix"}),
        required=False,
    )
    note = forms.FloatField(
        label="Note",
        widget=widgets.NumberInput(attrs={"placeholder": "Par note"}),
        required=False,
    )

    def clean_prix(self):
        prix = self.cleaned_data.get("prix")
        if prix is not None and prix < 0:
            raise forms.ValidationError("Le prix ne peut pas être négatif.")
        return prix

    def clean_temps_trajet(self):
        durée = self.cleaned_data.get("temps_trajet")
        if durée:
            # Conversion des heures et minutes
            heure_minute = re.findall(r"(\d+)(h|m)", durée)
            total_minutes = 0
            for val, unit in heure_minute:
                if unit == "h":
                    # Conversion des heures en minutes
                    total_minutes += int(val) * 60
                elif unit == "m":
                    # Ajout des minutes
                    total_minutes += int(val)

            # Conversion en timedelta (en minutes) obligatoire
            return timedelta(minutes=total_minutes)
        return None


# ---------------------------- Gestion du profil utilisateur ---------------------------->


class ChoixRoleForm(forms.ModelForm):
    class Meta:
        model = ChoixRole
        fields = ["role"]
        widgets = {"role": forms.Select(choices=ChoixRole.ROLE)}


class PreferenceForm(forms.ModelForm):
    class Meta:
        model = Preference
        fields = [
            "fumeur",
            "animaux",
            "exigences_personnelles",
            "exigences_particulieres",
        ]
        widgets = {
            "fumeur": forms.Select(choices=Preference.FUMEUR),
            "animaux": forms.Select(choices=Preference.ANIMAUX),
            "exigences_particulieres": forms.Select(
                choices=Preference.EXIGENCES_PARTICULIERES,
            ),
            "exigences_personnelles": forms.Textarea(
                attrs={
                    "placeholder": "Exigences particulières",
                }
            ),
        }

    exigences_particulieres = forms.ChoiceField(
        choices=Preference.EXIGENCES_PARTICULIERES, required=False
    )
    exigences_personnelles = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Exigences particulières"}),
        required=False,
    )

    def clean_exigences_personnelles(self):
        exigences_personnelles = self.cleaned_data.get("exigences_personnelles")
        if len(exigences_personnelles) > 200:
            raise forms.ValidationError(
                "Les exigences personnelles ne doivent pas dépasser 200 caractères."
            )
        return exigences_personnelles

    def __init__(self, *args, **kwargs):
        super(PreferenceForm, self).__init__(*args, **kwargs)
        self.fields["exigences_particulieres"].required = False

    def clean_exigences_particulieres(self):
        exigences_particulieres = self.cleaned_data.get("exigences_particulieres")
        if len(exigences_particulieres) > 200:
            raise forms.ValidationError(
                "Les exigences particulières ne doivent pas dépasser 200 caractères."
            )
        return exigences_particulieres

    def __init__(self, *args, **kwargs):
        super(PreferenceForm, self).__init__(*args, **kwargs)
        self.fields["exigences_particulieres"].required = False


class VoitureForm(forms.ModelForm):
    class Meta:
        model = Voiture
        fields = [
            "marque",
            "modele",
            "couleur",
            "immatriculation",
            "annee",
            "type_moteur",
            "places",
        ]
        widgets = {
            "marque": forms.Select(choices=Voiture.MARQUE),
            "modele": forms.Select(choices=Voiture.MODELE),
            "couleur": forms.Select(choices=Voiture.COULEUR),
            "type_moteur": forms.Select(choices=Voiture.TYPE_MOTEUR),
            "places": forms.Select(choices=Voiture.PLACES),
            "immatriculation": forms.TextInput(attrs={"placeholder": "XX-XXX-XX"}),
            "annee": forms.Select(choices=Voiture.annee),
        }

    def clean_immatriculation(self):
        immatriculation = self.cleaned_data.get("immatriculation")
        if not re.match(r"^[A-Z]{2}-\d{3}-[A-Z]{2}$", immatriculation):
            raise forms.ValidationError(
                "L'immatriculation doit être de la forme XX-000-XX."
            )
        if Voiture.objects.filter(immatriculation=immatriculation).exists():
            raise forms.ValidationError("Cette immatriculation est déjà utilisée.")
        return immatriculation
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        champs_obligatoires = [
            "marque",
            "modele",
            "couleur",
            "immatriculation",
            "annee",
            "type_moteur",
            "places",
        ]
        for champ in champs_obligatoires:
            self.fields[champ].required = True



# ---------------------------- Gestion de l'adresse utilisateur ---------------------------->


class AdresseForm(forms.ModelForm):
    class Meta:
        model = AdresseUser
        fields = [
            "numero",
            "type_voie",
            "nom_rue",
            "complement",
            "code_postal",
            "ville",
            "pays",
            "telephone",
            "email",
            "photo",
        ]
        widgets = {
            "numero": forms.NumberInput(attrs={"placeholder": "Numéro du bâtiment"}),
            "type_voie": forms.Select(choices=AdresseUser.TYPE_VOIE),
            "nom_rue": forms.TextInput(attrs={"placeholder": "Nom de la rue"}),
            "complement": forms.TextInput(
                attrs={"placeholder": "Complément d'adresse"}
            ),
            "code_postal": forms.NumberInput(attrs={"placeholder": "Code postal"}),
            "ville": forms.TextInput(attrs={"placeholder": "Ville"}),
            "pays": forms.Select(choices=AdresseUser.PAYS),
            "telephone": forms.NumberInput(
                attrs={"placeholder": "Numéro de téléphone"}
            ),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "photo": forms.FileInput(),
        }
    # On va chercher l'email a l'inscription
    def __init__(self, *args,user = None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email

    def clean_numero(self):
        numero = self.cleaned_data.get("numero")
        if numero and (len(str(numero)) > 10 or not str(numero).isdigit()):
            raise ValidationError("Le numéro doit contenir au maximum 10 chiffres.")
        return numero

    def clean_code_postal(self):
        code_postal = self.cleaned_data.get("code_postal")
        if code_postal and (
            len(str(code_postal)) != 5 or not str(code_postal).isdigit()
        ):
            raise ValidationError("Le code postal doit contenir exactement 5 chiffres.")
        return code_postal

    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.exclude(id=self.instance.user.id).filter(email=email).exists():
            raise ValidationError("Cet email appartient déjà à un autre utilisateur.")

        return email

    def clean(self):
        cleaned_data = super().clean()
        required_fields = [
            "numero",
            "code_postal",
            "nom_rue",
            "ville",
            "telephone",
            "email",
        ]
        for field in required_fields:
            if not cleaned_data.get(field):
                raise forms.ValidationError(f"Le champ {field} est obligatoire.")
        return cleaned_data



# ---------------------------- Gestion des réservations de trajet ---------------------------->


class ReservationTrajetForm(forms.ModelForm):
    class Meta:
        model = ReservationTrajet
        fields = ["places"]
        widgets = {"places": forms.Select(choices=ReservationTrajet.places)}


class StatutReservationForm(forms.ModelForm):
    class Meta:
        model = ReservationTrajet
        fields = ["etat_reservation"]
        widgets = {
            "etat_reservation": forms.Select(choices=ReservationTrajet.ETAT_RESERVATION)
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["etat_reservation"].choices = [("Annulé", "Annulé")]

class TerminerTrajetForm(forms.ModelForm):
    class Meta:
        model = TrajetProposer
        fields = ["etat"]
        widgets = {
            "etat": forms.Select(choices=TrajetProposer.ETAT)
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["etat"].choices = [("Terminé", "Terminé")]

class Demarrer_ou_annulerForm(forms.ModelForm):
    class Meta:
        model = TrajetProposer
        fields = ["etat"]
        widgets = {
            "etat": forms.Select(choices=TrajetProposer.ETAT)
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["etat"].choices = [("En cours", "Demarrer"),("Annulé", "Annuler")]

class AvisForm(forms.ModelForm):
    class Meta:
        model = NoteUser
        fields = ["avis", "note", "commentaire", "passager", "chauffeur", "trajet"]
        widgets = {
            "avis": forms.Select(choices=NoteUser.AVIS),
            "note": forms.Select(choices=NoteUser.NOTE),
            "commentaire": forms.Textarea(attrs={"placeholder": "Votre commentaire"}),
            "passager": forms.HiddenInput(),
            "chauffeur": forms.HiddenInput(),
            "trajet": forms.HiddenInput(),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.instance.passager = user
            self.fields["passager"].initial = user.id
            self.fields["passager"].widget = forms.HiddenInput()
            self.fields["chauffeur"].widget = forms.HiddenInput()
            self.fields["trajet"].widget = forms.HiddenInput()

            if trajet := self.initial.get("trajet"):
                self.fields["trajet"].initial = trajet.id
                self.fields["chauffeur"].initial = trajet.user.id

                self.fields["chauffeur"].widget.attrs["readonly"] = True
                self.fields["trajet"].widget.attrs["readonly"] = True
                self.fields["passager"].widget.attrs["readonly"] = True

class ContactForm(forms.Form):

    pseudo = forms.CharField(
        max_length=100,
        label="Prénom",
        widget=forms.TextInput(attrs={"placeholder": "Prénom"}),
        required=True,
    )
    email = forms.EmailField(
        max_length=100,
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Email"}),
        required=True,
    )
    telephone = forms.CharField(
        max_length=10,
        label="Téléphone",
        widget=forms.TextInput(attrs={"placeholder": "Téléphone"}),
        required=True,
    )
    sujet = forms.CharField(
        max_length=100,
        label="Sujet",
        widget=forms.TextInput(attrs={"placeholder": "Sujet"}),
        required=True,
    )
    message = forms.CharField(
        label="Message",
        widget=forms.Textarea(attrs={"placeholder": "Message"}),
        required=True,
    )
    reponse = forms.CharField(
        label="Réponse",
        widget=forms.Textarea(attrs={"placeholder": "Réponse"}),
        required=False,
    )

    def clean_message(self):
        message = self.cleaned_data.get("message")
        if len(message) > 200:
            raise forms.ValidationError(
                "Le message ne doit pas dépasser 200 caractères."
            )
        return message

    def __init__(self, *args, user=None, **kwargs):
        # initialise le formulaire si l'utilisateur possede un compte et est connecté
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields["pseudo"].initial = user.username
            self.fields["email"].initial = user.email
            self.fields["telephone"].initial = user.adresse_user.telephone

            if user.is_authenticated:
                for field in ["pseudo", "email", "telephone"]:
                    self.fields[field].widget.attrs["readonly"] = True

class ModerationAvisPositifForm(forms.ModelForm):
    class Meta:
        model = NoteUser
        fields = ["commentaire"]
        widgets = {
            "commentaire": forms.Textarea(attrs={"placeholder": "Ajoutez un commentaire ici"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["commentaire"].widget.attrs["readonly"] = True

    def clean_commentaire(self):
        commentaire = self.cleaned_data.get("commentaire")
        if len(commentaire) > 100:
            raise forms.ValidationError(
                "Le commentaire ne doit pas dépasser 100 caractères."
            )
        return commentaire

class AfficherTrajetForm(forms.Form):
    chauffeur = forms.CharField(
        label="Chauffeur",
        widget=forms.TextInput(attrs={"placeholder": "Chauffeur"}),
        required=True,
    )

    passager = forms.CharField(
        label="Passager",
        widget=forms.TextInput(attrs={"placeholder": "Passager"}),
        required=True,
    )

    trajet = forms.CharField(
        label="Trajet",
        widget=forms.TextInput(attrs={"placeholder": "Trajet"}),
        required=True,
    )

    date_reservation = forms.CharField(
        label="Date de réservation",
        widget=forms.TextInput(attrs={"placeholder": "Date de réservation"}),
        required=False,
    )
    prix = forms.CharField(
        label="Prix",
        widget=forms.TextInput(attrs={"placeholder": "Prix"}),
        required=False,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["chauffeur"].widget.attrs["readonly"] = True
        self.fields["passager"].widget.attrs["readonly"] = True
        self.fields["trajet"].widget.attrs["readonly"] = True
        self.fields["date_reservation"].widget.attrs["readonly"] = True
        self.fields["prix"].widget.attrs["readonly"] = True
class ModerationTrajetForm(forms.ModelForm):

    class Meta:
        model = NoteUser
        fields = ["commentaire","etat_paiement","avis"]
        widgets = {
            "etat_paiement": forms.Select(choices=ReservationTrajet.ETAT_PAIEMENT),
            "avis": forms.Select(choices=NoteUser.AVIS),
            "commentaire": forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["etat_paiement"].choices = [
            (key, value)
            for key, value in self.fields["etat_paiement"].choices
            if key != "En attente"
        ]
        self.fields["commentaire"].widget.attrs["readonly"] = True

    def clean_commentaire(self):
        commentaire = self.cleaned_data.get("commentaire")
        if len(commentaire) > 200:
            raise forms.ValidationError(
                "Le commentaire ne doit pas dépasser 200 caractères."
            )
        return commentaire

class AfficherReservationForm(forms.Form):
    jour = forms.CharField(
        label="Jour",
        widget=forms.TextInput(attrs={"placeholder": "Jour"}),
        required=True,
    )
    total_gain = forms.CharField(
        label="Total gain",
        widget=forms.TextInput(attrs={"placeholder": "Total gain"}),
        required=True,
    )
    total_resa = forms.CharField(
        label="Total réservation",
        widget=forms.TextInput(attrs={"placeholder": "Total réservation"}),
        required=True,
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["jour"].widget.attrs["readonly"] = True
        self.fields["total_gain"].widget.attrs["readonly"] = True
        self.fields["total_resa"].widget.attrs["readonly"] = True
