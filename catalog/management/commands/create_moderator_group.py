"""Команда создания группы модераторов продуктов с нужными правами."""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from catalog.models import Product

GROUP_NAME = "Модератор продуктов"
PERMISSION_CODENAMES = ("can_unpublish_product", "delete_product")


class Command(BaseCommand):
    help = "Создаёт группу «Модератор продуктов» и назначает ей права на снятие с публикации и удаление товаров"

    def handle(self, *args, **options):
        group, _ = Group.objects.get_or_create(name=GROUP_NAME)

        content_type = ContentType.objects.get_for_model(Product)
        permissions = [
            Permission.objects.get(codename=codename, content_type=content_type) for codename in PERMISSION_CODENAMES
        ]
        group.permissions.set(permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f"Группа «{group.name}» готова, назначено прав: {len(permissions)} "
                f"({', '.join(p.codename for p in permissions)})"
            )
        )
