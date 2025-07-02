
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from django.conf import settings


def reservation_token(username):
    s = URLSafeTimedSerializer(settings.SECRET_KEY)
    return s.dumps(username, salt="avis-covoiturage")