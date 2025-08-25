from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class MultiFieldModelBackend(ModelBackend):
    """
    Login: email, username yoki phone orqali ruxsat beriladi
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = None
        for field in ['username', 'email', 'phone']:
            try:
                kwargs = {field: username}
                user = UserModel.objects.get(**kwargs)
                if user.check_password(password):
                    return user
            except UserModel.DoesNotExist:
                continue
        return None
