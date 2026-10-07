from django.apps import AppConfig


class CatalogConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "catalog"

    def ready(self):
        """Подключить сигналы сброса кеша при старте приложения."""
        import catalog.signals  # noqa: F401
