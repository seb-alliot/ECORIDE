
from itsdangerous import URLSafeTimedSerializer
from django.conf import settings


def reservation_token(username):
    securite = URLSafeTimedSerializer(settings.SECRET_KEY)
    return securite.dumps(username, salt="avis-covoiturage")