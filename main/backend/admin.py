from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from .models import (
    NoteUser,
    AdresseUser,
    ChoixRole,
    Voiture,
    TrajetProposer,
    Preference,
    ReservationTrajet,
    CreditUser,
    Commission,
)
from .forms import (
    TrajetForm,
    VoitureForm,
    AdresseForm,
    CustomUserForm,
    ReservationTrajetForm,
)



class CustomUserAdmin(UserAdmin):
    form = CustomUserForm
    fieldsets = [
        ("Pseudo", {"fields": ("username", "password")}),
        ("Email de l'utilisateur", {"fields": ("email",)}),
        ("Etat du compte", {"fields": ("is_active",)}),
        ("Groupes", {"fields": ("groups",)}),
        ("Permissions", {"fields": ("user_permissions",)}),
        ("Date de création", {"fields": ("date_joined",)}),
        ("Dernière connexion", {"fields": ("last_login",)}),
        (
            "Informations personnelles",
            {
                "fields": (
                    "is_staff",
                )
            },
        ),
    ]

    list_display = [
        "id",
        "username",
        "email",
        "is_active",
        "is_staff",
    ]
    search_fields = ["username", "email"]
    list_filter = ["is_active", "is_staff"]
    list_per_page = 10


    list_display = ["username",'is_staff', "email", "is_active"]
    list_filter = ["is_active"]
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "password",
        "is_active",
        "is_staff",
    ]
    search_fields = ["username", "email"]
    list_filter = ["is_active", "is_staff"]
    list_per_page = 10

@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "valeur",
    ]
    list_editable = ["valeur"]
    search_fields = ["id", "valeur"]
    list_per_page = 10


@admin.register(CreditUser)
class CreditUserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "credit",
    ]
    list_editable = ["credit"]
    search_fields = ["user__username", "user__email"]
    list_filter = ["user"]
    list_per_page = 10

@admin.register(NoteUser)
class NoteUserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "passager",
        "chauffeur",
        "note",
        "note_attribuee",
        "avis",
        "avis_donne",
        "commentaire",
        "commentaire_attribuee",
        "commentaire_moderer",
        "decision_prise",
    ]
    search_fields = [
        "passager",
        "chauffeur",
        "note",
        "avis",
        "commentaire",
        "commentaire_moderer",
        "decision_prise",
    ]
    list_editable = [
        "avis",
        "commentaire",
    ]
    list_filter = [
        "passager",
        "chauffeur",
        "avis",
        "note",
        "commentaire_moderer",
        "decision_prise",
    ]
    list_per_page = 10


@admin.register(AdresseUser)
class AdresseUserAdmin(admin.ModelAdmin):
    form = AdresseForm
    list_display = [
        "id",
        "user",
        "numero",
        "type_voie",
        "complement",
        "nom_rue",
        "code_postal",
        "ville",
        "pays",
        "telephone",
        "email",
        "photo",
    ]
    search_fields = [
        "user",
        "numero",
        "type_voie",
        "complement",
        "nom_rue",
        "code_postal",
        "ville",
        "pays",
        "telephone",
        "email",
        "photo",
    ]
    list_editable = [
        "user",
        "numero",
        "type_voie",
        "complement",
        "nom_rue",
        "code_postal",
        "ville",
        "pays",
        "telephone",
        "email",
        "photo",
    ]
    list_filter = [
        "user",
        "numero",
        "type_voie",
        "complement",
        "nom_rue",
        "code_postal",
        "ville",
        "pays",
        "telephone",
        "email",
        "photo",
    ]
    list_per_page = 104
    fieldsets = [
        ("utilisateur", {"fields": ["user"]}),
        ("Le batiment et le type de voie", {"fields": ["numero", "type_voie"]}),
        ("le nom de la rue", {"fields": ["nom_rue", "complement"]}),
        ("Code postal et ville", {"fields": ["code_postal", "ville"]}),
        ("Pays", {"fields": ["pays"]}),
        ("Contact", {"fields": ["telephone", "email"]}),
        ("Photo", {"fields": ["photo"]}),
    ]


@admin.register(ChoixRole)
class ChoixRoleAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "role"]
    search_fields = ["role"]
    list_filter = ["role"]
    list_per_page = 10
    list_editable = ["role"]


