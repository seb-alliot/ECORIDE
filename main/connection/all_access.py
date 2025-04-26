from django.contrib.auth.models import User

def is_superuser_or_moderateur(user):
    return isinstance(user, User) and (
        # on vérifie si l'utilisateur est un superutilisateur ou appartient à un groupe spécifique comme 'moderateur' ou 'admin'
        user.is_superuser or user.groups.filter(name__in=['moderateur', 'admin']).exists()
    )