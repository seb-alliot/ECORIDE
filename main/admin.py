from django.contrib import admin
from .models import (
    CreditUser,
    NoteUser,
    AdresseUser,
    ChoixRole,
    Voiture,
    TrajetProposer,
    Preference,
    ReservationTrajet,
    ChangerStatutTrajet,
)
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


# Register your models here.
class CreditUserInline(admin.TabularInline):
    model = CreditUser
    extra = 1


class ChoiceRoleInline(admin.TabularInline):
    model = ChoixRole
    extra = 1


class CustomUserAdmin(UserAdmin):
    fieldsets = [
        ("Pseudo", {"fields": ("username", "password")}),
        ("Email de l'utilisateur", {"fields": ("email",)}),
        ("Etat du compte", {"fields": ("is_active",)}),
    ]
    # On ajoute les models CreditUser et ChoixRole a l'interface admin lors de la création d'un utilisateur
    inlines = [CreditUserInline, ChoiceRoleInline]

    list_display = ["username", "email", "get_role", "get_credit", "is_active"]
    list_filter = ["is_active"]

    # On combine les models via les formulaires à la creation d'un utilisateur via l'interface admin
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:
            CreditUser.objects.create(user=obj, role="passager")
            ChoixRole.objects.create(user=obj)

    def get_role(self, obj):
        role = ChoixRole.objects.filter(user=obj).first()
        return role.role if role else "Aucun"

    get_role.short_description = "Role"

    def get_credit(self, obj):
        credit = CreditUser.objects.filter(user=obj).first()
        return credit.credit if credit else 0

    get_credit.short_description = "Crédit"


# On désactive le model admin de base pour le remplacer
# par le custom qui accepte les cominaisons de models
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


class UserAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "password",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
        "is_superuser",
        "date_joined",
        "last_login",
    ]
    search_fields = ["username", "email", "first_name", "last_name"]
    list_filter = ["is_active", "is_staff", "is_superuser", "date_joined", "last_login"]
    list_per_page = 10


@admin.register(NoteUser)
class NoteUserAdmin(admin.ModelAdmin):
    list_display = [
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


@admin.register(Voiture)
class VoitureAdmin(admin.ModelAdmin):
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


@admin.register(TrajetProposer)
class TrajetProposerAdmin(admin.ModelAdmin):
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
        ("Avec", {"fields": ["voiture", "type_moteur"]}),
        ("Nombre de places", {"fields": ["places"]}),
        ("Pour combien", {"fields": ["prix", "total_payer"]}),
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
    list_display = [
        "id",
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
        ("Combien ?", {"fields": ["places", "prix_par_passager"]}),
        ("Etat", {"fields": ["etat_reservation"]}),
        ("Remboursement", {"fields": ["reservation_rembourser"]}),
    ]


@admin.register(ChangerStatutTrajet)
class ChangerStatutTrajetAdmin(admin.ModelAdmin):
    list_display = ["id", "trajet", "statut"]
    search_fields = ["trajet", "statut"]
    list_filter = ["trajet", "statut"]
    list_per_page = 10
