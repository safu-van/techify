from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("email should be given")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


# Custom User
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    referral_code = models.CharField(max_length=8, unique=True, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = CustomUserManager()
