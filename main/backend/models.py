from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.utils import timezone
from django.core.validators import MinValueValidator, RegexValidator
from datetime import date, datetime, timedelta
from decimal import Decimal
import uuid
from django.db.models import Sum

class Commission(models.Model):
    valeur = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Valeur de la commission",
    )

    def save(self, *args, **kwargs):
        # supprime toute autre commission avant d’enregistrer, on créer un singleton
        Commission.objects.exclude(id=self.id).delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.valeur}"


class CreditUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="credit",
        verbose_name="Utilisateur",
    )
    credit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name="Crédit actuel de l'utilisateur",
    )

    class Meta:
        verbose_name = "Crédit utilisateur"
        verbose_name_plural = "Crédits utilisateurs"

    def __str__(self):
        return f"Solde de {self.user.username}: {self.credit} €"

    def add_credit(self, montant):
        self.credit += Decimal(montant)
        self.save()
        return f"Crédit ajouté: {montant} €"


class NoteUser(models.Model):
    NOTE = [
        (Decimal(1), "1"),
        (Decimal(2), "2"),
        (Decimal(3), "3"),
        (Decimal(4), "4"),
        (Decimal(5), "5"),
    ]
    AVIS = [
        ("","---"),
        ("oui", "oui"),
        ("non", "non"),
    ]

    passager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="jury",
        verbose_name="Passager",
    )
    chauffeur = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="accusé",
        verbose_name="Chauffeur",
    )
    trajet = models.ForeignKey(
        "TrajetProposer",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="bout_du_tunnel",
        verbose_name="Trajet concerné",
    )

    note = models.DecimalField(
        choices=NOTE,
        max_digits=2,
        decimal_places=1,
        blank=True,
        null=True,
        verbose_name="Note",
    )
    note_attribuee = models.BooleanField(default=False, verbose_name="Noté ?")

    avis = models.CharField(
        choices=AVIS,
        max_length=100,
        default="oui",
        verbose_name="Ça s'est bien passé ?",
    )
    avis_donne = models.BooleanField(default=False, verbose_name="Avis donné ?")

    commentaire = models.TextField(
        null=True, blank=True, verbose_name="Commentaire laissé"
    )
    commentaire_attribuee = models.BooleanField(
        default=False, verbose_name="Commenté ?"
    )

    commentaire_moderer = models.BooleanField(default=False)

    etat_paiement = models.CharField(
        max_length=20,
        choices=[("Payer", "valider le paiement"), ("Refuser", "Refuser le paiement")],
        default="Payer",
        verbose_name="Statut du paiement",
    )
    decision_prise = models.BooleanField(default=False, verbose_name="Administré ?")

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        verbose_name = "Note utilisateur"
        verbose_name_plural = "Notes utilisateurs"
        unique_together = ["chauffeur", "passager", "trajet"]

    def __str__(self):
        return f"Note de {self.chauffeur}: {self.note} {self.commentaire} {self.avis} "


class TokenValidation(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="token_validation"
    )
    token = models.CharField(max_length=128, unique=True)
    action = models.CharField(max_length=20, default="default_action")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # Vérifie si le token est expiré (2h max)
        return timezone.now() - self.created_at > timezone.timedelta(hours=2)

    def __str__(self):
        return f"Token pour {self.user.username} ({self.action})"


