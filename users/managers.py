"""Менеджер пользовательской модели User (вход по email, а не по username)."""

from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Создаёт обычных и супер-пользователей по email вместо username."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Общая часть create_user/create_superuser: нормализовать email, захэшировать пароль, сохранить."""
        if not email:
            raise ValueError("Email обязателен для создания пользователя")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Создать обычного пользователя. is_staff и is_superuser по умолчанию выключены."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Создать суперпользователя для manage.py createsuperuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")

        return self._create_user(email, password, **extra_fields)
