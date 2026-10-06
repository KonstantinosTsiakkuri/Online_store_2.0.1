"""Контроллеры приложения users: регистрация, вход, выход."""

import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView

from users.forms import UserLoginForm, UserRegisterForm

logger = logging.getLogger(__name__)


class UserRegisterView(CreateView):
    """Регистрация нового пользователя. После успешного создания отправляет приветственное письмо."""

    form_class = UserRegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):
        """Сохранить пользователя, сразу залогинить его и отправить приветственное письмо."""
        response = super().form_valid(form)
        login(self.request, self.object)
        self._send_welcome_email(self.object.email)
        messages.success(self.request, "Регистрация прошла успешно! Добро пожаловать.")
        return response

    def _send_welcome_email(self, email):
        """
        Отправить письмо отдельно от основной логики, чтобы сбой почты не мешал регистрации.

        Пользователь должен быть создан в любом случае: ошибки SMTP (SMTPException)
        и сетевые ошибки (OSError, в том числе TimeoutError) перехватываются,
        попадают в лог, а пользователю показывается предупреждение вместо падения страницы.
        """
        try:
            send_mail(
                subject="Добро пожаловать в интернет-магазин",
                message="Спасибо за регистрацию! Ваш аккаунт успешно создан.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except (SMTPException, OSError) as error:
            logger.error("Не удалось отправить приветственное письмо на %s: %s", email, error)
            messages.warning(
                self.request,
                "Аккаунт создан, но приветственное письмо отправить не удалось.",
            )


class UserLoginView(LoginView):
    """Вход по email и паролю."""

    authentication_form = UserLoginForm
    template_name = "users/login.html"
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    """Выход. В Django 5+ выполняется только по POST-запросу."""
