from django.conf import settings
from ....models import  Voiture, ChoixRole, Preference, User
from ....models import CreditUser, AdresseUser


def initialisation_template(request):
    user = request.user
    role = None
    preference = None
    adresse_user = None
    voiture = None
    credit = None
    is_moderateur = False
    admin = False
    credit_superuser = None


    if request.user.is_authenticated:
        try:
            admin = request.user.groups.filter(name='admin').exists()
            is_moderateur = request.user.groups.filter(name='moderateur').exists()
            credit = CreditUser.objects.get(user=user)
            superuser = User.objects.filter(username='ECORIDE').first()
            credit_superuser = CreditUser.objects.filter(user=superuser).first()
            voiture = Voiture.objects.filter(user=user)
            role = ChoixRole.objects.filter(user=user).first()
            preference = Preference.objects.filter(user_preference=user).first()
            adresse_user = AdresseUser.objects.filter(user=user).first()
            if adresse_user is None:
                adresse_user = AdresseUser(user=user, email=user.email)
        except CreditUser.DoesNotExist:
            credit = None

    return {
        'photo_default_url': f"{settings.MEDIA_URL}photo_default/photo_default.jpg",

        #utilisateur
        "credit_superuser": credit_superuser,
        "admin": admin,
        "is_moderateur": is_moderateur,
        "role": role,
        "preference": preference,
        'voiture': voiture,
        "adresse_user": adresse_user,
        "credit": credit,
    }
