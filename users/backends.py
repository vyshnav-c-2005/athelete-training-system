from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameBackend(ModelBackend):
    """
    Custom authentication backend to login users using either email or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # 'username' argument might be passed as 'email' or 'username'
        if username is None:
            username = kwargs.get('email')
        
        if not username:
            return None

        try:
            # Check for user by username OR email (case insensitive)
            user = User.objects.get(
                Q(username__iexact=username) | Q(email__iexact=username)
            )
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Should not happen if unique constraints are enforced, but safe fallback
            return User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).order_by('id').first()
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