class ActivationToken(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expiration_time = self.created_at + timedelta(hours=24)
        return timezone.now() > expiration_time

    def activate(self):
        self.user.credit += 20
        self.user.is_active = True
        self.user.save()
        self.delete()
        return True

    def __str__(self):
        return f"Token for {self.user.username}"


class AdresseUser(models.Model):

    TYPE_VOIE = [
        ("Rue", "Rue"),
        ("Avenue", "Avenue"),
        ("Boulevard", "Boulevard"),
        ("Impasse", "Impasse"),
        ("Place", "Place"),
        ("Route", "Route"),
        ("Chemin", "Chemin"),
        ("Allée", "Allée"),
    ]
    PAYS = [
        ("", "Pays"),
        ("AF", "Afghanistan"),
        ("AL", "Albanie"),
        ("DZ", "Algérie"),
        ("AD", "Andorre"),
        ("AO", "Angola"),
        ("AR", "Argentine"),
        ("AM", "Arménie"),
        ("AU", "Australie"),
        ("AT", "Autriche"),
        ("AZ", "Azerbaïdjan"),
        ("BS", "Bahamas"),
        ("BH", "Bahreïn"),
        ("BD", "Bangladesh"),
        ("BB", "Barbade"),
        ("BY", "Biélorussie"),
        ("BE", "Belgique"),
        ("BZ", "Belize"),
        ("BJ", "Bénin"),
        ("BT", "Bhoutan"),
        ("BO", "Bolivie"),
        ("BA", "Bosnie-Herzégovine"),
        ("BW", "Botswana"),
        ("BR", "Brésil"),
        ("BN", "Brunei"),
        ("BG", "Bulgarie"),
        ("BF", "Burkina Faso"),
        ("BI", "Burundi"),
        ("KH", "Cambodge"),
        ("CM", "Cameroun"),
        ("CA", "Canada"),
        ("CV", "Cap-Vert"),
        ("KY", "Îles Caïmans"),
        ("CF", "République Centrafricaine"),
        ("TD", "Tchad"),
        ("CL", "Chili"),
        ("CN", "Chine"),
        ("CO", "Colombie"),
        ("KM", "Comores"),
        ("CG", "Congo"),
        ("CD", "République Démocratique du Congo"),
        ("CR", "Costa Rica"),
        ("HR", "Croatie"),
        ("CU", "Cuba"),
        ("CY", "Chypre"),
        ("CZ", "République tchèque"),
        ("DK", "Danemark"),
        ("DJ", "Djibouti"),
        ("DM", "Dominique"),
        ("DO", "République dominicaine"),
        ("EC", "Équateur"),
        ("EG", "Égypte"),
        ("SV", "Salvador"),
        ("GQ", "Guinée équatoriale"),
        ("ER", "Érythrée"),
        ("EE", "Estonie"),
        ("SZ", "Eswatini"),
        ("ET", "Éthiopie"),
        ("FI", "Finlande"),
        ("FR", "France"),
        ("GA", "Gabon"),
        ("GM", "Gambie"),
        ("GE", "Géorgie"),
        ("DE", "Allemagne"),
        ("GH", "Ghana"),
        ("GR", "Grèce"),
        ("GD", "Grenade"),
        ("GT", "Guatemala"),
        ("GN", "Guinée"),
        ("GW", "Guinée-Bissau"),
        ("GY", "Guyana"),
        ("HT", "Haïti"),
        ("HN", "Honduras"),
        ("HU", "Hongrie"),
        ("IS", "Islande"),
        ("IN", "Inde"),
        ("ID", "Indonésie"),
        ("IR", "Iran"),
        ("IQ", "Irak"),
        ("IE", "Irlande"),
        ("IL", "Israël"),
        ("IT", "Italie"),
        ("CI", "Côte d'Ivoire"),
        ("JM", "Jamaïque"),
        ("JP", "Japon"),
        ("JO", "Jordanie"),
        ("KZ", "Kazakhstan"),
        ("KE", "Kenya"),
        ("KI", "Kiribati"),
        ("KR", "Corée du Sud"),
        ("KW", "Koweït"),
        ("KG", "Kirghizistan"),
        ("LA", "Laos"),
        ("LV", "Lettonie"),
        ("LB", "Liban"),
        ("LS", "Lesotho"),
        ("LR", "Libéria"),
        ("LY", "Libye"),
        ("LT", "Lituanie"),
        ("LU", "Luxembourg"),
        ("MO", "Macao"),
        ("MK", "Macédoine du Nord"),
        ("MG", "Madagascar"),
        ("MW", "Malawi"),
        ("MY", "Malaisie"),
        ("MV", "Maldives"),
        ("ML", "Mali"),
        ("MT", "Malte"),
        ("MH", "Îles Marshall"),
        ("MQ", "Martinique"),
        ("MR", "Mauritanie"),
        ("MU", "Maurice"),
        ("YT", "Mayotte"),
        ("MX", "Mexique"),
        ("FM", "Micronésie"),
        ("MD", "Moldavie"),
        ("MC", "Monaco"),
        ("MN", "Mongolie"),
        ("ME", "Monténégro"),
        ("MA", "Maroc"),
        ("MZ", "Mozambique"),
        ("MM", "Myanmar"),
        ("NA", "Namibie"),
        ("NR", "Nauru"),
        ("NP", "Népal"),
        ("NL", "Pays-Bas"),
        ("NZ", "Nouvelle-Zélande"),
        ("NI", "Nicaragua"),
        ("NE", "Niger"),
        ("NG", "Nigéria"),
        ("NO", "Norvège"),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="adresse_user",
        verbose_name="Utilisateur",
    )
    numero = models.CharField(max_length=10, verbose_name="Numéro du batiment")
    type_voie = models.CharField(max_length=100, choices=TYPE_VOIE)
    nom_rue = models.CharField(max_length=100)
    complement = models.CharField(max_length=100, null=True, blank=True)
    code_postal = models.IntegerField(
        validators=[
            RegexValidator(
                regex=r"^\d{5}$",
                message="Le code postal doit contenir exactement 5 chiffres.",
            )
        ],
    )
    ville = models.CharField(max_length=100)
    pays = models.CharField(choices=PAYS, max_length=100, default="Pays")
    telephone = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        validators=[
            RegexValidator(
                regex=r"^\d{10}$",
                message="Le numéro de téléphone doit contenir 10 chiffres.",
            )
        ],
    )
    email = models.EmailField(max_length=100, null=True, blank=True)
    photo = models.ImageField(
        upload_to="user",
        default="photo_default/photo_default.jpg",
        null=True,
        blank=True,
        verbose_name="Photo de profil",
    )

    class Meta:
        verbose_name = "Information sur l'utilisateur"
        verbose_name_plural = "Informations sur les utilisateurs"

    def save(self, *args, **kwargs):
        if self.pk:
            vieille_image = AdresseUser.objects.get(pk=self.pk).photo
            if vieille_image and vieille_image != self.photo:
                vieille_image.delete(save=False)

        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.photo},{self.numero} {self.type_voie} {self.nom_rue},{self.complement} {self.ville},{self.code_postal}, {self.telephone},{self.email},{self.pays}, {self.user.username}"


