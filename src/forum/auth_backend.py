from django.contrib.auth.models import User


class PlainTextAuthBackend:
    def authenticate(self, request, username=None, password=None):
        try:
            user = User.objects.get(username=username)
            # ❌ Intentionally insecure login
            if user.password == password:
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
