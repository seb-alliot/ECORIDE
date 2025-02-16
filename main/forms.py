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
from main.models import (
    TrajetProposer,
    ChangerStatutTrajet,
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
        widget=forms.TextInput(attrs={"placeholder": "Votre identifiant"}),
        required=True,
    )
    email = forms.EmailField(
        max_length=100,
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Votre email"}),
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
        widget=forms.PasswordInput(attrs={"placeholder": "valider le mot de passe"}),
        required=True,
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if not re.match(r"^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$", password1):
            raise forms.ValidationError(
                "Le mot de passe doit contenir au moins 8 caractères, une lettre majuscule, une lettre minuscule et un chiffre."
            )
        return password1

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
        widget=forms.TextInput(attrs={"placeholder": "Votre identifiant"}),
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
        widget=forms.PasswordInput(attrs={"placeholder": "Votre mot de passe"}),
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
        widget=forms.EmailInput(attrs={"placeholder": "Votre email"}),
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
            {"placeholder": "Nouveau mot de passe"}
        )
        self.fields["new_password2"].widget.attrs.update(
            {"placeholder": "Confirmer le mot de passe"}
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
            "type_moteur",
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
            "type_moteur": forms.Select(choices=Voiture.TYPE_MOTEUR),
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

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["voiture"].queryset = Voiture.objects.filter(user=user)


class StatutTrajetForm(forms.ModelForm):

    class Meta:
        model = ChangerStatutTrajet
        fields = ["statut"]
        widgets = {"statut": forms.Select(choices=TrajetProposer.ETAT)}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        statut = "Disponible"
        self.fields["statut"].choices = [
            (key, value)
            for key, value in self.fields["statut"].choices
            if key != "Disponible"
        ]


class RechercheTrajetForm(forms.Form):
    ville_depart = forms.CharField(
        max_length=100,
        label="Ville de départ",
        widget=forms.TextInput(attrs={"placeholder": "Départ de..."}),
        required=True,
    )
    ville_arrivee = forms.CharField(
        max_length=100,
        label="Ville d'arrivée",
        widget=forms.TextInput(attrs={"placeholder": "Arrivée à..."}),
        required=True,
    )
    date = forms.DateField(
        label="Date", widget=forms.DateInput(attrs={"type": "date"}), required=True
    )

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if date < datetime.now().date():
            raise forms.ValidationError("La date ne peut pas être dans le passé.")
        return date


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
                widget=widgets.NumberInput(
                    attrs={'placeholder': 'Filtrer par note'}),
        required=False,)

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
        return immatriculation


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

    def self(self):
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


class AvisForm(forms.ModelForm):
    class Meta:
        model = NoteUser
        fields = ["avis","note", "commentaire", "passager","chauffeur","trajet"]
        widgets = {
            "avis": forms.Select(choices=NoteUser.AVIS),
            "note": forms.Select(choices=NoteUser.NOTE),
            "commentaire": forms.Textarea(attrs={"placeholder": "Votre commentaire"}),
            "passager": forms.HiddenInput(),
            "chauffeur": forms.HiddenInput(),
            "trajet": forms.HiddenInput(),
        }

    def clean_commentaire(self):
        commentaire = self.cleaned_data.get("commentaire")
        if len(commentaire) > 200:
            raise forms.ValidationError("Le commentaire ne doit pas dépasser 200 caractères.")
        return commentaire

    def __init__(self, *args,user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.instance.passager = user
            self.fields["passager"].initial = user.id
            self.fields["passager"].widget = forms.HiddenInput()
            self.fields["chauffeur"].widget = forms.HiddenInput()
            self.fields["trajet"].widget = forms.HiddenInput()

            if trajet:=self.initial.get("trajet"):
                self.fields["trajet"].initial = trajet.id
                self.fields["chauffeur"].initial = trajet.user.id

                self.fields["chauffeur"].widget.attrs["readonly"] = True
                self.fields["trajet"].widget.attrs["readonly"] = True
                self.fields["passager"].widget.attrs["readonly"] = True
                



class ContactForm(forms.Form):

    pseudo = forms.CharField(
        max_length=100,
        label="Prénom",
        widget=forms.TextInput(attrs={"placeholder": "Votre prénom"}),
        required=True,
    )
    email = forms.EmailField(
        max_length=100,
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Votre email"}),
        required=True,
    )
    telephone = forms.CharField(
        max_length=10,
        label="Téléphone",
        widget=forms.TextInput(attrs={"placeholder": "Votre téléphone, facultatif"}),
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
        widget=forms.Textarea(attrs={"placeholder": "Votre message"}),
        required=True,
    )

    def clean_message(self):
        message = self.cleaned_data.get("message")
        if len(message) > 200:
            raise forms.ValidationError("Le message ne doit pas dépasser 200 caractères.")
        return message

    def __init__(self, *args,user=None, **kwargs):
        #initialise le formulaire si l'utilisateur possede un compte et est connecté
        super().__init__(*args, **kwargs)

        if user and user.is_authenticated:
            self.fields["pseudo"].initial = user.username
            self.fields["email"].initial = user.email
            self.fields["telephone"].initial = user.adresse_user.telephone

            self.fields["pseudo"].widget.attrs["readonly"] = True
            self.fields["email"].widget.attrs["readonly"] = True
            self.fields["telephone"].widget.attrs["readonly"] = True
