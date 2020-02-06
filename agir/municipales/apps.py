from django.apps import AppConfig


class MunicipalesConfig(AppConfig):
    name = "agir.municipales"

    def ready(self):
        from . import campagnes
