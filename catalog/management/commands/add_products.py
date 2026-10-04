"""Команда наполнения каталога данными из фикстур."""

from django.core.management import call_command
from django.core.management.base import BaseCommand

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Очищает каталог и заново загружает категории и продукты из фикстур"

    def handle(self, *args, **options):
        Product.objects.all().delete()
        Category.objects.all().delete()

        call_command("loaddata", "category.json")
        call_command("loaddata", "product.json")

        self.stdout.write(
            self.style.SUCCESS(
                f"Загружено категорий: {Category.objects.count()}, продуктов: {Product.objects.count()}"
            )
        )
