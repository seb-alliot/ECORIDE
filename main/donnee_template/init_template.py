from django.conf import settings
from ..models import  Voiture, ChoixRole, Preference
from ..models import CreditUser, AdresseUser

def initialisation_template(request):
    photo_default_url = settings.MEDIA_URL + "photo_default/photo_default.jpg"
    user = request.user

    if request.user.is_authenticated:
        try:
            is_moderateur = request.user.groups.filter(name='moderateur').exists()
            credit = CreditUser.objects.get(user=user)
            voiture = Voiture.objects.filter(user=user)
            role = ChoixRole.objects.filter(user=user).first()
            preference = Preference.objects.filter(user_preference=user).first()
            adresse_user = AdresseUser.objects.filter(user=user).first()
            if adresse_user is None:
                adresse_user = AdresseUser(user=user, email=user.email)
        except CreditUser.DoesNotExist:
            credit = None

    if user.is_anonymous:
        credit = None
        adresse_user = None
        voiture = None
        role = None
        preference = None
        is_moderateur = False

    context = {
        #Photo par defaut
        'photo_default_url': photo_default_url,

        #utilisateur
        "is_moderateur": is_moderateur,
        "role": role,
        "preference": preference,
        'voiture': voiture,
        "adresse_user": adresse_user,

        "credit": credit,
    }
    return context