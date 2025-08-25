from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    def create_user(self, username, email, phone, password=None, **extra_fields):
        if not username and not email and not phone:
            raise ValueError("Foydalanuvchi uchun kamida bitta login identifikator kerak (email, username yoki telefon)")
        if email:
            email = self.normalize_email(email)

        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        
        # ✅ Parolni tekshirish
        validate_password(password, user)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, phone, password, **extra_fields)
