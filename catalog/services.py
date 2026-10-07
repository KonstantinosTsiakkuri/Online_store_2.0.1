"""Бизнес-логика каталога: выборки товаров с низкоуровневым кешированием."""

from django.conf import settings
from django.core.cache import cache

from catalog.models import Product


def get_products_by_category(category_id: int) -> list[Product]:
    """
    Вернуть список всех товаров указанной категории.

    Результат кешируется под ключом ``category_{category_id}`` на
    ``settings.CACHE_TTL_CATEGORY_PRODUCTS`` секунд. Фильтр по публикации не применяется:
    публичная главная страница тоже показывает все товары, поведение единообразно.
    """
    key = f"category_{category_id}"
    products = cache.get(key)

    # Именно `is None`, а не `not products`: пустая категория (пустой список) тоже
    # должна кешироваться, иначе за ней каждый раз ходили бы в базу.
    if products is None:
        # list(), а не ленивый QuerySet: в кеш кладём уже вычисленный результат.
        products = list(Product.objects.filter(category_id=category_id).select_related("category"))
        cache.set(key, products, settings.CACHE_TTL_CATEGORY_PRODUCTS)

    return products
