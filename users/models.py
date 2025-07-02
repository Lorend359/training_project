from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Менеджер для кастомной модели пользователя."""

    def create_user(self, email: str, full_name: str, password: str = None, **extra_fields):
        """
        Создаёт и возвращает обычного пользователя.
        Email обязателен, т.к. он используется как логин.
        """
        if not email:
            raise ValueError("Email обязателен для создания пользователя")

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email: str, full_name: str, password: str = None, **extra_fields):
        """
        Создаёт и возвращает суперпользователя.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, full_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Кастомная модель пользователя. Используется email вместо username.
    Добавлено поле ФИО.
    """

    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.full_name} <{self.email}>"


# Файл: users/models.py
# Комментарии:

# Используем AbstractBaseUser + PermissionsMixin, т.к. хотим:
# - заменить username на email
# - добавить поле ФИО (обязательно для преподавателей)
# - оставить возможность логиниться через email
# - управлять правами (через PermissionsMixin)

# UserManager нужен для правильного создания пользователя и суперпользователя
# (иначе команда createsuperuser работать не будет)
