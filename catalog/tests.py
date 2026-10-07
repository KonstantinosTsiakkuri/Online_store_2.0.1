"""Тесты кеширования: сервис списка товаров категории, сигналы, страницы."""

from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from catalog.models import Category, Product
from catalog.services import get_products_by_category
from users.models import User

LOCMEM_CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}


@override_settings(CACHES=LOCMEM_CACHES)
class CategoryServiceCacheTests(TestCase):
    """Сервис get_products_by_category и его низкоуровневый кеш."""

    def setUp(self):
        cache.clear()
        self.category = Category.objects.create(name="Смартфоны")
        self.other_category = Category.objects.create(name="Ноутбуки")
        self.phone = Product.objects.create(name="Телефон", category=self.category, price="100.00")
        self.laptop = Product.objects.create(name="Ноутбук", category=self.other_category, price="500.00")
        cache.clear()  # создание товаров сбросило ключи сигналами — начинаем с пустого кеша

    def test_returns_only_products_of_given_category(self):
        products = get_products_by_category(self.category.pk)
        self.assertEqual(products, [self.phone])

    def test_result_is_list_not_queryset(self):
        self.assertIsInstance(get_products_by_category(self.category.pk), list)

    def test_cache_key_has_exact_format(self):
        get_products_by_category(self.category.pk)
        self.assertIsNotNone(cache.get(f"category_{self.category.pk}"))

    def test_second_call_makes_no_queries(self):
        get_products_by_category(self.category.pk)
        with self.assertNumQueries(0):
            get_products_by_category(self.category.pk)

    def test_empty_category_is_cached_too(self):
        empty = Category.objects.create(name="Пустая")
        self.assertEqual(get_products_by_category(empty.pk), [])
        self.assertEqual(cache.get(f"category_{empty.pk}"), [])
        with self.assertNumQueries(0):
            self.assertEqual(get_products_by_category(empty.pk), [])

    def test_saving_product_invalidates_cache(self):
        get_products_by_category(self.category.pk)
        self.assertIsNotNone(cache.get(f"category_{self.category.pk}"))
        self.phone.price = "150.00"
        self.phone.save()
        self.assertIsNone(cache.get(f"category_{self.category.pk}"))

    def test_creating_product_invalidates_cache(self):
        get_products_by_category(self.category.pk)
        Product.objects.create(name="Новый телефон", category=self.category, price="10.00")
        self.assertIsNone(cache.get(f"category_{self.category.pk}"))
        self.assertEqual(len(get_products_by_category(self.category.pk)), 2)

    def test_deleting_product_invalidates_cache(self):
        get_products_by_category(self.category.pk)
        self.phone.delete()
        self.assertIsNone(cache.get(f"category_{self.category.pk}"))
        self.assertEqual(get_products_by_category(self.category.pk), [])

    def test_moving_product_invalidates_old_and_new_category(self):
        get_products_by_category(self.category.pk)
        get_products_by_category(self.other_category.pk)
        self.phone.category = self.other_category
        self.phone.save()
        self.assertIsNone(cache.get(f"category_{self.category.pk}"))
        self.assertIsNone(cache.get(f"category_{self.other_category.pk}"))


@override_settings(CACHES=LOCMEM_CACHES)
class CategoryProductsViewTests(TestCase):
    """Страница товаров категории."""

    def setUp(self):
        cache.clear()
        self.category = Category.objects.create(name="Смартфоны", description="Мобильные телефоны")
        self.other_category = Category.objects.create(name="Ноутбуки")
        Product.objects.create(name="Айфон", category=self.category, price="100.00")
        Product.objects.create(name="Самсунг", category=self.category, price="90.00")
        Product.objects.create(name="Макбук", category=self.other_category, price="500.00")

    def test_returns_200_with_own_products_only(self):
        response = self.client.get(reverse("catalog:category_products", args=[self.category.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Айфон")
        self.assertContains(response, "Самсунг")
        self.assertNotContains(response, "Макбук")
        self.assertContains(response, "Мобильные телефоны")

    def test_unknown_category_returns_404_and_does_not_cache(self):
        response = self.client.get(reverse("catalog:category_products", args=[99999]))
        self.assertEqual(response.status_code, 404)
        self.assertIsNone(cache.get("category_99999"))

    def test_empty_category_shows_message(self):
        empty = Category.objects.create(name="Пустая")
        response = self.client.get(reverse("catalog:category_products", args=[empty.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "В этой категории пока нет товаров")

    def test_second_request_makes_no_product_queries(self):
        url = reverse("catalog:category_products", args=[self.category.pk])
        self.client.get(url)
        with self.assertNumQueries(1):  # остаётся только get_object_or_404(Category)
            self.client.get(url)


@override_settings(CACHES=LOCMEM_CACHES)
class ProductDetailCacheTests(TestCase):
    """Кеширование страницы товара (cache_page)."""

    def setUp(self):
        cache.clear()
        self.category = Category.objects.create(name="Смартфоны")
        self.owner = User.objects.create_user(email="owner@example.com", password="StrongPass123")
        self.stranger = User.objects.create_user(email="stranger@example.com", password="StrongPass123")
        self.product = Product.objects.create(name="Айфон", category=self.category, price="100.00", owner=self.owner)
        self.url = reverse("catalog:product_detail", args=[self.product.pk])

    def test_detail_returns_200_for_authenticated_user(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Айфон")

    def test_detail_links_to_category_page(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url)
        self.assertContains(response, reverse("catalog:category_products", args=[self.category.pk]))

    def test_detail_response_varies_on_cookie(self):
        self.client.force_login(self.owner)
        response = self.client.get(self.url)
        self.assertIn("Cookie", response.headers.get("Vary", ""))

    def test_authenticated_page_is_served_from_cache_on_second_request(self):
        self.client.force_login(self.owner)
        self.client.get(self.url)
        # Второй запрос — из кеша: ни товар, ни пользователя из БД не читаем.
        with self.assertNumQueries(0):
            response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_404_is_not_cached(self):
        self.client.force_login(self.owner)
        missing = reverse("catalog:product_detail", args=[99999])
        self.assertEqual(self.client.get(missing).status_code, 404)
        Product.objects.create(id=99999, name="Появился", category=self.category, price="1.00")
        self.assertEqual(self.client.get(missing).status_code, 200)

    def test_anonymous_redirect_is_not_cached(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.url).status_code, 200)

    def test_403_on_update_is_not_cached(self):
        update_url = reverse("catalog:product_update", args=[self.product.pk])
        self.client.force_login(self.stranger)
        self.assertEqual(self.client.get(update_url).status_code, 403)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(update_url).status_code, 200)