@admin.register(Voiture)
class VoitureAdmin(admin.ModelAdmin):
    form = VoitureForm

    fieldsets = [
        ("Propriétaire", {"fields": ["user"]}),
        ("Voiture", {"fields": ["marque", "modele"]}),
        (
            "Caractéristiques",
            {
                "fields": [
                    "couleur",
                    "type_moteur",
                    "places",
                    "immatriculation",
                    "annee",
                ]
            },
        ),
    ]
    list_display = [
        "id",
        "user",
        "marque",
        "modele",
        "couleur",
        "type_moteur",
        "places",
        "immatriculation",
        "annee",
    ]
    search_fields = [
        "user",
        "marque",
        "modele",
        "couleur",
        "type_moteur",
        "places",
        "immatriculation",
        "annee",
    ]
    list_filter = ["user", "type_moteur", "places", "immatriculation"]
    list_per_page = 10

    class Media:
        js = ("js/admin/voiture_admin.js",)


@admin.register(TrajetProposer)
class TrajetProposerAdmin(admin.ModelAdmin):
    form = TrajetForm
    list_display = [
        "id",
        "chauffeur",
        "etat",
        "trajet_rembourser",
        "chauffeur",
        "ville_depart",
        "ville_arrivee",
        "date",
        "heure",
        "prix",
        "total_payer",
        "temps_trajet",
        "voiture",
    ]
    search_fields = [
        "chauffeur",
        "etat",
        "trajet_rembourser",
        "chauffeur",
        "ville_depart",
        "ville_arrivee",
        "date",
        "heure",
        "prix",
        "total_payer",
        "temps_trajet",
        "voiture",
    ]
    list_filter = [
        "chauffeur",
        "etat",
        "trajet_rembourser",
        "chauffeur",
        "ville_depart",
        "ville_arrivee",
        "date",
        "heure",
        "prix",
        "total_payer",
        "temps_trajet",
        "voiture",
    ]
    list_per_page = 10
    fieldsets = [
        ("Proposer par", {"fields": ["chauffeur"]}),
        ("Trajet", {"fields": ["ville_depart", "ville_arrivee"]}),
        ("Quand", {"fields": ["date", "heure"]}),
        ("Nombre de places", {"fields": ["places"]}),
        ("Voiture", {"fields": ["voiture"]}),
        ("Pour combien", {"fields": ["prix"]}),
        ("Temps de trajet", {"fields": ["temps_trajet"]}),
        ("Etat", {"fields": ["etat"]}),
        ("Remboursement", {"fields": ["trajet_rembourser"]}),
    ]


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user_preference",
        "exigences_particulieres",
        "exigences_personnelles",
        "fumeur",
        "animaux",
    ]
    search_fields = [
        "user_preference",
        "exigences_particulieres",
        "exigences_personnelles",
        "fumeur",
        "animaux",
    ]
    list_filter = [
        "user_preference",
        "exigences_particulieres",
        "exigences_personnelles",
        "fumeur",
        "animaux",
    ]
    list_per_page = 10


@admin.register(ReservationTrajet)
class ReservationTrajetAdmin(admin.ModelAdmin):
    form = ReservationTrajetForm
    list_display = [
        "id",
        "passager",
        "trajet_reserver",
        "passager",
        "prix_par_passager",

        "places",
        "reservation_rembourser",
        "etat_reservation",
    ]
    search_fields = [
        "trajet_reserver",
        "passager",
        "prix_par_passager",
        "places",
        "reservation_rembourser",
        "etat_reservation",
    ]
    list_filter = [
        "trajet_reserver",
        "passager",
        "prix_par_passager",
        "places",
        "reservation_rembourser",
        "etat_reservation",
    ]
    list_per_page = 10
    fieldsets = [
        ("Qui ?", {"fields": ["passager"]}),
        ("Pour ou ?  ", {"fields": ["trajet_reserver"]}),
        ("Combien ?", {"fields": ["places"]}),
        ("Etat", {"fields": ["etat_reservation"]}),
        ("Remboursement", {"fields": ["reservation_rembourser"]}),
    ]
