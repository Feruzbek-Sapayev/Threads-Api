from django.db import models
import shortuuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager
from django.core.validators import RegexValidator, MinLengthValidator



username_validator = RegexValidator(
    regex=r'^(?!.*[._]{2})(?![._])[a-zA-Z0-9._]{1,30}(?<![._])$',
    message=(
        "Username faqat harflar, raqamlar, nuqta (.) va pastki chiziq (_) dan iborat bo'lishi kerak. "
        "Username '.' yoki '_' bilan boshlanmasligi yoki tugamasligi va ketma-ket ikki '.' yoki '__' bo'lmasligi kerak."
    )
)


def generate_shortuuid():
    return shortuuid.uuid()[:11]

def random_file_path(instance, filename):
    ext = filename.split('.')[-1]
    random_name = generate_shortuuid()
    username = instance.username
    return f'uploads/users/{username}/avatar/{random_name}.{ext}'


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, validators=[username_validator, MinLengthValidator(3, message="Username kamida 3 ta belgidan iborat bo'lishi kerak.")])
    email = models.EmailField(max_length=150, unique=True)
    phone = models.CharField(max_length=13, unique=True)
    fullname = models.CharField(max_length=150)
    bio = models.CharField(max_length=150, null=True, blank=True)
    photo = models.ImageField(verbose_name="profile_picture", upload_to=random_file_path, null=True, blank=True)
    link = models.URLField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'  # bu ishlatiladi lekin custom backendda override qilinadi
    REQUIRED_FIELDS = ['email', 'phone']

    def __str__(self):
        return self.username
    

class UserFollow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'  # Men kimlarga obuna bo‘lganman
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'  # Menga kimlar obuna bo‘lgan
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')  # Bir odamni ikki marta follow qilib bo‘lmaydi

    def __str__(self):
        return f"{self.follower} ➡️ {self.following}"