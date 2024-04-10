from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class AuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user_model = get_user_model()
        try:
            # Имя пользователя нечувствительно к регистру
            user = user_model.objects.get(username__iexact=username)
        except user_model.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
