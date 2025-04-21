from django.contrib.auth.models import User

def is_superuser_or_moderateur(user):
    return isinstance(user, User) and (
        user.is_superuser or user.groups.filter(name='moderateur').exists()
    )
