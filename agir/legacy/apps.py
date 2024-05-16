from django.apps import AppConfig


class LegacyConfig(AppConfig):
    name = "agir.legacy"

    def ready(self):
        from . import europeennes2019
        from . import presidentielle2017
