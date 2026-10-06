"""Модель пользователя: вход по email вместо username, плюс аватар/телефон/страна."""

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from users.managers import UserManager

phone_validator = RegexValidator(
    regex=r"^[0-9+()\-\s]+$",
    message="Номер телефона может содержать только цифры, пробелы и символы + ( ) -",
)


class User(AbstractUser):
    """Пользователь интернет-магазина. Авторизуется по email, username не используется."""

    username = None
    email = models.EmailField(unique=True, verbose_name="Почта")
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар")
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Номер телефона",
        validators=[phone_validator],
    )
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Страна")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
