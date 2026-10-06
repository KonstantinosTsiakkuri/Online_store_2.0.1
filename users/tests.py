"""Тесты аутентификации: регистрация, вход и ограничение доступа к товарам."""

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.models import Category, Product
from users.models import User

LOCMEM_EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


class AnonymousAccessTests(TestCase):
    """Какие страницы видит аноним, а какие требуют входа."""

    @classmethod
    def setUpTestData(cls):
        """Одна категория и один товар — достаточно для проверки маршрутов."""
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.product = Product.objects.create(
            name="Тестовый товар",
            category=cls.category,
            price="100.00",
        )

    def test_product_list_is_public(self):
        """Список товаров открыт анониму."""
        response = self.client.get(reverse("catalog:home"))
        self.assertEqual(response.status_code, 200)

    def test_product_detail_requires_login(self):
        """Детальная страница товара редиректит анонима на вход."""
        url = reverse("catalog:product_detail", args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_product_create_requires_login(self):
        """Создание товара редиректит анонима на вход."""
        response = self.client.get(reverse("catalog:product_create"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_product_update_requires_login(self):
        """Редактирование товара редиректит анонима на вход."""
        url = reverse("catalog:product_update", args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_product_delete_requires_login(self):
        """Удаление товара редиректит анонима на вход."""
        url = reverse("catalog:product_delete", args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response.url)

    def test_register_page_is_public(self):
        """Страница регистрации открыта анониму."""
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_login_page_is_public(self):
        """Страница входа открыта анониму."""
        response = self.client.get(reverse("users:login"))
        self.assertEqual(response.status_code, 200)


class AuthenticatedAccessTests(TestCase):
    """Доступ к товарам для уже вошедшего пользователя."""

    @classmethod
    def setUpTestData(cls):
        cls.category = Category.objects.create(name="Тестовая категория")
        cls.product = Product.objects.create(
            name="Тестовый товар",
            category=cls.category,
            price="100.00",
        )

    def setUp(self):
        """Перед каждым тестом логинимся под свежесозданным пользователем."""
        self.user = User.objects.create_user(email="buyer@example.com", password="StrongPass123")
        self.client.force_login(self.user)

    def test_product_detail_returns_200(self):
        url = reverse("catalog:product_detail", args=[self.product.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_product_create_returns_200(self):
        response = self.client.get(reverse("catalog:product_create"))
        self.assertEqual(response.status_code, 200)


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL_BACKEND)
class RegistrationTests(TestCase):
    """Регистрация: успешные и ошибочные сценарии."""

    def test_valid_registration_creates_user_and_sends_email(self):
        """Корректные данные создают пользователя и отправляют ровно одно письмо."""
        response = self.client.post(
            reverse("users:register"),
            data={
                "email": "newuser@example.com",
                "password1": "StrongPass123",
                "password2": "StrongPass123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["newuser@example.com"])

    def test_password_mismatch_does_not_create_user(self):
        """Несовпадающие пароли — пользователь не создаётся, форма возвращает ошибку."""
        response = self.client.post(
            reverse("users:register"),
            data={
                "email": "mismatch@example.com",
                "password1": "StrongPass123",
                "password2": "DifferentPass456",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="mismatch@example.com").exists())
        self.assertIn("password2", response.context["form"].errors)
        self.assertEqual(len(mail.outbox), 0)

    def test_duplicate_email_does_not_create_user(self):
        """Регистрация на уже занятый email не создаёт второго пользователя."""
        User.objects.create_user(email="taken@example.com", password="StrongPass123")
        response = self.client.post(
            reverse("users:register"),
            data={
                "email": "taken@example.com",
                "password1": "AnotherPass123",
                "password2": "AnotherPass123",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email="taken@example.com").count(), 1)
        self.assertIn("email", response.context["form"].errors)


class LoginTests(TestCase):
    """Вход по email и паролю."""

    def setUp(self):
        self.user = User.objects.create_user(email="login@example.com", password="StrongPass123")

    def test_correct_credentials_log_in(self):
        """Верная пара email/пароль логинит пользователя — редирект, и сессия реально авторизована."""
        response = self.client.post(
            reverse("users:login"),
            data={"username": "login@example.com", "password": "StrongPass123"},
        )
        self.assertEqual(response.status_code, 302)
        # Сессия сохраняется в self.client, поэтому следующий запрос в этом же
        # тесте уже должен проходить как авторизованный пользователь.
        protected_response = self.client.get(reverse("catalog:product_create"))
        self.assertEqual(protected_response.status_code, 200)

    def test_wrong_password_shows_form_error(self):
        """Неверный пароль — 200 и ошибка формы, пользователь не залогинен."""
        response = self.client.post(
            reverse("users:login"),
            data={"username": "login@example.com", "password": "WrongPassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