class ChoixRole(models.Model):
    ROLE = [
        ("chauffeur", "Chauffeur"),
        ("passager", "Passager"),
    ]
    role = models.CharField(choices=ROLE, default="passager")
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="role", verbose_name="Utilisateur"
    )

    class Meta:
        verbose_name = "Role utilisateur"
        verbose_name_plural = "Roles utilisateurs"

    def __str__(self):
        return f"  { self.get_role_display()}"


class Voiture(models.Model):
    def get_year_choices():
        current_year = datetime.now().year
        return [(year, str(year)) for year in reversed(range(1950, current_year + 1))]

    TYPE_MOTEUR = [
        ("Electrique", "Electrique"),
        ("Hybride", "Hybride"),
        ("essence", "Essence"),
        ("diesel", "Diesel"),
    ]
    PLACES = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
    ]
    COULEUR = [
        ("noir", "Noir"),
        ("blanc", "Blanc"),
        ("gris_clair", "Gris clair"),
        ("gris_fonce", "Gris foncé"),
        ("argente", "Argenté"),
        ("bleu_metallise", "Bleu métallisé"),
        ("vert_metallise", "Vert métallisé"),
        ("rouge_metallise", "Rouge métallisé"),
        ("cuivre", "Cuivre"),
        ("or", "Or"),
        ("rouge", "Rouge"),
        ("bleu", "Bleu"),
        ("vert", "Vert"),
        ("jaune", "Jaune"),
        ("orange", "Orange"),
        ("beige", "Beige"),
        ("marron", "Marron"),
        ("bleu_nuit", "Bleu nuit"),
        ("vert_emeraude", "Vert émeraude"),
        ("rouge_rubis", "Rouge rubis"),
        ("blanc_perle", "Blanc perle"),
        ("noir_obsidienne", "Noir obsidienne"),
        ("noir_mat", "Noir mat"),
        ("gris_mat", "Gris mat"),
        ("bleu_mat", "Bleu mat"),
        ("rouge_mat", "Rouge mat"),
        ("violet", "Violet"),
        ("bleu_turquoise", "Bleu turquoise"),
        ("vert_lime", "Vert lime"),
    ]
    MARQUE = [
        ("audi", "Audi"),
        ("bmw", "BMW"),
        ("chevrolet", "Chevrolet"),
        ("citroen", "Citroën"),
        ("fiat", "Fiat"),
        ("ford", "Ford"),
        ("honda", "Honda"),
        ("hyundai", "Hyundai"),
        ("jeep", "Jeep"),
        ("kia", "Kia"),
        ("land_rover", "Land Rover"),
        ("lexus", "Lexus"),
        ("mazda", "Mazda"),
        ("mercedes", "Mercedes"),
        ("mini", "Mini"),
        ("mitsubishi", "Mitsubishi"),
        ("nissan", "Nissan"),
        ("opel", "Opel"),
        ("peugeot", "Peugeot"),
        ("porsche", "Porsche"),
        ("renault", "Renault"),
        ("seat", "Seat"),
        ("skoda", "Skoda"),
        ("subaru", "Subaru"),
        ("suzuki", "Suzuki"),
        ("tesla", "Tesla"),
        ("toyota", "Toyota"),
        ("volkswagen", "Volkswagen"),
        ("volvo", "Volvo"),
    ]
    MODELE = {
        "audi": [
            ("a1", "A1"),
            ("a3", "A3"),
            ("a4", "A4"),
            ("a5", "A5"),
            ("a6", "A6"),
            ("q3", "Q3"),
            ("q5", "Q5"),
            ("q7", "Q7"),
            ("q8", "Q8"),
        ],
        "bmw": [
            ("serie 1", "Série 1"),
            ("serie 3", "Série 3"),
            ("serie 5", "Série 5"),
            ("serie 7", "Série 7"),
            ("x1", "X1"),
            ("x3", "X3"),
            ("x5", "X5"),
            ("x6", "X6"),
            ("z4", "Z4"),
        ],
        "chevrolet": [
            ("camaro", "Camaro"),
            ("cruze", "Cruze"),
            ("equinox", "Equinox"),
            ("malibu", "Malibu"),
            ("silverado", "Silverado"),
            ("spark", "Spark"),
            ("tahoe", "Tahoe"),
            ("traverse", "Traverse"),
        ],
        "citroen": [
            ("berlingo", "Berlingo"),
            ("c1", "C1"),
            ("c3", "C3"),
            ("c3 aircross", "C3 Aircross"),
            ("c4", "C4"),
            ("c4 cactus", "C4 Cactus"),
            ("c5", "C5"),
        ],
        "fiat": [
            ("500", "500"),
            ("500l", "500L"),
            ("500x", "500X"),
            ("doblo", "Doblo"),
            ("panda", "Panda"),
            ("tipo", "Tipo"),
        ],
        "ford": [
            ("edge", "Edge"),
            ("explorer", "Explorer"),
            ("fiesta", "Fiesta"),
            ("focus", "Focus"),
            ("kuga", "Kuga"),
            ("mustang", "Mustang"),
        ],
        "honda": [
            ("accord", "Accord"),
            ("civic", "Civic"),
            ("crv", "CR-V"),
            ("hrv", "HR-V"),
            ("insight", "Insight"),
            ("jazz", "Jazz"),
        ],
        "hyundai": [
            ("i10", "i10"),
            ("i20", "i20"),
            ("i30", "i30"),
            ("kona", "Kona"),
            ("nexo", "Nexo"),
            ("santa fe", "Santa Fe"),
            ("tucson", "Tucson"),
        ],
        "jeep": [
            ("jcherokee", "Cherokee"),
            ("compass", "Compass"),
            ("cherokee", "Grand Cherokee"),
            ("gladiator", "Gladiator"),
            ("renegade", "Renegade"),
            ("wrangler", "Wrangler"),
        ],
        "kia": [
            ("ceed", "Ceed"),
            ("picanto", "Picanto"),
            ("rio", "Rio"),
            ("sportage", "Sportage"),
            ("sorento", "Sorento"),
            ("stonic", "Stonic"),
        ],
        "land_rover": [
            ("defender", "Defender"),
            ("discovery", "Discovery"),
            ("evoque", "Evoque"),
            ("range rover", "Range Rover"),
        ],
        "lexus": [
            ("es", "ES"),
            ("gx", "GX"),
            ("is", "IS"),
            ("lexus_nx", "NX"),
            ("lexus_rx", "RX"),
            ("lexus_ux", "UX"),
        ],
        "mazda": [
            ("2", "2"),
            ("mazda 3", "3"),
            ("mazda 6", "6"),
            ("mazda cx30", "CX-30"),
            ("mazda cx5", "CX-5"),
            ("mazda mx5", "MX-5"),
        ],
        "mercedes": [
            ("classe a", "Classe A"),
            ("classe c", "Classe C"),
            ("classe e", "Classe E"),
            ("classe s", "Classe S"),
            ("gla", "GLA"),
            ("glc", "GLC"),
            ("gle", "GLE"),
            ("gls", "GLS"),
        ],
        "mini": [
            ("clubman", "Clubman"),
            ("convertible", "Convertible"),
            ("countryman", "Countryman"),
            ("cooper", "Cooper"),
        ],
        "mitsubishi": [
            ("eclipse_cross", "Eclipse Cross"),
            ("lancer", "Lancer"),
            ("outlander", "Outlander"),
            ("space_star", "Space Star"),
        ],
        "nissan": [
            ("juke", "Juke"),
            ("leaf", "Leaf"),
            ("micra", "Micra"),
            ("patrol", "Patrol"),
            ("qashqai", "Qashqai"),
            ("xtrail", "X-Trail"),
        ],
        "opel": [
            ("astra", "Astra"),
            ("corsa", "Corsa"),
            ("grandland", "Grandland"),
            ("insignia", "Insignia"),
            ("mokka", "Mokka"),
            ("zafira", "Zafira"),
        ],
        "peugeot": [
            ("2008", "2008"),
            ("3008", "3008"),
            ("308", "308"),
            ("5008", "5008"),
            ("508", "508"),
            ("208", "208"),
        ],
        "porsche": [
            ("911", "911"),
            ("cayenne", "Cayenne"),
            ("macan", "Macan"),
            ("panamera", "Panamera"),
            ("taycan", "Taycan"),
        ],
        "renault": [
            ("captur", "Captur"),
            ("clio", "Clio"),
            ("kadjar", "Kadjar"),
            ("koleos", "Koleos"),
            ("megane", "Mégane"),
            ("talisman", "Talisman"),
        ],
        "seat": [
            ("arona", "Arona"),
            ("ateca", "Ateca"),
            ("ibiza", "Ibiza"),
            ("leon", "Leon"),
            ("tarraco", "Tarraco"),
        ],
        "skoda": [
            ("fabia", "Fabia"),
            ("karoq", "Karoq"),
            ("kodiaq", "Kodiaq"),
            ("octavia", "Octavia"),
            ("superb", "Superb"),
        ],
        "subaru": [
            ("forester", "Forester"),
            ("impreza", "Impreza"),
            ("outback", "Outback"),
            ("xv", "XV"),
        ],
        "suzuki": [
            ("ignis", "Ignis"),
            ("jimny", "Jimny"),
            ("swift", "Swift"),
            ("vitara", "Vitara"),
        ],
        "tesla": [
            ("model 3", "Model 3"),
            ("model s", "Model S"),
            ("model x", "Model X"),
            ("model y", "Model Y"),
        ],
        "toyota": [
            ("camry", "Camry"),
            ("celica", "Celica"),
            ("corolla", "Corolla"),
            ("highlander", "Highlander"),
            ("land cruiser", "Land Cruiser"),
            ("rav4", "RAV4"),
            ("yaris", "Yaris"),
        ],
        "volkswagen": [
            ("arteon", "Arteon"),
            ("golf", "Golf"),
            ("passat", "Passat"),
            ("polo", "Polo"),
            ("tiguan", "Tiguan"),
            ("touareg", "Touareg"),
        ],
        "volvo": [
            ("s60", "S60"),
            ("v60", "V60"),
            ("xc40", "XC40"),
            ("xc60", "XC60"),
            ("xc90", "XC90"),
        ],
    }

    marque = models.CharField(max_length=30, choices=MARQUE, default="Marque")
    modele = models.CharField(choices=MODELE, max_length=50, default="Modele")
    couleur = models.CharField(choices=COULEUR, max_length=50, default="Couleur")
    type_moteur = models.CharField(
        choices=TYPE_MOTEUR, max_length=50, verbose_name="Moteur"
    )
    places = models.CharField(choices=PLACES, default="Nombre de places")
    immatriculation = models.CharField(max_length=10)
    annee = models.IntegerField(choices=get_year_choices(), default=datetime.now().year)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="voiture",
        verbose_name="Utilisateur",
    )

    class Meta:
        verbose_name = "Voiture"
        verbose_name_plural = "Voitures"

    def places_disponibles(self):
        return self.places - self.places_reserver

    def __str__(self):
        return f"{ self.marque} {self.modele}"


