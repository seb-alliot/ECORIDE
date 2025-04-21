from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from django.conf import settings

def confirm_token(token, expiration=259200):  # 3 jours en secondes
    signature = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        return signature.loads(token, salt="avis-covoiturage", max_age=expiration)
    except BadSignature:
        # Si l'utilisateur n'est pas le bon
        return None
    except SignatureExpired:
        # Si le token a expiré
        return None