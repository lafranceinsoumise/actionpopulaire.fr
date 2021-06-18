from django.apps import AppConfig


class GestionConfig(AppConfig):
    name = "agir.gestion"
    verbose_name = "Gestion et comptes"

    def ready(self):
        from . import signals