class TrajetProposer(models.Model):

    PLACES = [
        (1, "1 place"),
        (2, "2 places"),
        (3, "3 places"),
        (4, "4 places"),
        (5, "5 places"),
        (6, "6 places"),
    ]
    ETAT = [
        ("Disponible", "Disponible"),
        ("En cours", "Demarrer"),
        ("Terminé", "Terminé"),
        ("Annulé", "Annulé"),
    ]
    etat = models.CharField(choices=ETAT, max_length=15, default="Disponible")
    trajet_rembourser = models.BooleanField(default=False)
    chauffeur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chauffeur"
    )
    passager = models.ManyToManyField(
        User, through="ReservationTrajet", related_name="passager"
    )
    ville_depart = models.CharField(max_length=50)
    ville_arrivee = models.CharField(max_length=50)
    date = models.DateField(default=date.today)
    heure = models.TimeField(blank=True, default=now)
    places = models.IntegerField(choices=PLACES)
    prix = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Prix par passager",
    )
    total_payer = models.DecimalField(
        max_digits=5, decimal_places=2, blank=True, null=True, default=Decimal("0.00")
    )
    temps_trajet = models.DurationField(blank=False, null=False)
    voiture = models.ForeignKey(
        "Voiture",
        on_delete=models.CASCADE,
        related_name="voiture",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        verbose_name = "Trajet proposé"
        verbose_name_plural = "Trajets proposés"

    def mise_a_jour_total_payer(self):
        total_paye = 0
        reservations = ReservationTrajet.objects.filter(trajet_reserver=self)
        for reservation in reservations:
            if reservation.prix_par_passager is not None and self.prix is not None:
                total_paye += reservation.prix_par_passager * reservation.places
            else:
                total_paye += 0

        self.total_payer = total_paye
        self.save()

    def __str__(self):
        return f"{self.ville_depart} -> {self.ville_arrivee} {self.date} {self.heure}"


class Preference(models.Model):
    FUMEUR = [
        ("Fumeur", "fumeur accepté"),
        ("Non\fumeur", "non fumeur"),
    ]
    ANIMAUX = [
        ("Animaux", "animaux autorisés"),
        ("Pas_d'animaux", "pas d'animaux"),
    ]
    EXIGENCES_PARTICULIERES = [
        ("silence", "Silence pendant le trajet"),
        ("bagages_limites", "Bagages limités"),
        ("musique", "Musique pendant le trajet"),
        ("ponctualite", "Ponctualité obligatoire"),
        ("nourriture_non_autorisee", "Pas de nourriture à bord"),
        ("conduite_partagee", "Partager la conduite"),
    ]
    exigences_particulieres = models.CharField(
        choices=EXIGENCES_PARTICULIERES,
        max_length=50,
        default="Pas d'exigences particulières",
        verbose_name="Preference en plus",
    )
    exigences_personnelles = models.TextField(
        max_length=500, null=True, blank=True, verbose_name="Preferences personnelles"
    )
    fumeur = models.CharField(choices=FUMEUR, max_length=50, default="Non_fumeur")
    animaux = models.CharField(choices=ANIMAUX, max_length=50, default="Animaux")
    user_preference = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="preference",
        verbose_name="Utilisateur concerné",
    )

    class Meta:
        verbose_name = "Préférence de l'utilisateur"
        verbose_name_plural = "Préférences des utilisateurs"

    def __str__(self):
        return f"{self.fumeur} {self.animaux}{ self.get_fumeur_display() } { self.get_animaux_display() } {self.get_exigences_particulieres_display()} {self.exigences_personnelles}"


