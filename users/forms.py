"""Формы приложения users: регистрация и вход по email."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from catalog.forms import StyledFormMixin
from users.models import User


class UserRegisterForm(StyledFormMixin, UserCreationForm):
    """Форма регистрации: email + пароль + подтверждение пароля (поля password1/password2 — из UserCreationForm)."""

    class Meta:
        model = User
        fields = ("email",)

    def __init__(self, *args, **kwargs):
        """Навесить Bootstrap-стили на все поля формы, включая унаследованные password1/password2."""
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_styles()


class UserLoginForm(StyledFormMixin, AuthenticationForm):
    """Форма входа: поле username переподписано и отрисовывается как email."""

    username = forms.EmailField(
        label="Почта",
        widget=forms.EmailInput(attrs={"autofocus": True}),
    )

    def __init__(self, *args, **kwargs):
        """Навесить Bootstrap-стили на все поля формы."""
        super().__init__(*args, **kwargs)
        self._apply_bootstrap_styles()
