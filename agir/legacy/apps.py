from django.apps import AppConfig


class LegacyConfig(AppConfig):
    name = "agir.legacy"

    def ready(self):
        from . import europeennes