class ReservationTrajet(models.Model):
    ETAT_PAIEMENT = [
        ("Payer", "Payer"),
        ("En attente", "En attente"),
        ("Refuser", "Refuser"),
    ]

    ETAT_RESERVATION = [
        ("Reserver", "Réservé"),
        ("Terminé", "Terminé"),
        ("Annulé", "Annulé"),
    ]
    trajet_reserver = models.ForeignKey(
        TrajetProposer,
        on_delete=models.SET_NULL,
        related_name="reservations",
        null=True,
        blank=True,
    )
    passager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name="reservation_passager",
        null=True,
        blank=True,
    )
    prix_par_passager = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("0.00")
    )
    places = models.IntegerField(choices=TrajetProposer.PLACES, blank=True, null=True)

    etat_reservation = models.CharField(
        choices=ETAT_RESERVATION,
        default="Reserver",
        max_length=20,
        verbose_name="Etat de la réservation",
    )
    reservation_rembourser = models.BooleanField(default=False)

    etat_paiement = models.CharField(
        choices=ETAT_PAIEMENT,
        default="Payer",
        max_length=20,
        verbose_name="Etat du paiement",
    )
    trajet_payer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Réservation de trajet"
        verbose_name_plural = "Réservations de trajets"

    def paiement_passager(self, places_reservees):
        prix_total = self.trajet_reserver.prix * places_reservees
        if self.pk:
            self.places += places_reservees
            self.prix_par_passager += prix_total
        else:
            self.places = places_reservees
            self.prix_par_passager = prix_total
        self.save()

        self.trajet_reserver.mise_a_jour_total_payer()

        credit_user = CreditUser.objects.get(user=self.passager)
        credit_user.credit -= prix_total
        credit_user.save()
        return self

    @classmethod
    def paiement_total_passager(cls, user, trajet=None):
        filtre = {"passager": user, "etat_reservation": "Reserver"}
        if trajet:
            # Filtrer par trajet spécifique
            filtre["trajet_reserver"] = trajet

        total_paye = cls.objects.filter(**filtre).aggregate(
            total=Sum("prix_par_passager")
        )["total"]

        return total_paye if total_paye else 0

    def __str__(self):
        return f"{self.passager} a réservé {self.places} places pour le trajet {self.trajet_reserver}d'un montant de {self.prix_par_passager} €"


class ChangerStatutTrajet(models.Model):

    statut = models.CharField(
        choices=TrajetProposer.ETAT, max_length=15, default="Disponible"
    )
    trajet = models.ForeignKey(
        TrajetProposer,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="statut",
    )
    modified_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Changer le statut du trajet"
        verbose_name_plural = "Changer le statut des trajets"

    def __str__(self):
        return f"Le statut du trajet {self.trajet} a été modifié en {self.statut} le {self.modified_at}"
