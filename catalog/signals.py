"""Сигналы приложения catalog: сброс кеша списка товаров категории при изменении товаров."""

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from catalog.models import Product


def _category_cache_key(category_id) -> str:
    """Ключ кеша списка товаров категории — ровно такой же, как в catalog.services."""
    return f"category_{category_id}"


@receiver(pre_save, sender=Product)
def remember_old_category(sender, instance, **kwargs):
    """
    Перед сохранением запомнить прежнюю категорию товара.

    Если товар переносят в другую категорию, нужно сбросить кеш и новой, и старой —
    старое значение после save() в самом объекте уже недоступно, поэтому берём его из БД.
    """
    instance._old_category_id = None
    if instance.pk:
        instance._old_category_id = (
            Product.objects.filter(pk=instance.pk).values_list("category_id", flat=True).first()
        )


@receiver(post_save, sender=Product)
def invalidate_category_cache_on_save(sender, instance, **kwargs):
    """После сохранения товара сбросить кеш его категории (и старой, если категория сменилась)."""
    cache.delete(_category_cache_key(instance.category_id))
    old_category_id = getattr(instance, "_old_category_id", None)
    if old_category_id is not None and old_category_id != instance.category_id:
        cache.delete(_category_cache_key(old_category_id))


@receiver(post_delete, sender=Product)
def invalidate_category_cache_on_delete(sender, instance, **kwargs):
    """После удаления товара сбросить кеш его категории."""
    cache.delete(_category_cache_key(instance.category_id))
